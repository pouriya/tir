#! /usr/bin/env python3

import logging

logging.basicConfig(level=logging.ERROR, format='%(levelname)-2s: %(message)s')
logger = logging.getLogger(__name__)

import sys

try:
    from tir import *
except ImportError:
    logger.error('could not found \'tir\' Python package installed on this system')
    sys.exit(1)

import subprocess
import traceback
from optparse import OptionParser
import datetime
from pathlib import Path
import os


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
op.add_option('-a'
             ,'--about'
             ,help='shows program\'s description and exits'
             ,action='store_const'
             ,dest='about'
             ,const=True
             ,default=False)
opts = op.parse_args()[0]
if opts.about:
    print('Python crawler for http://time.ir website')
    sys.exit(0)

def find_dates(html):
    container_top = search(html.body, 'div', 'class', 'topWrapper')
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
    container_top = search(html.body, 'div', 'class', 'topWrapper')
    calendar_wrapper = search(container_top, 'div', 'class', ('calendarWrapper',))
    calendar_container = search(calendar_wrapper, 'div', 'id', ('CalendarContainer',))
    event_calendar = search(calendar_container, 'div', 'class', 'eventCalendar')
    main_calendar = search(event_calendar, 'div', 'class', 'mainCalendar')
    day_list = search(main_calendar, 'div', 'class', 'dayList')
    day_list = [parse_day(day) for day in day_list.getchildren() if day.tag != 'br']
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
    container_top = search(html.body, 'div', 'class', 'topWrapper')
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
        count = 35
        if len(self.days) == 42:
            count = 42
        while offset < count:
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
                (type1, type2) = ('o', 't')
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
        self._print('{:^13}'.format(self.date.month_name), 'M')
        self._print('(')
        self._print(self.date.month, 'm')
        self._print(') ')
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

# class for check&save request body in local cache, once saved it's not send
# another request in the day, instead get data from local cache
# it will improve the performance and save time
    
class Caching:
    file_path = ""

    def check_cache(self):
        self.file_path = self.cache_folder() + '/.tir_cache'
        cache_file_content = self.get_read_file()
        if not cache_file_content:
            return ""
        finally_cache = {
            'date' : cache_file_content[:10],
            'body' : cache_file_content[11:],
        }
        return finally_cache

    def cache_folder(self):
        cache_folder = Path(str(Path.home()) + '/.cache/')
        if not cache_folder.is_dir():
            os.mkdir(check_cache)
        return str(cache_folder)

    def get_read_file(self):
        self.check_file_exist(self.file_path)
        with open(self.file_path) as cache_file:
            return cache_file.read()

    def check_file_exist(self, file_path):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w'): pass

    def write_response(self, body):
        body = str(datetime.date.today()) + body
        with open(self.file_path, 'w', encoding= "utf-8") as cache_file:
            cache_file.write(body)

    def is_today(self, cache_date):
        return str(datetime.date.today()) == cache_date
    
    def delete(self):
        with open(self.file_path, 'w', encoding= "utf-8") as cache_file:
            cache_file.write("")


def warn_notifier_error(command, exception):
    text = 'Notifier ERROR: could not work with command {!r} on this system'.format(command)
    if opts.color:
            text = '\033[1;30m' + text + '\033[0m' # gray (dark)
    print(text)

def main(data):
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
    
    if opts.solar or opts.gregorian or opts.calendar or opts.time or opts.quote or opts.calendar:
        print()
        text = '{}Powered by {}{}http://time.ir{}'
        if opts.color:
            text = text.format('\033[1;30m', '\033[0m', '\033[0;36m', '\033[0m')
        else:
            text = text.format('', '', '', '')
        print(text)

status_code = 0
cache        = Caching()
read_cache   = False
update_cache = False
data         = ""
try:
    cache_content = cache.check_cache()
    if not cache_content or not cache.is_today(cache_content['date']):
        data = Request().get()
        update_cache = True
    else:
        data = cache_content['body']
        read_cache = True
    main(data)
    # Everything is ok to keep new data in cache:
    if update_cache:
        cache.write_response(data)
except KeyboardInterrupt:
    print()
except Exception as exception:
    # We have red cache and something went wrong, So it's better to delete it:
    if read_cache:
        cache.delete()
    print()
    print()
    logger.error('It seems that something was changed in time.ir or themes!\n'\
                 'Pleas open an issue in:\n'                                  \
                 '\thttps://github.com/Pouriya-Jahanbakhsh/tir/issues/new\n'  \
                 'with below details:')
    traceback.print_exc()
    print()
    status_code = 1
sys.exit(status_code)
