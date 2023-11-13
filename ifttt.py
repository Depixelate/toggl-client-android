"""
Function(s) to deal with IFTTT Webhooks
"""

import time
import requests
import toggl
import logging

IFTTT_KEY = "ebnnyeYuoXIQPVETP3csWrF1FzIwfZH6nQRtYpnu6UH"
IFTTT_DELAY = 5
REQUEST_TIMEOUT = 10
#DELAY = 5


def phone_notification():
    """
    triggers the phone alarm via IFTTT webhook
    """
    while True:
        try:
            logging.info("Calling IFTTT Webhook...")
            data = requests.get(
                f"https://maker.ifttt.com/trigger/pomo_done/with/key/{IFTTT_KEY}",
                timeout=REQUEST_TIMEOUT,
            )

            logging.info("IFTTT Response: %s", toggl.log_str(data))
            break

        except Exception as _:  # pylint:disable=W0718
            logging.exception(
                "Error While Making IFTTT Request! Trying again in 5 seconds..."
            )
            time.sleep(IFTTT_DELAY)

