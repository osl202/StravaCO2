import requests
import json
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def get_data():
    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    payload = {
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'refresh_token': 'a14357cb242f42779c91dc30dc152a1871ec4c2b',
        'grant_type': "refresh_token",
        'f': 'json'
    }

    print("Requesting Token...\n")
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']
    print("Access Token = {}\n".format(access_token))

    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}
    my_dataset = requests.get(activites_url, headers=header, params=param).json()

    
    

def load_data():

    try:
        with open("data/running_data.json", "r") as file:
            print("File found!")
            my_dataset = json.load(file)
        return my_dataset

    except FileNotFoundError:
        print('File does not exist.  Calling API to retrieve data...')
        my_dataset = get_data()

