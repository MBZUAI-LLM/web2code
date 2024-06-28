import argparse
from code2image import save_webpage

def main(args):
            
    save_webpage(args.html_file_directory, args.output_directory, \
                    args.wait_time, \
                    args.viewport_width, \
                    args.viewport_height, \
                    args.cuda)

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(description='Convert HTML files to images')
    parser.add_argument('--html_file_directory', type=str, required=True, help='Directory containing HTML files')
    parser.add_argument('--output_directory', type=str, required=True, help='Directory to save the output images')
    parser.add_argument('--wait_time', type=int, default=5, help='Time to wait before taking the screenshot')
    parser.add_argument('--viewport_width', type=int, default=1920, help='Viewport width')
    parser.add_argument('--viewport_height', type=int, default=1080, help='Viewport height')
    parser.add_argument('--cuda', action='store_true', help='Use CUDA')

    args = parser.parse_args()
    main(args)


