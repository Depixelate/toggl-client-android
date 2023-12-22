"""
Function(s) to deal with IFTTT Webhooks
"""
import logging
import requests
import toggl_punish_utils.toggl as toggl
import toggl_punish_utils.request_utils as request_utils

IFTTT_KEY = "ebnnyeYuoXIQPVETP3csWrF1FzIwfZH6nQRtYpnu6UH"
IFTTT_DELAY = 5
REQUEST_TIMEOUT = 10


# def phone_notification():
#     """
#     triggers the phone alarm via IFTTT webhook
#     """
#     while True:
#         try:
            # logging.info("Calling IFTTT Webhook...")
            # data = requests.get(
            #     f"https://maker.ifttt.com/trigger/pomo_done/with/key/{IFTTT_KEY}",
            #     timeout=REQUEST_TIMEOUT,
            # )

            # logging.info("IFTTT Response: %s", toggl.log_str(data))
            
#             break

#         except Exception as _:  # pylint:disable=W0718
#             logging.exception(
#                 "Error While Making IFTTT Request! Trying again in 5 seconds..."
#             )
#             time.sleep(IFTTT_DELAY)

def _phone_notification():
    """
    internal phone notification caller..
    """
    logging.info("Calling IFTTT Webhook...")
    data = requests.get(
        f"https://maker.ifttt.com/trigger/pomo_done/with/key/{IFTTT_KEY}",
        timeout=request_utils.TIMEOUT,
    )
    data.raise_for_status()

    logging.debug("IFTTT Response: %s", toggl.log_str(data))
    return data

def phone_notification():
    """
    Actual phone notification caller, with exception handling built-in
    """
    return request_utils.run_request(_phone_notification)
