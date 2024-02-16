from pathlib import Path

from projects.utils import read_jsonl, read_json
from string import Template
import re

def replace_tabs_and_newlines(input_string):
    result_string = re.sub(r'[\t\n]+', ' ', input_string)
    return result_string

def generate_input_prompt(datum, input_content, image):
    id = datum['id']
    content_text = replace_tabs_and_newlines(datum["content_text"])
    context = replace_tabs_and_newlines(datum["context"])
    link_description = replace_tabs_and_newlines(datum["link_description"])
    image_description = replace_tabs_and_newlines(datum["image_description"])
    source = datum["source"]
    metadata = ""
    if source == "twitter":
        source_meta = datum["twitter_source_meta"]
        user_meta = datum["twitter_user_meta"]
        if source_meta:
            metadata += source_meta
        if user_meta:
            metadata += user_meta
    elif source == "naver":
        source_meta = datum["naver_source_meta"]
        if source_meta:
            metadata += source_meta
    elif source == "dcinside":
        source_meta = datum["dcinside_source_meta"]
        if source_meta:
            metadata += source_meta
        user_meta = datum["dcinside_user_meta"]
        if user_meta:
            metadata += user_meta

    input_prompt = f"""CONTENT:
- TEXT: {content_text}"""
    if image_description != "" and input_content not in ["text_only", "all_except_image"]:
        if image == "gpt4":
            gpt4_image_file = Path(__file__).parents[2] / "data" / "testset" / "final" / "suplementary" / "gpt4image.json"
            gpt4_image_dict = read_json(gpt4_image_file)
            image_description = replace_tabs_and_newlines(gpt4_image_dict[id])
        input_prompt += f"\n- IMAGE: {image_description}"
    if link_description != "" and input_content not in ["text_only", "text_image"]:
        input_prompt += f"\n- LINK: {link_description}"
    if context != "" and input_content not in [
        "text_only",
        "text_image",
        "content_only",
        "metadata",
    ]:
        input_prompt += f"\nCONTEXT: {context}"
    if metadata != "" and input_content not in [
        "text_only",
        "text_image",
        "content_only",
        "context",
    ]:
        input_prompt += f"\nMETADATA: {metadata}"

    return input_prompt

def process_single_category_description(category_name, category_info, subcategory_info, english):
    # English or Korean
    if english:
        category_file_name = "categories_english_final.jsonl"
    else:
        category_file_name = "categories_final.jsonl"
    descriptions = read_jsonl(
        Path(__file__).parents[2] / "task_description" / category_file_name
    )
    description_dict = None
    for description in descriptions:
        if description["category"] == category_name:
            description_dict = description
            break
    assert description_dict is not None, f"Cannot find description for {category_name}"
    category_desc = description_dict["category_description"]

    # Category information
    if category_info == "both":
        if english:
            template = '**{category_name}** is {category_description}.'
        else:
            template = '**{category_name}**는 {category_description}이다.'
        prompt = template.format(category_name=category_name, category_description=category_desc)
    elif category_info == "name":
        template = '**{category_name}**'
        prompt = template.format(category_name=category_name)

    # Subcategory information
    if subcategory_info != "none":
        subcategories = description_dict["subcategories"]
        for subcategory in subcategories:
            subcategory_name = subcategory["subcategory"]
            subcategory_desc = subcategory["subcategory_description"]
            if subcategory_info == "name":
                prompt += f"\n\t- {subcategory_name}"
            elif subcategory_info == "desc" and subcategory_desc != "":
                prompt += f"\n\t- {subcategory_desc}"
            elif subcategory_info == "both":
                if subcategory_desc == "":
                    prompt += f"\n\t- {subcategory_name}"
                else:
                    prompt += f"\n\t- {subcategory_name}: {subcategory_desc}"

    return prompt

def process_multiple_category_description(category_names, category_info, subcategory_info, english):
    total_prompt = ""
    total_type_prompt = ""
    for idx, category_name in enumerate(category_names):
        category_prompt = process_single_category_description(category_name, category_info, subcategory_info, english)
        total_prompt += f"- CATEGORY {idx+1}: {category_prompt}\n"
    
    return total_prompt, total_type_prompt
