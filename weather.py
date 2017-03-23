from __future__ import print_function
'''
Hello student in computational thinking! You don't need to open this file.
'''


_USE_CLASSES = False
_START_CONNECTED = False
_NEVER_FAIL = True

__version__ = '7'

import sys, zlib, base64
try:
    import simplejson as json
except ImportError:
    import json

HEADER = {'User-Agent': 'CORGIS Weather library for educational purposes'}
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
            raise WeatherException("The cache file '{}' was not found, and I cannot disconnect without one.".format(filename))
    for key in _CACHE.keys():
        _CACHE_COUNTER[key] = 0
    _CONNECTED = False
        
################################################################################
# Domain Objects
################################################################################
        
class Location(object):
    """
    A detailed description of a location
    """
    def __init__(self, latitude, longitude, elevation, name):
        """
        Creates a new Location
        
        :param self: This object
        :type self: Location
        :param latitude: The latitude (up-down) of this location.
        :type latitude: float
        :param longitude: The longitude (left-right) of this location.
        :type longitude: float
        :param elevation: The height above sea-level (in feet).
        :type elevation: int
        :param name: The city and state that this location is in.
        :type name: string
        :returns: Location
        """
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.name = name
        
    def __unicode__(self):
        return "<Location: {}>".format(self.name)

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
        return {'latitude': self.latitude, 'longitude': self.longitude,  
                'elevation': self.elevation,
                'name': self.name}

    
    @staticmethod
    def _from_json(json_data):
        """
        Creates a Location from json data.
        
        :param json_data: The raw json data to parse
        :type json_data: dict
        :returns: Location
        """
        return Location(_parse_float(json_data.get('latitude', 0.0)),
                        _parse_float(json_data.get('longitude', 0.0)),
                        _parse_int(json_data.get('elevation', 0)),
                        json_data.get('areaDescription', ''))

class Weather(object):
    """
    A structured representation the current weather.
    """
    def __init__(self, temp, dewpoint, humidity, wind_speed, wind_direction, description, image_url, visibility, windchill, pressure):
        """
        Creates a new Weather
        
        :param self: This object
        :type self: Weather
        :param temp: The current temperature (in Fahrenheit).
        :type temp: int
        :param dewpoint: The current dewpoint temperature (in Fahrenheit).
        :type dewpoint: int
        :param humidity: The current relative humidity (as a percentage).
        :type humidity: int
        :param wind_speed: The current wind speed (in miles-per-hour).
        :type wind_speed: int
        :param wind_direction: The current wind direction (in degrees).
        :type wind_direction: int
        :param description: A human-readable description of the current weather.
        :type description: string
        :param image_url: A url pointing to a picture that describes the weather.
        :type image_url: string
        :param visibility: How far you can see (in miles).
        :type visibility: float
        :param windchill: The perceived temperature (in Fahrenheit).
        :type windchill: int
        :param pressure: The barometric pressure (in inches).
        :type pressure: float
        :returns: Weather
        """
        self.temp = temp
        self.dewpoint = dewpoint
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.description = description
        self.image_url = image_url
        self.visibility = visibility
        self.windchill = windchill
        self.pressure = pressure
        
    def __unicode__(self):
        return "<Weather: {}F and {}>".format(self.temperature, self.description)

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
        return {'temperature': self.temp,
                'dewpoint': self.dewpoint,
                'humidity': self.humidity,
                'wind_speed': self.wind_speed,
                'wind_direction': self.wind_direction,
                'description': self.description,
                'image_url': self.image_url,
                'visibility': self.visibility,
                'windchill': self.windchill,
                'pressure': self.pressure}
    
    @staticmethod
    def _from_json(json_data):
        """
        Creates a Weather from json data.
        
        :param json_data: The raw json data to parse
        :type json_data: dict
        :returns: Weather
        """
        return Weather(_parse_int(json_data.get('Temp', 0)),
                       _parse_int(json_data.get('Dewp', 0)),
                       _parse_int(json_data.get('Relh', 0)),
                       _parse_int(json_data.get('Winds', 0)),
                       _parse_int(json_data.get('Windd', 0)),
                       json_data.get('Weather', ''),
                       json_data.get('Weatherimage', ''),
                       _parse_float(json_data.get('Visibility', 0.0)),
                       _parse_int(json_data.get('WindChill', 0)),
                       _parse_float(json_data.get('SLP', 0.0)))

