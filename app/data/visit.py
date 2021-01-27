from app import db, log
from app.data import utils as mutils
from app.data.models import Visit


def add_visit(timeslot, code):
    try:
        visit = Visit(code=code, timeslot=timeslot)
        db.session.add(visit)
        db.session.commit()
        log.info(f'visit added: {timeslot}')
        return visit
    except Exception as e:
        mutils.raise_error('could not add visit', e)
    return None


def delete_visit(code=None):
    try:
        visit = get_first_visit(code=code)
        db.session.delete(visit)
        db.session.commit()
        log.info(f'visit deleted: {code}')
    except Exception as e:
        mutils.raise_error('could not delete visit', e)


def get_visits(end_user=None, timeslot=None, code=None, socketio_sid=None, first=False):
    try:
        visits =Visit.query
        if end_user:
            visits = visits.filter(Visit.end_user == end_user)
        if timeslot:
            visits = visits.filter(Visit.timeslot == timeslot)
        if code:
            visits = visits.filter(Visit.code == code)
        if socketio_sid:
            visits = visits.filter(Visit.socketio_sid == socketio_sid)
        if first:
            visits = visits.first()
        else:
            visits = visits.all()
        return visits
    except Exception as e:
        mutils.raise_error('could not get visit', e)
    return None



def get_first_visit(end_user=None, timeslot=None, code=None, socketio_sid=None):
    return get_visits(end_user, timeslot, code, socketio_sid, first=True)


def update_email_sent_by_id(id, value):
    try:
        visit = Visit.query.get(id)
        visit.set_email_sent(value)
        log.info(f'visit email-sent update {id} {value}')
        return visit
    except Exception as e:
        mutils.raise_error(f'could not update visit email-sent {id} {value}', e)
    return None


def update_enable_by_id(id, value):
    try:
        visit = Visit.query.get(id)
        visit.enabled = value
        db.session.commit()
        log.info(f'visit enable update {id} {value}')
        return visit
    except Exception as e:
        mutils.raise_error(f'could not update visit enable {id} {value}', e)
    return None


def subscribe_ack_email_sent(cb, opaque):
    return Visit.subscribe_ack_email_sent(cb, opaque)


def subscribe_ack_email_send_retry(cb, opaque):
    return Visit.subscribe_ack_email_send_retry(cb, opaque)


def subscribe_enabled(cb, opaque):
    return Visit.subscribe_enabled(cb, opaque)


def get_first_not_sent_registration():
    visit = Visit.query.filter(Visit.enabled)
    visit = visit.filter(Visit.email_sent == False)
    visit = visit.first()
    return visit







