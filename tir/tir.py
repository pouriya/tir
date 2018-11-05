import requests
import lxml.html
from collections import namedtuple
import subprocess


# named tuples:
# used for parsed data and themes

Date = namedtuple('Date', ['year'        # e.g. '2018'
                          ,'season'      # '01'-'03' which means 3rd season
                          ,'season_name' # e.g. 'Bahar' or 'Spring'
                          ,'month'       # '01'-'12'
                          ,'month_name'  # e.g. 'Shahrivar' or 'June'
                          ,'day'         # '01'-'31'
                          ,'weekday'])   # e.g. 'Shanbeh' or 'Saturday'

Day = namedtuple('Day', ['is_disabled' # boolean
                        ,'is_today'    # boolean
                        ,'is_holiday'  # boolean
                        ,'solar'       # '01'-'31'
                        ,'gregorian'   # '01'-'31'
                        ,'qamari'])    # '01'-'31'

Time = namedtuple('Time', ['hour'     # '00'-'23'
                          ,'minute'   # '00'-'59'
                          ,'second']) # '00'-'59'

Quote = namedtuple('Quote', ['author', 'text']) # string


# each item in theme should be 2-sized tuple
# first element is start and second element is stop
# for example defining ('\033[1;31m', '\033[0m') as value of 'disabled'
#  in CalendarTheme, means that print disabled days in Red color.
CalendarTheme = namedtuple('CalendarTheme', ['disabled'
                                            ,'holiday'
                                            ,'today'
                                            ,'normal'
                                            ,'solar'
                                            ,'other_days'])

DateTheme = namedtuple('Date', ['year'
                               ,'seasons'
                               ,'month'
                               ,'month_name'
                               ,'weekday'
                               ,'day'])

TimeTheme = namedtuple('TimeTheme', ['hour'
                                    ,'minute'
                                    ,'second'])

# parser functions:

def transform_date(data):
    # for example it may be 'چهارشنبه - ۹ آبان ۱۳۹۷'
    data = data.split('-')
    weekday = data[0].strip()
    if not is_a_to_z(weekday): # it's farsi
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
    if is_a_to_z(date[2]):
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


def transform_number(number):
    number2 = ''
    for char in number:
        unicode_number = ord(char)
        if 1775 < unicode_number < 1786: # ۰-۹ farsi
            number2 += chr(unicode_number - 1728) # transform farsi ۰-۹ to 0-9
            continue
        if 1631 < unicode_number < 1642: # ۰-۹ arabic
            number2 += chr(unicode_number - 1584) # transform arabic ۰-۹ to 0-9
            continue
        if 47 < ord(char) < 58: # 0-9
            number2 += char
            continue
        raise ValueError('unknown farsi number {!r}'.format(number))
    if len(number2) == 1:
        number2 = '0' + number2
    return number2


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


def is_a_to_z(data):
    for char in data:
        number = ord(char)
        if 96 < number < 123: # a-z
            continue
        if 64 < number < 91:  # A-Z
            continue
        return False
    return True

# search funcion and its utilities which used for parsed HTML page:

def search(element, tag, attr, val):
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
        raise _TagNotFound(tag, attr, val)
    return element

class _TagNotFound(Exception):

    def __init__(self, tag, attr=None, value=None):
        text = 'could not found HTML tag {!r} '.format(tag)
        if attr:
            text += 'with attribute '
            if type(attr) == tuple:
                text += 'which should contain {!r} '.format(attr[0])
            else:
                text += '{!r} '.format(attr)
            text += 'and value '
            if type(value) == tuple:
                text += 'which should contain {!r}'.format(value[0])
            else:
                text += '{!r}'.format(value)
        Exception.__init__(self, text)

# A class which makes request for fetching HTML page:

class Request:

    def __init__(self
                ,url='http://time.ir'
                ,user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'
                ,headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}):
        self.url = url
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

# An HTML parser which accepts some transformers, and after parsing HTML
#  page, runs each transformer with parsed data


class HTMLParser:
    
    def __init__(self, text, transformers):
        self.html = lxml.html.fromstring(text)
        self.transformers = transformers

    def parse(self):
        transform_data = {}
        for name, transformer in self.transformers.items():
            transform_data[name] = transformer(self.html)
        return transform_data

