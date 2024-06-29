# Keep this file in the llava/serve directory

import argparse
import torch
import json
import re

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import process_images, tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria

import requests
from PIL import Image
from io import BytesIO
from transformers import TextStreamer
import os

def load_image(image_file):
    if image_file.startswith('http://') or image_file.startswith('https://'):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content)).convert('RGB')
    else:
        image = Image.open(image_file).convert('RGB')
    return image

def load_images_from_directory(directory):
    images = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(directory, filename)
            image = load_image(file_path)
            images.append(image)
    return images

def save_output_to_html(output, output_directory, input_image_filename):
    base_name, ext = os.path.splitext(os.path.basename(input_image_filename))
    output_file = os.path.join(output_directory, f"{base_name}_output.html")
    with open(output_file, "w") as f:
        f.write(output)
    
def save_response_to_jsonl(image_id, output, output_file):
    with open(output_file, 'a') as file:
        json_line = {"image_id": image_id, "output": output}
        file.write(json.dumps(json_line) + "\n")

def is_yes_or_no(value):
    # Normalize the string by removing unwanted characters and then lower case the result
    # Specifically allowing trailing "</s>" with or without a preceding dot
    normalized_value = re.sub(r'\.</s>$', '</s>', value.lower())  # Normalize ending with dot
    normalized_value = re.sub(r'</s>$', '', normalized_value)  # Remove the trailing "</s>"
    normalized_value = re.sub(r'[^a-zA-Z]', '', normalized_value)  # Remove other non-letters
    
    # Check if the normalized string is "yes" or "no"
    return normalized_value in ("yes", "no")

def main(args):

    if not args.output_directory.endswith('/'):
        args.output_directory += '/'
    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    # Model
    disable_torch_init()

    model_name = get_model_name_from_path(args.model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(args.model_path, args.model_base, model_name, args.load_8bit, args.load_4bit, device=args.device)

    # read jsonl file
    with open(args.qa_file, 'r') as file:
        for line in file:
            qa_pair = json.loads(line)
            image_filename = qa_pair["image"]
            question_id = qa_pair["question_id"]
            image = load_image(os.path.join(args.image_directory, image_filename))
             
            if 'llama-2' in model_name.lower():
                conv_mode = "llava_llama_2"
            elif "v1" in model_name.lower():
                conv_mode = "llava_v1"
            elif "mpt" in model_name.lower():
                conv_mode = "mpt"
            else:
                conv_mode = "llava_v0"

            if args.conv_mode is not None and conv_mode != args.conv_mode:
                print('[WARNING] the auto inferred conversation mode is {}, while `--conv-mode` is {}, using {}'.format(conv_mode, args.conv_mode, args.conv_mode))
            else:
                args.conv_mode = conv_mode

            conv = conv_templates[args.conv_mode].copy()
            if "mpt" in model_name.lower():
                roles = ('user', 'assistant')
            else:
                roles = conv.roles
            try:
                print(f"--------------PROCESSING NEW IMAGE: {image_filename}-------------------")

                image_tensor = process_images([image], image_processor, model.config)
                if type(image_tensor) is list:
                    image_tensor = [image.to(model.device, dtype=torch.float16) for image in image_tensor]
                else:
                    image_tensor = image_tensor.to(model.device, dtype=torch.float16)

                attempts = 1
                while True:
                    if args.debug:
                        print(f"{roles[0]}: {qa_pair['Q']}")

                    inp = qa_pair["Q"]
                    print(f"{roles[1]}: ", end="")

                    if image is not None:
                        # first message
                        if model.config.mm_use_im_start_end:
                            inp = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + inp
                        else:
                            inp = DEFAULT_IMAGE_TOKEN + '\n' + inp
                        conv.append_message(conv.roles[0], inp)
                        image = None
                    else:
                        # later messages
                        conv.append_message(conv.roles[0], inp)
                    conv.append_message(conv.roles[1], None)
                    prompt = conv.get_prompt()

                    input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).to(model.device)
                    stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
                    keywords = [stop_str]
                    stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)
                    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

                    with torch.inference_mode():
                        output_ids = model.generate(
                            input_ids,
                            images=image_tensor,
                            do_sample=True if args.temperature > 0 else False,
                            temperature=args.temperature,
                            max_new_tokens=args.max_new_tokens,
                            streamer=streamer,
                            use_cache=True,
                            stopping_criteria=[stopping_criteria])

                    output = tokenizer.decode(output_ids[0, input_ids.shape[1]:]).strip()
                    conv.messages[-1][-1] = output

                    if args.debug:
                        print("\n", {"prompt": prompt, "outputs": output}, "\n")
                    
                    if is_yes_or_no(output) or attempts >= 2:
                        with open(args.output_directory + "/results.jsonl", "a") as f:
                            f.write(json.dumps({"q_id": question_id, "image": image_filename, "pred": output, "actual": qa_pair["A"]}) + "\n")
                        if attempts >= 2:
                            print(f"Output: {output} is not in the correct format")
                        break
                    else: 
                        attempts += 1

            except Exception as e:
                print(f"Error processing image: {image_filename}")
                print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-directory", type=str, required=True, help="Directory containing input images")
    parser.add_argument("--qa-file", type=str, required=True, help="Path to the file containing QA pairs")
    parser.add_argument("--output-directory", type=str, required=True, help="Directory to save the output HTML file")
    parser.add_argument("--model-path", type=str, default="facebook/opt-350m")
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--image-file", type=str, required=False)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--conv-mode", type=str, default=None)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--load-8bit", action="store_true")
    parser.add_argument("--load-4bit", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args)
