from flask import render_template
from flask_login import login_required

from app import admin_required
from app.application import socketio as msocketio, utils as mutils
from . import settings
from app.application import settings as msettings


@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    default_settings['timeslot-first-start'] = mutils.datetime_to_formiodate(default_settings['timeslot-first-start'])
    return render_template('/settings/settings.html',
                           settings_form=settings_formio, default_settings=default_settings)


def update_settings_cb(msg, client_sid=None):
    data = msg['data']
    if data['setting'] == 'timeslot-first-start':
        data['value'] = mutils.formiodate_to_datetime(data['value'])
    msettings.set_configuration_setting(data['setting'], data['value'])


msocketio.subscribe_on_type('settings', update_settings_cb)

from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
    {
        "display": "form",
        "components": [
            {
                "title": "Digitale schoolbezoeken",
                "theme": "success",
                "collapsible": false,
                "key": "digitaleSchoolbezoeken",
                "type": "panel",
                "label": "Panel",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Registratieformulier",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "dsb-register-visitor-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingsmail : onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "dsb-register-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingsmail : inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "dsb-register-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Teams-meeting URL EVEN",
                        "tableView": true,
                        "persistent": false,
                        "key": "dsb-teams-meeting-url-even",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Teams-meeting URL ONEVEN",
                        "tableView": true,
                        "persistent": false,
                        "key": "dsb-teams-meeting-url-odd",
                        "type": "textfield",
                        "input": true
                    }
                ]
            },
            {
                "title": "Algemeen",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "algemeen",
                "type": "panel",
                "label": "Algemeen",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Gasten worden toegelaten",
                        "tableView": false,
                        "persistent": false,
                        "key": "enable-enter-guest",
                        "type": "checkbox",
                        "input": true,
                        "defaultValue": false
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Stage 2 configuratie",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "stage2Configuratie",
                "type": "panel",
                "label": "Stage 2 configuratie",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Wanneer wordt stage 2 actief?",
                        "optionsLabelPosition": "right",
                        "inline": false,
                        "tableView": false,
                        "defaultValue": "start-timeslot",
                        "values": [
                            {
                                "label": "Na start tijdslot",
                                "value": "start-timeslot",
                                "shortcut": ""
                            },
                            {
                                "label": "Na aanmelden",
                                "value": "logon",
                                "shortcut": ""
                            }
                        ],
                        "persistent": false,
                        "key": "stage-2-start-timer-at",
                        "type": "radio",
                        "input": true
                    },
                    {
                        "label": "Tijd begint te lopen na de start van het tijdslot",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "stage-2-delay-start-timer-until-start-timeslot",
                        "conditional": {
                            "show": true,
                            "when": "stage-2-start-timer-at",
                            "eq": "logon"
                        },
                        "type": "checkbox",
                        "input": true
                    },
                    {
                        "label": "Tijd vooraleer stage 2 zichtbaar wordt (seconden)",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "defaultValue": 0,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "stage-2-delay",
                        "type": "number",
                        "input": true,
                        "labelWidth": 50
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Stage 3 configuratie",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "stage3Configuratie1",
                "type": "panel",
                "label": "Stage 3 configuratie",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Wanneer wordt stage 3 actief?",
                        "optionsLabelPosition": "right",
                        "inline": false,
                        "tableView": false,
                        "defaultValue": "start-timeslot",
                        "values": [
                            {
                                "label": "Na start tijdslot",
                                "value": "start-timeslot",
                                "shortcut": ""
                            },
                            {
                                "label": "Na aanmelden",
                                "value": "logon",
                                "shortcut": ""
                            }
                        ],
                        "persistent": false,
                        "key": "stage-3-start-timer-at",
                        "type": "radio",
                        "input": true
                    },
                    {
                        "label": "Tijd begint te lopen na de start van het tijdslot",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "stage-3-delay-start-timer-until-start-timeslot",
                        "conditional": {
                            "show": true,
                            "when": "stage-3-start-timer-at",
                            "eq": "logon"
                        },
                        "type": "checkbox",
                        "input": true
                    },
                    {
                        "label": "Tijd vooraleer stage 3 zichtbaar wordt (seconden)",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "defaultValue": 0,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "stage-3-delay",
                        "type": "number",
                        "input": true,
                        "labelWidth": 50
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Tijdslot configuratie",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "tijdslotConfiguratie",
                "type": "panel",
                "label": "Tijdslot configuratie",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Eerste tijdslot start om",
                        "labelPosition": "left-left",
                        "displayInTimezone": "location",
                        "allowInput": false,
                        "format": "dd/MM/yyyy HH:mm",
                        "tableView": false,
                        "enableMinDateInput": false,
                        "datePicker": {
                            "disableWeekends": false,
                            "disableWeekdays": false
                        },
                        "enableMaxDateInput": false,
                        "timePicker": {
                            "showMeridian": false
                        },
                        "persistent": false,
                        "key": "timeslot-first-start",
                        "type": "datetime",
                        "timezone": "Europe/London",
                        "input": true,
                        "widget": {
                            "type": "calendar",
                            "timezone": "Europe/London",
                            "displayInTimezone": "location",
                            "locale": "en",
                            "useLocaleSettings": false,
                            "allowInput": false,
                            "mode": "single",
                            "enableTime": true,
                            "noCalendar": false,
                            "format": "dd/MM/yyyy HH:mm",
                            "hourIncrement": 1,
                            "minuteIncrement": 1,
                            "time_24hr": true,
                            "minDate": null,
                            "disableWeekends": false,
                            "disableWeekdays": false,
                            "maxDate": null
                        }
                    },
                    {
                        "label": "Lengte van een tijdslot",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "timeslot-length",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Aantal tijdsloten",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "timeslot-number",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Aantal gasten per tijdslot",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "timeslot-max-guests",
                        "type": "number",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "BEZOEKERS : Registratie template en e-mail",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate1",
                "type": "panel",
                "label": "BEZOEKERS : Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Web registratie template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "register-guest-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-guest-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-guest-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "VLOER MEDEWERKERS : Registratie template en e-mail",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "RegistratieTemplate2",
                "type": "panel",
                "label": "VLOER MEDEWERKERS : Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Web registratie template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "register-floor-coworker-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-floor-coworker-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-floor-coworker-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "SCHOOL MEDEWERKERS : Registratie template en e-mail",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "RegistratieTemplate3",
                "type": "panel",
                "label": "SCHOOL MEDEWERKERS : Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Web registratie template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "register-fair-coworker-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-fair-coworker-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-fair-coworker-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Registratie template en e-mail",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "RegistratieTemplate",
                "type": "panel",
                "label": "Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Web registratie template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "register-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Teams-meeting bevestigingse-mail",
                "theme": "primary",
                "collapsible": true,
                "hidden": true,
                "key": "teamsMeetingBevestigingseMail",
                "type": "panel",
                "label": "Teams-meeting bevestigingse-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "meeting-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "meeting-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "E-mail server settings",
                "theme": "primary",
                "collapsible": true,
                "key": "eMailServerSettings",
                "type": "panel",
                "label": "E-mail server settings",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Aantal keer dat een e-mail geprobeerd wordt te verzenden",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "email-send-max-retries",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Tijd (seconden) tussen het verzenden van e-mails",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "persistent": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "email-task-interval",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Max aantal e-mails per minuut",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "persistent": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "emails-per-minute",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Basis URL",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "key": "base-url",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "E-mails mogen worden verzonden",
                        "tableView": false,
                        "persistent": false,
                        "key": "enable-send-email",
                        "type": "checkbox",
                        "input": true,
                        "defaultValue": false
                    }
                ],
                "collapsed": true
            }
        ]
    }