# Transformer functions and their utilities:

def find_dates(html):
    container_top = search(html.body, 'div', 'class', ('container top',))
    date = search(container_top, 'div', 'class', ('todayDate',))
    rows = search(date, 'div', 'class', 'row')
    solar = find_date(rows, 'shamsi')
    gregorian = find_date(rows, 'gregorian')
    return {'solar': solar, 'gregorian': gregorian}


def find_date(rows, _type):
    row = search(rows, 'div', 'class', ('today-' + _type,))
    date = search(row, 'span', 'class', 'show date').text
    date_numeral = search(row, 'span', 'class', 'show numeral').text
    
    (weekday, (year, month_name, day)) = transform_date(date)
    (year, season, month, day) = transform_numeral_date(date_numeral)
    (season_name, season_number) = season
    return Date(year        = year
               ,season      = season_number
               ,season_name = season_name
               ,month       = month
               ,month_name  = month_name
               ,day         = day
               ,weekday     = weekday)


def find_calendar(html):
    container_top = search(html.body, 'div', 'class', ('container top',))
    calendar_wrapper = search(container_top, 'div', 'class', ('calendarWrapper',))
    calendar_container = search(calendar_wrapper, 'div', 'id', ('CalendarContainer',))
    event_calendar = search(calendar_container, 'div', 'class', 'eventCalendar')
    main_calendar = search(event_calendar, 'div', 'class', 'mainCalendar')
    day_list = search(main_calendar, 'div', 'class', 'dayList')
    day_list = [parse_day(day) for day in day_list.getchildren() if day.tag != 'br']
    assert(len(day_list) == 35)
    return day_list


def parse_day(day):
    if day.tag == 'br':
        return
    is_disabled = False
    is_today = False
    for attr, value in day.attrib.items():
        if attr == 'class':
            if value.find('disabled') != -1:
                is_disabled = True
            elif value.find('today') != -1:
                is_today = True
    info = day.getchildren()[0]
    is_holiday = False
    for attr, value in info.attrib.items():
        if attr == 'class':
            if value.find('holiday') != -1:
                is_holiday = True
    day_number_jalali = transform_number(search(info, 'div', 'class', ('jalali',)).text)
    day_number_gregorian = transform_number(search(info, 'div', 'class', ('miladi',)).text)
    day_number_qamari = transform_number(search(info, 'div', 'class', ('qamari',)).text)
    return Day(is_disabled
              ,is_today
              ,is_holiday
              ,day_number_jalali
              ,day_number_gregorian
              ,day_number_qamari)


def find_quote(html):
    container_top = search(html.body, 'div', 'class', ('container top',))
    random_quote = search(container_top, 'div', 'class', 'randomQuote')
    author = search(random_quote, 'a', 'class', ('quoteAuthor',)).text
    quote = search(random_quote, 'span', 'class', ('quoteText',)).text
    return Quote(author, quote)

# classes for printing transformer's data on screen:

