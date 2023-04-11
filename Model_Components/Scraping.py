import os
import logging
import time
import pandas as pd
import re
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from Model_Components.HelperFunctions import timeit, ensure_connect
from Model_Components.Mining import TextMiner


class DataScraper:
    """This class handles the connecting and scraping of Rightmove"""
    def __init__(self, pc_sample, n_per_region, fields_of_interest):
        # Base parameters
        self.pc_sample = pc_sample
        self.n_per_region = n_per_region
        self.fields_of_interest = fields_of_interest
        self.raw_data_cols = (["postcode"] + list(self.fields_of_interest.keys()))
        self.raw_data = pd.DataFrame(columns=self.raw_data_cols)


    @timeit
    def scrape_data(self):
        """This function scrapes all the data that is of interest, for all properties in the sample range."""

        unique_regions = self.pc_sample["region_gpt"].unique()
        remaining_regions = unique_regions[self.current_j:]

        for region in remaining_regions:

            for pc in self.pc_sample.loc[self.pc_sample["region_gpt"] == region, "postcode"]:
                self.current_pc = pc
                browser = self.load_for_postal(pc)
                pages_to_scrape = self.record_depth(browser)
                page_index = self.current_page
                for page in range(page_index, pages_to_scrape):
                    self.current_page = page

                    if page > 0:
                        self.flip_page(browser)

                    page_data = self.extract_data(browser, pc)
                    self.raw_data = pd.concat([self.raw_data, page_data], ignore_index=True)
                self.current_page = 1

                if self.current_i >= self.n_per_region:
                    self.current_i = 0
                    self.current_j += 1

                self.current_completion = ((self.current_j * self.n_per_region + self.current_i) / len(self.pc_sample['region_gpt']))
                logging.info(f"Scraping {round(100 * self.current_completion, 1)}% complete.")
                self.current_i += 1



            self.current_region = region
            logging.info(f"Scraping {region} complete.")

        logging.info(f"Scraping completed. {len(self.raw_data)} properties have been found.")

        return self.raw_data

    def load_for_postal(self, postal_code):
        """This function accesses Rightmove and navigates to the first page of available properties."""

        chrome_driver_path = Service(os.getcwd() + "/chromedriver_win32/chromedriver.exe")

        browser = webdriver.Chrome(service=chrome_driver_path)
        url = "https://www.rightmove.co.uk/"
        ensure_connect(lambda: browser.get(url))

        search_box = browser.find_element(By.CSS_SELECTOR, 'input[name="typeAheadInputField"]')
        search_box.send_keys(postal_code)
        search_box.send_keys(Keys.RETURN)

        find_properties_button = browser.find_element(By.ID, 'submit')
        find_properties_button.click()

        return browser

    def record_depth(self, browser):
        """This function records how many pages there are on the website for the postcode."""
        try:
            pages_element = browser.find_element(By.CSS_SELECTOR, 'div.pagination-pageSelect')
            pages_string = pages_element.text

            if not pages_string == '':
                total_pages = int(pages_string.split()[-1])
            else:
                total_pages = 0

            if isinstance(total_pages, type(None)):
                print("glitch1")

            return total_pages

        except:
            print("glitch2")

    def flip_page(self, browser):
        """This function flips to the next page in the list of properties."""

        next_button = browser.find_element(By.CSS_SELECTOR, 'button.pagination-direction--next')
        next_button.click()
        time.sleep(1)
        return

    def extract_data(self, browser, pc):
        """This function loops through every property on the current page and extracts all fields of interest."""

        properties_data = []

        property_elements = browser.find_elements(By.CSS_SELECTOR, '.l-searchResult.is-list')

        for prop in property_elements:
            property_data = self.extract_fields(prop)
            properties_data.append(property_data)

        properties_data = pd.DataFrame(properties_data)

        properties_data["postcode"] = pc

        return properties_data

    def extract_fields(self, prop):
        """This function extracts the fields of interest from one property."""

        property_data = dict.fromkeys(self.raw_data_cols)

        if self.fields_of_interest["price"]:
            try:
                price_element = prop.find_element(By.CSS_SELECTOR, '.propertyCard-priceValue')
                price = self.format_field(price_element.text)
            except:
                price = None
            property_data["price"] = price

        if self.fields_of_interest["property_type"]:
            try:
                property_type_element = prop.find_element(By.CSS_SELECTOR, '.property-information')
                property_type = self.format_field(property_type_element.text)
            except:
                property_type = None
            property_data["property_type"] = property_type

        if self.fields_of_interest["bedrooms"]:
            try:
                bedrooms_element = prop.find_element(By.CSS_SELECTOR, '.no-svg-bed-icon + .text')
                bedrooms = self.format_field(bedrooms_element.text)
            except:
                bedrooms = None
            property_data["bedrooms"] = bedrooms

        if self.fields_of_interest["bathrooms"]:
            try:
                bathrooms_element = prop.find_element(By.CSS_SELECTOR, '.no-svg-bathroom-icon + .text')
                bathrooms = self.format_field(bathrooms_element.text)
            except:
                bathrooms = None
            property_data["bathrooms"] = bathrooms

        if self.fields_of_interest["text"]:
            text_values, text = self.mine_text(prop)
            property_data.update(text_values)
            property_data["text"] = text

        return property_data

    def format_field(self, field_value):
        """
        Cleans and formats the input field_value by removing specific characters and converting to integer if possible.
        """

        field_value = field_value.replace('"', '')

        try:
            characters_to_remove = '£,'
            result = field_value.translate(str.maketrans("", "", characters_to_remove))

            try:
                result = int(result)
            except ValueError:
                result = result

            try:
                pattern = r'\n\d+'
                result = re.sub(pattern, '', result)
            except:
                result = result

        except:
            result = field_value

        return result

    def mine_text(self, prop):
        """Extract useful information from the property description using text mining. WIP"""

        text_values = dict.fromkeys(self.fields_of_interest["text_values"].keys())

        try:
            text_element = prop.find_element(By.CSS_SELECTOR, 'span[data-test="property-description"] span')
            text = text_element.text.replace('"', '')
            text_values = TextMiner(text, text_values).scan_contents()

            return text_values, text

        except:

            return text_values, None