class Forecast(object):
    """
    A prediction for future weather.
    """
    def __init__(self, period_name, period_time, temperature_label, temperature, probability_of_precipitation, description, image_url, long_description):
        """
        Creates a new Forecast
        
        :param self: This object
        :type self: Forecast
        :param period_name: A human-readable name for this time period (e.g. Tonight or Saturday).
        :type period_name: string
        :param period_time: A string representing the time that this period starts. Encoded as YYYY-MM-DDTHH:MM:SS, where the T is not a number, but a always present character (e.g. 2013-07-30T18:00:00).
        :type period_time: string
        :param temperature_label: Either 'High' or 'Low', depending on whether or not the predicted temperature is a daily high or a daily low.
        :type temperature_label: string
        :param temperature: The predicted temperature for this period (in Fahrenheit).
        :type temperature: int
        :param probability_of_precipitation: The probability of precipitation for this period (as a percentage).
        :type probability_of_precipitation: int
        :param description: A human-readable description of the predicted weather for this period.
        :type description: string
        :param image_url: A url pointing to a picture that describes the predicted weather for this period.
        :type image_url: string
        :param long_description: A more-detailed, human-readable description of the predicted weather for this period.
        :type long_description: string
        :returns: Forecast
        """
        self.period_name = period_name
        self.period_time = period_time
        self.temperature_label = temperature_label
        self.temperature = temperature
        if probability_of_precipitation is None:
            self.probability_of_precipitation = 0
        else:
            self.probability_of_precipitation = probability_of_precipitation
        self.description = description
        self.image_url = image_url
        self.long_description = long_description
        
    def __unicode__(self):
        return "<Forecast: {}>".format(self.period_name)

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
        return {'period_name': self.period_name,
                'period_time': self.period_time,
                'temperature_label': self.temperature_label,
                'temperature': self.temperature,
                'probability_of_precipitation': self.probability_of_precipitation,
                'description': self.description,
                'image_url': self.image_url,
                'long_description': self.long_description}
    
    @staticmethod
    def _from_json(json_data):
        """
        Creates a Forecast from json data.
        
        :param json_data: The raw json data to parse
        :type json_data: dict
        :returns: Forecast
        """
        return list(map(Forecast, json_data['time']['startPeriodName'],
                    json_data['time']['startValidTime'],
                    json_data['time']['tempLabel'],
                    list(map(_parse_int, json_data['data']['temperature'])),
                    list(map(_parse_int, json_data['data']['pop'])),
                    json_data['data']['weather'],
                    json_data['data']['iconLink'],
                    json_data['data']['text']))

class Report(object):
    """
    A container for the weather, forecasts, and location information.
    """
    def __init__(self, weather, forecasts, location):
        """
        Creates a new Report
        
        :param self: This object
        :type self: Report
        :param weather: The current weather for this location.
        :type weather: Weather
        :param forecasts: The forecast for the next 7 days and 7 nights.
        :type forecasts: listof Forecast
        :param location: More detailed information on this location.
        :type location: Location
        :returns: Report
        """
        self.weather = weather
        self.forecasts = forecasts
        self.location = location
        
    def __unicode__(self):
        return "<Report: {}>".format(self.location)

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
        return {'weather': self.weather._to_dict(),
                'forecasts': list(map(Forecast._to_dict, self.forecasts)),
                'location': self.location._to_dict()}
    
    @staticmethod
    def _from_json(json_data):
        """
        Creates a Report from json data.
        
        :param json_data: The raw json data to parse
        :type json_data: dict
        :returns: Report
        """
        return Report(Weather._from_json(json_data['currentobservation']),
                    Forecast._from_json(json_data),
                    Location._from_json(json_data['location']))
                    
