import logging
from datetime import datetime

from Model_Components.Sampling import PostcodeSampler
from Model_Components.Caching import CachedScraper, CacheRecover
from Model_Components.Transforming import DataTransformer
from Model_Components.Exporting import DataExporter
from Model_Components.HelperFunctions import configure_logging




class RightMoveModel:
    def __init__(self, import_cache=None, fields_of_interest=None, set_seed=None, n_per_region=1):
        self.import_cache = import_cache
        self.fields_of_interest = fields_of_interest
        self.n_per_region = n_per_region
        self.set_seed = set_seed

    def run(self):
        """This function linearly passes through all separate components of the model.
        """

        # Set-up logging
        output_id = datetime.now().strftime('%Y%m%d%H%M%S')
        configure_logging(output_id)
        logging.info(f"Starting program.")

        # Recover cache if any
        cache_recover = CacheRecover(import_cache=self.import_cache)

        # 1. Sample postal codes

        raw_data = cache_recover.recover_cache()

        pc_sampler = PostcodeSampler(n_per_region=self.n_per_region, set_seed=self.set_seed)
        pc_sample = pc_sampler.pc_sampler(import_cache=self.import_cache)

        # 2. Scrape data
        if not self.import_cache:
            raw_data = CachedScraper(pc_sample, n_per_region=self.n_per_region,
                                     fields_of_interest=self.fields_of_interest).run()

        # 3. Transform output into desired form
        clean_data = DataTransformer(raw_data).clean_data

        # 4. Export data
        DataExporter(clean_data, output_id).export()

