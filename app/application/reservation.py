from app import db, log, flask_app
from app.data import reservation as mreservation, meeting as mmeeting, settings as msettings, visit as mvisit, end_user as mend_user, floor as mfloor
from app.application import utils as mutils
import datetime, random, string, json


def add_end_user_and_visit(first_name, last_name, email, profile, sub_profile, timeslot=None, code=None):
    try:
        if not timeslot:
            timeslot = datetime.datetime.now().replace(microsecond=0)
        code = code if code else create_random_string()
        user = mend_user.get_first_end_user(email, profile, sub_profile)
        if profile == mend_user.Profile.E_GUEST:
            if user: # guest already present
                visit = mvisit.get_first_visit(code=code)
                if visit: # visit already present, overwrite timeslot
                    visit.set_timeslot(timeslot)
                    log.info(f'add end user: {first_name} {last_name} {email} {code} {profile} {code}: overwrite timeslot')
                else:
                    visit = mvisit.get_first_visit(end_user=user, timeslot=timeslot)
                    if not visit: # guest has this timeslot not yet
                        visit = mvisit.add_visit(timeslot, code)
                        user.add_visit(visit)
                        log.info(f'add end user: {first_name} {last_name} {email} {code} {profile} {code}: new timeslot')
                    else:
                        log.info(f'add end user: {first_name} {last_name} {email} {code} {profile} {code}: existing timeslot')
            else: # new guest
                user = mend_user.add_end_user(first_name, last_name, email, profile, sub_profile)
                visit = mvisit.add_visit(timeslot, code)
                user.add_visit(visit)
                log.info(f'add end user: {first_name} {last_name} {email} {code} {profile} {code}: new user')
        else:
            if user: # coworker already present
                visit = mvisit.get_first_visit(code=code)
                log.info(f'add end user: {first_name} {last_name} {email} {code} {profile} {code}: user already exists')
            else: # new coworker
                user = mend_user.add_end_user(first_name, last_name, email, profile, sub_profile)
                visit = mvisit.add_visit(timeslot, code)
                user.add_visit(visit)
                log.info(f'add end user: {first_name} {last_name} {email} {code} {profile} {code}: new user')
        return user, visit
    except Exception as e:
        mutils.raise_error('could not add end user/visit', e)
    return None, None


def add_available_period(period, period_length, max_nbr_boxes):
    return mreservation.add_available_period(period, period_length, max_nbr_boxes)


def get_available_timeslots():
    available_timeslots = []
    try:
        first_timeslot = msettings.get_configuration_setting('timeslot-first-start')
        nbr_timeslots = msettings.get_configuration_setting('timeslot-number')
        timeslot_length = msettings.get_configuration_setting('timeslot-length')
        nbr_guests_per_timeslot = msettings.get_configuration_setting('timeslot-max-guests')
        for i in range(nbr_timeslots):
            timeslot = first_timeslot + datetime.timedelta(minutes=timeslot_length * i)
            visits = mvisit.get_visits(timeslot=timeslot)
            nbr_visits = len(visits)
            available_timeslots.append({
                'label': timeslot.strftime('%d/%m/%Y %H:%M'),
                'value': i,
                'max_visits': nbr_guests_per_timeslot,
                'nbr_visits': nbr_visits,
                'nbr_visits_available': nbr_guests_per_timeslot - nbr_visits
            })
        return available_timeslots
    except Exception as e:
        mutils.raise_error('could not get available timeslots', e)
    return []


def get_available_floors():
    floors = mfloor.get_floors()
    return [{'label': f.level, 'value': f.id} for f in floors]


def get_visits_available_for_timeslot(index):
    try:
        first_timeslot = msettings.get_configuration_setting('timeslot-first-start')
        nbr_timeslots = msettings.get_configuration_setting('timeslot-number')
        timeslot_length = msettings.get_configuration_setting('timeslot-length')
        nbr_guests_per_timeslot = msettings.get_configuration_setting('timeslot-max-guests')
        if index >= nbr_timeslots:
            return -1
        timeslot = first_timeslot + datetime.timedelta(minutes=timeslot_length * index)
        visits = mvisit.get_visits(timeslot=timeslot)
        nbr_visits_available = nbr_guests_per_timeslot - len(visits)
        return nbr_visits_available
    except Exception as e:
        mutils.raise_error(f'could not get visits left for timeslot {index}', e)
    return -1


