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


def get_registrations(enabled=True, code=None, timeslot=None, email_sent=None):
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
        registrations = registrations.all()
        return registrations
    except Exception as e:
        mutils.raise_error('could not get registrations', e)
    return None


def get_first_registration(code=None, timeslot=None, email_sent=None):
    try:
        registrations = get_registrations(code=code, timeslot=timeslot, email_sent=email_sent)
        if registrations:
            return registrations[0]
    except Exception as e:
        mutils.raise_error('could not get registration', e)
    return None


def get_first_not_sent_registration():
    registration = get_first_registration(email_sent=False)
    return registration