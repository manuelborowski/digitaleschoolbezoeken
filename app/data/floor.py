from app import db, log
from app.data.models import Floor
from app.data import utils as mutils

def add_floor(level, name='', info=''):
    try:
        floor = Floor.query.filter(Floor.level == level).all()
        if floor:
            log.warning(f'Floor {level} {name} already exists')
            return None
        floor = Floor(level=level, name=name, info=info)
        db.session.add(floor)
        db.session.commit()
    except Exception as e:
        mutils.raise_error(f'could not add floor {level}', e)
    return floor


def get_floors():
    try:
        floors = Floor.query.filter().all()
        return floors
    except Exception as e:
        mutils.raise_error(f'could not get floors', e)
    return None


def get_first_floor(id=id):
    try:
        floor = Floor.query.filter(Floor.id == id).first()
        return floor
    except Exception as e:
        mutils.raise_error(f'could not get first floor', e)
    return None
