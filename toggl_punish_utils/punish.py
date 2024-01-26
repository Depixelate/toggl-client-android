"""
Checks toggl track to see if person idle for too long, if so punishes them.
"""
import logging
import re
from datetime import timedelta
import toggl_punish_utils.toggl as toggl
import toggl_punish_utils.request_utils as ru
import toggl_punish_utils.telegram as telegram

# import azure.functions as func


# PATH_PREFIX = "" #str(Path.home()) + "/data"

# app = func.FunctionApp()


# @app.schedule(
#     schedule="0 * * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
# )
# #Azure expects this name, so it has to be in camelCase, so we disable the pylint warning.
# def timer_trigger(myTimer: func.TimerRequest) -> None: #pylint: disable=C0103
#     """
#     The basic timer trigger function.
#     """
#     if myTimer.past_due:
#         logging.info("The timer is past due!")

#     main()

#!/usr/bin/python3


PERIOD = 60


class Regex:
    """
    Regular Expression Constants.
    """

    TIME = r"\((s?\d{1,2}):(\d{1,2})\)"
    DURATION = r"\((\d+)\)"
    COUNT = r"\(\s*count:\s*(\d+)\s*\)"
    # TIME = r"^\((\d{1,2}):(\d{1,2})\)"
    # DURATION = r"^\((\d+)\)"
    # COUNT = r"\(\s*count:\s*(\d+)\s*\)$"  # the /s at the beginning and end is there, because it might not start at end.


regex_dict = {"time": Regex.TIME, "duration": Regex.DURATION, "count": Regex.COUNT}

# COUNT_KEY = "punish_val"
# LAST_UPDATE_KEY = "last_update"
# DATA_PATH = f"{PATH_PREFIX}/punish_data.db"

# Porcelein

def get_last_count():
    """
    Looks at the currently running entries, and based on that, returns the count value of the latest entry.
    """
    entries = ru.run_request(toggl.get_entries)
    last_count = 0
    for entry in entries:
        # logging.info(entry["description"])
        count = re.findall(Regex.COUNT, entry["description"])
        # logging.info(count)
        if count:
            last_count = int(count[0])
            break
    return last_count


def update_punish_val(new_val, tags = None):
    """
    higher level function to replace current punish val with new one.
    """
    if tags is None:
        tags = []
    cur_timer = ru.run_request(toggl.get_curr_timer)
    desc_without_count = strip_desc([Regex.COUNT], cur_timer["description"])
    new_desc = gen_new_desc(desc_without_count, new_val)
    ru.run_request(toggl.update_timer, cur_timer, new_desc, tags)

# Plumbing

def gen_new_desc(desc_no_extras, punish_val = None, end=None, is_timed_task = False):
    """
    The timer description should always have the punish count displayed on it.
    This takes the desc. without the punish count, and the punish count,
    and combines them together to give the proper timer description.
    Since the system only has minute precision, it also rounds the end datetime to the nearest minute
    """
    punish_str = ""
    end_str = ""
    if punish_val is not None:
        punish_str = f"(count: {punish_val})"
    if end is not None:
        local_end = toggl.to_local(end)
        minute, second = local_end.minute, local_end.second
        new_minute = round(minute + second/60)
        diff = timedelta(minutes=new_minute-minute)
        logging.info("In gen_new_desc, end, minute, second: %s, %s, %s", end, minute, second)
        new_local_end = local_end + diff
        end_str = new_local_end.strftime("(s%I:%M)") if is_timed_task else new_local_end.strftime("(%I:%M)")
    new_desc = f"{end_str}{desc_no_extras}{punish_str}"
    return new_desc


def clamp_punish_val(new_val):
    """
    takes the new value that the program wants to assign to punish_val,
    and then adjusts it so that it lies within proper bounds.
    """
    if new_val < 0:
        new_val = 0
        logging.warning("punish_val was found to be negative, resetting to 0.")
    elif new_val > 5000:
        new_val = 0
        logging.warning("punish_val was found to be > 5000, resetting to 0.")

    return new_val


def get_results(regexs, desc):
    """
    Takes the description of the timer, and then runs the attribute regexs
    to extract information, like the punish count.
    """
    results = {name: re.findall(regex, desc) for name, regex in regexs.items()}
    return results


def strip_desc(regexs, desc):
    """
    This removes all the extras/attributes in the timer description
    as defined by the regexs, and then returns the resulting pure desc.
    """
    for regex in regexs:
        desc = re.sub(regex, "", desc)

    return desc


def remove_extras(regexs, desc):
    """
    This removes all the extras/attributes in the timer description
    as defined by the regexs, and then returns the resulting pure desc.
    """
    return strip_desc(regexs.values(), desc)

def start_nothing_timer(workspace_id, start, punish_val = None, tags = None, is_timed_task = False):
    """
    Starts "Nothing" Timer with the given punish val, tags, etc.
    """
    if(tags is None):
        tags = []
    new_desc = gen_new_desc(
        toggl.NOTHING_TIMER_NAME, punish_val, start + timedelta(minutes=2), is_timed_task
    )
    tags += last_update_tags(punish_val, "NS") # tells you the min as well, telling you extra sits
    if not is_timed_task:
        telegram.message('Nothing Timer started!')
        telegram.call()
    toggl.start_timer(start, new_desc, workspace_id, tags)

def last_update_tags(punish_val, timer_code):
    """
    Helper function to generate tags
    """
    cur_time = toggl.get_now()
    return ["waste", f"LU-{timer_code}-{cur_time.hour}:{cur_time.minute}-P-{punish_val}"]

# regexs = {k.lower() : v for k, v in vars(Regex)} //doesn't work, includes extra stuff.

# logging.basicConfig(
#     filemode="w",
#     filename="toggl_punish.log",
#     format="%(asctime)s %(levelname)s:%(message)s",
#     level=logging.INFO,
# )
# logging.info("=================NEW RUN=====================")
# my_scheduler = sched.scheduler(time.time, time.sleep)
# start_time = time.time()
# my_scheduler.enterabs(start_time, 1, main, (my_scheduler, start_time))
# my_scheduler.run()
