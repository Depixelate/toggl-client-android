"""
A few constants and functions for handling http requests
"""
import logging
import time

TIMEOUT = (10, 30)
DELAY = 5


def run_request(func, *args, retry = True, timeout=None, delay = None):
    """
    Runs a request until it succeeds.
    """
    global TIMEOUT
    if(timeout is None):
        timeout = TIMEOUT

    original_timeout = TIMEOUT
    TIMEOUT = timeout

    if(delay is None):
        delay = DELAY
        
    data = None
    while True:
        try:
            # logging.info("Calling IFTTT Webhook...")
            data = func(*args)
            # logging.info("IFTTT Response: %s", toggl.log_str(data))
            break

        except Exception as _:  # pylint:disable=W0718

            logging.exception(
                "Ran into the following exception while making request"
            )
            if(retry):
                logging.info("Trying again in %d seconds...",
                delay)
                time.sleep(delay)
            else:
                logging.info("Unable to make request, skipping...")
                break
    TIMEOUT = original_timeout
    return data