class DrawCalendar:

    def __init__(self, days, theme=None):
        self.days = days
        self.theme = theme


    def _print(self, text, _type='n'):
        if self.theme and _type:
            if _type == 'h':
                (start, stop) = self.theme.holiday
            elif _type == 't':
                (start, stop) = self.theme.today
            elif _type == 'd':
                (start, stop) = self.theme.disabled
            elif _type == 's':
                (start, stop) = self.theme.solar
            elif _type == 'o':
                (start, stop) = self.theme.other_days
            elif _type == 'q':
                (start, stop) = self.theme.qamari
            else: # _type == 'n'
                (start, stop) = self.theme.normal
            text = start + text + stop
        print(text, end='')


    def draw(self):
        self._draw_header()
        offset = 0
        week = []
        while offset < 35:
            week.append((offset, self.days[offset]))
            if len(week) == 7:
                self._draw_week(week)
                print()
                week = []
            offset += 1


    def _draw_header(self):
        self._print(' ________  ________  ________  ________  ________  ________ ', 'n')
        self._print(' ________\n', 'h')
        self._print('| Shanbe ||  Yek   ||   Do   ||   Se   || Chahar ||  Panj  |', 'n')
        self._print('| Jom\'eh |\n', 'h')


    def _draw_week(self, week):
        self._draw_week_top(week)
        print()
        self._draw_week_empty(week)
        print()
        self._draw_week_day_number(week)
        print()
        self._draw_week_day_numbers(week)
        print()
        self._draw_week_buttom(week)


    def _draw_week_top(self, week):
        for offset, day in week:
            if day.is_today:
                _type = 't'
            elif day.is_disabled:
                _type = 'd'
            elif day.is_holiday:
                _type = 'h'
            else:
                _type = 'n'
            self._print(' ' + ('_' * 8) + ' ', _type)


    def _draw_week_empty(self, week):
        for offset, day in week:
            if day.is_today:
                _type = 't'
            elif day.is_disabled:
                _type = 'd'
            elif day.is_holiday:
                _type = 'h'
            else:
                _type = 'n'
            self._print('|' + (' ' * 8) + '|', _type)


    def _draw_week_day_number(self, week):
        for offset, day in week:
            if day.is_today and day.is_holiday:
                (type1, type2) = ('t', 'h')
            elif day.is_today:
                (type1, type2) = ('t', 's')
            elif day.is_disabled and day.is_holiday:
                (type1, type2) = ('d', 'h')
            elif day.is_disabled:
                (type1, type2) = ('d', 'd')
            elif day.is_holiday:
                (type1, type2) = ('h', 'h')
            else:
                (type1, type2) = ('n', 'n')
            self._print('|   ', type1)
            self._print(day.solar, type2)
            self._print('   |', type1)


    def _draw_week_day_numbers(self, week):
        for offset, day in week:
            if day.is_today and day.is_holiday:
                (type1, type2) = ('o', 'h')
            elif day.is_today:
                (type1, type2) = ('o', 't')
            elif day.is_disabled:
                (type1, type2) = ('d', 'd')
            elif day.is_holiday:
                (type1, type2) = ('o', 'h')
            else:
                (type1, type2) = ('o', 'n')
            self._print('| ', type2)
            self._print(day.qamari, type1)
            self._print('  ')
            self._print(day.gregorian, type1)
            self._print(' |', type2)


    def _draw_week_buttom(self, week):
        for offset, day in week:
            if day.is_today:
                _type = 't'
            elif day.is_disabled:
                _type = 'd'
            elif day.is_holiday:
                _type = 'h'
            else:
                _type = 'n'
            self._print('|' + ('_' * 8) + '|', _type)


class PrintTime:

    def __init__(self, time, theme=None):
        self.time = time
        self.theme = theme


    def _print(self, unit, _type=None):
        if self.theme and _type:
            if _type == 'h':
                (start, stop) = self.theme.hour
            elif _type == 'm':
                (start, stop) = self.theme.minute
            else: # _type == 's'
                (start, stop) = self.theme.second
            unit = start + unit + stop
        print(unit, end='')


    def print(self):
        self._print(self.time.hour, 'h')
        print(':', end='')
        self._print(self.time.minute, 'm')
        if self.time.second:
            print(':', end='')
            self._print(self.time.second, 's')


