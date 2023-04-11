import logging

class DataTransformer:
    """This class is responsible for transforming the raw data to clean data ready for export."""
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @property
    def clean_data(self):
        """Removes duplicates and empty rows from the dataset and report clean sample size"""

        while True:
            try:
                if len(self.raw_data) == 0:
                    logging.info("Dataset is empty.Exiting program!")
                    break
                nonduplicated_data = self.raw_data.drop_duplicates()
                duplicates_attrition = (len(self.raw_data) - len(nonduplicated_data)) / len(self.raw_data) * 100
                logging.info(f"Attrition due to duplicates is {round(duplicates_attrition,1)}%")

                clean_data = nonduplicated_data[nonduplicated_data.iloc[:, 1:].notnull().any(axis=1)]
                true_sample = len(clean_data)
                attrition = (len(nonduplicated_data) - true_sample) / len(nonduplicated_data) * 100
                logging.info(f"Attrition due to empty rows is {round(attrition,1)}%")
                logging.info(f"After removing duplicates and empty rows, a sample of {true_sample} remains.")
                return clean_data
            except Exception:
                print(Exception)
                input("Could not transform data! Figure out why and press Enter")

