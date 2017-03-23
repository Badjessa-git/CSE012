from __future__ import print_function
'''
Hello student in computational thinking! You don't need to open this file.
'''

_USE_CLASSES = False
_START_CONNECTED = False

__version__ = '7'

import sys, zlib, base64
try:
    import simplejson as json
except ImportError:
    import json

HEADER = {'User-Agent': 'CORGIS Stock library for educational purposes'}
PYTHON_3 = sys.version_info >= (3, 0)

if PYTHON_3:
    from urllib.error import HTTPError
    import urllib.request as request
    from urllib.parse import quote_plus
else:
    from urllib2 import HTTPError
    import urllib2
    from urllib import quote_plus

################################################################################
# Auxilary
################################################################################

def _parse_int(value, default=0):
    """
    Attempt to cast *value* into an integer, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _parse_float(value, default=0.0):
    """
    Attempt to cast *value* into a float, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _parse_boolean(value, default=False):
    """
    Attempt to cast *value* into a bool, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return bool(value)
    except ValueError:
        return default

def _iteritems(_dict):
    """
    Internal method to factor-out Py2-to-3 differences in dictionary item
        iterator methods

    :param dict _dict: the dictionary to parse
    :returns: the iterable dictionary
    """
    if PYTHON_3:
        return _dict.items()
    else:
        return _dict.iteritems()


def _urlencode(query, params):
    """
    Internal method to combine the url and params into a single url string.

    :param str query: the base url to query
    :param dict params: the parameters to send to the url
    :returns: a *str* of the full url
    """
    return query + '?' + '&'.join(key+'='+quote_plus(str(value))
                                  for key, value in _iteritems(params))


def _get(url):
    """
    Internal method to convert a URL into it's response (a *str*).

    :param str url: the url to request a response from
    :returns: the *str* response
    """
    if PYTHON_3:
        req = request.Request(url, headers=HEADER)
        response = request.urlopen(req)
        return response.read().decode('utf-8')
    else:
        req = urllib2.Request(url, headers=HEADER)
        response = urllib2.urlopen(req)
        return response.read()


def _recursively_convert_unicode_to_str(input):
    """
    Force the given input to only use `str` instead of `bytes` or `unicode`.

    This works even if the input is a dict, list,
    """
    if isinstance(input, dict):
        return {_recursively_convert_unicode_to_str(key): _recursively_convert_unicode_to_str(value) for key, value in input.items()}
    elif isinstance(input, list):
        return [_recursively_convert_unicode_to_str(element) for element in input]
    elif PYTHON_3 and isinstance(input, str):
        return str(input.encode('ascii', 'replace').decode('ascii'))
    else:
        return input

def _from_json(data):
    """
    Convert the given string data into a JSON dict/list/primitive, ensuring that
    `str` are used instead of bytes.
    """
    return _recursively_convert_unicode_to_str(json.loads(data))

################################################################################
# Cache
################################################################################

_CACHE = {}
_CACHE_COUNTER = {}
_EDITABLE = False
_CONNECTED = False
_PATTERN = "repeat"


def _start_editing(pattern="repeat"):
    """
    Start adding seen entries to the cache. So, every time that you make a request,
    it will be saved to the cache. You must :ref:`_save_cache` to save the
    newly edited cache to disk, though!
    """
    global _EDITABLE, _PATTERN
    _EDITABLE = True
    _PATTERN = pattern


def _stop_editing():
    """
    Stop adding seen entries to the cache.
    """
    global _EDITABLE
    _EDITABLE = False


def _add_to_cache(key, value):
    """
    Internal method to add a new key-value to the local cache.
    :param str key: The new url to add to the cache
    :param str value: The HTTP response for this key.
    :returns: void
    """
    if key in _CACHE:
        _CACHE[key].append(value)
    else:
        _CACHE[key] = [_PATTERN, value]
        _CACHE_COUNTER[key] = 0


def _clear_key(key):
    """
    Internal method to remove a key from the local cache.
    :param str key: The url to remove from the cache
    """
    if key in _CACHE:
        del _CACHE[key]


def _save_cache(filename="cache.json"):
    """
    Internal method to save the cache in memory to a file, so that it can be used later.

    :param str filename: the location to store this at.
    """
    with open(filename, 'w') as f:
        json.dump({"data": _CACHE, "metadata": ""}, f)


def _lookup(key):
    """
    Internal method that looks up a key in the local cache.

    :param key: Get the value based on the key from the cache.
    :type key: string
    :returns: void
    """
    if key not in _CACHE:
        return ""
    if _CACHE_COUNTER[key] >= len(_CACHE[key][1:]):
        if _CACHE[key][0] == "empty":
            return ""
        elif _CACHE[key][0] == "repeat" and _CACHE[key][1:]:
            return _CACHE[key][-1]
        elif _CACHE[key][0] == "repeat":
            return ""
        else:
            _CACHE_COUNTER[key] = 1
    else:
        _CACHE_COUNTER[key] += 1
    if _CACHE[key]:
        return _CACHE[key][_CACHE_COUNTER[key]]
    else:
        return ""


def connect():
    """
    Connect to the online data source in order to get up-to-date information.

    :returns: void
    """
    global _CONNECTED
    _CONNECTED = True

def _load_from_string(data):
    '''Loads the cache from the string'''
    global _CACHE
    if PYTHON_3:
        data = json.loads(data.decode("utf-8"))
    else:
        data = json.loads(data)
    _CACHE = _recursively_convert_unicode_to_str(data)['data']

def disconnect(filename=None):
    """
    Connect to the local cache, so no internet connection is required.

    :returns: void
    """
    global _CONNECTED, _CACHE
    if filename is not None:
        try:
            with open(filename, 'r') as f:
                _load_from_string(f.read())
        except (OSError, IOError) as e:
            raise StockServiceException("The cache file '{}' was not found, and I cannot disconnect without one.".format(filename))
    for key in _CACHE.keys():
        _CACHE_COUNTER[key] = 0
    _CONNECTED = False

################################################################################
# Exceptions
################################################################################


class StockServiceException(Exception):
    pass

################################################################################
# Domain Objects
################################################################################


class Stock(object):

    """
    A stock contains the change, change percentage, exchange name,
    last trade price, last trade date and time, and ticker_name name for a stock
    """
    def __init__(self, change_number=None, change_percentage=None,
                 exchange_name='', last_trade_price=None,
                 last_trade_date_and_time=None, ticker_name=''):

        """
        Creates a new Stock

        :param change_number: The change in the stock since opening.
        :type change_number: float
        :param change_percentage: The percentage change in the stock since opening.
        :type change_percentage: float
        :param exchange_name: The exchange name that a stock is listed under.
        :type exchange_name: str
        :param last_trade_price: The last traded price for this stock.
        :type last_trade_price: float
        :param last_trade_date_and_time: The last traded date and time for this stock.
        :type last_trade_date_and_time: str
        :param ticker_name: The name of the stock.
        :type ticker_name: str
        :returns: Stock
        """

        self.change_number = _parse_float(change_number)            # c
        self.change_percentage = _parse_float(change_percentage)    # cp
        self.exchange_name = exchange_name                          # e
        self.last_trade_price = _parse_float(last_trade_price)      # l
        self.last_trade_date_and_time = last_trade_date_and_time    # lt
        self.ticker_name = ticker_name                              # s

    def __unicode__(self):
        string = """
        <Stock Change: {}, Change (Percentage): {}, Exchange Name: {},
        Last Trade Price: {}, Last Trade Date and Time: {}, Ticker: {}>
        """
        return string.format(self.change_number,
                             self.change_percentage,
                             self.exchange_name,
                             self.last_trade_price,
                             self.last_trade_date_and_time,
                             self.ticker_name)

    def __repr__(self):
        string = self.__unicode__()

        if not PYTHON_3:
            return string.encode('utf-8')

        return string

    def __str__(self):
        string = self.__unicode__()

        if not PYTHON_3:
            return string.encode('utf-8')

        return string

    def _to_dict(self):
        return {'change_number': self.change_number,
                'change_percentage': self.change_percentage,
                'exchange_name': self.exchange_name,
                'last_trade_price': self.last_trade_price,
                'last_trade_date_and_time': self.last_trade_date_and_time,
                'ticker_name': self.ticker_name}

    @staticmethod
    def _from_clean_json(json_data):
        """
        Creates a Stock from clean json data.

        :param json_data: The raw json data to parse
        :type json_data: dict
        :returns: Stock
        """
        if json_data is None:
            return Stock()
        try:
            chg_num = _parse_float(json_data['change_number'])
            chg_per = _parse_float(json_data['change_percentage'])
            ex_name = json_data['exchange_name']
            lst_trd_price = _parse_float(json_data['last_trade_price'])
            lst_trd_date_time = json_data['last_trade_date_and_time']
            tick = json_data['ticker_name']
            stock = Stock(chg_num, chg_per, ex_name, lst_trd_price,
                          lst_trd_date_time, tick)
            return stock
        except KeyError as e:
            raise StockServiceException("The stock information from the server was incomplete.")
    
    @staticmethod
    def _from_json(json_data):
        """
        Creates a Stock from json data.

        :param json_data: The raw json data to parse
        :type json_data: dict
        :returns: Stock
        """
        if json_data is None:
            return Stock()
        try:
            chg_num = _parse_float(json_data['c'])
            chg_per = _parse_float(json_data['cp'])
            ex_name = json_data['e']
            lst_trd_price = _parse_float(json_data['l'])
            lst_trd_date_time = json_data['lt']
            tick = json_data['t']
            stock = Stock(chg_num, chg_per, ex_name, lst_trd_price,
                          lst_trd_date_time, tick)
            return stock
        except KeyError as e:
            raise StockServiceException("The stock information from the server was incomplete.")


################################################################################
# Service Methods
################################################################################
def _fetch_past_stock_info(params, online):
    """
    Internal method to form and query the corgis server for historical stock
    data

    :param dict params: the parameters to pass to the server
    :returns: the JSON response object
    """
    baseurl = 'http://think.cs.vt.edu/corgis/data/stocks/'
    query = _urlencode(baseurl, params)

    try:
        result = _get(query) if (online or _CONNECTED) else _lookup(query)
    except HTTPError:
        raise StockServiceException("Make sure you entered a valid stock symbol! Otherwise, check your internet connection and then try again.")

    if not result:
        raise StockServiceException("There were no results")

    try:
        if (online or _CONNECTED) and _EDITABLE:
            _add_to_cache(query, result)
        json_res = json.loads(result)
    except ValueError:
        raise StockServiceException("Internal Error - the result from the server could not be understood. Please report this.")
        
    if 'success' in json_res:
        if not json_res['success']:
            if json_res['message']:
                raise StockServiceException("The server returned something incorrect, error message: " + json_res['message'])
            else:
                raise StockServiceException("The server returned something incorrect, result: " + json_res)
    else:
        raise StockServiceException("The result from the server was invalid:" + json_res)

    return json_res

def _fetch_stock_info(params, online):
    """
    Internal method to form and query the server

    :param dict params: the parameters to pass to the server
    :returns: the JSON response object
    """
    baseurl = 'https://www.google.com/finance/info'
    query = _urlencode(baseurl, params)

    try:
        result = _get(query) if (online or _CONNECTED) else _lookup(query)
    except HTTPError:
        raise StockServiceException("Make sure you entered a valid stock symbol! Otherwise, check your internet connection and then try again.")

    if not result:
        raise StockServiceException("There were no results")

    if online or _CONNECTED:
        result = result.replace("// ", "")  # Remove Strange Double Slashes
        result = result.replace("\n", "")  # Remove All New Lines

    try:
        if (online or _CONNECTED) and _EDITABLE:
            _add_to_cache(query, result)
        json_res = json.loads(result)
    except ValueError:
        raise StockServiceException("Internal Error - the result from the server could not be understood. Please report this.")

    return json_res

def batch_get_stocks(tickers, online=False):
    if not isinstance(tickers, str):
        raise StockServiceException("Please enter a string of stocks")
    params = {'q': tickers}
    json_res = _fetch_stock_info(params, online)
    stocks = list(map(Stock._from_json, json_res))
    if _USE_CLASSES:
        return stocks
    else:
        return [s._to_dict() for s in stocks]
        
FAKE_STOCK_DATA = {'FB':   [1.1, 1.0, 0.7, 0.12, -0.3, -0.34, -0.1, -0.45, -0.74],
                   'AAPL': [0.47, 0.53, 0.42, 0.41, 0.30, 0.10, -0.46, -0.84, -1.13],
                   'MSFT': [0.75, 0.80, 0.71, 0.67, 0.5, 0.15, 0.09, 0.03, 0.31],
                   'GOOG': [-0.27, -0.15, -0.11, 0.12, 0.3, 0.1, -0.3, -0.1, -0.09]}

def get_current_complete(ticker, online=False):
    """
    Retrieves current stock information.
    
    :param str ticker: the String of the stock that you want
    :returns: a dictionary of stock information
    """
    if not isinstance(ticker, str):
        raise StockServiceException("Please enter a string of a stock")
    ticker = ticker.upper()

    params = {'q': ticker}
    json_res = _fetch_stock_info(params, online)
    stock = Stock._from_json(json_res[0])
    if _USE_CLASSES:
        return stock
    else:
        return stock._to_dict()
        
def normalize_ticker(ticker):
    ticker = ticker.upper()
    if ticker in ('FB', 'FACEBOOK'): return 'FB'
    elif ticker in ('AAPL', 'APPLE'): return 'AAPL'
    elif ticker in ('MSFT', 'MICROSOFT'): return 'MSFT'
    elif ticker in ('GOOG', 'GOOGLE'): return 'GOOG'
    else: return ticker

def get_current(ticker, online=False):
    '''
    Retrieves past stock information
    
    :param str ticker: The string of the stock that you want.
    :returns: a list of stock information dictionaries
    '''
    if not isinstance(ticker, str):
        raise StockServiceException("Please enter a string of a stock")
    ticker = ticker.upper()
    if normalize_ticker(ticker) in FAKE_STOCK_DATA:
        return FAKE_STOCK_DATA[normalize_ticker(ticker)][0]

    params = {'q': ticker}
    json_res = _fetch_stock_info(params, online)
    stock = Stock._from_json(json_res[0])
    return stock.change_number
    
def get_past(ticker, online=False):
    '''
    Retrieves past stock information
    
    :param str ticker: The string of the stock that you want.
    :returns: a list of stock changes
    '''
    if not isinstance(ticker, str):
        raise StockServiceException("Please enter a string of a stock")
    ticker = ticker.upper()
    if normalize_ticker(ticker) in FAKE_STOCK_DATA:
        return FAKE_STOCK_DATA[normalize_ticker(ticker)]

    params = {'ticker': ticker}
    json_res = _fetch_past_stock_info(params, online)['result']
    stocks = list(map(Stock._from_clean_json, json_res))
    if _USE_CLASSES:
        return stocks
    else:
        return [s.change_number for s in stocks]
    
def get_past_complete(ticker, online=False):
    '''
    Retrieves complete past stock information
    
    :param str ticker: The string of the stock that you want.
    :returns: a list of stock changes
    '''
    if not isinstance(ticker, str):
        raise StockServiceException("Please enter a string of a stock")
    ticker = ticker.upper()

    params = {'ticker': ticker}
    json_res = _fetch_past_stock_info(params, online)['result']
    stocks = list(map(Stock._from_clean_json, json_res))
    if _USE_CLASSES:
        return stocks
    else:
        return [s._to_dict() for s in stocks]
    
_load_from_string(zlib.decompress(base64.b64decode(
	'''eJztm11v2jAUhv9K5NvRkDjOB0hVRdW1N+vaqb1aU6HUuBAVQpaYthPivy8mn04CJBT'''
	'''WafINKG9Oiv3kjXvOMSzByKEO6EtLMKHU73e7dOJ6LzIO5Vcqk9Gii+fB2A27LKwb0j'''
	'''l+Cbtn1MUvJDgdDG6/RZc+gID4xKGgI4Gl7UmSHQnhYkptdpIJkrSM39g5PHG8MRl6i'''
	'''9kTCViIDRRZ1W3QqcT4JMDEo86YbIgj7+lfc2ZJzPfB3cXgBxc1dUI6pIEzIsNoGmTo'''
	'''eKMhddMLbjCVjI4E+3rv9lr6enG/6Vo/cHFyTa8nmyYXFyMpjIPBsUEcsOo0o6A0g6A'''
	'''ciwHqK0obBgYUDAQDwUAwEAwEA8Fgbwbs7bET507hAmMShiyKBgtieyvwGGVWLD0Lo/'''
	'''zs7e1NHs/n4ymR8XzWfXY9x8Ok63rP87Nfp5fnpYTsYWkDdxR/JOwZlmlBhDSoq9Bi4'''
	'''wNRkiaxc5fn60OSHOaUwDSRTFPWjVgZPrvvNSpeBBU1TD46DqEsJ7QBzxJM00HUoo5O'''
	'''D0c0TEKgoqITVTlRjHvViOL6ivpzHYWTgC9RkqjGSmGYuejnip4ofFyi4nk6cTwZryU'''
	'''fT0N+5gjF0KbxJJliJEocWFHXiMpqafoml4kCks7sJBqckkiFcRRlv6DBVCvFpnpxgs'''
	'''FaG7mvibI+/D0dZYerxxYmvLq5udpiQ01ByDCs6NVClgk5G7JLdxlRj9hpesWJnJxbs'''
	'''SAf34tKyYtQVsyKF3Mx96Jm1HkxVXd6UTd1OXmgUzMW5l10Iy9nduTkEgKjr5p1fowW'''
	'''2xo7FlS/RqqPLE7w6aBevL67vN/mRd1CBuIsyK7YZUFkyEqv4sCimhswV/+6/zLCtTe'''
	'''oen/qb0/N3SnZL59i6j6kyz2zYj5OzbxXVCtLIdI2LYWw6j1u2cs1aNQvhZm+bSmMnk'''
	'''K1ZEEoGz3Ohu3aJjWW3Ldt8tlJkdYmKcpcsjkpip+9/zgxFAwEA8FAMBAMBAPB4GMMD'''
	'''tY0qdnH4tomUEV8iRD3braXCFkLiCsRimpeIuTq8UsE7XNKhHyKaYkQKVpaNOQlAqdm'''
	'''JUJRbd4tgVptiZDJfp22IXZ7iYDMUomgytZHSoRKG2/vfVWt2QqgmsdaAlqVCKxvuGN'''
	'''flTUq2y2CceevAQN0PAYt9pYZA/3TGBxtf73Vv4KsfywYCAaCgWAgGAgGrRk0LBDapW'''
	'''Y1m1v7JWeq3Gv4pTftaIlJqy+9sT0iqG2nH+/ftfEgTFr2DTAcMUdtiQEdnoJiNqRg/'''
	'''BNPYr5hKDAIDAKDwCAwCAwHwbArbVtFKdeMUCf55QIAqz8m8ejo'''
)))
connect() if _START_CONNECTED else disconnect()
