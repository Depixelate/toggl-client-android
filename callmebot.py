"""
Call me bot helper function
"""

import time
import requests
import toggl_punish_utils.toggl as toggl
import logging

# IFTTT_KEY = "ebnnyeYuoXIQPVETP3csWrF1FzIwfZH6nQRtYpnu6UH"
# IFTTT_DELAY = 5
REQUEST_TIMEOUT = 40
DELAY = 5


def phone_notification():
    """
    triggers a telegram phone call using CallMeBot
    """
    while True:
        try:
            logging.info("Calling via Telegram Bot at %s...", toggl.get_now())
            URL = "http://api.callmebot.com/start.php?user=@sukesshv&text=Create+A+New+Alarm&rpt=5&cc=missed"
            response = requests.post(URL, timeout=REQUEST_TIMEOUT)
            logging.info("Response from bot: %s", toggl.log_str(response))
            if response.status_code == 200:
                
                break
            else:
                logging.info("Error!, couldn't call bot, retrying in %s seconds...", DELAY)
                time.sleep(DELAY)
            
        except Exception as _:
            logging.exception(
                "Error while making call! Trying again in %d seconds",
                DELAY
            )
            time.sleep(DELAY)