def get_date_for_timeslot(index):
    try:
        first_timeslot = msettings.get_configuration_setting('timeslot-first-start')
        nbr_timeslots = msettings.get_configuration_setting('timeslot-number')
        timeslot_length = msettings.get_configuration_setting('timeslot-length')
        if index >= nbr_timeslots:
            return None
        timeslot = first_timeslot + datetime.timedelta(minutes=timeslot_length * index)
        return timeslot
    except Exception as e:
        mutils.raise_error(f'could not get timeslot date: {index}', e)
    return None


def get_index_for_timeslot(date):
    try:
        first_timeslot = msettings.get_configuration_setting('timeslot-first-start')
        timeslot_length = msettings.get_configuration_setting('timeslot-length')
        delta_time_minutes = (date - first_timeslot) / datetime.timedelta(minutes=1)
        index = delta_time_minutes / timeslot_length
        return int(index)
    except Exception as e:
        mutils.raise_error(f'could not get timeslot index: {date}', e)
    return None


def get_period_by_id(id):
    return mreservation.get_available_period_by_id(id)


def create_random_string(len=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


class RegisterSaveResult:
    def __init__(self, result, reservation={}):
        self.result = result
        self.reservation = reservation

    class Result:
        E_OK = 'ok'
        E_GUEST_OK = 'guest-ok'
        E_FLOOR_COWORKER_OK = 'floor-coworker-ok'
        E_NO_BOXES_SELECTED = 'no-boxes-selected'
        E_NOT_ENOUGH_BOXES = 'not-enough-boxes'
        E_COULD_NOT_REGISTER = 'could-not-register'
        E_NOT_ENOUGH_VISITS = 'not-enough-visits'
        E_NO_VISIT_SELECTED = 'no-visit-selected'
        E_NO_FLOOR_SELECTED = 'no-floor-selected'

    result = Result.E_OK
    reservation = {}


def delete_registration(reservation_code):
    try:
        user = mend_user.get_first_end_user(code=reservation_code)
        mvisit.delete_visit(code=reservation_code)
        if not user.visits:
            mend_user.delete_end_user(user=user)
    except Exception as e:
        mutils.raise_error(f'could not delete registration {reservation_code}', e)
    return RegisterSaveResult(result=RegisterSaveResult.Result.E_OK)


def add_or_update_registration(data, send_ack_email=True):
    try:
        if data['end-user-profile'] == mend_user.Profile.E_GUEST:
            reservation_info = {'code': flask_app.config['REGISTER_GUEST_CODE']}
            if 'radio-visit-timeslots' not in data or data['radio-visit-timeslots'] == '':
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_VISIT_SELECTED, reservation=reservation_info)
            nbr_visits_available = get_visits_available_for_timeslot(data['radio-visit-timeslots'])
            timeslot = get_date_for_timeslot(data['radio-visit-timeslots'])
            if nbr_visits_available <= 0:
                reservation_info.update({'timeslot': mutils.datetime_to_string(timeslot)})
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_NOT_ENOUGH_VISITS, reservation=reservation_info)
            registration_code = data['registration-code'] if data['registration-code'] != '' else None
            user, visit = add_end_user_and_visit(data['end-user-first-name'], data['end-user-last-name'], data['end-user-email'], mend_user.Profile.E_GUEST, None, timeslot, registration_code)
            if visit:
                if send_ack_email:
                    visit.set_email_sent(False)
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_GUEST_OK, reservation=visit.flat())
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)

        elif data['end-user-profile'] == mend_user.Profile.E_FLOOR_COWORKER:
            reservation_info = {'code': flask_app.config['REGISTER_FLOOR_COWORKER_CODE']}
            if 'radio-floor-levels' not in data or data['radio-floor-levels'] == '':
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_FLOOR_SELECTED, reservation=reservation_info)
            floor = mfloor.get_first_floor(data['radio-floor-levels'])
            reservation_info.update({'level': floor.level})
            registration_code = data['registration-code'] if data['registration-code'] != '' else None
            user, visit = add_end_user_and_visit(data['end-user-first-name'], data['end-user-last-name'], data['end-user-email'], mend_user.Profile.E_FLOOR_COWORKER, floor.level, None, registration_code)
            if visit:
                if send_ack_email:
                    visit.set_email_sent(False)
                return RegisterSaveResult(result=RegisterSaveResult.Result.E_FLOOR_COWORKER_OK, reservation=visit.flat())
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)
    except Exception as e:
        log.error(f'could not register: {e}')
    return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)