################################################################################
# Exceptions
################################################################################
class GeocodeException(Exception):
    pass
class WeatherException(Exception):
    pass

GEOCODE_ERRORS = {"REQUEST_DENIED": "The given address was denied.",
				  "ZERO_RESULTS": "The given address could not be found.",
				  "OVER_QUERY_LIMIT": "The service has been used too many times today.",
				  "INVALID_REQUEST": "The given address was invalid.",
				  "UNKNOWN_ERROR": "A temporary error occurred; please try again.",
				  "UNAVAILABLE": "The given address is not available offline."}
################################################################################
# Service call
################################################################################

def _get_report_request(latitude,longitude):
    """
    Used to build the request string used by :func:`get_report`.
    
    
    :param latitude: The latitude (up-down) of the location to get information about.
    :type latitude: float
    
    :param longitude: The longitude (left-right) of the location to get information about.
    :type longitude: float
    :returns: str
    """
    arguments = dict([("lat", latitude), ("FcstType", "json"), ("lon", longitude)])
    return _urlencode("http://forecast.weather.gov/MapClick.php", arguments)

def _get_report_string(latitude,longitude, online):
    """
    Like :func:`get_report` except returns the raw data instead.
    
    
    :param latitude: The latitude (up-down) of the location to get information about.
    :type latitude: float
    
    :param longitude: The longitude (left-right) of the location to get information about.
    :type longitude: float
    :returns: str
    """
    key = _get_report_request(latitude, longitude)
    result = _get(key) if (_CONNECTED or online) else _lookup(key)
    if (_CONNECTED or online) and _EDITABLE:
        _add_to_cache(key, result)
    return result

def get_report_by_latlng(latitude,longitude, online):
    """
    Gets a report on the current weather, forecast, and more detailed information about the location.
    
    
    :param latitude: The latitude (up-down) of the location to get information about.
    :type latitude: float
    
    :param longitude: The longitude (left-right) of the location to get information about.
    :type longitude: float
    :returns: Report
    """
    result = _get_report_string(latitude,longitude, online)
    if result:
        try:
            json_result = _from_json(result)
        except ValueError:
            raise WeatherException("This city was outside of the continental United States.")
        if _USE_CLASSES:
            return Report._from_json(json_result)
        else:
            return Report._from_json(json_result)._to_dict()
    else:
        if (_CONNECTED or online):
            raise WeatherException("No response from the server.")
        else:
            raise WeatherException("No data was in the cache for this location.")
    
def _geocode_request(address):
    """
    Used to build the request string used by :func:`geocode`.
    
    :param str address: A location (e.g., "Newark, DE") somewhere in the United States
    :returns: str
    """
    address = address.lower()
    arguments = dict([("address", address), ("sensor", "true")])
    return _urlencode("http://maps.googleapis.com/maps/api/geocode/json", arguments)
    
def simplify_address(address):
    return ",".join([p.strip() for p in address.lower().split(",")])
    
def _geocode(address, online):
    """
    Like :func:`geocode` except returns the raw data instead.
    
    :param str address: A location (e.g., "Newark, DE") somewhere in the United States
    :returns: str
    """
    address = simplify_address(address)
    # NYC is dumb and returns a weird first result...
    if (address in ("new york city,ny", "new york,ny",
                            "nyc", "nyc,ny")):
        return json.dumps({'status': 'OK', 'results': [{ 
                                'geometry': {'location': {
                                    'lat': 43.00034918200049,
                                    'lng': -75.49989885099967}}}]})
    key = _geocode_request(address)
    result = _get(key) if (_CONNECTED or online) else _lookup(key)
    if (_CONNECTED or online) and _EDITABLE:
        _add_to_cache(key, result)
    return result

