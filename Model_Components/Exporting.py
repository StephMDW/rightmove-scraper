import os
import logging
from datetime import datetime
import pandas as pd

class DataExporter:
    """This class is responsible for exporting the clean data to a CSV file."""
    def __init__(self, clean_data, output_id):
        self.clean_data = clean_data
        self.output_id = output_id

    def export(self):
        while True:
            try:
                if self.clean_data is None or (isinstance(self.clean_data, pd.DataFrame) and self.clean_data.empty):
                    break
                output_path = os.getcwd() + f"/Outputs/rightmove_data_{self.output_id}.csv"
                self.clean_data.to_csv(output_path, index=False)

                logging.info(f"Terminating program. Data saved in the following location: {output_path}")
                break
            except Exception:
                input("Could not save the data! Check if filepath is available before pressing Enter.")

