import os
import time
import concurrent.futures
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def count_png_files(directory):

    png_count = 0
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file extension is .png
            if file.lower().endswith('.png'):
                png_count += 1
    return png_count

def count_html_files(directory):

    html_count = 0
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file extension is .html
            if file.lower().endswith('.html'):
                html_count += 1
    return html_count

def process_html_file(file_dir, output_dir, wait_time, viewport_width, viewport_height, cuda, file_name):

    # Configure Chrome options to run headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument(f"--window-size={viewport_width},{viewport_height}")

    # Start a new web driver
    driver = webdriver.Chrome(options=chrome_options)

    # Load the local HTML file
    file_path = f'{file_dir}/{file_name}'
  
    driver.get(f'file://{file_path}')

    # Wait for the page to load
    time.sleep(wait_time)

    # Scroll to capture the entire page
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.PAGE_DOWN)

    # Wait for additional time if the page has dynamic content that loads after scrolling
    additional_wait_time = 1  # Adjust this time as needed
    time.sleep(additional_wait_time)

    # Capture a screenshot of the entire page
    screenshot = driver.get_screenshot_as_png()
    
    # Save the screenshot as an image with a unique name
    output_filepath = f'{output_dir}/{file_name.replace(".html", ".png")}'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if "_output.png" in output_filepath:
        output_filepath = output_filepath.replace("_output.png", ".png")

    if os.path.exists(output_filepath):
        # print(f"File already exists: {output_filepath}")
        driver.quit()
        return

    with open(output_filepath, "wb") as file:
        file.write(screenshot)

    # Close the web driver
    driver.quit()

def save_webpage(file_dir, output_dir, wait_time, viewport_width, viewport_height, cuda):
    html_files = [f for f in os.listdir(file_dir) if f.endswith('.html')]

    if count_png_files(output_dir) == count_html_files(file_dir):
        print("All HTML files have already been converted to images.")
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for file_name in html_files:
            try:
                future = executor.submit(process_html_file, file_dir, output_dir, wait_time, \
                                        viewport_width, viewport_height, cuda, file_name)
                futures.append(future)
            except Exception as e:
                print(f"Error processing file: {file_name}")
                print(e)

        # Wait for all futures to complete
        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing HTML files"):
            pass
    
    print("Processing completed.")

    if count_png_files(output_dir) == count_html_files(file_dir):
        print("All HTML files successfully converted to images.")
        print(f"Total files converted: {count_png_files(output_dir)}")
    else:
        print(f"Incomplete files: {count_html_files(file_dir) - count_png_files(output_dir)}")
        print("Some HTML files were not converted to images. \
              Please rerun the script to convert the remaining files.")

