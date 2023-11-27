import pandas as pd
import os

class ScraperValidator:
    def __init__(self, links_csv_path,results_file,statistics_file):
        
        # Get the full path to this directory
        main_dir = os.path.dirname(os.path.abspath(__file__))

        # Navigate to the project root directory
        project_root = os.path.dirname(main_dir)

        self.output_dir = os.path.join(project_root, 'data', 'outputs')
        self.links_csv_path = links_csv_path
        self.results_file = results_file
        self.statistics_file = statistics_file

    def check_files_exist(self, ids):

        data = []
        total_ids = len(ids)
        for index, page_id in enumerate(ids, start=1):
            data.append({
                'page_id': page_id,
                'html_exists': int(os.path.exists(os.path.join(self.output_dir, 'HTML', f'output_{page_id}.html'))),
                'pdf_exists': int(os.path.exists(os.path.join(self.output_dir, 'PDF', f'output_{page_id}.pdf'))),
                'viewport_exists': int(os.path.exists(os.path.join(self.output_dir, 'Viewport_Screenshots', f'output_{page_id}.png'))),
                'fullpage_exists': int(os.path.exists(os.path.join(self.output_dir, 'FullPage_Screenshots', f'output_{page_id}.png')))
            })

            # Calculate and print progress in percent
            progress = (index / total_ids) * 100
            print(f"Checking files: {progress:.2f}% complete", end='\r')

        print()  # Add a newline after the loop
        return pd.DataFrame(data)

    def merge_with_links(self, existence_df):
        links_df = pd.read_csv(self.links_csv_path, delimiter=";")
        links_df = links_df[['page_id', 'url']]
        merged_df = existence_df.merge(links_df, on='page_id', how='left')
        return merged_df

    def add_scrape_status_columns(self, df):
        columns_to_check = ['html_exists', 'pdf_exists', 'viewport_exists', 'fullpage_exists']
        df['all_zero'] = df[columns_to_check].apply(lambda row: int(all(x == 0 for x in row)), axis=1)
        df['at_least_one_not_all'] = df[columns_to_check].apply(lambda row: int(sum(row) > 0 and sum(row) < len(row)), axis=1)
        df['all_one'] = df[columns_to_check].apply(lambda row: int(all(x == 1 for x in row)), axis=1)
        return df
    
    def save_final_results(self, df):
        df.to_csv(self.results_file, index=False)

    def generate_statistics(self, df):
        statistics_data = {
            'Metric': ['Successful', 'Partially Successful', 'Not Successful'],
            'Count': [
                df['all_one'].sum(),
                df['at_least_one_not_all'].sum(),
                df['all_zero'].sum()
            ]
        }

        statistics_df = pd.DataFrame(statistics_data)

        partial_df = df[df['at_least_one_not_all'] == 1]
        for file_type in ['html', 'pdf', 'viewport', 'fullpage']:
            count = partial_df[f'{file_type}_exists'].sum()
            missing_count = df['at_least_one_not_all'].sum() - count
            statistics_df = statistics_df.append({'Metric': f'Missing {file_type.capitalize()}', 'Count': missing_count}, ignore_index=True)

        statistics_df.to_csv(self.statistics_file, index=False)

    def get_max_page_id(self):
        links_df = pd.read_csv(self.links_csv_path, delimiter=";")
        return links_df['page_id'].max()

    def run(self):
        print("Start creating statistics")
        max_page_id = self.get_max_page_id()
        page_ids = list(range(1, max_page_id + 1))

        existence_df = self.check_files_exist(page_ids)
        merged_df = self.merge_with_links(existence_df)
        final_df = self.add_scrape_status_columns(merged_df)
        self.save_final_results(final_df) # Save the final DataFrame to a CSV file
        self.generate_statistics(final_df)
        print("Finished creating statistics")