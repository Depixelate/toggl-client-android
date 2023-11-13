"""
Checks toggl track to see if person idle for too long, if so punishes them.
"""
import logging
import re
from datetime import timedelta
import azure.functions as func
import toggl
import telegram

# PATH_PREFIX = "" #str(Path.home()) + "/data"

app = func.FunctionApp()


@app.schedule(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
)
# Azure expects this name, so it has to be in camelCase, so we disable the pylint warning.
def timer_trigger(myTimer: func.TimerRequest) -> None:  # pylint: disable=C0103
    """
    The basic timer trigger function.
    """
    if myTimer.past_due:
        logging.info("The timer is past due!")

    main()

    #!/usr/bin/python3


PERIOD = 60

COUNT_KEY = "punish_val"
# LAST_UPDATE_KEY = "last_update"
# DATA_PATH = f"{PATH_PREFIX}/punish_data.db"


def gen_new_desc(desc_no_extras, punish_val, end=None):
    """
    The timer description should always have the punish count displayed on it.
    This takes the desc. without the punish count, and the punish count,
    and combines them together to give the proper timer description.
    Since the system only has minute precision, it also rounds the end datetime to the nearest minute
    """
    end_str = ""
    if end:
        local_end = toggl.to_local(end)
        minute, second = local_end.minute, local_end.second
        minute = round(minute + second/60)
        end_str = local_end.replace(minute=minute, second=second).strftime("(%I:%M)")
    new_desc = f"{end_str}{desc_no_extras}(count: {punish_val})"
    return new_desc


def update_punish_val(new_val):
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


def remove_extras(regexs, desc):
    """
    This removes all the extras/attributes in the timer description
    as defined by the regexs, and then returns the resulting pure desc.
    """
    for regex in regexs.values():
        desc = re.sub(regex, "", desc)

    return desc


def main():
    """
    The main function.
    """

    # NUM_REGEX = r"\d+"
    # TIME_REGEX = r"(\d{1,2}):(\d{2})"

    regexs = {}
    regexs["time"] = r"^\((\d{1,2}):(\d{1,2})\)"
    regexs["duration"] = r"^\((\d+)\)"
    regexs["count"] = r"\(\s*count:\s*(\d+)\s*\)$"

    logging.info("Entered Main V3")

    # next_time += PERIOD
    # scheduler.enterabs(next_time, 1, main, (scheduler, next_time))

    try:
        # with shelve.open(DATA_PATH) as shelf:
        #     punish_val = update_punish_val(
        #         shelf[COUNT_KEY] if COUNT_KEY in shelf else 0
        #     )
        punish_val = 120
        # last_update = (
        #     shelf[LAST_UPDATE_KEY]
        #     if LAST_UPDATE_KEY in shelf
        #     else toggl.get_now_utc()
        # )

        workspace_id = toggl.get_default_workspace_id()
        cur_timer = toggl.get_curr_timer()
        workspace_id = workspace_id if workspace_id else cur_timer["workspace_id"]

        logging.info("Initial punish_val = %s", punish_val)
        # logging.info("Initial last_update = %s", last_update)

        if cur_timer is None:
            desc = toggl.NOTHING_TIMER_NAME
            start = toggl.get_last_entry_end()
            toggl.start_timer(start, desc, workspace_id)
            cur_timer = toggl.get_curr_timer()

        desc = cur_timer["description"]

        start = toggl.from_toggl_format(cur_timer["start"])

        #end = start + timedelta(minutes=toggl.TASK_DEFAULT_THRESH)
        end = toggl.get_now_utc()
        cur_time = toggl.get_now()
        cur_time_utc = toggl.get_now_utc()

        logging.info("Now in UTC: %s", cur_time_utc)

          # datetime.now().astimezone()
        
        # tags = cur_timer["tags"]

        # for tag in tags:
        #     ret = re.findall(TIME_REGEX, tag)
        #     if ret:
        #         hour, minute = [int(field) for field in ret[0]]
        #
        #         break

        #     ret = re.findall(NUM_REGEX, tag)
        #     if ret:
        #
        #         break

        results = get_results(regexs, desc)
        if results["time"]:
            hour, minute = [int(field) for field in results["time"][0]]
            end = cur_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end = toggl.to_utc(end)
            while end <= start:
                end += timedelta(hours=12)
        elif results["duration"]:
            end = start + timedelta(minutes=int(results["duration"][0]))

        logging.info("Timer Expected End: %s", toggl.to_local(end))

        if not results["count"]:
            entries = toggl.get_entries()
            for entry in entries:
                results = get_results(regexs, entry["description"])
                if results["count"]:
                    break
            else:
                results["count"] = ["0"]

        punish_val = update_punish_val(int(results["count"][0]))

        desc_no_extras = remove_extras(regexs, desc)

        # if not re.search(COUNT_REGEXP, desc):
        #     desc_no_extras = desc
        # else:

        #     desc_no_extras = re.sub(COUNT_REGEXP, r"", desc)
        is_nothing = desc_no_extras.casefold() == toggl.NOTHING_TIMER_NAME.casefold()
        if is_nothing:
            end = start + timedelta(minutes=toggl.NOTHING_THRESH)

        new_desc = gen_new_desc(desc_no_extras, punish_val, end)

        if desc_no_extras == toggl.PUNISH_TIMER_NAME:
            if cur_time.hour >= 0 and cur_time.hour <= 1:
                count_since_start = int((cur_time_utc - start).total_seconds() / PERIOD)
                count_since_start = min(count_since_start, 120)
                punish_val = update_punish_val(punish_val - count_since_start)
                logging.info("Count since start: %d", count_since_start)
                new_desc = f"(06:00)Sleep(count: {punish_val})"
                logging.info(
                    "Created a sleep toggl timer, new punish val: %d", punish_val
                )
            else:
                last_update = toggl.from_toggl_format(cur_timer["at"])
                logging.info("Last time timer updated: %s", last_update)
                time_since_update = cur_time_utc - last_update
                secs_since_update = time_since_update.total_seconds()
                punish_amount = round(secs_since_update / PERIOD)
                punish_val = update_punish_val(punish_val + punish_amount)
                # last_update = cur_time_utc
                new_desc = gen_new_desc(desc_no_extras, punish_val)
            toggl.update_timer(cur_timer, new_desc)

        elif cur_time_utc >= end:
            if is_nothing:
                extra = (cur_time_utc - end).total_seconds()
                extra = int(extra / PERIOD)

                punish_val = update_punish_val(
                    punish_val + 30 + extra
                )

                new_desc = gen_new_desc(toggl.PUNISH_TIMER_NAME, punish_val)
                # last_update = cur_time_utc

                toggl.start_timer(cur_time_utc, new_desc, workspace_id)
            else:
                new_desc = gen_new_desc(
                    toggl.NOTHING_TIMER_NAME, punish_val, end + timedelta(minutes=2)
                )
                telegram.call()
                toggl.start_timer(end, new_desc, workspace_id)
        elif desc != new_desc:
            toggl.update_timer(cur_timer, new_desc)

        logging.info("Final punish_val=%s", punish_val)
        # logging.info("Final last_update=%s", last_update)

        # with shelve.open(DATA_PATH) as shelf:
        #     shelf[COUNT_KEY] = punish_val
        # shelf[LAST_UPDATE_KEY] = last_update
    except Exception as _:  # pylint: disable=W0718
        logging.exception("Ran into the following error: ")


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
