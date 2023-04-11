import time
import logging
import os
from functools import wraps

"""This file contains general set up information and small functionalities
that don't belong elsewhere."""

def configure_logging(output_id):
    "Helperfunction that allows for formatted logs to appear while processing text"

    filepath = os.getcwd() + f"\\Outputs\\Logs\\logger_{output_id}.txt"
    logging.basicConfig(filename=filepath, filemode="w", level=logging.INFO,
                        format="%(asctime)s - [%(filename)s:%(lineno)d]-[%(funcName)s] %(message)s ",
                        datefmt="%H:%M:%S")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s - [%(filename)s:%(lineno)d]-[%(funcName)s] %(message)s ", datefmt="%H:%M:%S"))
    logging.getLogger("").addHandler(console)

    logging.info(f"Logging configured to write to file: {filepath}")



def timeit(func):
    """Helperfunction that is used for clocking how fast a function runs."""

    @wraps(func)
    def timeit_wrapper(*args, **kwargs):

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        if total_time < 60:
            logging.info(f'Function: {func.__name__} took {total_time:.4f} seconds')
            return result
        elif total_time >= 60:
            if total_time <= 3600:
                logging.info(f'Function: {func.__name__} took {total_time / 60:.4f} minutes')
                return result
            else:

                logging.info(f'Function: {func.__name__} took {total_time / 3600:.4f} hours')
                return result

    return timeit_wrapper


def ensure_connect(func, automatic_attempts=5, sleep_time=10, *args, **kwargs):
    """This function can be wrapped around a function from the Selenium browser class to handle connection issues."""
    attempt = 1
    while True:
        try:
            func(*args, **kwargs)
            break
        except:
            logging.info(
                f"Could not connect to website. Retrying...(automatic attempt {attempt} of {automatic_attempts})")
            attempt += 1
            time.sleep(sleep_time)
            if attempt == automatic_attempts:
                input("Could not execute the function. Ensure you are connected to the internet and press Enter")
