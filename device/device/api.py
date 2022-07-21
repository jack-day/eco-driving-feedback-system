"""
API Interaction

Provides interaction with the EcoDriven web app REST API.
"""
from config import CONFIG
import requests
import requests.exceptions as reqExcs
from datetime import datetime

lastRequestSuccessful = True


def apiCall(func):
    def wrapper(*args, **kwargs):
        if CONFIG['apiURL']:
            return func(*args, **kwargs)

    return wrapper


@apiCall
def createJourney(journey):
    """Calls POST /api/journeys to create a journey, returning it's ID"""
    global lastRequestSuccessful
    try:
        response = requests.post(f'{CONFIG["apiURL"]}/journeys',
            headers={'Authorization': f'Bearer {CONFIG["apiAccessToken"]}'},
            json=journey,
            timeout=5
        )

        if response.ok:
            lastRequestSuccessful = True
            data = response.json()
            return data['id']
        else:
            lastRequestSuccessful = False
            print(
                f'[{datetime.now().isoformat()}] Create journey API call ' +
                f'failed with status code {response.status_code}'
            )
    except (reqExcs.ConnectTimeout, reqExcs.ConnectionError):
        lastRequestSuccessful = False
        print('Create journey API call timed out')


@apiCall
def updateJourney(journeyID, data):
    """Calls PUT /api/journeys/:journeyID to update a journey"""
    global lastRequestSuccessful
    try:
        response = requests.put(f'{CONFIG["apiURL"]}/journeys/{journeyID}',
            headers={'Authorization': f'Bearer {CONFIG["apiAccessToken"]}'},
            json=data,
            timeout=5
        )

        if response.ok:
            lastRequestSuccessful = True
        else:
            lastRequestSuccessful = False
            print(
                f'[{datetime.now().isoformat()}] Update journey API call ' +
                f'failed with status code {response.status_code}'
            )
    except (reqExcs.ConnectTimeout, reqExcs.ConnectionError):
        lastRequestSuccessful = False
        print('Update journey API call timed out')


@apiCall
def addScores(scores):
    """Calls POST /api/scores to add scores"""
    global lastRequestSuccessful
    try:
        response = requests.post(f'{CONFIG["apiURL"]}/scores',
            headers={'Authorization': f'Bearer {CONFIG["apiAccessToken"]}'},
            json=scores,
            timeout=5
        )

        if response.ok:
            lastRequestSuccessful = True
        else:
            lastRequestSuccessful = False
            print(
                f'[{datetime.now().isoformat()}] Add scores API call ' +
                f'failed with status code {response.status_code}'
            )
    except (reqExcs.ConnectTimeout, reqExcs.ConnectionError):
        lastRequestSuccessful = False
        print('Add scores API call timed out')
