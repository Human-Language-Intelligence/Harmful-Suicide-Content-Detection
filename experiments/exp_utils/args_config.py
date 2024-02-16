import argparse

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_multiclass_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type = str, default = 'multiclass')
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-16k-0613", choices=["gpt-3.5-turbo-16k-0613", "gpt-4-0613", "gpt-4-1106-preview", 'clova'])
    parser.add_argument('--answer_idx', help='answer index of category', 
                        type=int, default=0, choices=[-1, 0, 1, 2, 3, 4])
    parser.add_argument("--category_info", type=str, default="both", choices=["name", "both"])
    parser.add_argument(
        "--subcategory_info", type=str, default="both", choices=["none", "name", "desc", "both"]
    )
    parser.add_argument("--n_shot", type=int, default=0)
    parser.add_argument("--n_neg_shot", type=int, default=0)
    parser.add_argument(
        "--input_content",
        type=str,
        default="allinput",
        choices=["allinput", "text_only", "text_image", "content_only", "context", "metadata", "all_except_image"],
    )
    parser.add_argument("--random_seed", type=int, default=42)
    parser.add_argument("--sampling_method", type=str, default="random", help="random or index_<start_index>")
    parser.add_argument("--debug", type=lambda x : str2bool(x), default=False)
    parser.add_argument("--english", type=lambda x : str2bool(x), default=False)
    parser.add_argument("--image", type=str, default="human", choices=["human", "gpt4", "vision"])
    parser.add_argument("--extra_name", type=str, default='basic')
    parser.add_argument("--filter_column", type=str, default="all", choices=["all", "image_description", "link_description", "context"])
    parser.add_argument("--generate_plot", action="store_true") # test only
    args = parser.parse_args()

    return args

def get_multiclass_experimentname(prompt, answer_idx, category_info, subcategory_info, n_shot, n_neg_shot, input_content, random_seed, sampling_method, model, english, image, extra_name):
    experiment_name = (
        f"{prompt}_{answer_idx}_{input_content}_{model}_{category_info}_{subcategory_info}"
    )
    if image != "human":
        experiment_name += f"_image{image}"
    if english:
        experiment_name += "_english"
    if n_shot > 0:
        experiment_name += f"_{n_shot}shot"
    if n_neg_shot > 0:
        experiment_name += f"_{n_neg_shot}negshot"
    if sampling_method != "random":
        experiment_name += f"_{sampling_method}"
    if random_seed != 42:
        experiment_name += f"_seed{random_seed}"
    if extra_name != 'basic':
        experiment_name += f"_{extra_name}"
    
    return experiment_name