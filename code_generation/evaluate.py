import os
import time
import argparse
from gpt4_vision_evaluation import gpt4_vision_evaluation

def main(args):

    pred_output_dir=args.pred_file_dir
    gt_output_dir=args.gt_file_dir

    if args.gpt4v:
        gpt4_vision_evaluation(gt_output_dir, pred_output_dir, args.output_dir, args.api_key)
        
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="usage")

    parser.add_argument('--gt_file_dir', type=str, default='data/gt/', help='Path to ground truth html file directory')
    parser.add_argument('--pred_file_dir', type=str, default='data/pred/', help='Path to predicted html file directory')
    parser.add_argument('--output_dir', type=str, help='Path to save the regenerated webpage images')
    parser.add_argument('--gpt4v', action='store_true', help='Use GPT4 for evaluation')
    parser.add_argument('--api_key', type=str, help='API key for GPT4')

    args = parser.parse_args()

    main(args)