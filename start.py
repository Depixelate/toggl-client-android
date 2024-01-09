"""
Android Client For Toggl because toggl official always can't sync for some reason
"""
import logging
import sys
import toggl_punish_utils.request_utils as ru
import toggl_punish_utils.toggl as toggl

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.INFO,
)

def get_cur_timer():
    """
    returns the current timer
    """
    cur_timer = ru.run_request(toggl.get_curr_timer, retry=False, timeout=(5, 15))
    return cur_timer

def print_cur_timer(cur_timer):
    """
    prints the current timer
    """
    if cur_timer is not None:
        print(f"Current Timer: {cur_timer['description']}")
    else:
        print("No Timer Running/Unable to get Current Timer")

def main():
    workspace_id = ru.run_request(toggl.get_default_workspace_id)

    while True:
        desc = input("Enter timer description: ")
        if desc.strip().casefold() == "r":
            cur_timer = get_cur_timer()
            print_cur_timer(cur_timer)
        elif desc.strip().casefold() == "":
            cur_timer = get_cur_timer()
            print_cur_timer(cur_timer)
            if(cur_timer is not None):
                ru.run_request(toggl.stop_cur_timer, workspace_id, cur_timer["id"], retry=False, timeout=(5, 15))
                print("Current Timer Stopped!")
        else:        
            ru.run_request(toggl.start_timer, toggl.get_now_utc(), desc, workspace_id)
            print("Timer started successfully!")
            cur_timer = get_cur_timer()
            print_cur_timer(cur_timer)


if __name__ == "__main__":
    main()
