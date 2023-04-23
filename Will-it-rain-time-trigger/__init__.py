import datetime
import logging
import sys
import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv


import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
   # load configuration from .env file
    load_dotenv()

    # configure LOGGING
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
                        level= logging.INFO)

    # Create a Twilio account to get these secrets
    TWILLIO_ACCOUNT_SID = os.environ.get('TWILLIO_ACCOUNT_SID')
    TWILLIO_AUTH_TOKEN = os.environ.get('TWILLIO_AUTH_TOKEN')
    TWILLIO_MOBILE_NUMBER = os.environ.get('TWILLIO_MOBIL_NUMBER')
    API_OPENWEATHER_KEY = os.environ.get('OW_API')
    YOUR_MOBIL_NUMBER = os.environ.get('NOTIFICATION_MOBILE_NUMBER')

    

    COORDINATES = {
        "praha": (50.087811, 14.420460),    # Prague, Czech Republic
        'neuried': (48.093079, 11.465850)   # Neuried, Germany
    }

    API_URL_ONE_CALL = 'https://api.openweathermap.org/data/2.5/onecall'

    params = {
        'lat': COORDINATES['praha'][0],
        'lon': COORDINATES['praha'][1],
        'appid': API_OPENWEATHER_KEY,
        'exclude': 'current,minutely,daily',
        'lang': 'cz',
    }

    try:
        response = requests.get(url=API_URL_ONE_CALL, params=params)
        response.raise_for_status()
        logging.info(f'Open Weather Request Status: {response.reason}')
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e.response.content.decode('utf-8')}")
        sys.exit("Fatal Error")
    else:
        data = response.json()['hourly']
        will_rain = False

        for hour in data[slice(12)]:
            if 900 > hour['weather'][0]['id']:
                will_rain = True
                logging.info('OW: It will be raining today. An SMS will be send.')
            else:
                logging.info('OW: TODAY will not be raining. End of program...\n')
        if will_rain:
            client = Client(TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN)
            message = client.messages \
                .create(
                body="It's going to rain. Remember to bring an ☂️",
                from_=TWILLIO_MOBILE_NUMBER,
                to= YOUR_MOBIL_NUMBER
            )
            logging.info(f"SMS was sent '{message.status}'. End of program...\n")
