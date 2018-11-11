"""
tir.utils
~~~~~~~~~~~~~~
This module provides utility functions that are used within Tir
"""


def transform_date(data):
    """ """
    # for example it may be 'چهارشنبه - ۹ آبان ۱۳۹۷'
    data = data.split('-')
    weekday = data[0].strip()
    if not weekday.isalpha(): # it's farsi
        weekday = transform_weekday(weekday)
    date = transform_date_with_string_month(data[1].strip())
    return (weekday, date)

def transform_numerical_date(data):
    """ """
    # for example '1397/12/6' or 2018-2-25 which is my birthday :)
    if data.find('/') != -1:
        type_ = 'solar'
    else: # assume gregorian
        type_ = 'gregorian'
    data = data.strip().replace('/', '-').split('-')
    (year, month, day) = (transform_number(data[0])
                         ,transform_number(data[1])
                         ,transform_number(data[2]))
    season = find_season(int(month), type_)
    return (year, season, month, day)

def transform_date_with_string_month(date):
    """ """
    date = date.split()
    if date[2].isalpha():
        (year, day, month) = (date[0], date[1], date[2])
    else: # It's farsi
        (day, month, year) = (transform_number(date[0])
                             ,transform_month(date[1])
                             ,transform_number(date[2]))
    return (year, month, day)

def transform_weekday(weekday):
    """ """
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

def transform_month(month):
    """ """
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

def transform_number(numbers):
    """ Converts Persian and Arabic numbers to English numbers"""
    new_format = ''

    mapping_dictionary = {
            # Persian numbers
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',

            # Arabic numbers
            '.': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
            }

    for number in numbers:
        result = mapping_dictionary.get(number, None)
        if result is None:
            raise ValueError('unknown farsi number {!r}'.format(number))
        new_format += result
    return new_format.zfill(2)

