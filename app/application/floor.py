from app.data import utils as mutils, floor as mfloor


def get_floors():
    return mfloor.get_floors()


mfloor.add_floor('CLB', 'CLB')
mfloor.add_floor('Scholengemeenschap', 'Scholengemeenschap')
mfloor.add_floor('Internaat', 'Internaat')