def _get_report(address, online):
    """
    Gets a report on the current weather, forecast, and more detailed information about the location.
    
    :param str address: A location (e.g., "Newark, DE") somewhere in the United States
    :returns: report
    """
    response = _geocode(address, online)
    if response == "":
        if _CONNECTED or online:
            raise GeocodeException("Nothing was returned from the server.")
        else:
            raise GeocodeException("The given city was not in the cache.")
    try:
        geocode_data = _from_json(response)
    except ValueError:
        raise GeocodeException("The response from the Server was invalid. Perhaps the internet is down?")
    status = geocode_data.get('status', 'INVALID_RETURN')
    if status == 'OK':
        try:
            results = geocode_data['results']
            if results:
                location = results[0]['geometry']['location']
                latitude = location['lat']
                longitude = location['lng']
            else:
                raise GeocodeException("The address could not be found; check that it's valid on Google Maps.")
        except KeyError:
            raise GeocodeException("The response from the Geocode server was invalid. Perhaps this wasn't a valid address?")
        return get_report_by_latlng(latitude, longitude, online)
    else:
        raise GeocodeException(GEOCODE_ERRORS.get(status, "Unknown error occurred: "+status))
        
def normalize_city(city):
    city = city.lower()
    if city in ("blacksburg, va", "blacksburg,va", "blacksburg va", "blacksburg", "va", "virginia"):
        return "BLACKSBURG"
    if city in ("seattle, wa", "seattle,wa", "seattle wa", "seattle", "wa", "seattle"):
        return "SEATTLE"
    if city in ("miami, fl", "miami,fl", "miami fl", "miami", "fl", "miami"):
        return "MIAMI"
    if city in ("san jose, ca", "san jose,ca", "san jose ca", "san jose", "ca", "california"):
        return "SANJOSE"
    if city in ("new york, ny", "new york,ny", "new york ny", "ny", "new york"):
        return "NEWYORK"
    return city

FAKE_FORECASTS = {
    'BLACKSBURG':[{'temperature': 28, 'humidity':  20, 'wind':  7}, {'temperature': 11, 'humidity': 50, 'wind': 10},
                  {'temperature': 31, 'humidity': 100, 'wind':  5}, {'temperature': 12, 'humidity': 90, 'wind': 15},
                  {'temperature': 34, 'humidity':  30, 'wind': 19}, {'temperature': 16, 'humidity':  0, 'wind': 28},
                  {'temperature': 37, 'humidity':   0, 'wind': 12}, {'temperature': 18, 'humidity':  0, 'wind': 14},
                  {'temperature': 36, 'humidity':   0, 'wind':  4}, {'temperature': 18, 'humidity': 60, 'wind':  0}],
    'SEATTLE':   [{'temperature': 56, 'humidity': 10, 'wind':  7}, {'temperature': 40, 'humidity': 0, 'wind': 9},
                  {'temperature': 54, 'humidity': 0, 'wind':  9}, {'temperature': 38, 'humidity': 20, 'wind': 3},
                  {'temperature': 57, 'humidity':  10, 'wind': 10}, {'temperature': 39, 'humidity':  30, 'wind': 6},
                  {'temperature': 60, 'humidity':  20, 'wind':  7}, {'temperature': 42, 'humidity':  0, 'wind': 7},
                  {'temperature': 65, 'humidity':  0, 'wind':  2}, {'temperature': 41, 'humidity': 0, 'wind': 2}],
    'MIAMI':     [{'temperature': 69, 'humidity': 60, 'wind': 12}, {'temperature': 59, 'humidity': 60, 'wind': 14},
                  {'temperature': 51, 'humidity': 60, 'wind': 15}, {'temperature': 68, 'humidity': 60, 'wind': 17},
                  {'temperature': 60, 'humidity':  40, 'wind': 11}, {'temperature': 68, 'humidity': 40, 'wind':  9},
                  {'temperature': 62, 'humidity':  30, 'wind':  8}, {'temperature': 68, 'humidity':  30, 'wind': 10},
                  {'temperature': 61, 'humidity':  30, 'wind':  5}, {'temperature': 68, 'humidity':  30, 'wind':  3}],
    'SANJOSE':   [{'temperature': 52, 'humidity': 0, 'wind': 10}, {'temperature': 31, 'humidity': 0, 'wind': 11},
                  {'temperature': 53, 'humidity': 0, 'wind': 13}, {'temperature': 32, 'humidity': 0, 'wind':  6},
                  {'temperature': 52, 'humidity': 0, 'wind':  7}, {'temperature': 32, 'humidity': 0, 'wind':  8},
                  {'temperature': 49, 'humidity': 0, 'wind':  3}, {'temperature': 32, 'humidity': 0, 'wind':  4},
                  {'temperature': 49, 'humidity': 0, 'wind':  2}, {'temperature': 32, 'humidity': 0, 'wind':  5}],
    'NEWYORK':   [{'temperature': 44, 'humidity':   70, 'wind':  5}, {'temperature': 37, 'humidity':  40, 'wind': 10},
                  {'temperature': 34, 'humidity':   0, 'wind': 27}, {'temperature': 21, 'humidity':  0, 'wind': 17},
                  {'temperature': 35, 'humidity':   0, 'wind': 15}, {'temperature': 21, 'humidity': 0, 'wind': 4},
                  {'temperature': 40, 'humidity':  30, 'wind': 17}, {'temperature': 34, 'humidity': 30, 'wind': 9},
                  {'temperature': 43, 'humidity': 30, 'wind': 8}, {'temperature': 38, 'humidity': 30, 'wind': 4}]
    }
