from app import log, flask_app
from app.data import settings as msettings, dsb_timeslot as mdsb_timeslot, dsb_registration as mdsb_registration
from app.application import utils as mutils
import json, datetime


def get_available_timeslots(default_value=None):
    available_timeslots = []
    try:
        default_date = mutils.datetime_to_formiodate(default_value) if default_value else None
        configured_timeslot_bases = mdsb_timeslot.get_timeslots()
        all_registrations = mdsb_registration.get_registrations()
        registration_cache = [r.timeslot for r in all_registrations]
        if default_value:
            registration_cache.remove(default_value)
        date_label = ''
        value_list = []
        for base in configured_timeslot_bases:
            for i in range(base.number):
                configured_timeslot = base.date + datetime.timedelta(minutes=i * base.length)
                if configured_timeslot in registration_cache: continue
                date_string = mutils.datetime_to_dutch_date_string(configured_timeslot)
                if date_label != date_string:
                    date_label = date_string
                    value_list = []
                    available_timeslots.append({
                        'label': date_label,
                        'values': value_list,
                        'key': f'select-timeslot-{mutils.datetime_to_formiodate(base.date)}'
                    })
                time_string = mutils.datetime_to_time_string(configured_timeslot)
                value_list.append({
                    'label': time_string,
                    'value': mutils.datetime_to_formiodate(configured_timeslot)
                })
                if default_date and  value_list[-1]['value'] == default_date:
                    available_timeslots[-1]['default-value'] = default_date
        return available_timeslots
    except Exception as e:
        mutils.raise_error('could not get available timeslots', e)
    return []




def get_default_values(code=None):
    try:
        if code == flask_app.config['REGISTER_DSB_GUEST']:
            timeslots = get_available_timeslots()
            register_template = json.loads(msettings.get_configuration_setting('dsb-register-visitor-template'))
            return register_template, {}, timeslots
        registration = mdsb_registration.get_first_registration(code=code)
        timeslots = get_available_timeslots(registration.timeslot)
        register_template = json.loads(msettings.get_configuration_setting('dsb-register-visitor-template'))
        default_settings = registration.flat()
        default_settings['registration-date-of-birth'] = mutils.datetime_to_formiodate(default_settings['registration-date-of-birth'])
        return register_template, default_settings, timeslots
    except Exception as e:
        mutils.raise_error(f'could not get reservation by code {code}', e)
    return {}, []

class RegisterSaveResult:
    def __init__(self, result, reservation={}):
        self.result = result
        self.reservation = reservation

    class Result:
        E_OK = 'ok'
        E_NO_TIMESLOT_SELECTED = 'no-timeslot-selected'
        E_TIMESLOT_ALREADY_SELECTED = 'timeslot-already-selected'
        E_COULD_NOT_REGISTER = 'could-not-register'

    result = Result.E_OK
    reservation = {}


def add_or_update_registration(data, send_ack_email=True):
    try:
        available_timeslots = get_available_timeslots()
        timeslot_found = False
        timeslot = None
        for base in available_timeslots:
            if base['key'] in data and data[base['key']] != '':
                timeslot = mutils.formiodate_to_datetime(data[base['key']])
                timeslot_found = True
                break
        registration_info = {'code': flask_app.config['REGISTER_DSB_GUEST']}
        if not timeslot_found:
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_TIMESLOT_SELECTED, reservation=registration_info)
        registration = mdsb_registration.get_first_registration(timeslot=timeslot)
        if registration:
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_TIMESLOT_ALREADY_SELECTED, reservation=registration_info)

        date_of_birth = mutils.formiodate_to_datetime(data['registration-date-of-birth'])
        code = data['registration-code']
        if code != '':
            registration = mdsb_registration.get_first_registration(code=code)
            registration = mdsb_registration.update_registration(registration, timeslot, data['registration-first-name'], data['registration-last-name'], data['registration-email'], date_of_birth, code)
        else:
            code = mutils.create_random_string()
            registration = mdsb_registration.add_registration(timeslot, data['registration-first-name'], data['registration-last-name'], data['registration-email'], date_of_birth, code)
        if registration:
            if send_ack_email:
                registration.set_email_sent(False)
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_OK, reservation=registration.flat())
        return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)
    except Exception as e:
        log.error(f'could not register: {e}')
    return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)


def delete_registration(code):
    mdsb_registration.delete_registration(code)