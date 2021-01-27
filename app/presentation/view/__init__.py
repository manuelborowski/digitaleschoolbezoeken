from app.application import reservation as mreservation, settings as msettings
from app import flask_app
import json

false = False
true = True
null = None


def prepare_registration_form(registration_code):
    template, default_values, timeslots, floors = mreservation.get_default_values(registration_code)
    if timeslots:
        update_timeslots(timeslots, template, 'radio-visit-timeslots')
    if floors:
        update_floors(floors, template, 'radio-floor-levels')
    return {
        'default': default_values,
        'form': template
    }


def update_timeslots(timeslots, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            value_template = component['values'][0]
            component['values'] = []
            for timeslot in timeslots:
                if timeslot['nbr_visits_available'] <= 0:
                    continue
                new_value = dict(value_template)
                new_value['label'] = timeslot['label']
                new_value['value'] = timeslot['value']
                component['values'].append(new_value)
            return
        if 'components' in component:
            update_timeslots(timeslots, component, key)
    return


def update_floors(floors, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            value_template = component['values'][0]
            component['values'] = []
            for floor in floors:
                new_value = dict(value_template)
                new_value['label'] = floor['label']
                new_value['value'] = floor['value']
                component['values'].append(new_value)
            return
        if 'components' in component:
            update_floors(floors, component, key)
    return


def update_available_periods(periods, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            select_template = component['components'][0]
            data_template = component['components'][0]['data']['values'][0]
            component['components'] = []
            for period in periods:
                if period['boxes_available'] <= 0:
                    continue
                new = dict(select_template)
                new['data'] = dict({'values': []})
                for value in range(period['boxes_available'] + 1):
                    new_data = dict(data_template)
                    new_data['label'] = str(value)
                    new_data['value'] = str(value)
                    new['data']['values'].append(new_data)
                new['label'] = period['period']
                new['key'] = f'select-boxes-{period["id"]}'
                component['components'].append(new)
            return
        if 'components' in component:
            update_available_periods(periods, component, key)
    return


