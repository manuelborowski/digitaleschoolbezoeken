from app.data.models import EndUser, Visit, Fair, Floor
from app.data import utils as mutils, visit as mvisit
import random, string, datetime
from app import log, db


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


class Profile(EndUser.Profile):
    pass


class School(Fair.School):
    pass


class Level(Floor.Level):
    pass


def add_end_user(first_name, last_name, email, profile, sub_profile):
    try:
        user = EndUser(first_name=first_name, last_name=last_name, email=email, profile=profile, sub_profile=sub_profile)
        db.session.add(user)
        db.session.commit()
        log.info(f'Enduser {user.full_name()} added')
        return user
    except Exception as e:
        mutils.raise_error('could not add end user', e)
    return None


def delete_end_user(code=None, user=None):
    try:
        if not user:
            user = get_first_end_user(code=code)
        db.session.delete(user)
        db.session.commit()
        log.info(f'end user deleted: {code}')
    except Exception as e:
        mutils.raise_error('could not delete end user', e)




def get_first_end_user(email=None, profile=None, sub_profile=None, code=None):
    try:
        user = EndUser.query
        if email:
            user =user.filter(EndUser.email == email)
        if profile:
            user = user.filter(EndUser.profile == profile)
        if sub_profile:
            user = user.filter(EndUser.sub_profile == sub_profile)
        if code:
            user = user.join(Visit).filter(Visit.code == code)
        user = user.first()
        return user
    except Exception as e:
        mutils.raise_error('could not get end user', e)
    return None


def update_end_user(user, visit=None):
    try:
        if visit:
            user.visits.append(visit)
        db.session.commit()
        return user
    except Exception as e:
        mutils.raise_error(f'could not update end user {user.full_name()}', e)
    return None


def set_socketio_sid(code, sid):
    try:
        visit = mvisit.get_first_visit(code=code)
        visit.socketio_sid = sid
        db.session.commit()
        log.info(f'Enduser {visit.end_user.full_name()} logged in')
        return visit
    except Exception as e:
        mutils.raise_error(f'could not set socketio_sid {code} {sid}', e)
