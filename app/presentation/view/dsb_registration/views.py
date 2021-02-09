from . import dsb_registration
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import base_multiple_items
from app.data import dsb_registration as mddsb_registration
from app.application import dsb_registration as mdsb_registration, socketio as msocketio, tables as mtables
from app.data.models import SchoolReservation, AvailablePeriod, DsbRegistration
from app.presentation.layout.utils import flash_plus, button_pressed
from app.presentation.view import update_available_periods, false, true, null, dsb_prepare_registration_form

import json


@dsb_registration.route('/dsb_registration', methods=['POST', 'GET'])
@login_required
def show():
    if current_user.is_at_least_supervisor:
        return base_multiple_items.show(table_configuration_at_least_supervisor)
    return base_multiple_items.show(table_configuration_user)


@dsb_registration.route('/dsb_registration/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    return base_multiple_items.ajax(table_configuration_user)


@dsb_registration.route('/dsb_registration/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    if button_pressed('edit'):
        return item_edit()
    if button_pressed('delete'):
        return item_delete()


def item_edit(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        if chbx_id_list:
            id = int(chbx_id_list[0])  # only the first one can be edited
        ret = dsb_prepare_registration_form(id=id)
        if ret.result == ret.Result.E_COULD_NOT_REGISTER:
            flash_plus('Fout opgetreden')
        if ret.result == ret.Result.E_NO_REGISTRATION_FOUND:
            flash_plus('Sorry, geen registratie gevonden')
        if ret.result == ret.Result.E_OK:
            return render_template('end_user/register.html', config_data=ret.registration,
                                   registration_endpoint='dsb_registration.registration_save')
    except Exception as e:
        flash_plus('Fout opgetreden', e)
        log.error(f'could not edit dsb_registration {request.args}: {e}')
        return redirect(url_for('dsb_registration.show'))


def item_delete():
    try:
        chbx_id_list = request.form.getlist('chbx')
        mdsb_registration.delete_registration(id_list=chbx_id_list)
    except Exception as e:
        log.error(f'Could not delete regisration: {e}')
        flash_plus(u'Kan de registraties niet verwijderen', e)
    return redirect(url_for('dsb_registration.show'))


@dsb_registration.route('/registration_save/<string:form_data>', methods=['POST', 'GET'])
@login_required
@supervisor_required
def registration_save(form_data):
    try:
        data = json.loads(form_data)
        if data['cancel-reservation']:
            try:
                mdsb_registration.delete_registration(code=data['registration-code'])
            except Exception as e:
                flash_plus('Kon de reservatie niet verwijderen', e)
        else:
            try:
                ret = mdsb_registration.add_or_update_registration(data, update_by_end_user=False)
                if ret.result == ret.Result.E_NO_TIMESLOT_SELECTED:
                    flash_plus('Geen tijdslot geselecteerd')
                if ret.result == ret.Result.E_TIMESLOT_ALREADY_SELECTED:
                    flash_plus('Tijdslot is al gereserveerd')
            except Exception as e:
                flash_plus('Fout opgetreden', e)
    except Exception as e:
        flash_plus('Fout opgetreden', e)
    return redirect(url_for('dsb_registration.show'))


def update_registration_cb(msg, client_sid=None):
    if msg['data']['column'] == 7:  # mail sent column
        mdsb_registration.update_email_sent_by_id(msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 8:  # enable send mail column
        mdsb_registration.update_enable_by_id(msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 9:  # update tx-retry column
        mdsb_registration.update_email_send_retry_by_id(msg['data']['id'], msg['data']['value'])
    # msocketio.send_to_room({'type': 'celledit-dsb-registration', 'data': {'status': True}}, client_sid)


msocketio.subscribe_on_type('celledit-dsb-registration', update_registration_cb)


def ack_email_sent_cb(value, opaque):
    msocketio.broadcast_message({'type': 'celledit-dsb-registration', 'data': {'reload-table': True}})


mdsb_registration.subscribe_email_sent(ack_email_sent_cb, None)
mdsb_registration.subscribe_email_send_retry(ack_email_sent_cb, None)
mdsb_registration.subscribe_enabled(ack_email_sent_cb, None)

table_configuration_user = {
    'view': 'dsb_registration',
    'title': 'Registraties',
    'buttons': [ ],
    'delete_message': u'Wilt u deze registratie(s) verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'Id', 'data': 'id', 'order_by': DsbRegistration.id, 'orderable': True},
        {'name': 'Tijdslot', 'data': 'timeslot', 'order_by': DsbRegistration.timeslot, 'orderable': True},
        {'name': 'Naam', 'data': 'full_name', 'order_by': DsbRegistration.first_name, 'orderable': True},
        {'name': 'E-mail', 'data': 'registration-email', 'order_by': DsbRegistration.email, 'orderable': True},
        {'name': 'Geboortedatum', 'data': 'date_of_birth', 'order_by': DsbRegistration.date_of_birth,
         'orderable': True},
        {'name': 'Teamsmeeting', 'data': 'meeting-url', },
    ],
    'filter': [],
    'item': {
        # 'edit': {'title': 'Wijzig een reservatie', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        # 'add': {'title': 'Voeg een reservatie toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mddsb_registration.pre_filter,
    'format_data': mddsb_registration.format_data,
    'search_data': mddsb_registration.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-dsb-registration',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}

table_configuration_at_least_supervisor_update = {
    'buttons' : ['edit', 'delete'],
    'template': [
        {'name': 'E-mail verzonden', 'data': 'email_sent', 'order_by': DsbRegistration.email_sent, 'orderable': True,
         'celltoggle': 'standard', 'width': '1%'},
        {'name': 'Actief', 'data': 'enabled', 'order_by': DsbRegistration.enabled, 'orderable': True,
         'celltoggle': 'standard', 'width': '1%'},
        {'name': 'Tx-retry', 'data': 'email-send-retry', 'order_by': DsbRegistration.email_send_retry,
         'orderable': True,
         'celledit': 'text', 'width': '1%'},
    ]
}

table_configuration_at_least_supervisor =  mtables.table_configuration_deep_copy_and_update(table_configuration_user, table_configuration_at_least_supervisor_update)