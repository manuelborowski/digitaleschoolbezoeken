from app import db, log
from app.data import utils as mutils
from app.data.models import DsbRegistration


def add_registration(timeslot, first_name, last_name, email, date_of_birth, code):
    try:
        registration = DsbRegistration(timeslot=timeslot, first_name=first_name, last_name=last_name, email=email, date_of_birth=date_of_birth, code=code)
        db.session.add(registration)
        db.session.commit()
        log.info(f'Registration added: {timeslot}')
        return registration
    except Exception as e:
        mutils.raise_error('could not add registration', e)
    return None


def delete_registration(code=None, id_list=None):
    try:
        if id_list:
            for id in id_list:
                registration = get_first_registration(id=id)
                db.session.delete(registration)
            db.session.commit()
            return None
        registration = DsbRegistration.query
        if code is not None:
            registration = registration.filter(DsbRegistration.code == code)
        registration = registration.first()
        db.session.delete(registration)
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not delete registration', e)
    return None


def update_registration(registration, timeslot, first_name, last_name, email, date_of_birth, code):
    try:
        registration.timeslot = timeslot
        registration.first_name = first_name
        registration.last_name = last_name
        registration.email = email
        registration.date_of_birth = date_of_birth
        registration.code = code
        log.info(f'Registration updated: {timeslot}')
        db.session.commit()
        return registration
    except Exception as e:
        mutils.raise_error('could not update registration', e)
    return None


def get_registrations(enabled=None, code=None, timeslot=None, email_sent=None, id=None):
    try:
        registrations = DsbRegistration.query
        if enabled is not None:
            registrations = registrations.filter(DsbRegistration.enabled == enabled)
        if timeslot is not None:
            registrations = registrations.filter(DsbRegistration.timeslot == timeslot)
        if code is not None:
            registrations = registrations.filter(DsbRegistration.code == code)
        if email_sent is not None:
            registrations = registrations.filter(DsbRegistration.email_sent == email_sent)
        if id is not None:
            registrations = registrations.filter(DsbRegistration.id == id)
        registrations = registrations.all()
        return registrations
    except Exception as e:
        mutils.raise_error('could not get registrations', e)
    return None


def get_first_registration(enabled=None, code=None, timeslot=None, email_sent=None, id=None):
    try:
        registrations = get_registrations(enabled=enabled, code=code, timeslot=timeslot, email_sent=email_sent, id=id)
        if registrations:
            return registrations[0]
    except Exception as e:
        mutils.raise_error('could not get registration', e)
    return None


def get_first_not_sent_registration():
    registration = get_first_registration(enabled=True, email_sent=False)
    return registration


def update_email_send_retry_by_id(id, value):
    try:
        registration = DsbRegistration.query.get(id)
        registration.set_email_send_retry(value)
        log.info(f'registration email-send-retry update {id} {value}')
        return registration
    except Exception as e:
        mutils.raise_error(f'could not update registration email-send-retry {id} {value}', e)
    return None



def update_email_sent_by_id(id, value):
    try:
        registration = DsbRegistration.query.get(id)
        registration.set_email_sent(value)
        log.info(f'registration email-sent update {id} {value}')
        return registration
    except Exception as e:
        mutils.raise_error(f'could not update registration email-sent {id} {value}', e)
    return None


def update_enable_by_id(id, value):
    try:
        registration = DsbRegistration.query.get(id)
        registration.set_enabled(value)
        db.session.commit()
        log.info(f'Registration enable update {id} {value}')
        return registration
    except Exception as e:
        mutils.raise_error(f'could not update registration enable {id} {value}', e)
    return None


def subscribe_email_sent(cb, opaque):
    return DsbRegistration.subscribe_email_sent(cb, opaque)


def subscribe_email_send_retry(cb, opaque):
    return DsbRegistration.subscribe_email_send_retry(cb, opaque)


def subscribe_enabled(cb, opaque):
    return DsbRegistration.subscribe_enabled(cb, opaque)


def pre_filter():
    return db.session.query(DsbRegistration)


def search_data(search_string):
    search_constraints = []
    search_constraints.append(DsbRegistration.email.like(search_string))
    search_constraints.append(DsbRegistration.first_name.like(search_string))
    search_constraints.append(DsbRegistration.last_name.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    for i in db_list:
        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out


