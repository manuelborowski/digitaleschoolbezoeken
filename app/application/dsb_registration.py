from app import log, flask_app
from app.data import settings as msettings, dsb_timeslot as mdsb_timeslot, dsb_registration as mdsb_registration
from app.application import utils as mutils
import json, datetime


def get_available_timeslots(selected_date=None):
    available_timeslots = []
    try:
        selected_date_string = mutils.datetime_to_formiodate(selected_date) if selected_date else None
        configured_timeslot_bases = mdsb_timeslot.get_timeslots()
        all_registrations = mdsb_registration.get_registrations(enabled=True)
        registration_cache = [r.timeslot for r in all_registrations]
        if selected_date and selected_date in registration_cache:
            registration_cache.remove(selected_date)
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
                if selected_date_string and value_list[-1]['value'] == selected_date_string:
                    available_timeslots[-1]['default-value'] = selected_date_string
        return available_timeslots
    except Exception as e:
        mutils.raise_error('could not get available timeslots', e)
    return []


class RegisterSaveResult:
    def __init__(self, result, registration={}):
        self.result = result
        self.registration = registration

    class Result:
        E_OK = 'ok'
        E_NO_TIMESLOT_SELECTED = 'no-timeslot-selected'
        E_TIMESLOT_ALREADY_SELECTED = 'timeslot-already-selected'
        E_NO_REGISTRATION_FOUND = 'no-registration-found'
        E_COULD_NOT_REGISTER = 'could-not-register'

    result = Result.E_OK
    registration = {}


def get_default_values(code=None, id=None):
    try:
        register_endpoint = {'code': flask_app.config['REGISTER_DSB_GUEST']}
        if code is not None:
            # new registration
            if code == flask_app.config['REGISTER_DSB_GUEST']:
                timeslots = get_available_timeslots()
                register_template = json.loads(msettings.get_configuration_setting('dsb-register-visitor-template'))
                ret = {
                    'template': register_template,
                    'default': {},
                    'timeslots': timeslots}
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_OK, registration=ret)
            else:
                # guest makes an update
                registration = mdsb_registration.get_first_registration(code=code)
                if not registration:
                    return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_REGISTRATION_FOUND, registration=register_endpoint)
        elif id is not None:
            # administrator makes an update
            registration = mdsb_registration.get_first_registration(id=id)
            if not registration:
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_REGISTRATION_FOUND,registration=register_endpoint)
        else:
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)
        timeslots = get_available_timeslots(registration.timeslot)
        register_template = json.loads(msettings.get_configuration_setting('dsb-register-visitor-template'))
        default_settings = registration.flat()
        default_settings['registration-date-of-birth'] = mutils.datetime_to_formiodate(default_settings['registration-date-of-birth'])
        ret = {
            'template': register_template,
            'default': default_settings,
            'timeslots': timeslots}
        return RegisterSaveResult(result=RegisterSaveResult.Result.E_OK, registration=ret)
    except Exception as e:
        mutils.raise_error(f'could not get reservation by code {code}', e)
    return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)



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
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_TIMESLOT_SELECTED, registration=registration_info)

        code = data['registration-code']
        registration = mdsb_registration.get_first_registration(code=code) if code != '' else None
        registration_from_timeslot = mdsb_registration.get_first_registration(timeslot=timeslot, enabled=True)
        if registration:
            if registration_from_timeslot and registration is not registration_from_timeslot:
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_TIMESLOT_ALREADY_SELECTED, registration=registration_info)
        elif registration_from_timeslot:
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_TIMESLOT_ALREADY_SELECTED, registration=registration_info)

        date_of_birth = mutils.formiodate_to_datetime(data['registration-date-of-birth'])
        if registration:
            registration = mdsb_registration.update_registration(registration, timeslot, data['registration-first-name'], data['registration-last-name'], data['registration-email'], date_of_birth, code)
        else:
            code = mutils.create_random_string()
            registration = mdsb_registration.add_registration(timeslot, data['registration-first-name'], data['registration-last-name'], data['registration-email'], date_of_birth, code)
        if registration:
            if send_ack_email:
                registration.set_email_sent(False)
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_OK, registration=registration.flat())
        return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)
    except Exception as e:
        log.error(f'could not register: {e}')
    return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)


def get_registration_by_id(id=None):
    mdsb_registration.get_first_registration(id=id)


def delete_registration(code=None, id_list=None):
    return mdsb_registration.delete_registration(code=code, id_list=id_list)


def update_email_send_retry_by_id(id, value):
    try:
        return mdsb_registration.update_email_send_retry_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update registration email-send-retry {id}, {value}', e)
    return None


def update_email_sent_by_id(id, value):
    try:
        return mdsb_registration.update_email_sent_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update registration email-sent {id}, {value}', e)
    return None


def update_enable_by_id(id, value):
    try:
        return mdsb_registration.update_enable_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update registration enable {id}, {value}', e)
    return None


def subscribe_email_sent(cb, opaque):
    return mdsb_registration.subscribe_email_sent(cb, opaque)


def subscribe_email_send_retry(cb, opaque):
    return mdsb_registration.subscribe_email_send_retry(cb, opaque)


def subscribe_enabled(cb, opaque):
    return mdsb_registration.subscribe_enabled(cb, opaque)


