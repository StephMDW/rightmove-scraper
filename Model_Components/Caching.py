import json
import logging
import traceback
import os
from datetime import datetime
import pandas as pd

from Model_Components.Scraping import DataScraper


class CachedScraper(DataScraper):
    """This function inherits from DataScraper and adds caching functionality.
    Caching is relevant as the scraping process might be interrupted for multitude of reasons.
    If an error occurs, caching kicks in and will reinitialize the process with minimal data corruption."""

    def __init__(self, pc_sample, n_per_region, fields_of_interest):
        super().__init__(pc_sample, n_per_region, fields_of_interest)

        # Caching parameters
        self.cache_id = None
        self.current_run = 0
        self.current_region = None
        self.current_pc = None
        self.current_page = 1
        self.current_i = 1
        self.current_j = 0
        self.current_completion = None


    def run(self):
        """This function runs the underlying scrape_data function and provides caching functionality at failure."""


        automatic_attempts = int(20)

        while True:
            try:
                if self.cache_id:  # if a cache id exist, it must mean there is a cache built in a previous run
                    self.take_cache(cache_data_path, cache_param_path)
                self.current_run += 1
                self.raw_data = self.scrape_data()
                break
            except Exception:
                logging.info("Encountered an error!:")
                traceback.print_exc()
                logging.info(f"Scraping failed (attempt {self.current_run}/{automatic_attempts})! "
                             f"Starting cache procedure...")
                cache_data_path, cache_param_path = self.make_cache()

                self.current_run += 1
                if self.current_run > automatic_attempts:
                    logging.info("Could not complete scraping. Retries were not successful.")
                    logging.info("Ending program.")
                    exit()

                logging.info(f"Starting {self.current_run}th attempt out of {automatic_attempts}")

        return self.raw_data

    def make_cache(self):
        """Caching allows incomplete outputs and parameters to be saved."""
        self.cache_id = datetime.now().strftime("%Y%m%d%H%M%S")
        cache_directory = os.path.join(os.getcwd(), "Outputs", "Cache")
        cache_directory_data = os.path.join(cache_directory, "Data")
        cache_data_name = f"data_{str(self.cache_id)}.csv"
        cache_params_name = f"params_{str(self.cache_id)}.json"
        cache_data_path = os.path.join(cache_directory_data, cache_data_name)
        cache_param_path = os.path.join(cache_directory, "Params", cache_params_name)

        self.raw_data.to_csv(cache_data_path, index=False)
        self.set_params(vars(self), cache_param_path)

        logging.info(f"Data succesfuly cached in: {cache_data_path}")
        logging.info(f"Current parameters successfully cached in: {cache_param_path}")

        return cache_data_path, cache_param_path

    def take_cache(self, cache_data_path, cache_param_path):
        """This function retrieves the cache stored from the previous run."""
        try:
            self.raw_data = pd.read_csv(cache_data_path)
            uncached_params = self.get_params(cache_param_path)
            self.unpack_cache(uncached_params)
            logging.info(f"Cache with ID {self.cache_id} succesfully retrieved and unpacked!")
        except:
            logging.info("Cache retrieval is corrupted! Exiting program.")

    def unpack_cache(self, attr_dict):
        """This function loads the retrieved parameters back into the object"""
        for attr_name, attr_value in attr_dict.items():
            setattr(self, attr_name, attr_value)

    def set_params(self, params, file_name):
        """This function saves important params to a json file"""
        params_dict = params.copy()

        keys_to_remove = {'raw_data', 'n_per_region', 'fields_of_interest', 'raw_data_cols'}

        for key in keys_to_remove:
            params_dict.pop(key, None)

        if isinstance(params_dict['pc_sample'], pd.DataFrame):
            params_dict['pc_sample'] = params_dict['pc_sample'].to_dict(orient='records')

        with open(file_name, 'w') as f:
            json.dump(params_dict, f)

    def get_params(self, cache_param_path):
        """This function retrieves params from a json file"""
        with open(cache_param_path, 'r') as f:
            params = json.load(f)

        # Convert 'pc_sample' back to a DataFrame if it was stored as a list of dictionaries
        if isinstance(params['pc_sample'], list):
            params['pc_sample'] = pd.DataFrame(params['pc_sample'])

        return params


class CacheRecover:
    """This class is responsible for preparing a cache for processing, instead of running the algorithm again."""

    def __init__(self, import_cache):
        self.import_cache = import_cache

    def recover_cache(self):
        if self.import_cache:
            cache_path = os.getcwd() + "/Outputs/Cache/"
            selected_cache = f"Data/data_{self.import_cache}.csv"
            try:
                selected_params = json.load(open(cache_path + f"Params/params_{self.import_cache}.json", 'r'))
            except:
                logging.info("Invalid cache! Terminating program.")
                exit()
            raw_data = pd.read_csv(cache_path + selected_cache)
            logging.info(f"This is a cache recovery program using cache: {self.import_cache}!")
            cache_completion = selected_params['current_completion'] * 100
            final_run = selected_params["current_run"]
            logging.info(f"At failure, cache was {round(cache_completion, 2)}% complete")
            logging.info(f"This cache could not be completed after {final_run} runs.")
            return raw_data
        else:
            return None
