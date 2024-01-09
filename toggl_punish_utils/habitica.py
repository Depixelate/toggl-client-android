"""
python convenience functions for interfacing with the habitica api
"""
# /* ========================================== */
# /* [Users] Required script data to fill in    */
# /* ========================================== */
import logging
import requests
import toggl_punish_utils.toggl as toggl
import toggl_punish_utils.request_utils as ru

TIMEOUT = ru.TIMEOUT

USER_ID = "e544ce9c-d7a4-448c-8b1b-f6b4c4595be1"
API_TOKEN = "c0b7ac19-9616-4f1a-b0d9-7e9ae9de0465"  # // Do not share this to anyone
# WEB_APP_URL = "https://script.google.com/macros/s/AKfycbza2ycTHQAfNt_L53DrjXKf1uJOiePT3x1R5SGl7vbwSojuLMSsRWh5z6ujZfzrdkNu6A/exec"

# /* ========================================== */
# /* [Users] Required customizations to fill in */
# /* ========================================== */
# // [Developers] Place all mandatory user-modified variables here
# // - e.g, skill to use, number of times to use, task to use skill on, etc.

# /* ========================================== */
# /* [Users] Optional customizations to fill in */
# /* ========================================== */
# // [Developers] Place all optional user-modified variables here
# // - e.g. enable/disable notifications, enable/disable script features, etc.

# /* ========================================== */
# /* [Users] Do not edit code below this line   */
# /* ========================================== */
# // [Developers] Place your user ID and script name here
# // - This is used for the "X-Client" HTTP header
# // - See https://habitica.fandom.com/wiki/Guidance_for_Comrades#X-Client_Header
AUTHOR_ID = "e544ce9c-d7a4-448c-8b1b-f6b4c4595be1"
SCRIPT_NAME = "OneScriptToRuleThemAll"
HEADERS = {
    "x-client": AUTHOR_ID + "-" + SCRIPT_NAME,
    "x-api-user": USER_ID,
    "x-api-key": API_TOKEN,
}


# // [Developers] Add global variables here
# // - Note that these do not persist in between script calls
# // - If you want to save values between calls, use PropertiesService
# // - See https://developers.google.com/apps-script/reference/properties/properties-service

# Porcelein


def remove_coins(coin_cost):
    """
    helper function to remove a certain number of coins
    """
    ALIAS = "togglHabiticaPunish"
    ru.run_request(create_reward, ALIAS, coin_cost)
    ru.run_request(buy_reward, ALIAS)
    ru.run_request(delete_reward, ALIAS)


# Plumbing


