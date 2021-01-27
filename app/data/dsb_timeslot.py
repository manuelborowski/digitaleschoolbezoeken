from app import db, log
from app.data import utils as mutils
from app.data.models import DsbTimeslot


def add_timeslot(date, length, number, coworker_1='', coworker_2=''):
    try:
        timeslot = DsbTimeslot.query.filter(DsbTimeslot.date == date).first()
        if timeslot:
            timeslot.length = length
            timeslot.number = number
            timeslot.coworker_1 = coworker_1
            timeslot.coworker_2 = coworker_2
        else:
            timeslot = DsbTimeslot(date=date, length=length, number=number, coworker_1=coworker_1, coworker_2=coworker_2)
            db.session.add(timeslot)
            log.info(f'timeslot added: {date}')
        db.session.commit()
        return timeslot
    except Exception as e:
        mutils.raise_error('could not add timeslot', e)
    return None


def get_timeslots(active=True):
    try:
        timeslots = DsbTimeslot.query
        if active is not None:
            timeslots = timeslots.filter(DsbTimeslot.active == active)
        timeslots = timeslots.order_by(DsbTimeslot.date).all()
        return timeslots
    except Exception as e:
        mutils.raise_error('could not get timeslots', e)
    return None
