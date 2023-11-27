import argparse
import pandas as pd
import os
from datetime import datetime
from scraper import TUMWebScraper, UnexpectedAlertPresentException
from scraper_validator import ScraperValidator


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Web Scraper')
    parser.add_argument('--input_file', type=str, help='Path to the input CSV file')
    parser.add_argument('--chrome_driver', type=str, required=True, help='Path to the ChromeDriver executable')
    parser.add_argument('--start', type=int, help='The start parameter')
    parser.add_argument('--end', type=int, help='The end parameter')
    parser.add_argument('--html', action='store_true', default=True, help='Perform HTML scrape (default: True)')
    parser.add_argument('--pdf', action='store_true', default=False, help='Perform PDF scrape (default: False)')
    parser.add_argument('--viewport_screenshot', action='store_true', default=False, help='Take viewport screenshot (default: False)')
    parser.add_argument('--full_page_screenshot', action='store_true', default=False, help='Take full page screenshot (default: True)')
    parser.add_argument('--validation', action='store_true', default=False, help='Calculate statistics of webscrapting task')
    args = parser.parse_args()

    # Get the full path to the directory where main.py is located
    main_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the project root directory
    project_root = os.path.dirname(main_dir)

    # Extracting file name from input_file argument
    file_name = os.path.splitext(os.path.basename(args.input_file))[0]

    # Constructing the path for the results and statistics file
    results_file = os.path.join(project_root, 'data', 'outputs', f'results_{file_name}.csv')
    statistics_file = os.path.join(project_root,'data', 'outputs', f'statistics_{file_name}.csv')

    # Check if results file exists, otherwise read the input file
    # if os.path.exists(results_file):
    #     df = pd.read_csv(results_file, delimiter=";")     
    # else:
    #     df = pd.read_csv(args.input_file, delimiter=";")
    df = pd.read_csv(args.input_file, delimiter=";")
    first_time = not('all_zero' in df.columns)

    # Ensuring the directories exist
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    os.makedirs(os.path.dirname(statistics_file), exist_ok=True)


    # Iterating through the DataFrame
    for index, row in df.iloc[args.start:args.end].iterrows():

        url = row['url']
        iterator = row['page_id']
        print(f"\n [{iterator}] URL: {url} \n")

        # Skip if already successfully crawled
        if  not first_time and row['all_zero'] == 0:
            print("\n Already successfully crawled :)\n")
            continue

        scraper = TUMWebScraper(url, iterator,args.chrome_driver,args)

        try:
            scraper.run()
        except UnexpectedAlertPresentException:
            print("\nCaught Alert!\n")
        except Exception as e:
            print(f"Error with URL {url}: {str(e)}")
    
    if args.validation:
        # After scraping, call ScraperValidator
        validator = ScraperValidator(args.input_file, results_file, statistics_file)
        validator.run()

if __name__ == "__main__":
    main()