def get_temperature(address, online=False):
    """
    Gets the current temperature

    :param str address: A location (e.g., "Newark, DE") somewhere in the
    United States
    :return: an int temperature
    """
    if not online and (not _CONNECTED and normalize_city(address) in FAKE_FORECASTS):
        return FAKE_FORECASTS[normalize_city(address)][0]['temperature']
    address = simplify_address(address)
    report = _get_report(address, online)
    if _USE_CLASSES:
        return report.weather.temp
    else:
        return report['weather']['temperature']

def get_forecasts(address, online=False):
    """
    Gets the high temperatures for the time period

    :param str address: A location (e.g., "Newark, DE") somewhere in the
    United States
    :return list: a list of ints
    """
    if not online and (not _CONNECTED and normalize_city(address) in FAKE_FORECASTS):
        return [f['temperature'] for f in FAKE_FORECASTS[normalize_city(address)]]
    address = simplify_address(address)
    report = _get_report(address, online)
    if _USE_CLASSES:
        templist = [f.temperature for f in report.forecasts]
    else:
        templist = [f['temperature'] for f in report['forecasts']]
    return templist
    
def get_report(address, online=False):
    """
    Gets either complete information about a location or partial information.

    :param str address: A location (e.g., "Newark, DE") somewhere in the
    United States
    :return list: a dictionary
    """
    if not online and (not _CONNECTED and normalize_city(address) in FAKE_FORECASTS):
        return FAKE_FORECASTS[normalize_city(address)][0]
    address = simplify_address(address)
    report = _get_report(address, online)
    if _USE_CLASSES:
        templist = report.forecasts[0]
    else:
        templist = report['forecasts'][0]
    return templist
    
def get_forecasted_reports(address, online=False):
    """
    Gets either complete information about a location or partial information.

    :param str address: A location (e.g., "Newark, DE") somewhere in the
    United States
    :return list: a dictionary
    """
    if not online and (not _CONNECTED and normalize_city(address) in FAKE_FORECASTS):
        return FAKE_FORECASTS[normalize_city(address)]
    address = simplify_address(address)
    report = _get_report(address, online)
    if _USE_CLASSES:
        templist = report.forecasts
    else:
        templist = report['forecasts']
    return templist
    
