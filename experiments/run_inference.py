from pathlib import Path
import random
import argparse
import asyncio
import time
from tqdm import tqdm
from string import Template
from loguru import logger

from projects.utils.file_utils import read_yaml, read_jsonl, append_jsonl, write_yaml
from projects.models.gpt.async_inference import request_chatgpt
from projects.models.clova.async_inference import request_clova
from projects.suicide_contents.experiment.utils.prompt_utils import (
    generate_input_prompt, process_multiple_category_description
)
from projects.suicide_contents.data_utils.schema import ModelResponse
from projects.suicide_contents.experiment.utils.exp_utils import (
    get_multiclass_args, 
    get_multiclass_experimentname
)
'''
TODO: english
'''
CONFIG = read_yaml('config/config.yaml')
CATEGORIES = CONFIG['CATEGORIES']
ENGLISH_CATEGORIES = CONFIG['ENGLISH_CATEGORIES']
MODEL_PARAMS = CONFIG['MODEL_PARAMS']

def process_fewshot_prompt(n_shot, input_content, image, english):
    # Load train dataset
    if english:
        train_data = read_jsonl(Path(__file__).parents[1] / "data" / "testset" / "final" / "train_english.jsonl")
    else:
        train_data = read_jsonl(Path(__file__).parents[1] / "data" / "testset" / "final" / "train.jsonl")

    fewshot_prompt_list = []
    for idx, category in enumerate(CATEGORIES):
        # Sampling fewshot data from category
        fewshot_data = [datum for datum in train_data if datum["human_labels"]["label_category"] == category]
        fewshot_data = random.sample(fewshot_data, n_shot)
        for fewshot_datum in fewshot_data:
            fewshot_input_prompt = generate_input_prompt(fewshot_datum, input_content, image)
            fewshot_prompt = f"\n{fewshot_input_prompt}\nSelected CATEGORY: CATEGORY {idx+1}\n"
            fewshot_prompt_list.append(fewshot_prompt)
    # Shuffle fewshot data category order
    fewshot_prompt_list = random.sample(fewshot_prompt_list, len(fewshot_prompt_list))
    fewshot_prompt = "".join(fewshot_prompt_list)

    return fewshot_prompt

async def inference_single_datum(datum, template, exp_name, input_content, model, model_params, image, categories):
    input_prompt_format = generate_input_prompt(datum, input_content, image)
    user_prompt = Template(template).substitute(input=input_prompt_format.strip())
    t0 = time.time()
    if 'gpt' in model:
        _, result, _, usage, _, _ = await request_chatgpt(
            model=model,
            system="",
            user=user_prompt,
            **model_params,
        )
    elif 'clova' in model:
        result, usage = await request_clova(
            request_text=user_prompt,
            **model_params,
        )
    inference_time = time.time() - t0
    # Postprocess
    predicted_category = None
    for idx, category_name in enumerate(categories):
        if category_name in result or str(idx+1) in result:
            predicted_category = category_name
            break
    # Hardwarning
    #assert predicted_category is not None, f"Cannot find predicted category in {result}"
    # Softwarning
    if predicted_category is None:
        logger.warning(f"Cannot find predicted category in {result}")
        predicted_category = ""

    # Save result as model_response
    model_response = ModelResponse(
        model=model,
        inference_parameters=model_params,
        inference_time=inference_time,
        num_token=usage,
        rationale="",
        category=predicted_category,
        subcategory="",
        raw_output = result,
    )
    datum["inferences"][exp_name] = model_response.model_dump()

    if DEBUG:
        logger.debug(f"\n{user_prompt}{result}\n")

    return datum


