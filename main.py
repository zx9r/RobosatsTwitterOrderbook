import json
import logging
import time

import requests
import tweepy

import config
from currencies import CURRENCIES
from twitter_secrets import *

logging.basicConfig(filename='debug.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info('Bot Starting...')


def create_tweet(book_order):
    message = f"""
Type: {config.ROBOSATS_ORDER_TYPE[order['type']]}
Amount: {int(float(order['amount'])):,}
Currency: {CURRENCIES[str(order['currency'])]}
Payment method: {order['payment_method']} 
Premium: {order['premium']}%
Price: {int(float(order['price'])):,}
http://unsafe.robosats.com/order/{order['id']}
http://robosats6tkf3eva7x2voqso3a5wcorsnw34jveyxfqi2fu7oyheasid.onion
    """
    return message


# Load persistence file. It includes already posted order ids
try:
    with open(config.persistence_file, 'r') as f:
        published_orders = json.load(f)
except FileNotFoundError:
    logger.info("Persistence file not found")
    published_orders = []

# Create Twitter client
client = tweepy.Client(bearer_token=TWITTER_API_BEARER_TOKEN,
                       consumer_key=TWITTER_API_KEY,
                       consumer_secret=TWITTER_API_KEY_SECRET,
                       access_token=TWITTER_API_ACCESS_TOKEN,
                       access_token_secret=TWITTER_API_ACCESS_TOKEN_SECRET)

# Main loop where we will poll Robosats for the orderbook and tweet new orders
while True:
    logger.info('Fetching Robosats order book')
    order_book = None
    while not order_book:
        try:
            order_book = requests.get(config.ROBOSATS_API_ORDERBOOK, proxies=config.proxies).json()
        except ConnectionError as e:
            logger.exception("Error retrieving orderbook. Waiting 10 secs to retry")
            time.sleep(10)

    for order in order_book:
        if order['id'] not in published_orders:
            message = create_tweet(order)
            logger.debug(message)
            response = client.create_tweet(text=message, user_auth=True)
            logger.debug(response)
            published_orders.append(order['id'])

    with open(config.persistence_file, 'w') as f:
        json.dump(published_orders, f)

    logger.info(f'Job done. Sleeping for {config.POLL_INTERVAL} seconds')
    time.sleep(config.POLL_INTERVAL)