def get_highs_lows(address, online=False):
    """
    Gets the high temperatures for the time period

    :param str address: A location (e.g., "Newark, DE") somewhere in the
    United States
    :return list: a list of ints
    """
    if not online and (not _CONNECTED and normalize_city(address) in FAKE_FORECASTS):
        return {'highs': [f['temperature'] for f in FAKE_FORECASTS[normalize_city(address)]][::2],
                'lows': [f['temperature'] for f in FAKE_FORECASTS[normalize_city(address)]][1::2]}
    address = simplify_address(address)
    report = _get_report(address, online)
    if _USE_CLASSES:
        templist = [f.temperature for f in report.forecasts]
    else:
        templist = [f['temperature'] for f in report['forecasts']]
    return {'highs': templist[::2], 'lows': templist[1::2]}

def get_all_forecasted_temperatures(online=False):
    """
    Gets the high temperatures for the time period

    :param str address: A location (e.g., "Newark, DE") somewhere in the
    United States
    :return list: a list of ints
    """
    if not online and not _CONNECTED:
        return [
            {"city": "Blacksburg, VA", "forecasts": get_forecasts("blacksburg")},
            {"city": "Seattle, WA", "forecasts": get_forecasts("seattle")},
            {"city": "Miami, FL", "forecasts": get_forecasts("miami")},
            {"city": "San Jose, CA", "forecasts": get_forecasts("san jose")},
            {"city": "New York, NY", "forecasts": get_forecasts("new york")},
        ]
    else:
        raise WeatherException("This function is not supported in online mode.")

