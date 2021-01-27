from app.data import settings as msettings, reservation as mreservation, meeting as mmeeting, visit as mvisit, end_user as mend_user, dsb_registration as mdsb_registration
from app import email, log, email_scheduler, flask_app
import datetime, time, re
from flask_mail import Message

def send_email(to, sender, subject, content):
    msg = Message(sender=sender, recipients=[to], subject=subject, html=content)
    try:
        email.send(msg)
        return True
    except Exception as e:
        log.error(f'send_email: ERROR, could not send email: {e}')
    return False


# def return_table_row(name, value):
def return_table_row(*cell_values):
    row_string = '<tr>'
    for value in cell_values:
        row_string += f'<td style="border:1px solid black;">{value}</td>'
    row_string += '</tr>'
    return row_string
    # return f'<tr><td style="border:1px solid black;">{name}</td> <td style="border:1px solid black;">{value}</td></tr>'


def send_dsb_register_ack(**kwargs):
    try:
        registration = mdsb_registration.get_first_not_sent_registration()
        if registration:
            email_send_max_retries = msettings.get_configuration_setting('email-send-max-retries')
            if registration.email_send_retry >= email_send_max_retries:
                registration.set_enabled(False)
                return
            registration.set_email_send_retry(registration.email_send_retry + 1)
            flat = registration.flat()
            email_subject = msettings.get_configuration_setting('dsb-register-mail-ack-subject-template')
            email_content = msettings.get_configuration_setting('dsb-register-mail-ack-content-template')

            email_subject = email_subject.replace('{{TAG-TIMESLOT}}', flat['timeslot'])

            email_content = email_content.replace('{{TAG-TIMESLOT}}', flat['timeslot'])
            base_url = msettings.get_configuration_setting("base-url")
            even_timeslot = (int((registration.timeslot.minute) / 10) % 2) == 0
            if even_timeslot:
                teams_meeting_url = msettings.get_configuration_setting('dsb-teams-meeting-url-even')
            else:
                teams_meeting_url = msettings.get_configuration_setting('dsb-teams-meeting-url-odd')
            update_url = f'{base_url}/dsb/register?code={registration.code}'

            email_content = email_content.replace('{{TAG-ENTER-URL}}', f'<a href="{teams_meeting_url}">link</a>')
            email_content = email_content.replace('{{TAG-UPDATE-URL}}', f'<a href="{update_url}">hier</a>')
            sender = flask_app.config['MAIL_USERNAME']
            log.info(f'"{email_subject}" to {registration.email}')
            ret = send_email(registration.email, sender, email_subject, email_content)
            if ret:
                registration.set_email_sent(True)
            return ret
        return False
    except Exception as e:
        log.error(f'Could not send e-mail {e}')
    return False


def send_register_ack(**kwargs):
    try:
        visit = mvisit.get_first_not_sent_registration()
        if visit:
            email_send_max_retries = msettings.get_configuration_setting('email-send-max-retries')
            if visit.email_send_retry >= email_send_max_retries:
                visit.set_enabled(False)
                return
            visit.set_email_send_retry(visit.email_send_retry + 1)
            flat = visit.flat()
            if visit.end_user.profile == mend_user.Profile.E_GUEST:
                email_subject = msettings.get_configuration_setting('register-guest-mail-ack-subject-template')
                email_content = msettings.get_configuration_setting('register-guest-mail-ack-content-template')

                email_subject = email_subject.replace('{{TAG-TIMESLOT}}', flat['timeslot'])

                email_content = email_content.replace('{{TAG-TIMESLOT}}', flat['timeslot'])
                base_url = msettings.get_configuration_setting("base-url")
                enter_url = f'{base_url}/enter?code={visit.code}'
                update_url = f'{base_url}/register?code={visit.code}'

                email_content = email_content.replace('{{TAG-ENTER-URL}}', f'<a href="{enter_url}">link</a>')
                email_content = email_content.replace('{{TAG-UPDATE-URL}}', f'<a href="{update_url}">hier</a>')

            elif visit.end_user.profile == mend_user.Profile.E_FLOOR_COWORKER:
                email_subject = msettings.get_configuration_setting('register-guest-mail-ack-subject-template')
                email_content = msettings.get_configuration_setting('register-guest-mail-ack-content-template')

                email_subject = email_subject.replace('{{TAG-TIMESLOT}}', flat['timeslot'])

                email_content = email_content.replace('{{TAG-TIMESLOT}}', flat['timeslot'])
                base_url = msettings.get_configuration_setting("base-url")
                enter_url = f'{base_url}/enter?code={visit.code}'
                update_url = f'{base_url}/register?code={visit.code}'

                email_content = email_content.replace('{{TAG-ENTER-URL}}', f'<a href="{enter_url}">link</a>')
                email_content = email_content.replace('{{TAG-UPDATE-URL}}', f'<a href="{update_url}">hier</a>')

            log.info(f'"{email_subject}" to {visit.end_user.email}')
            ret = send_email(visit.end_user.email, email_subject, email_content)
            if ret:
                visit.set_email_sent(True)
            return ret
        return False
    except Exception as e:
        log.error(f'Could not send e-mail {e}')
    return False


