import json

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from control.logic import init_device
from control.models import devices_list, LaunchHistory
from .forms import AddDevice, get_control_form


def index_view(request):
    """Главная страница"""
    # for i in range(len(devices_list.devices)):
    #     print(i, devices_list.devices[i].name)

    return render(request, 'index.html',
                  {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0})


def docs_view(request):
    """Документация"""
    return render(request, 'docs.html')


def device_settings_view(request, device_id):
    """Настройки устройства"""
    device = devices_list.devices[device_id]
    if request.method == 'POST':
        form = device.form_settings(request.POST)
        # print('Валидация = ', form.is_valid())
        # print('Связь = ', form.is_bound)
        # print('Нет ошибок = ', not form.errors)
        if form.is_valid():
            print('Данные формы', form.cleaned_data)
            device.from_dict(form.cleaned_data)
            device.save()
            print('Данные к отправке на устройство', device.to_dict())
            # TODO: отправить POST запрос с новыми настройками на устройство дождаться ответа и вывести "Настройки сохранены"


            url = 'http://' + device.ip_address
            r = requests.post()


            return render(request, 'device/settings.html', {'devices': devices_list.get_dict(),
                                                            'device': device, 'idx': device_id,
                                                            'submenu': 0,
                                                            'form': form, 'response': form.cleaned_data})
    else:
        form = device.form_settings()
        print('Изменение начальных данных', device.to_dict())
        form.update_initial_values(device.to_dict())
    return render(request, 'device/settings.html', {'devices': devices_list.get_dict(),
                                                    'device': device, 'idx': device_id,
                                                    'submenu': 0,
                                                    'form': form, 'response': ''})


