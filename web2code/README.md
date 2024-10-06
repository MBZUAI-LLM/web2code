# Web2Code

## Contents
- [Install](#install)
- [CrystalChat-MLLM Weights](#crystalchat-mllm-weights)
- [CLI Inference](#cli-inference)
- [Train](#train)

## Install

To setup the conda environment, follow the same steps as LLaVA as highlighted in [README_LLAVA.md](README_LLAVA.md).


## CrystalChat-MLLM Weights
Please check out our [LLM360/CrystalChat-7B-MLLM](https://huggingface.co/LLM360/CrystalChat-7B-MLLM) for the MLLM model based on CrystalChat trained on LLAVA fine-tuning data and [LLM360/CrystalChat-7B-Web2Code](https://huggingface.co/LLM360/CrystalChat-7B-Web2Code) for the Web2Code model.


## CLI Inference

Chat about images using our model. It also supports multiple GPUs, 4-bit and 8-bit quantized inference. 

```Shell
python -m llava.serve.cli \
    --model-path /path/to/the/model \
    --image-file "path_to_image.jpg" \
    --load-4bit
```

## Train

### Hyperparameters
We use a similar set of hyperparameters as Vicuna in finetuning.  Both hyperparameters used in pretraining and finetuning are provided below.


1. Pretraining

| Hyperparameter | Global Batch Size | Learning rate | Epochs | Max length | Weight decay |
| --- | ---: | ---: | ---: | ---: | ---: |
| Web2Code | 256 | 1e-3 | 1 | 2048 | 0 |

2. Finetuning

| Hyperparameter | Global Batch Size | Learning rate | Epochs | Max length | Weight decay |
| --- | ---: | ---: | ---: | ---: | ---: |
| Web2Code | 128 | 2e-5 | 1 | 2048 | 0 |

### Pretrain (feature alignment)

Please download the 558K subset of the LAION-CC-SBU dataset with BLIP captions we use in the paper [here](https://huggingface.co/datasets/liuhaotian/LLaVA-Pretrain).

Training script with DeepSpeed ZeRO-2: [`pretrain_crystal_chat.sh`](scripts/v1_5/pretrain_crystal_chat.sh).

### Visual Instruction Tuning

1. Prepare data

Please download the annotation of the final mixture the LLaVA instruction tuning data [llava_v1_5_mix665k.json](https://huggingface.co/datasets/liuhaotian/LLaVA-Instruct-150K/blob/main/llava_v1_5_mix665k.json), and download the images from constituting datasets:

- COCO: [train2017](http://images.cocodataset.org/zips/train2017.zip)
- GQA: [images](https://downloads.cs.stanford.edu/nlp/data/gqa/images.zip)
- OCR-VQA: [download script](https://drive.google.com/drive/folders/1_GYPY5UkUy7HIcR0zq3ZCFgeZN7BAfm_?usp=sharing), **we save all files as `.jpg`**
- TextVQA: [train_val_images](https://dl.fbaipublicfiles.com/textvqa/images/train_val_images.zip)
- VisualGenome: [part1](https://cs.stanford.edu/people/rak248/VG_100K_2/images.zip), [part2](https://cs.stanford.edu/people/rak248/VG_100K_2/images2.zip)

After downloading all of them, organize the data as follows in `./playground/data`,

```
├── coco
│   └── train2017
├── gqa
│   └── images
├── ocr_vqa
│   └── images
├── textvqa
│   └── train_images
└── vg
    ├── VG_100K
    └── VG_100K_2
```

To prepare the Web2Code dataset, download the annotation and images of the final dataset [[Web2Code Dataset](https://huggingface.co/datasets/MBZUAI/Web2Code)]

Web2Code_image
```
├── games
│   ├── 01
│   ├── ...
│   └── 09
├── jobs
│   ├── 03
│   ├── ...
│   └── 13
```



2. Start training!

Visual instruction tuning takes around 26 hours for the model on 16x A100 (40G).
Pretraining takes around 20 hours for the model on 16x A100 (40G). 

Training script with DeepSpeed ZeRO-3: [`finetune_crystal_chat_sh`](scripts/v1_5/pretrain_crystal_chat.sh).


## Citation

If you find our work helpful for your research, please consider giving a star ⭐ and citation 📝

```
@article{web2code2024,
  title={Web2Code: A Large-scale Webpage-to-Code Dataset and Evaluation Framework for Multimodal LLMs},
  author={Sukmin Yun and Haokun Lin and Rusiru Thushara and Mohammad Qazim Bhat and Yongxin Wang and Zutao Jiang and Mingkai Deng and Jinhong Wang and Tianhua Tao and Junbo Li and Haonan Li and Preslav Nakov and Timothy Baldwin and Zhengzhong Liu and Eric P. Xing and Xiaodan Liang and Zhiqiang Shen},
  journal={arXiv preprint arXiv:2406.20098},
  year={2024}
}
```

