from Model_Components.Model import RightMoveModel

"""
Author: Stephane Mertens de Wilmars

Date: 06/04/2023

Description:
* This script scrapes a representative sample of price and quality attributes from properties listed on the
 UK real estate website Rightmove using the Selenium package. 
 
Instructions:
* The user only needs to change the input parameters below and click run.

Notes:
* Compatible with Chrome

"""

# INPUT PARAMETERS

import_cache = None  # "20230411000133"  # Fill in cache_id,in memory (eg. "20230410155536") for it to be loaded. This is a recovery measure.

fields_of_interest = {
    "price": True,
    "property_type": True,
    "bedrooms": True,
    "bathrooms": True,
    "text": True,
    "text_values": {  # The user can write any textstrings in this dictionary, for which the scraper will search.
        "fully furnished": True,
        "parking space": True,
    },
}

n_per_region = 40  # Amount of postcodes to be sampled from one region

set_seed = 12

# RUNNING THE MODEL

RightMoveModel(import_cache=import_cache, fields_of_interest=fields_of_interest, n_per_region=n_per_region,
               set_seed=set_seed).run()