@csrf_exempt
def device_statistics_view(request, device_id):
    """Статистика устройства"""
    print("Индекс устройства в списке: ", device_id)
    device = devices_list.devices[device_id]
    charts = device.return_values
    print("Графики", charts)
    response_text = ''
    json_data = ''
    title = ''
    subtitle = 'Устройство: ' + device.name
    if request.method == 'POST':
        # TODO: добавить обращение к устройству
        title = 'Статистика текущей работы устройства'
        # POST запрос с устройства. обработка запроса с пришедшими данными статистики
        if device.current_launch:
            # устройство запущено добавляем данные в статистику
            response_text = 'С устройства пришли данные'

            if device.current_launch.file_is_empty():
                # TODO: Для постонного принятия данных с устройства использовать подход Comet
                # TODO: Установить длительное соединение и посылать данные через него
                file_format = json.loads(request.body, encoding="utf-8")
                print(file_format)
                device.current_launch.set_format(file_format)  # формат json файла с первой порцией данных
                data = {}
                for key, item in file_format.items():
                    data[key] = item['data'][0]
                print('Вычленненные данные', data)
                layer = get_channel_layer()
                async_to_sync(layer.group_send)('statistic', {
                    'type': 'receive_statistic',
                    'content': data
                })
                return HttpResponse('')
                # {"time": {"name": "Время","suffix": " мин","label_format": "{value} мин","data":[0]},"temp": {"name": "Температура","suffix": "\\xB0C","label_format": "{value}\\xB0C","data":[22]},"power": {"name": "Мощность","suffix": "%","label_format": "{value} %","data":[100]},"container": {"name": "Контейнер","suffix": "","label_format": "№ {value}","data":[1]}}
            else:
                new_statistics = json.loads(request.body)  # данные вида {'time': 1, 'temp': 24, 'power': 50, 'container': 0}
                device.current_launch.update_statistics(new_statistics)

                layer = get_channel_layer()
                async_to_sync(layer.group_send)('statistic', {
                    'type': 'receive_statistic',
                    'content': new_statistics
                })
                return HttpResponse('')  # content='', content_type=None, status=200, reason=None
        else:
            # неизвестная фигня
            print('Что-то сверхъестественное')
            response_text = 'Что-то сверхъестественное'
    else:
        if device.current_launch:
            print('Загружаем данные из текущего файла')
            json_data = device.current_launch.get_statistic()
            print(json_data)
        else:
            last_launch = LaunchHistory.get_last_launch(device)
            if last_launch:
                print('--->', last_launch)
                response_text = str(last_launch.statistics)
                title = 'Статистика предыдущего процесса работы устройства'
                print('Путь', last_launch.statistics)
                with open(last_launch.statistics, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                print('Данные для графика', json_data)
            else:
                response_text = 'Статистики еще нет'
                print('Статистики еще нет')
        # posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        # запрос GET, рендеринг последней активной статистики
        # запрос от пользователя

    # TODO: Убрать 'response': response_text
    print(response_text)
    print(title)
    print(subtitle)
    print(json_data)
    return render(request, 'device/statistics.html',
                  {'devices': devices_list.get_dict(), 'device': device,
                   'idx': device_id, 'submenu': 1, 'response': response_text,
                   "json_data": json_data, 'title': title, 'subtitle': subtitle})


# @csrf_exempt
def device_control_view(request, device_id):  # , mode=''
    """Управление устройством"""
    # Какие действия будут выполняться на этой странице, возможно хватит настроек
    print("Индекс устройства в списке: ", device_id)
    device = devices_list.devices[device_id]
    launch_parameters = device.control_protocol['params']
    ControlForm, buttons = get_control_form(launch_parameters)
    response_text = ''
    if request.method == 'GET':
        # запрос от клиента на загрузку страницы
        form = ControlForm()
    else:  # POST запрос, нажатие на кнопку формы
        # пришли параметры управления устройства
        # отправить устройству команды управления
        form = ControlForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            for btn in buttons:
                if btn['id'] in request.POST:
                    url = btn['url']
                    print(url)
                    response_text = 'Нажата кнопка "' + btn['title'] + '" '
                    # TODO: послать запрос на устройстко на url
                    print('Отправить запрос на', device.ip_address)
                    device_url = 'http://' + '127.0.0.1:8000' + url
                    print(device_url)
                    r = requests.post(device_url, json=form.cleaned_data)  # json=form.cleaned_data device.ip_address
                    print(r.status_code)
                    # print(r.text)
                    if r.status_code == requests.codes.ok:
                        print('Запрос выполнен успешно')
                        response_text += 'Запрос выполнен успешно'
                        print(r.text)  # Принять с устройства строку, например "Устройство успешно запущено"
                        # print(r.json())
                    else:
                        # TODO: Обработать ошибку с утсройства, считать ее из ответа и вывести на экран
                        print(r.text)
                        print('Ошибка')
        else:
            response_text = 'Некорректный ввод'

    return render(request, 'device/control.html', {'devices': devices_list.get_dict(), 'device': device,
                                                   'idx': device_id, 'submenu': 2,
                                                   'form': form, 'buttons': buttons,
                                                   'response': response_text})


# def page_add_view(request):
#     if request.method == 'GET':
#         form = devices_list[0].form_settings
#     return render(request, 'add_device.html',
#                   {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0, 'form': form})


def add_device(request):
    """Добавление устройства"""
    if request.method == 'POST':
        form = AddDevice(request.POST)
        if form.is_valid():
            # print(form)
            # print(form.cleaned_data['ip_address'])
            if devices_list.get_device(form.cleaned_data['ip_address']):
                return render(request, 'add_device.html', {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0,
                                                           'form': form, 'connection': 2,
                                                           'response': "Устройство уже добавлено"})
            # TODO: Послать запрос устройству для инициализации
            r = requests.get('http://' + '127.0.0.1:8000' + '/init')  # form.cleaned_data['ip_address']
            print(r.status_code)
            # content_response = r.text
            print(r.text)
            # ожидаемый ответ:
            # {
            #   'name': "", 'ip_address': "",
            #   'wap_login': "", 'wap_password': "",
            #   'wifi_login': "", 'wifi_password': "",
            #   'settings': [], 'return_values': []
            # }
            if r.status_code == requests.codes.ok:
                connection = 1
                device = init_device(r.json())
                # print('Настройки: ', device.settings)

                # FIXME: Убрать
                # device.starting(0)
            else:
                connection = 0
            return render(request, 'add_device.html', {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0,
                                                       'form': form, 'connection': connection, 'response': r.text})
    else:
        form = AddDevice()
    return render(request, 'add_device.html', {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0,
                                               'form': form, 'connection': 2, 'response': ""})


def init_device_http(request):
    """Функция приемник запросов, симуляция устройства"""
    data = {'name': "Самогонный аппарат - GET",
            'type': "AM",
            'ip_address': "127.0.0.1",
            'wap_login': "login",
            'wap_password': "password",
            'wifi_login': "login",
            'wifi_password': "password",
            'settings': [{'name': 'Программа 1',
                          'modes': [{'name': 'Режим 1', 'temp': 75, 'time': 30},
                                    {'name': 'Режим 2', 'temp': 95, 'time': 240},
                                    {'name': 'Режим 3', 'temp': 100, 'time': 30},
                                    {'name': 'Режим 4', 'temp': 30, 'time': 0},
                                    {'name': 'Режим 5', 'temp': 30, 'time': 0}],
                          'pid': {'p': 1, 'i': 1, 'd': 1}},
                         {'name': 'Программа 2',
                          'modes': [{'name': 'Режим 1', 'temp': 75, 'time': 30},
                                    {'name': 'Режим 2', 'temp': 95, 'time': 240},
                                    {'name': 'Режим 3', 'temp': 100, 'time': 30},
                                    {'name': 'Режим 4', 'temp': 30, 'time': 0},
                                    {'name': 'Режим 5', 'temp': 30, 'time': 0}],
                          'pid': {'p': 1, 'i': 1, 'd': 1}}],
            'return_values': [{'design': 'temp', 'name': 'Температура', 'value': 35.5},
                              {'design': 'time', 'name': 'Время', 'value': 10},
                              {'design': 'container', 'name': 'Сосуд', 'value': 1},
                              {'design': 'power', 'name': 'Мощность', 'value': 1}],
            'control_protocol': {"html": "",
                                 "params": [{
                                     "title": "Программа",
                                     "id": "program",
                                     "type": "select",
                                     "field": "settings",
                                     "options": ['Программа 1', 'Программа 2']
                                 }, {
                                     "title": "Запуск",
                                     "id": "start",
                                     "type": "button-start",
                                     "url": "/start",
                                     "is_active": True
                                 }, {
                                     "title": "Пауза",
                                     "id": "pause",
                                     "type": "button-pause",
                                     "url": "/pause",
                                     "is_active": False
                                 }, {
                                     "title": "Стоп",
                                     "id": "stop",
                                     "type": "button-stop",
                                     "url": "/stop",
                                     "is_active": False
                                 }]
                                 }
            }
    if request.method == 'GET':
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def start_view(request):
    """Функция приемник запросов, симуляция устройства"""
    print(request.method)
    if request.method == 'POST':
        print('Запрос пишел на устройство')
        print('request.body:', request.body)
        print('request.POST:', request.POST)
        print('Данные на утсройстве:', json.loads(request.body))
    return HttpResponse('')


# def get_device_statistic(request):
#     data = {"time": {"name": "Время", "data": [0]},
#             "temp": {"name": "Температура", "data": [22]},
#             "power": {"name": "Мощность", "data": [100]},
#             "container": {"name": "Контейнер", "data": [1]}}
#     return requests.post('http://' + '127.0.0.1:8000' + '/post', json=json.dumps(data))

    # for i in range(10):
    #     data = {'time': i,
    #             'temp': random.uniform(0, 1),
    #             'power': 50,
    #             'container': 0
    #             }
    #     yield requests.post('http://' + '127.0.0.1:8000' + '/post', json=json.dumps(data))


def condition_db(request):
    """Для админа"""
    # 127.0.0.1:8000/admin/condition
    # FIXME: Убрать
    from control.models import Device, AlcoholMachine

    # Device.delete_everything()
    # AlcoholMachine.delete_everything()
    # LaunchHistory.delete_everything()

    devices = Device.get_all_objects()
    html = "Записей в таблице \"Device\": " + str(len(devices)) + "<br>"
    am = AlcoholMachine.get_all_objects()
    html += "Записей \"AlcoholMachine\": " + str(len(am)) + "<br>"
    history = LaunchHistory.get_all_objects()
    html += "Записей \"LaunchHistory\": " + str(len(history)) + "<br>"
    from django.utils.safestring import mark_safe

    return render(request, 'admin/condition.html', {'response': mark_safe(html)})


# def test(request):
#     if request.method == 'GET':
#         print(request.GET)
#         print(request.GET.get('a'))
#         print(request.GET.get('b'))
#         print(request.GET.getlist('c'))
#         return HttpResponse('')
