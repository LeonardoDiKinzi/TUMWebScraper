# Web Scraping Tool

## Description
This project provides a web scraping tool designed to automate the collection of data from specified web pages. It is particularly useful for extracting information from a list of URLs provided in a CSV file. The tool is capable of downloading page contents in various formats, including HTML, PDF, and full-page screenshots.

## Features
Data Extraction: Extracts data from web pages listed in a CSV file.
Multiple Output Formats: Supports downloading of page contents as HTML, PDF, or screenshots.
Cookie Banner Handling: Includes support to remove most of the common cookie banners
Customizable Range: Allows users to specify the range of pages to scrape.
Chrome Driver Integration: Compatible with Chrome drivers for browser automation.

## Prerequisites
Before using the tool, ensure the following prerequisites are met:

### Python Environment: A Python environment should be set up on your system.
### Chrome Driver: 
Download the appropriate Chrome driver for your version of the Chrome browser from ChromeDriver - [WebDriver for Chrome](https://chromedriver.chromium.org/downloads).
Place the driver file in the folder drivers

## Setting Up the Tool
Clone the Repository: Clone this Git repository to your local machine.
Install Dependencies: Run pip install -r requirements.txt to install the required Python packages.

## Usage
### 1. Preparing the Input File
Create a CSV file named Landing_pages.csv (you can also call it differently) and place it in data/inputs. It needs to have the following format and needs to be ; seperated:

| page_id | url                          |
|---------|------------------------------|
| 1       | https://example.com/page1    |
| 2       | https://example.com/page2    |
| 3       | https://example.com/page3    |



### 2. Running the Tool

#### Command-Line Arguments

The web scraping tool accepts several command-line arguments to customize its operation. Below is a description of each argument:

#### `--input_file`
- **Description**: Path to the CSV file containing the URLs to scrape.
- **Usage**: `--input_file "path/to/file"`
- **Example**: `--input_file "data/inputs/Landing_pages.csv"`

#### `--chrome_driver`
- **Description**: Path to the Chrome driver executable.
- **Usage**: `--chrome_driver "path/to/driver"`
- **Example**: `--chrome_driver "drivers/chromedriver_115.exe"`

#### `--start`
- **Description**: The starting index of URLs in the CSV file to begin scraping.
- **Usage**: `--start number`
- **Example**: `--start 40`

#### `--end`
- **Description**: The ending index of URLs in the CSV file to stop scraping.
- **Usage**: `--end number`
- **Example**: `--end 50`

#### `--html`
- **Description**: Flag to save scraped pages as HTML files.
- **Usage**: `--html`
- **Example**: Include `--html` to save HTML files.

#### `--pdf`
- **Description**: Flag to save scraped pages as PDF files.
- **Usage**: `--pdf`
- **Example**: Include `--pdf` to save PDF files.

#### `--full_page_screenshot`
- **Description**: Flag to capture and save full-page screenshots of the URLs.
- **Usage**: `--full_page_screenshot`
- **Example**: Include `--full_page_screenshot` to save screenshots.

#### `--validation`
- **Description**: Enable validation mode to calculate statistics of the web scraping task.
- **Usage**: `--validation`
- **Example**: Include `--validation` to activate the ScraperValidator.

#### Example Command

To run the tool with a combination of these arguments, you might use a command like this:

```bash
python src/main.py --input_file "data/inputs/Landing_pages.csv" --chrome_driver "drivers/chromedriver_115.exe" --start 40 --end 50 --html --pdf --full_page_screenshot --validation
```

## Contributing
Feel free to fork this repository and submit pull requests with your improvements.

## License
This project is licensed under MIT License.