class PrintDate:

    def __init__(self, date, theme=None):
        self.date = date
        self.theme = theme

    def _print(self, item, _type=None):
        if self.theme and _type:
            if _type == 'y':
                (start, stop) = self.theme.year
            elif _type == 'm':
                (start, stop) = self.theme.month
            elif _type == 'd':
                (start, stop) = self.theme.day
            elif _type == 'w':
                (start, stop) = self.theme.weekday
            elif type(_type) == int: # season number
                (start, stop) = self.theme.seasons[_type-1]
            else: # _type == 'M':
                (start, stop) = self.theme.month_name
            item = start + item + stop
        print(item, end='')


    def print(self):
        self._print('{:^10}'.format(self.date.weekday), 'w')
        self._print(' ')
        self._print(self.date.day, 'd')
        spaces = 10 - len(self.date.month_name)
        if spaces % 2 == 0:
            (left, right) = (spaces // 2, spaces // 2)
        else:
            (left, right) = (spaces // 2 + 1, spaces // 2)
        self._print(' ' * left)
        self._print(self.date.month_name, 'M')
        self._print('(')
        self._print(self.date.month, 'm')
        self._print(')' + (' ' * right))
        self._print(self.date.year, 'y')
        self._print(' ')
        self._print('{:^10}'.format(self.date.season_name), int(self.date.season))


class Notify:

    def __init__(self, command='notify-send', arguments=[]):
        self.command = command
        self.arguments = arguments


    def _detect_time(self, text):
        if text == None:
            return None
        time = 0
        sentences = text.split('.')
        for sentence in sentences:
            words = sentence.split(' ')
            for word in words:
                for char in word:
                    time += 50
                _len = len(word)
                if 3 < _len < 8:
                    time += 300
                elif _len > 7:
                    time += 500
                else: # _len < 4
                    time += 200
            time += 50
        return time

    
    def notify(self):
        for argument in self.arguments:
            if argument == None:
                return
        subprocess.call([self.command] + self.arguments)


class NotifyQuote(Notify):

    def __init__(self, quote):
        Notify.__init__(self)
        time = self._detect_time(quote.text)
        self.arguments = ['-t'
                         ,str(time)
                         ,'time.ir - {}'.format(quote.author)
                         ,quote.text]


class NotifyHolidays(Notify):

    def __init__(self, days):
        (day1, day2) = self._find_two_next_days(days)
        
        if day1 and day1.is_holiday and day2 and day2.is_holiday:
            text = 'فردا و پس فردا تعطیل هستند'
        elif day1 and day1.is_holiday:
            text = 'فردا تعطیل است'
        elif day2 and day2.is_holiday:
            text = 'پس فردا تعطیل است'
        else:
            text = None

        Notify.__init__(self)
        self.arguments = ['-t'
                         ,'5000'
                         ,'time.ir'
                         ,text]

    def _find_two_next_days(self, days):
        day1 = None
        day2 = None
        found_today = False
        for day in days:
            if day.is_today:
                found_today += 1
                continue
            if found_today:
                if day1:
                    day2 = day
                    break
                day1 = day
        return (day1, day2)


if __name__ == '__main__':
    import sys
    import logging
    import traceback
    from optparse import OptionParser
    import datetime

    logging.basicConfig(level=logging.ERROR, format='%(levelname)-2s: %(message)s')
    logger = logging.getLogger(__name__)

    op = OptionParser()
    op.add_option('-s'
                 ,'--solar'
                 ,help='Does not show solar date'
                 ,action='store_const'
                 ,dest='solar'
                 ,const=False
                 ,default=True)
    op.add_option('-g'
                 ,'--gregorian'
                 ,help='Does not show gregorian date'
                 ,action='store_const'
                 ,dest='gregorian'
                 ,const=False
                 ,default=True)
    op.add_option('-c'
                 ,'--calendar'
                 ,help='Does not show calendar'
                 ,action='store_const'
                 ,dest='calendar'
                 ,const=False
                 ,default=True)
    op.add_option('-t'
                 ,'--time'
                 ,help='Does not show time'
                 ,action='store_const'
                 ,dest='time'
                 ,const=False
                 ,default=True)
    op.add_option('-C'
                 ,'--color'
                 ,help='Does not show colored text'
                 ,action='store_const'
                 ,dest='color'
                 ,const=False
                 ,default=True)
    op.add_option('-q'
                 ,'--quote'
                 ,help='Does not notify for quote'
                 ,action='store_const'
                 ,dest='quote'
                 ,const=False
                 ,default=True)
    op.add_option('-H'
                 ,'--holidays'
                 ,help='Does not notify for holidays'
                 ,action='store_const'
                 ,dest='holidays'
                 ,const=False
                 ,default=True)
    opts = op.parse_args()[0]

    def warn_notifier_error(command, exception):
        error_text = 'Notifier ERROR: could not work with command {!r} on this system'.format(command)
        if opts.color:
                error_text = '\033[1;30m' + error_text + '\033[0m' # gray (dark)
        print(error_text)

    def main():
        data = Request().get()
        transformers = {1: find_dates
                       ,2: find_calendar
                       ,3: find_quote}
        transformed = HTMLParser(data, transformers).parse()
        now = datetime.datetime.now()
        transformed[4] = Time(hour   = transform_number(str(now.hour))
                             ,minute = transform_number(str(now.minute))
                             ,second = transform_number(str(now.second)))
        
        dates = transformed[1]
        
        if opts.solar:
            solar_date = dates['solar']
            print('Emruz: ', end='')
            date_theme = None
            if opts.color:
                date_theme = DateTheme(year      = ('\033[0;36m', '\033[0m')
                                      ,seasons   = (('\033[1;31m', '\033[0m')  # green for Spring
                                                   ,('\033[1;31m', '\033[0m')  # red for Summer
                                                   ,('\033[1;33m', '\033[0m')  # yellow for Autumn
                                                   ,('\033[1;36m', '\033[0m')) # blue for Winter
                                      ,month     = ('\033[1;33m', '\033[0m')
                                      ,month_name= ('\033[1;35m', '\033[0m')
                                      ,weekday   = ('\033[1;34m', '\033[0m')
                                      ,day       = ('\033[1;36m', '\033[0m'))
            PrintDate(solar_date, date_theme).print()
            print()        

        if opts.gregorian:
            gregorian_date = dates['gregorian']
            print('Today: ', end='')
            date_theme = None
            if opts.color:
                date_theme = DateTheme(year      = ('\033[0;36m', '\033[0m')
                                      ,seasons   = (('\033[1;31m', '\033[0m')
                                                   ,('\033[1;31m', '\033[0m')
                                                   ,('\033[1;33m', '\033[0m')
                                                   ,('\033[1;36m', '\033[0m'))
                                      ,month     = ('\033[1;33m', '\033[0m')
                                      ,month_name= ('\033[1;35m', '\033[0m')
                                      ,weekday   = ('\033[1;34m', '\033[0m')
                                      ,day       = ('\033[1;36m', '\033[0m'))
            PrintDate(gregorian_date, date_theme).print()
            print()

        
        if opts.time:
            time = transformed[4]
            time_theme = None
            if opts.color:
                time_theme = TimeTheme(hour   = ('\033[1;31m', '\033[0m') # red
                                      ,minute = ('\033[1;31m', '\033[0m')
                                      ,second = ('\033[1;31m', '\033[0m'))
            print('System time: ', end='')
            PrintTime(time, time_theme).print()
            print()

        if opts.calendar:
            calendar_days = transformed[2]
            calendar_theme = None
            if opts.color:
                calendar_theme = CalendarTheme(disabled   = ('\033[1;30m', '\033[0m')  # gray (dark)
                                              ,holiday    = ('\033[1;31m', '\033[0m')  # red
                                              ,today      = ('\033[1;32m', '\033[0m')  # green (bold)
                                              ,normal     = ('\033[1;37m', '\033[0m')  # white
                                              ,solar      = ('\033[1;32m', '\033[0m')  # green
                                              ,other_days = ('\033[0;37m', '\033[0m')) # gray (light)
            DrawCalendar(calendar_days, calendar_theme).draw()
            if not opts.color: # user did not see colored calendar so he/she does not know about holidays
                for day in calendar_days:
                    if day.is_today:
                        if day.is_holiday:
                            print('*.' * 13 + ' Today is Holiday ' + '.*' * 13)
                    break

        if opts.quote:
            quote = transformed[3]
            notifier = NotifyQuote(quote)
            try:
                notifier.notify()
            except Exception as exception:
                warn_notifier_error(notifier.command, exception)

        if opts.holidays:
            days = transformed[2]
            notifier = NotifyHolidays(days)
            try:
                notifier.notify()
            except Exception as exception:
                warn_notifier_error(notifier.command, exception)

    status_code = 0
    try:
        main()
    except Exception as exception:
        print()
        print()
        logger.error('It seems that something was changed in time.ir or themes!\n'\
                     'Pleas open an issue in:\n'\
                     '\thttps://github.com/Pouriya-Jahanbakhsh/tir/issues/new\n'\
                     'with below details:')
        traceback.print_exc()
        print()
        status_code = 1
    sys.exit(status_code)
