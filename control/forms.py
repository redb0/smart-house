from django import forms

from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class AddDevice(forms.Form):
    ip_address = forms.GenericIPAddressField(label='Ip-адрес устройства',
                                             initial="192.168.0.1",
                                             max_length=15)


class DeviceSettings(forms.Form):
    name = forms.CharField(label='Наименование устройства', max_length=50)
    ip_address = forms.GenericIPAddressField(label='Ip-адрес устройства', max_length=15)
    wap_login = forms.CharField(label='Логин точки доступа', max_length=50)
    wap_password = forms.CharField(label='Пароль точки доступа', max_length=50)
    wifi_login = forms.CharField(label='Логин WiFi сети', max_length=50)
    wifi_password = forms.CharField(label='Пароль WiFi сети', max_length=50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.tabs = []

        if self.__class__.tabs:
            self.helper.form_tag = False
            self.helper.layout = Layout(
                TabHolder(
                    *self.__class__.tabs
                )
            )
            self.helper.layout.append(Submit('submit', 'Сохранить'))

    def update_initial_values(self, data: dict):
        for field_name in self.base_fields.keys():
            if field_name in DeviceSettings.base_fields:
                self.fields[field_name].initial = data[field_name]
            else:
                constituents = field_name.split('_')
                if (len(constituents) == 2) and constituents[0].isdigit() and (constituents[1] == 'name'):
                    idx = int(constituents[0])
                    self.fields[field_name].initial = data['settings'][idx]['name']
                if (len(constituents) == 4) and constituents[0].isdigit() and constituents[1].isdigit() and (constituents[2] == 'modes'):
                    idx_program = int(constituents[0])
                    idx_mode = int(constituents[1])
                    self.fields[field_name].initial = data['settings'][idx_program]['modes'][idx_mode][constituents[3]]
                if (len(constituents) == 3) and constituents[0].isdigit() and (constituents[1] == 'pid') and (constituents[2] in ['p', 'i', 'd']):
                    idx_program = int(constituents[0])
                    self.fields[field_name].initial = data['settings'][idx_program]['pid'][constituents[2]]


# class AlcoholMachine(DeviceSettings):
#     # tabs = []
#
#     def __init__(self, data, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.tabs = []
#
#         self.add_fields(data)
#
#         if self.tabs:
#             self.helper.form_tag = False
#             self.helper.layout = Layout(
#                 TabHolder(
#                     Tab('Main',
#                         'name',
#                         'ip_address',
#                         'wap_login',
#                         'wap_password',
#                         'wifi_login',
#                         'wifi_password',
#                         ),
#                     *self.tabs
#                 )
#             )
#             self.helper.layout.append(Submit('submit', 'Сохранить'))
#
#     # @staticmethod
#     def add_fields(self, data: dict):
#
#         print()
#         print(self.fields)
#         for field_name in self.fields.keys():
#             self.fields[field_name].initial = data[field_name]
#             print(field_name, ': ', self.fields[field_name].initial)
#
#         settings = data['settings']
#         # self.fields['name']
#         for i in range(len(settings)):
#             field_names = [str(i) + '_name']
#             self.fields[str(i) + '_name'] = forms.CharField(label='Наименование программы',
#                                                             initial=settings[i]['name'], max_length=50)
#             self.__setattr__(str(i) + '_name', forms.CharField(label='Наименование программы',
#                                                                initial=settings[i]['name'], max_length=50))
#             # setattr(AlcoholMachine, str(i) + '_name', forms.CharField(label='Наименование программы',
#             #                                                           initial=settings[i]['name'], max_length=50))
#             for j in range(len(settings[i]['modes'])):
#                 field_names.append(str(i) + '_' + str(j) + '_modes_name')
#                 self.fields[field_names[-1]] = forms.CharField(label='Наименование режима',
#                                                                initial=settings[i]['modes'][j]['name'],
#                                                                max_length=50)
#                 self.__setattr__(field_names[-1], forms.CharField(label='Наименование режима',
#                                                                   initial=settings[i]['modes'][j]['name'],
#                                                                   max_length=50))
#                 # setattr(AlcoholMachine, field_names[-1], forms.CharField(label='Наименование режима',
#                 #                                                          initial=settings[i]['modes'][j]['name'],
#                 #                                                          max_length=50))
#                 field_names.append(str(i) + '_' + str(j) + '_modes_temp')
#                 self.fields[field_names[-1]] = forms.FloatField(label='Температура',
#                                                                 initial=settings[i]['modes'][j]['temp'])
#                 self.__setattr__(field_names[-1], forms.FloatField(label='Температура',
#                                                                    initial=settings[i]['modes'][j]['temp']))
#                 # setattr(AlcoholMachine, field_names[-1], forms.FloatField(label='Температура',
#                 #                                                           initial=settings[i]['modes'][j]['temp']))
#                 field_names.append(str(i) + '_' + str(j) + '_modes_time')
#                 self.fields[field_names[-1]] = forms.IntegerField(label='Время',
#                                                                   initial=settings[i]['modes'][j]['time'])
#                 self.__setattr__(field_names[-1], forms.IntegerField(label='Время',
#                                                                      initial=settings[i]['modes'][j]['time']))
#                 # setattr(AlcoholMachine, field_names[-1], forms.IntegerField(label='Время',
#                 #                                                             initial=settings[i]['modes'][j]['time']))
#             for key in settings[i]['pid'].keys():
#                 name = str(i) + '_pid_' + key
#                 field_names.append(name)
#                 if key == 'p':
#                     label = 'Пропорциональный коэффициент'
#                 elif key == 'p':
#                     label = 'Интегральный коэффициент'
#                 else:
#                     label = 'Дифференциальный коэффициент'
#                 self.fields[name] = forms.FloatField(label=label, initial=settings[i]['pid'][key])
#                 self.__setattr__(name, forms.FloatField(label=label, initial=settings[i]['pid'][key]))
#                 # setattr(AlcoholMachine, name, forms.FloatField(label=label, initial=settings[i]['pid'][key]))
#             self.tabs.append(Tab(settings[i]['name'], *field_names, css_id=str(i)))
#
#     def update_initial_values(self, data: dict):
#         for field_name in self.base_fields.keys():
#
#
#             if field_name != 'settings':
#                 self.base_fields[field_name].initial = data[field_name]
#             else:
#                 settings = data['settings']
#                 for i in range(len(settings)):
#                     field_name = str(i) + '_name'
#                     self.base_fields[field_name].initial = settings[i]['name']
#                     for j in range(len(settings[i]['modes'])):
#                         for key in settings[i]['modes'][j].keys():
#                             field_name = str(i) + '_' + str(j) + '_modes_' + key
#                             self.base_fields[field_name].initial = settings[i]['modes'][j][key]
#
#                     for key in settings[i]['pid'].keys():
#                         field_name = str(i) + '_pid_' + key
#                         self.base_fields[field_name].initial = settings[i]['pid'][key]


def generate_am_form_class(data: dict):
    tabs = []

    FormClass = type('FormClass', (DeviceSettings,), {})

    print()
    print(FormClass.base_fields)
    for field_name in FormClass.base_fields.keys():
        FormClass.base_fields[field_name].initial = data[field_name]
        print(field_name, ': ', FormClass.base_fields[field_name].initial)
    tabs.append(Tab('Основные', *FormClass.base_fields.keys(), css_id='0'))

    settings = data['settings']
    for i in range(len(settings)):
        field_names = [str(i) + '_name']
        FormClass.base_fields[str(i) + '_name'] = forms.CharField(label='Наименование программы',
                                                                  initial=settings[i]['name'], max_length=50)
        setattr(FormClass, str(i) + '_name', forms.CharField(label='Наименование программы',
                                                             initial=settings[i]['name'], max_length=50))
        for j in range(len(settings[i]['modes'])):
            for key in settings[i]['modes'][j].keys():
                field_names.append(str(i) + '_' + str(j) + '_modes_' + key)
                if key == 'name':
                    label = 'Наименование режима'
                elif key == 'temp':
                    label = 'Температура'
                else:
                    label = 'Время'
                FormClass.base_fields[field_names[-1]] = forms.CharField(label=label,
                                                                         initial=settings[i]['modes'][j][key],
                                                                         max_length=50)
                setattr(FormClass, field_names[-1], forms.CharField(label=label,
                                                                    initial=settings[i]['modes'][j][key],
                                                                    max_length=50))
        for key in settings[i]['pid'].keys():
            name = str(i) + '_pid_' + key
            field_names.append(name)
            if key == 'p':
                label = 'Пропорциональный коэффициент'
            elif key == 'i':
                label = 'Интегральный коэффициент'
            else:
                label = 'Дифференциальный коэффициент'
            FormClass.base_fields[name] = forms.FloatField(label=label, initial=settings[i]['pid'][key])
            setattr(FormClass, name, forms.FloatField(label=label, initial=settings[i]['pid'][key]))
        tabs.append(Tab(settings[i]['name'], *field_names, css_id=str(i + 1)))

    setattr(FormClass, 'tabs', tabs)

    return FormClass


def get_control_form(data: list):
    # "params": [{
    #     "title": "Программа",
    #     "id": "program",
    #     "type": "select",
    #     "field": "settings",
    #     "key": "pr",
    #     "options": []
    # }, {
    #     "title": "Запуск",
    #     "id": "start",
    #     "type": "button-start",
    #     "url": "start/",
    #     "is_active": true
    # }, {
    #     "title": "Пауза",
    #     "id": "pause",
    #     "type": "button-pause",
    #     "url": "pause/",
    #     "is_active": false
    # }, {
    #     "title": "Стоп",
    #     "id": "stop",
    #     "type": "button-stop",
    #     "url": "stop/",
    #     "is_active": false
    # }]
    ControlForm = type('ControlForm', (forms.Form,), {})
    buttons = []

    for field in data:
        if field['type'] == "select":
            CHOICES = ((i, field['options'][i]) for i in range(len(field['options'])))
            ControlForm.base_fields[field['id']] = forms.ChoiceField(label=field['title'], choices=CHOICES)
        elif "button" in field['type']:
            buttons.append(field)

        # elif field['type'] == "button-start":
        #     pass
        # elif field['type'] == "button-stop":
        #     pass
        # elif field['type'] == "button":
        #     pass
    return ControlForm, buttons



# def make_settings_form(data):
#     fields = {}
#     fields = {'name': forms.CharField(label='Наименование устройства', max_length=50),
#               'ip_address': forms.GenericIPAddressField(label='Ip-адрес устройства', max_length=15),
#               'wap_login': forms.CharField(label='Логин точки доступа', max_length=50),
#               'wap_password': forms.CharField(label='Пароль точки доступа', max_length=50),
#               'wifi_login': forms.CharField(label='Логин WiFi сети', max_length=50),
#               'wifi_password': forms.CharField(label='Пароль WiFi сети', max_length=50)}
#     if type(data['settings']) == list:
#         for i in range(len(data['settings'])):
#             for k in data['settings'][i].keys():
#                 v = data['settings'][i][k]
#                 if type(v) == str:
#                     fields[str(i) + '_' + k] = forms.CharField(label=k, initial=v)
#                 elif (type(v) == int) or (type(v) == float):
#                     fields[str(i) + '_' + k] = forms.FloatField(label=k, initial=v)
#                 elif (type(v) == list) or (type(v) == dict):
#                     for j in range(len(data['settings'][i][k])):
#                         new_v = data['settings'][i][k]
#                         if type(new_v) == dict:
#                             for key in new_v.keys():
#                                 if type(new_v[key]) == str:
#                                     fields[str(i) + '_' + k + '_' + str(j) + '_' + key] = forms.CharField(label=key,
#                                                                                                           initial=v)
#                                 elif (type(v) == int) or (type(v) == float):
#                                     fields[str(i) + '_' + k + '_' + str(j) + '_' + key] = forms.FloatField(label=key,
#                                                                                                            initial=v)
#                         elif type(new_v[key]) == str:
#                             fields[str(i) + '_' + k + '_' + str(j) + '_' + key] = forms.CharField(label=key, initial=v)
#                         elif (type(v) == int) or (type(v) == float):
#                             fields[str(i) + '_' + k + '_' + str(j) + '_' + key] = forms.FloatField(label=key, initial=v)
#     print(fields)
#
#     return type('DeviceSettings', (forms.BaseForm,), {'base_fields': fields})

# class DeviceSettingsForm(type):
#     def __new__(mcs, name, bases, dct):
#
#
#         return super(DeviceSettingsForm, mcs).__new__(mcs, name, bases, dct)
#
#     def __call__(cls, *args, **kwargs):
#         pass
#
#     def new_init(cls):
#         pass
