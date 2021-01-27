from app.data import utils as mutils, settings as msettings, models as mmodels
import datetime


def return_common_info():
    return msettings.get_test_server()


def formiodate_to_datetime(formio_date):
    date = datetime.datetime.strptime(':'.join(formio_date.split(':')[:2]), '%Y-%m-%dT%H:%M')
    return date


def datetime_to_formiodate(date):
    string = f"{datetime.datetime.strftime(date, '%Y-%m-%dT%H:%M')}:00+01:00"
    return string

def datetime_to_string(date):
    string = date.strftime('%d/%m/%Y %H:%M')
    return string


def raise_error(message, details=None):
    error = Exception(f'm({message}), d({details}), td({type(details).__name__})')
    raise error


