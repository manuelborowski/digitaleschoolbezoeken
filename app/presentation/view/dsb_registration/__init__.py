from flask import Blueprint

dsb_registration = Blueprint('dsb_registration', __name__)

from . import views
