from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context, request
from flask_login import login_required, current_user
from . import end_user
from app import log, socketio, admin_required, flask_app
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import end_user as mend_user, info_items as minfo_items, floor as mfloor, visit as mvisit, \
    reservation as mreservation, settings as msettings, email as memail, dsb_registration as mdsbregistration
import json, re
from app.data import reservation as dmreservation
from app.data.models import SchoolReservation
from app.presentation.view import base_multiple_items
from app.presentation.view import update_available_periods, false, true, null, prepare_registration_form, dsb_prepare_registration_form

@end_user.route('/dsb/register', methods=['POST', 'GET'])
def dsb_register():
    try:
        current_url = request.url
        current_url = re.sub(f'{request.url_rule.rule}.*', '', current_url)
        memail.set_base_url(current_url)
        code = request.args['code']
        config_data = dsb_prepare_registration_form(code)
        return render_template('end_user/register.html', config_data=config_data,
                               registration_endpoint = 'end_user.dsb_register_save')
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('end_user/messages.html', type='unknown-error', message=e)


@end_user.route('/dsb/register_save/<string:form_data>', methods=['POST', 'GET'])
def dsb_register_save(form_data):
    try:
        data = json.loads(form_data)
        if data['cancel-reservation']:
            try:
                mreservation.delete_registration(data['registration-code'])
                return render_template('end_user/messages.html', type='cancel-ok')
            except Exception as e:
                return render_template('end_user/messages.html', type='could-not-cancel', message=e)
        else:
            try:
                ret = mdsbregistration.add_or_update_registration(data)
                if ret.result == ret.Result.E_NO_TIMESLOT_SELECTED:
                    return render_template('end_user/messages.html', type='dsb-no-timeslot-selected', info=ret.reservation)
                if ret.result == ret.Result.E_TIMESLOT_ALREADY_SELECTED:
                    return render_template('end_user/messages.html', type='dsb-timeslot-already-selected', info=ret.reservation)
                if ret.result == ret.Result.E_OK:
                    return render_template('end_user/messages.html', type='dsb-register-ok', info=ret.reservation)
            except Exception as e:
                return render_template('end_user/messages.html', type='could-not-register', message=e)
            return render_template('end_user/messages.html', type='could-not-register')
    except Exception as e:
        return render_template('end_user/messages.html', type='unknown-error', message=e)



@end_user.route('/register', methods=['POST', 'GET'])
def register():
    try:
        current_url = request.url
        current_url = re.sub(f'{request.url_rule.rule}.*', '', current_url)
        memail.set_base_url(current_url)
        code = request.args['code']
        config_data = prepare_registration_form(code)
        return render_template('end_user/register.html', config_data=config_data,
                               registration_endpoint = 'end_user.register_save')
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('end_user/messages.html', type='unknown-error', message=e)


@end_user.route('/register_save/<string:form_data>', methods=['POST', 'GET'])
def register_save(form_data):
    try:
        data = json.loads(form_data)
        if data['cancel-reservation']:
            try:
                mreservation.delete_registration(data['registration-code'])
                return render_template('end_user/messages.html', type='cancel-ok')
            except Exception as e:
                return render_template('end_user/messages.html', type='could-not-cancel', message=e)
        else:
            try:
                ret = mreservation.add_or_update_registration(data)
                if ret.result == ret.Result.E_NO_VISIT_SELECTED:
                    return render_template('end_user/messages.html', type='no-visit-selected', info=ret.reservation)
                if ret.result == ret.Result.E_NOT_ENOUGH_VISITS:
                    return render_template('end_user/messages.html', type='not-enough-visits', info=ret.reservation)
                if ret.result == ret.Result.E_GUEST_OK:
                    return render_template('end_user/messages.html', type='register-guest-ok', info=ret.reservation)

                if ret.result == ret.Result.E_NO_FLOOR_SELECTED:
                    return render_template('end_user/messages.html', type='no-floor-selected', info=ret.reservation)
                if ret.result == ret.Result.E_FLOOR_COWORKER_OK:
                    return render_template('end_user/messages.html', type='register-floor-coworker-ok', info=ret.reservation)

            except Exception as e:
                return render_template('end_user/messages.html', type='could-not-register', message=e)
            return render_template('end_user/messages.html', type='could-not-register')
    except Exception as e:
        return render_template('end_user/messages.html', type='unknown-error', message=e)


@end_user.route('/enter', methods=['POST', 'GET'])
def enter():
    try:
        if not msettings.get_enable_enter_guest():
            return render_template('end_user/messages.html', type='not-opened-yet')
        code = request.args['code']
        end_user = mend_user.end_user_entered(code)
        clb_items = minfo_items.get_info_items('clb')
        flat_clb_items = [i.flat() for i in clb_items]
        config = {
            'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        }
    except Exception as e:
        log.error(f'coworker with args {request.args} could not enter: {e}')
        return render_template('end_user/messages.html', type='could-not-enter')
    return render_template('end_user/infomoment.html', user=end_user,
                           config=config, async_mode=socketio.async_mode, items=flat_clb_items)


