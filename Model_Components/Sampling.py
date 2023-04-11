import pandas as pd
import os
import logging

from Model_Components.HelperFunctions import timeit


class PostcodeSampler:
    """This class is responsible for randomly selecting postcodes for which to scrape data."""

    def __init__(self, n_per_region=5, set_seed=None):
        self.pc_list = None
        self.n_per_region = n_per_region
        self.set_seed = set_seed
        self.sample = pd.DataFrame(columns=["postcode", "region_gpt"])

    @timeit
    def pc_sampler(self, import_cache=None):
        """This function samples n*regions postcodes from the supplied list of postcodes.
            Countries: England, Scotland, Northern Ireland, Isle of Man, Wales, Guernsey, Isle of Man, Jersey
        """
        if import_cache:
            return

        self.pc_list = self.filter_sample(pc_list=pd.read_csv(os.getcwd() + "/Inputs/postalcodes.csv"))

        for region in self.pc_list["region_gpt"].unique():
            pc_region = self.pc_list.loc[self.pc_list["region_gpt"] == region]
            pc_region_sample = self.sample_from_country(pc_region, region)
            self.sample = pd.concat([self.sample, pc_region_sample], ignore_index=True)

        logging.info(f"Sampling {len(self.sample)} postcodes in total")

        return self.sample

    def sample_from_country(self, pc_region, region):
        """This samples n postcodes from the list of postcodes in a region."""

        pc_region_sample = pd.DataFrame(index=range(0, self.n_per_region), columns=pc_region.columns)
        pc_region_sample["region_gpt"] = region

        # sample n from list of strings

        sampled_strings = pc_region["postcode"].sample(self.n_per_region, random_state=self.set_seed)
        pc_region_sample["postcode"] = sampled_strings.reset_index(drop=True)

        return pc_region_sample

    def filter_sample(self, pc_list):
        """This function removes offshore countries."""

        excluded_countries = ["Isle of Man", "Guernsey", "Jersey"]
        pc_list = pc_list.loc[~pc_list["country_string"].isin(excluded_countries)]
        logging.info(f"Removed the following countries from the sample: {excluded_countries}")

        # np.savetxt('real_estate_data.csv', pc_list["region_gpt"].unique(), delimiter=',', fmt='%s')

        return pc_list