def run_cron():
    """
    Runs the Habitica cron
    """
    url = "https://habitica.com/api/v3/cron"
    response = requests.post(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug("Response to cron: %s", toggl.log_str(response))
    return response


def sync_stats():
    """
    python wrapper around syncing stats
    """
    url = "https://habitica.com/api/v3/user/stat-sync"
    response = requests.post(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug("Response to syncing stats: %s", toggl.log_str(response))
    return response


def get_tasks(task_type=None):
    """
    returns the user's task data
    """
    url = (
        f"https://habitica.com/api/v3/tasks/user?type={task_type}"
        if task_type
        else "https://habitica.com/api/v3/tasks/user"
    )
    response = requests.get(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug(
        "result of requesting tasks of type %s: %s", task_type, toggl.log_str(response)
    )
    return response.json()


def get_dailies():
    """
    returns the user's dailies
    """
    return get_tasks("dailys")


def set_task_text(task_id, new_text):
    """
    sets the text of the task with the given id to 'new_text'
    """
    url = f"https://habitica.com/api/v3/tasks/{task_id}"
    payload = {"text": new_text}
    response = requests.put(url=url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug(
        "result of setting text of task with id %s to %s: %s",
        task_id,
        new_text,
        toggl.log_str(response),
    )
    return response


def get_user_profile(fields=None):
    """
    returns the user's profile data
    """
    query_string = ""
    if fields:
        query_string = f"?userFields={','.join(fields)}"

    url = f"https://habitica.com/api/v3/user{query_string}"
    response = requests.get(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug(
        "result of requesting user_profile with this queryString=%s: %s",
        query_string,
        toggl.log_str(response),
    )
    return response.json()


def get_cron_history():
    """
    returns the previous crons that have been run
    """

    profile = get_user_profile(["history.exp"])
    return profile["data"]["history"]["exp"]

def is_player_in_inn():
    """
    returns whether the user is in the inn or not
    """
    profile = get_user_profile(["preferences"])
    return profile["data"]["preferences"]["sleep"]


def get_coins():
    """
    returns the number of coins the user has.
    """
    profile = get_user_profile(["stats.gp"])
    return profile["data"]["stats"]["gp"]

def toggle_player_in_inn():
    """
    toggles player in inn mode
    """
    url = "https://habitica.com/api/v3/user/sleep"
    response = requests.post(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug("Response to toggling sleep: %s", toggl.log_str(response))
    return response

def create_reward(alias, cost):
    """
    Creates a Reward in Habitica with the given alias and cost, the name is the same as the alias
    Note the alias must not have spaces, (It must be a valid identifier)
    """
    payload = {"text": alias, "type": "reward", "alias": alias, "value": cost}

    # params = {
    #   'method' : 'POST',
    #   'headers' : HEADERS,
    #   'contentType' : 'application/json',
    #   "payload" : JSON.stringify(payload),
    #   "muteHttpExceptions" : true
    # }
    url = "https://habitica.com/api/v3/tasks/user"
    response = requests.post(url=url, headers=HEADERS, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    # response = UrlFetchApp.fetch(url, params)
    logging.debug("create_reward response: %s", toggl.log_str(response))
    return response


def buy_reward(alias):
    """
    Purchases a reward with the given alias on behalf of the user
    """
    # const params = {
    #   'method': 'POST',
    #   'headers': HEADERS,
    #   "muteHttpExceptions" : true
    # };
    url = "https://habitica.com/api/v3/tasks/" + alias + "/score/down"
    response = requests.post(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug("buy_reward response: %s", toggl.log_str(response))
    return response


def delete_reward(alias):
    """
    Deletes the reward with the given alias on behalf of the user
    """
    # const params = {
    #   'method': 'DELETE',
    #   'headers': HEADERS,
    #   "muteHttpExceptions" : true
    # };
    url = "https://habitica.com/api/v3/tasks/" + alias
    response = requests.delete(url=url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    logging.debug("delete_reward response: %s", toggl.log_str(response))
    return response


# function doOneTimeSetup() {

#   createReward(ALIAS, 3);
#   buyReward(ALIAS);
#   deleteReward(ALIAS);
#   // [Developers] These are one-time initial setup instructions that we'll ask
#   //   the user to manually execute only once, during initial script setup
#   // - Add api_createWebhook() here, already set up to activate the trigger to the
#   //   event that you want to service
#   // - Feel free to do all other one-time setup actions here as well
#   //   e.g. creating tasks, reward buttons, etc.
# }

# function doPost(e) {

#   // [Developers] This is the function that will be executed whenever Habitica
#   //   encounters the designated event

#   const dataContents = JSON.parse(e.postData.contents);
#   const webhookType = dataContents.type;

#   console.log(dataContents);

#   if(!(webhookType === "scored" && dataContents.task.down && dataContents.task.type === "habit")) {
#     return HtmlService.createHtmlOutput();
#   }

#   const name = dataContents.task.text;
#   let coinsCost = 0;
#   const coinsRegex = /cost:\s*(\d+)/;
#   if (coinsRegex.test(name)) {
#     coinsCost = parseInt(name.match(coinsRegex)[1]);
#   }
#   const ALIAS = "PunishReward";
#   createReward(ALIAS, coinsCost);
#   buyReward(ALIAS);
#   deleteReward(ALIAS);
#   ///const punishCost = Math.trunc(coinsCost * 7.5);

#   //console.log(e);

#   // Logger.log(e);
#   //throw new Error(JSON.stringify(e));

#   // [Developers] Add script actions here

#   return HtmlService.createHtmlOutput();
# }

# // [Developers] Place all other functions below doOneTimeSetup() and doPost()
# // - Ideally prefix functions that access the API with "api_" to quickly see which ones
# //   access the API and be able budget your 30 requests per minute limit well
