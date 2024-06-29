# Webpage Code Generation Benchmark

Welcome to the Webpage Code Generation Benchmark! This guide will help you set up your environment, generate webpage screenshots, and run evaluations in a clear and user-friendly manner. Let's get started!

## Prerequisites

Before you begin, ensure your environment is similar to the LLaVA code base. Follow the instructions [here](https://github.com/haotian-liu/LLaVA/tree/main) to set up your environment.

You will also need to install the following additional packages:

```bash
pip install selenium
pip install tqdm
```

## Setup Instructions

### 1. Update the `cli.py` File

Navigate to the `llava/serve` directory and update the `cli.py` file. You can use the provided `cli.py` file for reference and modify it according to the model you are using. This step is crucial to save the HTML files.

### 2. Save HTML Files

Run the following command to save HTML files:

```bash
python llava/serve/cli.py \
    --image-directory <path to web2code evaluation image data directory> \
    --output-directory <path to output directory> \
    --model-path <path to the model> \
    --max-new-tokens 10000 \
    --load-4bit
```

### 3. Convert HTML Files to Webpage Screenshots

Ensure the HTML files are present in the output directory. You can rerun the script to generate any remaining files. Use the following command to convert HTML files to webpage screenshots:

```bash
python generate_images.py \
    --html_file_directory <path to html file directory> \
    --output_directory <path to the output directory> \
    --viewport_width 1920 \
    --viewport_height 1080 \
    --wait_time 5 \
    --cuda
```

### 4. Run the Evaluation

Finally, run the evaluation with the following command:

```bash
python evaluate.py \
    --gt_file_dir <path to ground truth file directory> \
    --pred_file_dir <path to predicted file directory> \
    --output_dir <path to the output directory> \
    --gpt4v \
    --api_key $API_KEY \
    --cuda
```

### Additional Tips

- **Environment Variables**: Make sure to set the `$API_KEY` environment variable with your API key.
- **Directory Structure**: Maintain a clear directory structure to avoid confusion when specifying paths.

By following these steps, you should be able to set up and run the Webpage Code Generation Benchmark smoothly. Happy benchmarking!
