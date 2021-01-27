# from app.data.models import EndUser, Visit, Fair, Floor
from app.data import utils as mutils, end_user as mend_user, visit as mvisit
import random, string, datetime
from app import log
from app.application import socketio as msocketio, room as mroom, settings as msettings


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


class Profile(mend_user.Profile):
    pass


class School(mend_user.School):
    pass


class Level(mend_user.Level):
    pass


def end_user_entered(code):
    visit = mvisit.get_first_visit(code=code)
    user = visit.end_user
    visit.set_timestamp()
    return visit.flat()


def remove_socketio_sid_cb(msg, sid):
    try:
        visit = mvisit.get_first_visit(socketio_sid=sid)
        if visit:
            mend_user.set_socketio_sid(visit.code, None)
            log.info(f'Enduser {visit.end_user.full_name()} logged out')
    except Exception as e:
        mutils.raise_error(f'could not remove socketio_sid {sid}', e)

msocketio.subscribe_on_type('disconnect', remove_socketio_sid_cb)


def new_end_user_cb(msg, client_sid):
    visit = mend_user.set_socketio_sid(msg['data']['user_code'], client_sid)
    if visit.end_user.profile == Profile.E_FAIR_COWORKER:
        show_stage(2, client_sid)
        show_stage(3, client_sid)
    elif visit.end_user.profile == Profile.E_GUEST:
        room = mroom.select_least_occupied_room(Level.E_CLB)
        room_owner = mend_user.get_first_end_user(code=room.code)
        add_chatroom(Level.E_CLB, room.code, room_owner.full_name(), client_sid)
        send_chat_history(room.code, client_sid)
        send_time_when_to_show_stage(2, visit)
    else:
        show_stage(2, client_sid)
        show_stage(3, client_sid)
        add_chatroom(visit.end_user.profile, visit.code, visit.end_user.full_name(), client_sid)
        send_chat_history(msg['data']['user_code'], client_sid)


def show_stage(stage, sid):
    msocketio.send_to_room({'type': f'stage-{stage}-visible', 'data': {'show': True}}, sid)


def add_chatroom(floor, code, title, sid):
    msocketio.send_to_room({'type': 'add-chat-room', 'data': {'floor': floor, 'room_code': code, 'title': title}}, sid)


def send_chat_history(room_code, client_sid):
    history = mroom.get_history(room_code)
    for chat_line in history:
        msg = {
            'type': 'chat-line',
            'data': chat_line
        }
        msocketio.send_to_room(msg, client_sid)


def send_time_when_to_show_stage(stage, visit):
    settings = msettings.get_configuration_settings()
    now = datetime.datetime.now()
    start_delay_at_start_timeslot = settings[f'stage-{stage}-start-timer-at'] == msettings.StageSetting.E_AFTER_START_TIMESLOT
    delay_start_timer_until_start_timeslot = settings[f'stage-{stage}-delay-start-timer-until-start-timeslot']
    delay = settings[f'stage-{stage}-delay']
    if start_delay_at_start_timeslot:
        show_time = visit.timeslot + datetime.timedelta(seconds=delay)
    elif now > visit.timeslot:
        show_time = now + datetime.timedelta(seconds=delay)
    elif delay_start_timer_until_start_timeslot:
        show_time = visit.timeslot + datetime.timedelta(seconds=delay)
    else:
        show_time = now + datetime.timedelta(seconds=delay)
    log.info(f'user {visit.end_user.full_name()} stage {stage}, show time at {show_time}')

    msocketio.send_to_room({'type': f'stage-show-time', 'data': {'stage': stage, 'show-time': str(show_time)}}, visit.socketio_sid)


def stage_show_time_cb(msg, client_sid):
    stage = msg['data']['stage']
    show_stage(stage, client_sid)


msocketio.subscribe_on_type('new-end-user', new_end_user_cb)
msocketio.subscribe_on_type('stage-show-time', stage_show_time_cb)

