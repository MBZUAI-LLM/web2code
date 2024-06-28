
# Webpage Understanding Benchmark

Welcome to the Webpage Understanding Benchmark! This guide will help you set up your environment, generate outputs, and run evaluations in a clear and user-friendly manner. Let's get started!

## Prerequisites

Before you begin, ensure your environment is set up similar to the LLaVA code base. Follow the instructions [here](https://github.com/haotian-liu/LLaVA/tree/main) to set up your environment.

## Setup Instructions

### 1. Include and Update `code_eval.py`

Place the `code_eval.py` file in the `llava/serve` directory. You may need to update this file according to the model you are using. This step is crucial for generating and saving the outputs.

### 2. Generate Outputs

Run the following command to generate outputs:

```bash
python llava/serve/code_eval.py \
    --image-directory <path to the ground truth image directory> \
    --qa-file <path to question answer .jsonl file> \
    --output-directory <path to the output directory> \
    --model-path <path to the model> \
    --load-4bit
```

### 3. Evaluate Outputs

After generating the outputs, run the following command to evaluate them:

```bash
python evaluate.py \
    --jsonl_file_path <path to output .jsonl file>
```

### Additional Tips

- **Environment Variables**: Ensure all necessary environment variables are set properly.
- **Directory Structure**: Maintain a clear directory structure to avoid confusion when specifying paths.
- **Model Configuration**: Make sure the `code_eval.py` file is properly configured for the specific model you are using.

By following these steps, you should be able to set up and run the Webpage Understanding Benchmark smoothly. Happy benchmarking!
