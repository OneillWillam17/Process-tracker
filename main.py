import os
import time
import requests
from datetime import datetime
from psutil import process_iter
from dotenv import load_dotenv

# gets env variables from any .env files including the graph id, and the username/token information for the api
load_dotenv()
USERNAME = os.getenv('PIXELA_USERNAME')
TOKEN = os.getenv('PIXELA_TOKEN')
GRAPH_ID = os.getenv('GRAPH_ID')


def add_pixel(date: datetime, amount: str):
    """
    Checks if there is a pixel already at the specified date, if so then takes the time already inputted in pixel and
    adds it to amount specified in the arg.
    if there's no pixel, then it creates a new pixel with the amount of time the process was open and plots it
    """
    endpoint = f"https://pixe.la/v1/users/{USERNAME}/graphs/{GRAPH_ID}/{date.strftime('%Y%m%d')}"
    headers = {"X-USER-TOKEN": TOKEN}
    amount_dict = {"quantity": amount}

    # send get request to see if a pixel already exists in location,
    # if so then take the current amount from there and add to it
    # if no pixel exists create a new one using put and add amount
    try:
        get_pixel = requests.get(url=endpoint, headers=headers)
        get_pixel.raise_for_status()

        # adds the amount currently on the pixel to the amount stored in amount_dict,
        # so we update total amount rather than replacing amount each time
        amount_already_on_pixel = get_pixel.json()['quantity']
        new_amount = str(float(amount_already_on_pixel) + float(amount))

        print(f"get_pixel: {get_pixel.json()}")
        print(f"New amount: {new_amount}")

        amount_dict['quantity'] = new_amount
    except requests.exceptions.HTTPError:
        # this means there is no pixel to take data from at this location/date
        # create a new pixel with just the amount from the arg/dict
        pass

    # after we adjust the amount that we have to add, we then create the pixel
    put_pixel = requests.put(url=endpoint, headers=headers, json=amount_dict)
    put_pixel.raise_for_status()

    print('Pixel added to graph successfully')


def is_running(application: str) -> bool:
    """Checks for a specific process in psutil, if running return True"""
    # iterates through all running processes and adds their name to a list
    list_of_processes = [p.name() for p in process_iter()]

    if application in list_of_processes:
        list_of_processes.clear()
        return True
    else:
        list_of_processes.clear()
        return False


# keeps track of if the specific process was opened within the loop, will contain a datetime object once process is open
time_since_opened = None
process = 'firefox.exe'

# infinite loop that runs every 5 minutes,
# it checks for a specific process and keeps track of total time that process was active on the computer
# after process closes, it calculates the total time and plots a point on the pixela graph using their api
print('Starting loop')
while True:
    if is_running(process):
        # if true it means the process is still active/running
        if time_since_opened is None:
            # means this is the first time the process has been seen (or opened) within the loop
            # mark the starting time the program is opened
            print(f'{process} opened for the first time')
            time_since_opened = datetime.now()
        else:
            # process has already been/is already open, and we already have a starting time
            pass
    else:
        # process isn't running
        # check if it was open during loop by checking if time_since_opened contains a value
        if time_since_opened is not None:
            print(f"{process} closed")
            # means the process was opened and closed at some point within loop
            # mark new time to determine how long process was open
            current_time = datetime.now()
            time_active = current_time - time_since_opened
            # gets the total minutes the process was active
            total_minutes = time_active.total_seconds() / 60

            print(f"\n{process} was open for {time_active}")

            # convert total minutes to str to become usable within the pixela api
            add_pixel(date=current_time, amount=str(total_minutes))

            print('https://pixe.la/@oneillwilliam17')

            # remove start time so program can run again without restarting file
            time_since_opened = None
        else:
            # means the process was never ran
            # and there is nothing to upload to pixela
            pass

    # 5-minute delay between iterations to prevent loop from running too often
    time.sleep(300)