async def main(prompt, model, answer_idx, category_info, subcategory_info, n_shot, n_neg_shot, input_content, random_seed, sampling_method, english, image, extra_name):
    # Set variables
    model_params = MODEL_PARAMS[model]
    # Experiment name
    experiment_name = get_multiclass_experimentname(prompt, answer_idx, category_info, subcategory_info, n_shot, n_neg_shot, input_content, random_seed, sampling_method, model, english, image, extra_name)
    result_dir = Path(__file__).parent / "result_RQ3" / experiment_name # FIXME: Result Path f"result_RQ{N}"
    logger.debug(f"Running experiment: {experiment_name}") #NOTE: experiment_name

    # Prompt
    prompts = read_yaml(Path(__file__).parent / "config" /"prompts.yaml")
    user_template = prompts[prompt]

    # # Fewshot for all data
    # if n_shot > 0:
    #     fewshot_prompt = process_fewshot_prompt(n_shot, input_content, image)
    # else:
    #     fewshot_prompt = ''

    # Save condition
    condition = {
        "model": model,
        "model_params": MODEL_PARAMS,
    }
    write_yaml(condition, result_dir / "condition.yaml")
    # Data
    if english:
        data = read_jsonl(Path(__file__).parents[1] / "data" / "testset" / "final" / "test_english.jsonl")
    else:
        data = read_jsonl(Path(__file__).parents[1] / "data" / "testset" / "final" / "test.jsonl")

    # Debug
    if DEBUG:
        data = random.sample(data, 1)
    completed_data = read_jsonl(result_dir / "result.jsonl")
    completed_ids = set([datum["id"] for datum in completed_data])
    current_tasks = set()
    inference_data = []
    # Run all data
    for datum in tqdm(data):
        if datum["id"] in completed_ids:
            continue
        # Generate category prompt
        answer_category = datum["human_labels"]["label_category"]
        # Random category prompt with answer fixed
        if answer_idx >=0 :
            categories = random.sample(CATEGORIES, len(CATEGORIES))
            cur_answer_idx = categories.index(answer_category)
            categories[answer_idx], categories[cur_answer_idx] = categories[cur_answer_idx], categories[answer_idx]
        # Original category sequence
        else:
            categories = CATEGORIES
        # English
        if english: # FIXME: If english, the sequence of categories is fixed as original order
            categories = ENGLISH_CATEGORIES
        category_description_prompt, category_type_prompt = process_multiple_category_description(
            categories, category_info, subcategory_info, english
        )
        # Fewshot for each data
        if n_shot > 0:
            fewshot_prompt = process_fewshot_prompt(n_shot, input_content, image, english)
        else:
            fewshot_prompt = ''
        # Generate user prompt
        cur_user_template = Template(user_template).safe_substitute(
            category_description=category_description_prompt.strip(), 
            category_types=category_type_prompt.strip(),
            examples=fewshot_prompt
        )
        # Run single data
        task = asyncio.create_task(
            inference_single_datum(datum, cur_user_template, experiment_name, input_content, model, model_params, image, categories)
            )
        current_tasks.add(task)
        # Async worker queue
        if len(current_tasks) >= 10:
            done, current_tasks = await asyncio.wait(current_tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                inference_datum = task.result()
                if not DEBUG:
                    append_jsonl(inference_datum, result_dir / "result.jsonl")
                inference_data.append(inference_datum)
    # Wait for remaining tasks    
    if len(current_tasks) > 0:
        logger.debug(f"Wait for remaining tasks : {len(current_tasks)}")
        done, current_tasks = await asyncio.wait(current_tasks, return_when=asyncio.ALL_COMPLETED)
        for task in done:
            inference_datum = task.result()
            if not DEBUG:
                append_jsonl(inference_datum, result_dir / "result.jsonl")
            inference_data.append(inference_datum)
    
    return inference_data

if __name__ == "__main__":
    # Get args
    args = get_multiclass_args()
    # Check model
    assert 'gpt' in args.model or 'clova' in args.model
    # Set random seed
    random.seed(args.random_seed)
    # Debug
    global DEBUG
    DEBUG = args.debug

    asyncio.run(main(
        args.prompt,
        args.model,
        args.answer_idx,
        args.category_info,
        args.subcategory_info,
        args.n_shot,
        args.n_neg_shot,
        args.input_content,
        args.random_seed,
        args.sampling_method,
        args.english,
        args.image,
        args.extra_name
    ))