def get_default_values(code=None):
    try:
        if code == flask_app.config['REGISTER_GUEST_CODE']:
            timeslots = get_available_timeslots()
            register_template = json.loads(msettings.get_configuration_setting('register-guest-template'))
            default_settings = {'end-user-profile': mend_user.Profile.E_GUEST}
            return register_template, default_settings, timeslots, []
        elif code == flask_app.config['REGISTER_FLOOR_COWORKER_CODE']:
            floors = get_available_floors()
            register_template = json.loads(msettings.get_configuration_setting('register-floor-coworker-template'))
            default_settings = {'end-user-profile': mend_user.Profile.E_FLOOR_COWORKER}
            return register_template, default_settings, [], floors
        elif code == flask_app.config['REGISTER_FAIR_COWORKER_CODE']:
            return {}, []
        else:
            visit = mvisit.get_first_visit(code=code)
            if visit.end_user.profile == mend_user.Profile.E_GUEST:
                register_template = json.loads(msettings.get_configuration_setting('register-guest-template'))
                timeslots = get_available_timeslots()
                default_settings = visit.flat()
                default_settings.update({'radio-visit-timeslots': get_index_for_timeslot(visit.timeslot) })
                return register_template, default_settings, timeslots
            else:
                default_settings = visit.flat()
                return default_settings, []
    except Exception as e:
        mutils.raise_error(f'could not get reservation by code {code}', e)
    return {}, []


def get_reservation_by_id(id):
    return mreservation.get_registration_by_id(id)


def delete_meeting(id=None, list=None):
    return mmeeting.delete_meeting(id, list)


def update_meeting_code_by_id(id, value):
    try:
        return mmeeting.update_meeting_code_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update meeting code {id}, {value}', e)
    return None


def update_meeting_email_sent_by_id(id, value):
    try:
        return mmeeting.update_meeting_email_sent_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update meeting email-sent {id}, {value}', e)
    return None


def update_meeting_email_enable_by_id(id, value):
    try:
        return mmeeting.update_meeting_email_enable_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update meeting enable email {id}, {value}', e)
    return None


def update_visit_email_sent_by_id(id, value):
    try:
        return mvisit.update_email_sent_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update visit email-sent {id}, {value}', e)
    return None


def update_visit_enable_by_id(id, value):
    try:
        return mvisit.update_enable_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update visit enable {id}, {value}', e)
    return None


def subscribe_meeting_ack_email_sent(cb, opaque):
    return mmeeting.subscribe_ack_email_sent(cb, opaque)


def subscribe_visit_ack_email_sent(cb, opaque):
    return mvisit.subscribe_ack_email_sent(cb, opaque)


def subscribe_visit_ack_email_send_retry(cb, opaque):
    return mvisit.subscribe_ack_email_send_retry(cb, opaque)


def subscribe_visit_enabled(cb, opaque):
    return mvisit.subscribe_enabled(cb, opaque)


add_available_period(datetime.datetime(year=2021, month=1, day=25), 4, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=1), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=8), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=22), 5, 4)
add_available_period(datetime.datetime(year=2021, month=3, day=1), 5, 4)


add_end_user_and_visit('manuel', 'borowski', 'emmanuel.borowski@gmail.com', mend_user.Profile.E_FLOOR_COWORKER, mend_user.Level.E_CLB, datetime.datetime(2021, 1, 1, 14, 0, 0), 'manuel-clb')
add_end_user_and_visit('manuel-internaat', 'borowski', 'emmanuel.borowski@gmail.com', mend_user.Profile.E_FLOOR_COWORKER, mend_user.Level.E_INTERNAAT, datetime.datetime(2021, 1, 1, 14, 0, 0), 'manuel-internaat')
add_end_user_and_visit('gast1', 'testachternaam', 'gast1@gmail.com', mend_user.Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 0, 0), 'gast1-1')
add_end_user_and_visit('gast1', 'testachternaam', 'gast1@gmail.com', mend_user.Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 30, 0), 'gast1-2') #seconde reigstration
add_end_user_and_visit('gast1', 'testachternaam', 'gast1@gmail.com', mend_user.Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 15, 30, 0), 'gast1-2') #overwrite timeslot
add_end_user_and_visit('gast1', 'testachternaam', 'gast1@gmail.com', mend_user.Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 15, 30, 0), 'gast1-3') #reject: same timeslot
add_end_user_and_visit('gast3', 'testachternaam', 'gast3@gmail.com', mend_user.Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 0, 0), 'gast3')
