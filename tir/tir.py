from collections import namedtuple

import requests

import lxml.html

from .exceptions import TagNotFound
from .utils import transform_number

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

# parser functions:

def transform_date(data):
    # for example it may be 'چهارشنبه - ۹ آبان ۱۳۹۷'
    data = data.split('-')
    weekday = data[0].strip()
    if not weekday.isalpha(): # it's farsi
        weekday = transform_weekday(weekday)
    date = transform_date_with_string_month(data[1].strip())
    return (weekday, date)

def transform_numeral_date(data):
    # for example '1397/12/6' or 2018-2-25 which is my birthday :)
    if data.find('/') != -1:
        _type = 'solar'
    else: # assume gregorian
        _type = 'gregorian'
    data = data.strip().replace('/', '-').split('-')
    (year, month, day) = (transform_number(data[0])
                         ,transform_number(data[1])
                         ,transform_number(data[2]))
    season = find_season(int(month), _type)
    return (year, season, month, day)

def transform_date_with_string_month(date):
    date = date.split()
    if date[2].isalpha():
        (year, day, month) = (date[0], date[1], date[2])
    else: # It's farsi
        (day, month, year) = (transform_number(date[0])
                             ,transform_month(date[1])
                             ,transform_number(date[2]))
    return (year, month, day)

def transform_weekday(weekday):
    if len(weekday) < 4: # shorter weekdays are شنبه or جمعه
        raise ValueError('unknown weekday {!r}'.format(weekday))
    farsi_weekdays_table = [('Shanbeh',   1588)  # ش
                           ,('1-Shanbeh', 1740)  # ی
                           ,('2-Shanbeh', 1583)  # د
                           ,('3-Shanbeh', 1587)  # س
                           ,('4-Shanbeh', 1670)  # چ
                           ,('5-Shanbeh', 1662)  # پ
                           ,('Jom\'eh',   1580)] # ج
    weekday_char1_unicode_number = ord(weekday[0])
    for farsi_weekday, char1_unicode_number in farsi_weekdays_table:
        if weekday_char1_unicode_number == char1_unicode_number:
            return farsi_weekday
    raise ValueError('unknown weekday {!r}'.format(weekday))


def find_season(month_number, _type):
    season_table = [('Bahar',    'Spring')
                   ,('Tabestan', 'Summer')
                   ,('Pa\'eez',  'Autumn')
                   ,('Zemestan', 'Winter')]
    if _type == 'solar':
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

def transform_month(month):
    if len(month) < 3: # Solar months shoudl contain at least 3 characterss
        raise ValueError('unknown solar-hijri month {!r}'.format(month))
    farsi_month_table = [('Farvardin',   (1601, None))  # ف
                        ,('Ordibehesht', (1575, 1585))  # ار
                        ,('Khordad',     (1582, None))  # خ
                        ,('Tir',         (1578, None))  # ت
                        ,('Mordad',      (1605, 1585))  # مر
                        ,('Shahrivar',   (1588, None))  # ش
                        ,('Mehr',        (1605, 1607))  # مه
                        ,('Aban',        (1575, 1576))  # اب
                        ,('Azar',        (1575, 1584))  # اذ
                        ,('Dey',         (1583, None))  # د
                        ,('Bahman',      (1576, None))  # ب
                        ,('Esfand',      (1575, 1587))] # اس
    (char1_number, char2_number) = (ord(month[0]), ord(month[1]))
    if char1_number == 1570:
        char1_number = 1575 # transform آ to ا (A without hat :D)
    for name, char_numbers in farsi_month_table:
        if char_numbers[0] == char1_number:
            if (not char_numbers[1] or char_numbers[1] == char2_number):
                return name
    raise ValueError('unknown solar month {!r}'.format(month))

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