def send_meeting_ack(**kwargs):
    try:
        meeting = mmeeting.get_first_not_sent_meeting()
        if meeting:
            email_subject = msettings.get_configuration_setting('meeting-mail-ack-subject-template')
            email_content = msettings.get_configuration_setting('meeting-mail-ack-content-template')

            email_subject = email_subject.replace('{{TAG-DATE}}', meeting.timeslot_string('%d/%m/%Y %H:%M'))

            email_content = email_content.replace('{{TAG-MEETING-URL}}', f'<a href="{meeting.teams_meeting_code}">{meeting.teams_meeting_code}</a>')
            email_content = email_content.replace('{{TAG-CLASSGROUP}}', meeting.classgroup)
            email_content = email_content.replace('{{TAG-DATE}}', meeting.timeslot_string('%d/%m/%Y %H:%M'))

            log.info(f'"{email_subject}" to {meeting.email}')
            ret = send_email(meeting.email, email_subject, email_content)
            if ret:
                meeting.set_email_sent(True)
            return ret
        return False
    except Exception as e:
        log.error(f'Could not send e-mail {e}')
    return False


send_email_config = [
    {'function': send_register_ack, 'args': {}},
    {'function': send_dsb_register_ack, 'args': {}},
    {'function': send_meeting_ack, 'args': {}},
]


run_email_task = True
def send_email_task():
    nbr_sent_per_minute = 0
    while run_email_task:
        with flask_app.app_context():
            at_least_one_email_sent = True
            start_time = datetime.datetime.now()
            job_interval = msettings.get_configuration_setting('email-task-interval')
            emails_per_minute = msettings.get_configuration_setting('emails-per-minute')
            while at_least_one_email_sent:
                at_least_one_email_sent = False
                for send_email in send_email_config:
                    if run_email_task and msettings.get_configuration_setting('enable-send-email'):
                        ret = send_email['function'](**send_email['args'])
                        if ret:
                            nbr_sent_per_minute += 1
                            now = datetime.datetime.now()
                            delta = now - start_time
                            if (nbr_sent_per_minute >= emails_per_minute) and (delta < datetime.timedelta(seconds=60)):
                                time_to_wait = 60 - delta.seconds + 1
                                log.info(f'send_email_task: have to wait for {time_to_wait} seconds')
                                time.sleep(time_to_wait)
                                nbr_sent_per_minute = 0
                                start_time = datetime.datetime.now()
                            at_least_one_email_sent = True
        if run_email_task:
                now = datetime.datetime.now()
                delta = now - start_time
                if delta < datetime.timedelta(seconds=job_interval):
                    time_to_wait = job_interval - delta.seconds
                    time.sleep(time_to_wait)


def set_base_url(url):
    msettings.set_configuration_setting('base-url', url)


def stop_send_email_task():
    global run_email_task
    run_email_task = False


def start_send_email_task():
    running_job = email_scheduler.get_job('send_email_task')
    if running_job:
        email_scheduler.remove_job('send_email_task')
    email_scheduler.add_job('send_email_task', send_email_task)

start_send_email_task()

