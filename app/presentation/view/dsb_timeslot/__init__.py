from flask import Blueprint

dsb_timeslot = Blueprint('dsb_timeslot', __name__)

from . import views
