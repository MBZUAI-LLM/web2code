import os
import json
import time
import base64
import requests

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def is_already_processed(output_jsonl_path, base_name):
    # if basename is already processed, skip
    if os.path.exists(output_jsonl_path):
        with open(output_jsonl_path, 'r') as file:
            
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    image_id = data.get("image_id")
                    if image_id == base_name:
                        print(f'Image {base_name} already processed.\n')
                        return True
            return False
    return False
          

def generate_responces(pred_dir, gt_dir, output_jsonl_path, api_key):

    # Set the headers
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    # Iterate over all files in pred_dir
    for pred_file in os.listdir(pred_dir):
        
        if pred_file.endswith(".png"):  # or any other image extension
            # Construct the full path for the predicted image
            pred_image_path = os.path.join(pred_dir, pred_file)

            # Extract the base name (without extension) and construct the corresponding ground truth path
            base_name = os.path.splitext(pred_file)[0]

            if is_already_processed(output_jsonl_path, base_name):
                continue

            # Check if the ground truth file exists
            gt_image_path = os.path.join(gt_dir, base_name + ".png")  # assuming ground truth images are also .jpg

            print(f"Processing image {gt_image_path}...")
            # Check if the ground truth file exists
            if os.path.exists(gt_image_path):
                # Getting the base64 string
                print(f"Encoding image {base_name}...")
                pred_base64_image = encode_image(pred_image_path)
                gt_base64_image = encode_image(gt_image_path)

            else:
                print(f"Ground truth image for {gt_image_path} not found.")
                continue # Change this line if you need to test all the files 
        
        else:
            # print(f"Skipping file {pred_file} as it is not an image.")
            continue
    
        payload = {
        "model":"gpt-4-turbo",
        "messages":[
            {
            "role": "system",
            "content": "You are an advanced AI model equipped with OCR and image processing capabilities, capable of analyzing visual elements in detail."
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": """
                        Your task is to assess two webpage images and output a score between 0 and 10 for each of the following questions.
                        If the answer to a question is a definite YES, output a score of 10, signifying perfect similarity.
                        Conversely, a definite NO should yield a score of 0, indicating no similarity.
                        For answers that fall in between, assign a score accordingly, where a higher number indicates a greater degree of similarity. Only provide the numerical score for each question, without any additional text.
                        Example contexts are provided for clarity. Examples provides the idea, but you can output any number in 0-10
                        range accordingly. Only output a comma separated list containing 10 numbers. DO NOT give score of 10 for any category unless otherwise the two images are identical.

                        Layout Consistency (Score: 0-10): Does the placement of headers, footers, and sidebars match in both webpages? (e.g., A score of 10 for identical layouts, 5 for similar but not exact placements, and 0 for completely different layouts.)
                        Element Alignment (Score: 0-10): Are elements like images, buttons, and text boxes aligned similarly on both pages? (e.g., A score of 10 for perfectly aligned elements, 6 for slight misalignments, and 0 for major misalignments.)
                        Proportional Accuracy (Score: 0-10): Do the sizes and aspect ratios of images, buttons, and text boxes appear consistent across both pages? (e.g., A score of 10 for exact proportions, 4 for noticeable size differences, and 0 for drastic inconsistencies.)
                        Visual Harmony (Score: 0-10): Do both webpages exhibit a similar level of visual harmony and balance in their design? (e.g., A score of 10 for harmonious designs, 5 for some dissonance, and 0 for clashing designs.)
                        
                        Color Scheme and Aesthetic Match (Score: 0-10): How closely do the color schemes of the two webpages align in terms of background and text colors? Evaluate the similarity in hues, saturation, and overall color aesthetics. (e.g., A score of 10 for perfectly matching color schemes, including identical hues and saturation levels, 6 for similar color palettes with minor variations, and 0 for starkly different color schemes that create entirely different visual impacts.)
                        Aesthetic Resemblance (Score: 0-10): Is the overall aesthetic appeal (modern, minimalistic, traditional, etc.) similar on both pages? (e.g., A score of 10 for identical aesthetics, 4 for somewhat similar but distinguishable styles, and 0 for completely different aesthetics.)
                        
                        Font Characteristics and Consistency (Score: 0-10): Assess the degree of consistency in font attributes across both webpages. This includes not only the font type and size but also the nuances of font style (italic, bold) and weight (light, regular, bold). (e.g., A score of 10 for complete uniformity in font type, size, style, and weight across both pages, 5 for consistency in font type and size but variations in style or weight, and 0 for wide disparities in font type, size, style, or weight, leading to a distinctly different textual appearance.)
                        Textual Content Match (Score: 0-10): Do the words and sentences match between the two webpages? (e.g., A score of 10 for identical text, 5 for some similar paragraphs or sections, and 0 for completely different textual content.)
                        Numeric and Special Character Accuracy (Score: 0-10): Are numbers, dates, and special characters (like email addresses) consistent between the two pages? (e.g., A score of 10 for exact matches, 6 for minor discrepancies, and 0 for major differences.)
                        
                        User Interface Consistency (Score: 0-10): Do the user interface elements (like menus, buttons, and forms) on both pages share a similar design language and appearance? (e.g., A score of 10 for identical UI elements, 6 for slight design variations, and 0 for completely different UI designs.)
                    """,
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{gt_base64_image}",
                },
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{pred_base64_image}",
                },
                },
            ],
            }
        ],
        "max_tokens":300,
        }
        attempt = 0
        while True:
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                
                data = response.json()
                print(data)
                content_str = data['choices'][0]['message']['content']

                # Append to JSONL file
                with open(output_jsonl_path, 'a') as file:
                    json_line = {"image_id": base_name, "output": content_str}
                    file.write(json.dumps(json_line) + "\n")
                    print(f'Image {base_name} processed successfully.\n')
                    break

            except Exception as e:
                print(f'Exception : {e}\n')
                
                attempt+=1

                if attempt >= 3:
                    print(f'Failed to process image: {base_name}\n')
                    break

                time.sleep(5)


def read_jsonl_and_get_outputs(file_path):

    total_images_processed=0
    vis_struct = 0
    color_aesthetic = 0
    textual_content = 0
    user_interface = 0
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                data = json.loads(line)
                image_id = data.get("image_id")
                output = data.get("output")

                try:
                    output_list=list(map(int, output.replace('\n', ',').strip(', ').split(',')))
                    if len(output_list) != 10:
                        print(f'Failed to process image: {image_id}')
                        continue
                    total_images_processed+=1
                    vis_struct+=sum(output_list[:4])/4
                    color_aesthetic+=sum(output_list[4:6])/2
                    textual_content+=sum(output_list[6:9])/3
                    user_interface+=output_list[9]
                except Exception as e:
                    print(f'Exception: {e}\n')
                    continue

        vis_struct/=total_images_processed
        color_aesthetic/=total_images_processed
        textual_content/=total_images_processed
        user_interface/=total_images_processed


        output_dir = os.path.dirname(file_path)
        output_file = os.path.join(output_dir, 'gpt4_vision_evaluation_output.log')

        with open(output_file, 'w') as file:
            file.write(f'Overall Similarity Score: {((vis_struct+color_aesthetic+textual_content+user_interface)/4):.4}\n')
            file.write(f'Visual_Structure_and_Alignment: {vis_struct:.4}\n')
            file.write(f'Color and Aesthetic Design: {color_aesthetic:.4}\n')
            file.write(f'Textual and Content Consistency: {textual_content:.4}\n')
            file.write(f'User Interface and Interactivity: {user_interface:.4}\n')


def gpt4_vision_evaluation(gt_output_dir, pred_output_dir, output_dir, api_key):
    """
    Evaluate the similarity between the ground truth and predicted webpage images using GPT4.
    
    Args:
    gt_output_dir: str, path to the ground truth webpage images
    pred_output_dir: str, path to the predicted webpage images

    Returns:
    None
    """

    # Create a JSONL file to store the outputs
    output_jsonl_path = os.path.join(output_dir, 'gpt4_vision_evaluation_output.jsonl')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate responses using GPT4
    generate_responces(pred_output_dir, gt_output_dir, output_jsonl_path, api_key)

    # Read the JSONL file and get the outputs
    read_jsonl_and_get_outputs(output_jsonl_path)