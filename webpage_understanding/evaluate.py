import json

def normalize_text(text):
    return text.replace('</s>', '').strip().upper()

def calculate_accuracy(jsonl_file):
    total_count = 0
    correct_count = 0

    with open(jsonl_file, 'r') as file:
        for line in file:
            data = json.loads(line)
            pred = normalize_text(data['pred'])
            actual = normalize_text(data['actual'])

            if pred == actual:
                correct_count += 1
            elif actual in pred[:5]:
                correct_count += 1
            total_count += 1

    accuracy = correct_count / total_count * 100.0 if total_count > 0 else 0
    return accuracy, correct_count, total_count

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate accuracy of model predictions")
    parser.add_argument('--jsonl_file_path', type=str, required=True, help='Path to the jsonl file containing model predictions and ground truth')

    args = parser.parse_args()
    score, correct_count, total_count = calculate_accuracy(args.jsonl_file_path)
    print(f'Accuracy Score: {score:.2f}')
    print(f'Correct Count: {correct_count}')
    print(f'Total Count: {total_count}')

