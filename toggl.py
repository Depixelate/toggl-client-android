"""
List of helper functions when dealing with toggl timers.
"""

from datetime import datetime, timezone, timedelta
import logging
from pprint import pformat
import requests
import toggl_punish_utils.request_utils as request_utils

API_TOKEN = "94210a87e4eda16f53bca10e9421636a"

PUNISH_TIMER_NAME = "PUNISH"
NOTHING_TIMER_NAME = "Nothing"
SLEEP_TIMER_NAME = "Sleep-Night"
BREAK_TIMER_NAME = "Break"

NOTHING_THRESH = 2
TASK_DEFAULT_THRESH = 25


def log_str(obj):
    """
    Takes an object, and returns a logging string displaying all its variables,
    or repr(obj) if it doesn't have a __dict__ attribute.
    """
    try:
        return pformat(vars(obj))
    except TypeError:
        return repr(obj)


def get_now_utc() -> datetime:
    """
    returns the current time in utc
    """
    return datetime.now(timezone.utc)


def get_now():
    """
    returns the current time in IST
    """
    return datetime.now(timezone(timedelta(hours=5, minutes=30), name="IST"))


def to_toggl_format(dtime: datetime):
    """
    converts a datetime object to the string format expected by toggl track
    """
    return dtime.strftime("%Y-%m-%dT%H:%M:%SZ")


def from_toggl_format(time_str: str) -> datetime:
    """
    converts a string expressing a datetime in toggl's format to a datetime object
    """
    if time_str[-1] == "Z":
        time_str = f"{time_str[:-1]}+00:00"
    return datetime.fromisoformat(time_str)


def get_curr_timer():
    """
    returns json data representing the currently running Toggl Timer
    """
    logging.info("Requesting Current Timer Info...")
    cur_timer = requests.get(
        "https://api.track.toggl.com/api/v9/me/time_entries/current",
        auth=(API_TOKEN, "api_token"),
        headers={"Content-Type": "application/json"},
        timeout=request_utils.TIMEOUT,
    )
    logging.info("Response: %s", log_str(cur_timer))
    return cur_timer.json()


def get_default_workspace_id():
    """
    gets the default workspace id
    """
    logging.info("Requesting User Data...")
    data = requests.get(
        "https://api.track.toggl.com/api/v9/me",
        auth=(API_TOKEN, "api_token"),
        headers={"content-type": "application/json"},
        timeout=request_utils.TIMEOUT,
    )
    workspace_id = data.json()["default_workspace_id"]
    logging.info("Response: %s", log_str(data))
    return workspace_id


def get_entries():
    """
    Queries Toggl Track for the list of most recent entries.
    They are sorted from most recent start to least recent start.
    """
    logging.info("Requesting Previous Timers...")
    data = requests.get(
        "https://api.track.toggl.com/api/v9/me/time_entries",
        auth=(API_TOKEN, "api_token"),
        headers={"content-type": "application/json"},
        timeout=request_utils.TIMEOUT,
    )
    json = data.json()
    logging.info("Latest entry: %s", json[0])
    return json


def get_last_entry_end():
    """
    Gets the list of entries from toggl api, then  get the last entry's end.
    """
    entries = get_entries()
    if entries is not None and len(entries) > 0:
        for entry in entries:
            if entry["duration"] > 0:  # Invalid entries will have duration 0,
                start = entry["stop"]  # running will have value < 0
                start = from_toggl_format(start)
                return start

    return get_now_utc()


def calc_duration(start: datetime):
    """
    Returns the value for the duration field for creating/updating a timer,
    which is -(the amount of seconds after the UNIX epoch the timer started)
    We set the duration to this value, even though Toggl V9 docs say to set to -1
    for a running timer, because the toggl desktop applications still use this value
    to calculate the duration to show on the mini-timer, instead of calculating it
    from start, as the V8 api says.
    """
    return -int(start.timestamp())


def start_timer(
    start: datetime, desc: str, workspace_id: int, tags: list[str] = ("waste",)
):
    """
    starts a running timer with the given start date and description in the
    given workspace with the given tags by calling toggl's api
    """
    tags = list(tags)
    logging.info(
        "Starting New Timer: start=%s, desc=%s, workspace_id=%s, tags=%s",
        start,
        desc,
        workspace_id,
        tags,
    )

    duration = calc_duration(start)
    data = requests.post(
        f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries",
        auth=(API_TOKEN, "api_token"),
        json={
            "created_with": "Requests",
            "description": desc,
            "tags": tags,
            "billable": False,
            "workspace_id": workspace_id,
            "duration": duration,
            "start": to_toggl_format(start),
            "end": None,
        },
        headers={"Content-Type": "application/json"},
        timeout=request_utils.TIMEOUT,
    )
    logging.info("Response: %s", log_str(data))
    return data.json()


def update_timer(old_timer, new_desc):
    """
    Updates the currently running timer on Toggl with a new description.
    """
    logging.info(
        "Updating Timer: new_desc = %s, old_timer = %s", new_desc, log_str(old_timer)
    )
    start, timer_id, workspace_id = (
        from_toggl_format(old_timer["start"]),
        old_timer["id"],
        old_timer["workspace_id"],
    )
    duration = calc_duration(start)
    new_timer = {
        "billable": old_timer["billable"],
        "description": new_desc,
        "duration": duration,
        "start": to_toggl_format(start),
        "workspace_id": workspace_id,
        "created_with": "requests",
        "project_id": old_timer["project_id"],
    }
    data = requests.put(
        f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries/{timer_id}",
        json=new_timer,
        headers={"content-type": "application/json"},
        auth=(API_TOKEN, "api_token"),
        timeout=request_utils.TIMEOUT,
    )

    # data = requests.patch(
    # f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries/{timer_id}',
    # json={"array": [{"op": "replace", "path": "/description", "value": new_desc}]},
    # headers={'content-type': 'application/json'},
    # auth = (API_TOKEN, 'api_token')
    # )

    logging.info("Response: %s", log_str(data))
    return data.json()


def to_utc(d_time: datetime):
    """
    converts an aware datetime with a given utc offset to the same datetime in UTC.
    """
    return d_time.replace(tzinfo=timezone.utc) - d_time.utcoffset()


def to_local(d_time: datetime):
    """
    converts a datetime in some other timezone to local time
    """
    now = get_now()
    local = now + (d_time - now)
    return local
