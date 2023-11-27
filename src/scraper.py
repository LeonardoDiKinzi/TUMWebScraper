import logging
import os
import base64
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from http import HTTPStatus

class TUMWebScraper:
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True,
        'paperWidth': 6.97,
        'paperHeight': 16.5,
    }

    def __init__(self, url, iterator, chrome_driver_path, args):
        self.url = url
        self.iterator = iterator
        self.args = args
        self.chrome_driver_path = chrome_driver_path

        # Create directories for output
        base_output_path = os.path.join('data', 'outputs')
        self.output_path_html = os.path.join(base_output_path, 'HTML')
        self.output_path_pdf = os.path.join(base_output_path, 'PDF')
        self.output_path_vp_screenshots = os.path.join(base_output_path, 'Viewport_Screenshots')
        self.output_path_fullpage_screenshots = os.path.join(base_output_path, 'FullPage_Screenshots')

        # Create directories if they don't exist
        os.makedirs(self.output_path_html, exist_ok=True)
        os.makedirs(self.output_path_pdf, exist_ok=True)
        os.makedirs(self.output_path_vp_screenshots, exist_ok=True)
        os.makedirs(self.output_path_fullpage_screenshots, exist_ok=True)

        # Initialize the WebDriver
        self.driver = self.initialize_webdriver()

    def run(self):
        try:
            self.driver.get(self.url)
            self.handle_cookies()

            if self.args.html:
                self.generate_html()

            if self.args.pdf:
                self.generate_pdf()

            if self.args.viewport_screenshot:
                self.generate_screenshot()

            if self.args.full_page_screenshot:
                self.generate_fullpage_screenshot()

        except Exception as e:
            logging.error(f"Error with URL {self.url}: {e}")

        finally:
            self.driver.quit()

    def initialize_webdriver(self):

        #initialise chrome options for headless
        webdriver_options = ChromeOptions()
        webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--disable-gpu')
        webdriver_options.add_argument("--disable-infobars")

        #get chrome driver for selenium (needs to be downloaded for you specific Chrome Webbrowser version and placed in folder drivers
        webdriver_service = ChromeService(self.chrome_driver_path)
        driver = webdriver.Chrome(service=webdriver_service, options=webdriver_options)
        driver.set_window_size(1920, 1080)
        return driver

    def generate_html(self):
        html_result = self.driver.page_source
        with open(os.path.join(self.output_path_html, f"output_{self.iterator}.html"), 'w', encoding='utf-8') as file:
            file.write(html_result)

    def generate_pdf(self):
        try:
            print_options = self.print_options.copy()
            pdf_result = self._send_devtools(self.driver, "Page.printToPDF", print_options)
            result = base64.b64decode(pdf_result['data'])  # decode file from base64 back to binary
            with open(os.path.join(self.output_path_pdf, f"output_{self.iterator}.pdf"), "wb") as pdf_file:
                pdf_file.write(result)
        except Exception as e:
            logging.error(f"Error generating PDF for URL {self.url}: {e}")

    def generate_screenshot(self):
        try:
            screenshot_path = os.path.join(self.output_path_vp_screenshots, f"output_{self.iterator}.png")
            self.driver.save_screenshot(screenshot_path)
        #handle alerts
        except UnexpectedAlertPresentException as ae: 
            logging.info("\nCaught Alert. \n")
            try:
                # switch to alert
                alert = self.driver.switch_to.alert
                # accept the alert
                alert.accept()
            except NoAlertPresentException:
                print("No alert present.")
            except:
                print("Alert could not be closed.")
        
        except Exception as e:
            logging.error(f"Error taking viewport screenshot for URL {self.url}: {e}")


    def generate_fullpage_screenshot(self):
        try:
           # Ref: https://stackoverflow.com/a/52572919/
            original_size = self.driver.get_window_size()
            required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
            required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
            self.driver.set_window_size(required_width, required_height)
            # driver.save_screenshot(path)  # has scrollbar
            self.driver.find_element(By.XPATH, "//body[1]").screenshot(os.path.join(self.output_path_fullpage_screenshots, "output_"+str(self.iterator)+".png"))  # avoids scrollbar
            self.driver.set_window_size(original_size['width'], original_size['height'])
        except Exception as e:
            logging.error(f"Error taking full page screenshot for URL {self.url}: {e}")

    def handle_cookies(self):

        """
        Attempt to remove the cookie banner by first waiting 3 seconds (wait until cookie banner appears) and then remove cookie banner by manually clicking the accept button
        """

        # List of possible button texts, translated to the site's language
        accept_texts = [
            "agree", "accept","accept all", "ok", "yes", "zustimmen","yes, continue",
            "consent","alle akzeptieren","save", "i agree", "got it", "understood",
            "i accept", "continue", "accept cookies", "allow cookies", "ok, continue",
            "allow all", "allow", "allow all cookies", "proceed", "akzeptieren","aceptar todo","accept & close","aceptar"
        ]

        try:
            time.sleep(5)  # Allow time for any cookie banners to appear
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            
            for text in accept_texts:
                try:
                    # Find all buttons on the page
                    buttons = self.driver.find_elements(By.TAG_NAME,'button') + self.driver.find_elements(By.TAG_NAME, 'a')

                    # Map button elements to their text
                    button_texts = [button.text.lower() for button in buttons]
                    # Convert the list of found button texts to a string
                    # found_button_texts_line = ", ".join(button_texts)
                    # print("Found button texts:", found_button_texts_line)

                    # Iterate through the buttons and check their text
                    for button in buttons:
                        buttonText = button.text.lower()

                        # Check if buttonText includes any of the words from the list
                        if any(accept_text in buttonText for accept_text in accept_texts):
                            # Click the button
                            button.click()
                            #print('MATCH')
                            break  # Stop the loop after clicking the button
                    break
                except NoSuchElementException:
                    continue
        except Exception as e:
            logging.warning(f"Cookie handling issue for URL {self.url}: {e}")


    def _send_devtools(self, driver, cmd, params):
        """
        Works only with chromedriver.
        Method uses cromedriver's api to pass various commands to it.
        """

        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')
