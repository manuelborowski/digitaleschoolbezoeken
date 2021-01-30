from app import db, log
from app.data import utils as mutils, settings as msettings
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


def pre_filter():
    return db.session.query(DsbTimeslot)


def search_data(search_string):
    search_constraints = []
    search_constraints.append(DsbTimeslot.date.like(search_string))
    search_constraints.append(DsbTimeslot.coworker_1.like(search_string))
    search_constraints.append(DsbTimeslot.coworker_2.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    meeting_url_even = msettings.get_configuration_setting('dsb-teams-meeting-url-even')
    meeting_url_odd = msettings.get_configuration_setting('dsb-teams-meeting-url-odd')
    html_meeting_url_even = f'<a href="{meeting_url_even}" target="_blank" >Hier klikken voor Teams meeting</a>'
    html_meeting_url_odd = f'<a href="{meeting_url_odd}" target="_blank" >Hier klikken voor Teams meeting</a>'
    for i in db_list:
        date_is_even = (int((i.date.minute) / 10) % 2) == 0
        if date_is_even:
            teams_meeting_url_1 = html_meeting_url_even
            teams_meeting_url_2 = html_meeting_url_odd
        else:
            teams_meeting_url_1 = html_meeting_url_odd
            teams_meeting_url_2 = html_meeting_url_even

        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append({
            'row_action': f'{i.id}',
            'date': em['date_1'],
            'coworker': em['coworker_1'],
            'meeting-url': teams_meeting_url_1
        })
        out.append({
            'row_action': f'{i.id}',
            'date': em['date_2'],
            'coworker': em['coworker_2'],
            'meeting-url': teams_meeting_url_2
        })
    return out


