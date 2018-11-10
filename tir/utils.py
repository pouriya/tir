"""
tir.utils
~~~~~~~~~~~~~~
This module provides utility functions that are used within Tir
"""


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

