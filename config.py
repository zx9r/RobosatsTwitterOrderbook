POLL_INTERVAL = 60*5

TWITTER_MAX_MESSAGE_LENGTH = 280

ROBOSATS_API_ORDERBOOK = \
    "http://robosats6tkf3eva7x2voqso3a5wcorsnw34jveyxfqi2fu7oyheasid.onion/api/book/?currency=0&type=2"

ROBOSATS_ORDER_TYPE = {
    0: "BUY",
    1: "SELL"
}

ROBOSATS_ORDER_TYPE_BUY = 0
ROBOSATS_ORDER_TYPE_SELL = 1

proxies = {'http':  'socks5h://localhost:9050',
           'https': 'socks5h://localhost:9050'}

persistence_file = 'published_tweets.json'
