"""
A few constants and functions for handling http requests
"""
import logging
import time

TIMEOUT = 10
DELAY = 5


def run_request(func, *args):
    """
    Runs a request until it succeeds.
    """
    while True:
        try:
            # logging.info("Calling IFTTT Webhook...")
            data = func(*args)
            # logging.info("IFTTT Response: %s", toggl.log_str(data))
            break

        except Exception as _:  # pylint:disable=W0718
            logging.exception(
                "Ran into the following exception while making request, Trying again in %d seconds...",
                DELAY,
            )
            time.sleep(DELAY)
    return data
