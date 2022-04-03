import json
import logging
import sys
import time

import requests
import tweepy

import config
import currencies
from twitter_secrets import *

logging.basicConfig(filename='debug.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info('Bot Starting...')


def create_tweet(book_order):
    # TODO: FIX amount could have decimals
    if book_order['has_range']:
        amount = f"{int(float(book_order['min_amount'])):,}-{int(float(book_order['max_amount'])):,}"
    else:
        amount = f"{int(float(book_order['amount'])):,}"

    currency = currencies.CURRENCIES[str(book_order['currency'])]
    flag = currencies.get_flag(currency)

    tweet = f"""
Type: {config.ROBOSATS_ORDER_TYPE[book_order['type']]}
Amount: {amount}
Currency: {currency} {flag}
Payment method: {book_order['payment_method']} 
Premium: {book_order['premium']}%
Price: {int(float(book_order['price'])):,}
LINK: http://unsafe.robosats.com/ref/pUk9azW4KTw
LINK (TOR): http://robosats6tkf3eva7x2voqso3a5wcorsnw34jveyxfqi2fu7oyheasid.onion/ref/pUk9azW4KTw
    """
    return tweet


def load_persistence_file():
    # Load persistence file. It includes already posted order ids
    try:
        with open(config.PERSISTENCE_FILE, 'r') as f:
            published_orders = json.load(f)
    except FileNotFoundError:
        logger.info("Persistence file not found")
        published_orders = []

    return published_orders


def create_twitter_client():
    client = tweepy.Client(bearer_token=TWITTER_API_BEARER_TOKEN,
                           consumer_key=TWITTER_API_KEY,
                           consumer_secret=TWITTER_API_KEY_SECRET,
                           access_token=TWITTER_API_ACCESS_TOKEN,
                           access_token_secret=TWITTER_API_ACCESS_TOKEN_SECRET)
    return client


def main():
    published_orders = load_persistence_file()
    twitter_client = create_twitter_client()

    # Main loop where we will poll Robosats for the orderbook and tweet new orders
    while True:
        logger.info('Fetching Robosats order book')
        order_book = None
        while not order_book:
            try:
                order_book = requests.get(config.ROBOSATS_API_ORDERBOOK, proxies=config.PROXIES).json()
            except requests.RequestException:
                logger.exception("Error retrieving orderbook. Waiting 10 secs to retry")
                time.sleep(10)

        for order in order_book:
            if order['id'] not in published_orders:
                message = create_tweet(order)
                logger.debug(message)
                response = twitter_client.create_tweet(text=message, user_auth=True)
                logger.debug(response)
                published_orders.append(order['id'])

        with open(config.PERSISTENCE_FILE, 'w') as f:
            json.dump(published_orders, f)

        logger.info(f'Job done. Sleeping for {config.POLL_INTERVAL} seconds')
        time.sleep(config.POLL_INTERVAL)


if __name__ == '__main__':
    while True:
        try:
            # main only returns in case of an unhandled exception
            main()
        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt. Quitting")
            sys.exit(0)
        except:
            logger.exception('Catched unexpected exception. Waiting 30 seconds to retry')
            time.sleep(30)