_load_from_string(zlib.decompress(base64.b64decode(
	'''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'''
	'''RAy6EqKIQrC0KZMyCczbtqIX17CgohSVch4jTaUZJMaMmJh9S3AR89Be+iS7xpRjHvV'''
	'''aCtpXd5GXlsY1nr2fOeaApnvf0qKUM8blg0+S6vgjIU1q3NRWRpCve15C1ld+helHyT'''
	'''AzA8A5SifesnhqSbqlJnxAEloQARlGRZ1rcjoQgViql1J9GlVCAsMLepmNAxac9Swwi'''
	'''B8tPImUw50lSV25UomW3FkLfnS0SJQoaa+BLxEqXgNSi8iZLxPgzk5HruzSbzEFzPQt'''
	'''d/4BUfXLV27EN0Y0+5sxa2lN2hcvWj63kRHpJg/jDpp15x1xS5d9bl4WlqV4qiy7yxZ'''
	'''S1ldwj/0E8yybmD6dl3zh1TkvEpWkGdAV0mklRVM3SkbfECUEKNaSkyTyoWVTUUuQWK'''
	'''2piulYyR3O64TSnSNUXl7Xe/+XcwT0hWsKLCeVc5nX1o6ubWdC06zIauIJ3zrnK6BEx'''
	'''yjcghaFr0H8mGgDnH2+g8/f6vfvp48tHHJU5+H4CTSRzPTl+8wJuFM8KzJS0cG89bKD'''
	'''0En19c2rOh544epdlk9nc8MC9Vheq4qgVN9D3e/F4+NzRJtSzTMk0Nfv9mFMU3mLCX/'''
	'''44C/wSTdhI6M9we3mpP8HB/xCMbzJyQrjfbu6Qb2inxAQnG8xFb/ANWLAqjd3SrxK9v'''
	'''f7gG0DLV7OUICx9S+tyOWQlyyf1zKD+X9Rskn8roVDOfy+qpLNdWuQjofo/r6eBqFAO'''
	'''EyytgNgWvz2+yCrOMpiHWR4nHMy7/CmtdE3tK04Mk9w8kjY/dmJZIRnOxWEhOOJH8wL'''
	'''bpSN49TF9k5ad4rN/6bHumTBcq5qOfFc93hlM2iDFdpW48T8Yv8XdI3mCRlL8i86PBw'''
	'''msHC+28V9O0Cu8W9wFj84fLwtPYnTp/BD5r7/Wfv/6pFV4SPeDciUahO8savXWwloTV'''
	'''o9B3wsIw4dKhPbbZSD7GX78UXmTtv/v1N3yEKrwZJVoWfTeU9WLn927oNNfEIivp7Kc'''
	'''Pl6/pkk8GlHBUHsyv+Pv5yWHdPD6fQTR57pMlVWgOf0Jh/N4J3WCcrMx/Ja/wy6vPTu'''
	'''gTT4+8Av7nzdyJxskNIkvPwLtK6Vtn7FfLZ09ratzgs0C1g+RhTfk3RCv8WvOopuw13'''
	'''jDC5dLpw7ryWAlYLk0f1ZQdBt58ejePwDmpQZ/Rd7+XB/sXfAQY37jLY5197MaNjD92'''
	'''8r/yx14ppfOUgmZ3KZOrLZOrLYurLYunLSjztIVL8bQFudqCXG0hrrYQV1tKpa3qsom'''
	'''d6ezCvnM8umJOLoIFaQsf2x4m9B87ePA7oSXdaMY2CaHNNxpCHxF/85Ct6RMN0ao6lW'''
	'''0nbKM+0el2fqKyXyw/Z7LHn2jsL8Vkv1g9xWK/2EOVVdBxdTwy2cdFzhEz1qtBhzj9C'''
	'''7IRP9HZX4j85c89j/2BWy8/qLxif9FJSOUIE2Llz/Z6EiycMAIX7qPjLW0Una94i7+N'''
	'''AiwZybmxpt4lPkd5XwHelvyvdS+GXjAfl98MJzZx+Khr7T3eoeorJW/69NNYpYWA5Vf'''
	'''pm/xzcEeBf+H6j+WJaFP43Kn94EQvFvH9iynWaebTF340CW1Dlmb+Q6n3fq1spBFKCl'''
	'''6tG6BFX7eRifsJk7MII7Q2OaN43XG5e/Q3MCbK+vOzNivrc7KBwdgAERsZz2Ij1Y97Y'''
	'''v9hh+Pk0254+3PoNRWInS9x/Qbt0W1VAsk+NQALN54AG3jBAtghAXuAhiRAXc3I+R6/'''
	'''x48gBHEAoAqmswmpyzan4B7MMK/uzI3poQO4ETDk7yRALnsrv7GnRNOPwJ0TLxwH/wY'''
	'''xPnjhjnHj/5nj/REfJnBzNm7DH03ALIgi985zJFArGxgTAzC1XR9vrHcOGXOAZlNMW7'''
	'''LZRmSzzbibYOkNfMcOyTWVjDnGmEX5gofBV8aQfU/qQZvwc1GYGFiZGJ3Qb3aTjzfWv'''
	'''c2LSflIxOOovOwKE6NI4NZJ+WLzYhDGkrIP8wjTaUesCv4bcbCtb5PrTB2JEvbTdWgX'''
	'''1uGo8TNTYZFhkzKsdLOEMEt1ekfTgtf02uItdCnlCmdglFGTcNr9mWl4NluYUJaZ6Bw'''
	'''txayt0Ni/2pNrxerXvskzSN1jrfcbpj7dFD4tyNFLIkJYX3/lCM08DPG3EdxFTvh5Ga'''
	'''giWui4AMIUKPVTfO8DsUf8ELr3924UgTM3vHcdb1wqS1ArWlaT1dKLJRxMQkr5dQUMU'''
	'''2GpQAYhNkOBtNwNPrmxcuXj6bmzYM/VMl0fHG/CCNbLcI5LbSX4BVQrL9hAQaXcxQ/z'''
	'''iGGL5ce32SGr7SySlKLKBS1aq6T94uLdy2UGV0KBLC2dws88gpmlMCiUIZLM8v5+8Z4'''
	'''hsZZklUe4DB8uDSvBpVP4rjIcw4nrMZyWnGyTZUeP1+SPk9//GgAK8pFT9skpODn56/'''
	'''8D9RnUfA=='''
)))

if _START_CONNECTED:
    connect()
else:
    disconnect()
