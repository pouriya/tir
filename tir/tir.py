from collections import namedtuple

import requests

import lxml.html

from .exceptions import TagNotFound
from .utils import (transform_date, transform_date_with_string_month,
                    transform_month, transform_number,
                    transform_numerical_date, transform_weekday)

Date = namedtuple('Date', ['year', 'season', 'month', 'month_name', 'day', 'weekday'])

Day = namedtuple('Day', ['is_disabled' # boolean
                        ,'is_today'    # boolean
                        ,'is_holiday'  # boolean
                        ,'solar'       # '01'-'31'
                        ,'gregorian'   # '01'-'31'
                        ,'qamari'])    # '01'-'31'

Time = namedtuple('Time', ['hour', 'minute', 'second'])

Quote = namedtuple('Quote', ['author', 'text'])


# each item in theme should be 2-sized tuple
# first element is start and second element is stop
# for example defining ('\033[1;31m', '\033[0m') as value of 'disabled'
#  in CalendarTheme, means that print disabled days in Red color.
CalendarTheme = namedtuple('CalendarTheme', ['disabled', 'holiday', 'today', 'normal', 'solar', 'other_days'])

DateTheme = namedtuple('Date', ['year', 'seasons', 'month', 'month_name', 'weekday', 'day'])

TimeTheme = namedtuple('TimeTheme', ['hour', 'minute', 'second'])

def find_season(month_number, type_):
    season_table = [
            ('Bahar',    'Spring'),
            ('Tabestan', 'Summer'),
            ("Pa'eez",  'Autumn'),
            ('Zemestan', 'Winter'),
            ]
    if type_ == 'solar':
        season_name_offset = 0
        if 0 < month_number < 4:
            season_number = '01'
        elif 3 < month_number < 7:
            season_number = '02'
        elif 6 < month_number < 10:
            season_number = '03'
        else: # 10, 11, 12
            season_number = '04'
    else: # assume gregorian
        season_name_offset = 1
        if 2 < month_number < 6:
            season_number = '01'
        elif 5 < month_number < 9:
            season_number = '02'
        elif 8 < month_number < 12:
            season_number = '03'
        else: # 12, 01, 02
            season_number = '04'
    season_name = season_table[int(season_number)-1][season_name_offset]
    return (season_name, season_number)

def search(element, tag, attr, val):
    """search funcion and its utilities which used for parsed HTML page """
    def _has_attr(sub_element):
        for attr2, val2 in sub_element.attrib.items():
            if type(attr) == tuple and type(val) == tuple:
                if attr2.find(attr[0]) != -1 and val2.find(val[0]) != -1:
                    return True
            elif type(attr) == tuple:
                if attr2.find(attr[0]) != -1 and val2 == val:
                    return True
            elif type(val) == tuple:
                if attr2 == attr and val2.find(val[0]) != -1:
                    return True
            else:
                if attr2 == attr and val2 == val:
                    return True
        return False

    def _search(element, tag, attr, val):
        for sub_element in element.getchildren():
            if sub_element.tag == tag:
                if attr == None:
                    return sub_element
                if _has_attr(sub_element):
                    return sub_element
            result = _search(sub_element, tag, attr, val)
            if result == None:
                continue
            return result
        return None

    element = _search(element, tag, attr, val)
    if element == None:
        raise TagNotFound(tag, attr, val)
    return element


class Request:
    """A class which makes request for fetching HTML page """
    def __init__(self,
            user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
            headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}):
        self.url='http://time.ir',
        for (key, _) in headers.items():
            if key.lower() == 'user-agent':
                break
        else:
            headers['user-agent'] = user_agent
        self.headers = headers

    def get(self):
        request = requests.get(self.url, headers=self.headers)
        body = request.text
        assert(len(body) > 10240) # It's normals size is about 80K, but wee need at least 10K to process
        return body


class HTMLParser:
    """An HTML parser which accepts some transformers, and after parsing HTML 
       page, runs each transformer with parsed data"""
    def __init__(self, text, transformers):
        self.html = lxml.html.fromstring(text)
        self.transformers = transformers

    def parse(self):
        transform_data = {}
        for name, transformer in self.transformers.items():
            transform_data[name] = transformer(self.html)
        return transform_data
