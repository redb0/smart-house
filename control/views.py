import json

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from control.communication import send_get, send_post
from control.control_settings import RESERVED_BUTTONS
from control.logic import init_device
from control.models import devices_list, LaunchHistory
from .forms import AddDevice, get_control_form


def index_view(request):
    """Главная страница"""
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
            response = send_post('127.0.0.1:8000', '/settings_test', json=form.cleaned_data, protocol='http')

            # response = send_post(device.ip_address, '/settings', json=form.cleaned_data, protocol='http')
            # Ожидаемый ответ:
            # {'saved': 0, 'message': 'сообщание ошибки'} - ошибка данные не сохранены,
            # {'saved': 1, 'message': 'Данные успешно сохранены'} - данные сохранены
            data_response = response.json()
            saved = data_response['saved']
            message = data_response['message']

            return render(request, 'device/settings.html', {'devices': devices_list.get_dict(),
                                                            'device': device, 'idx': device_id,
                                                            'submenu': 0,
                                                            'form': form,
                                                            'saved': saved, 'message': message,
                                                            'data': form.cleaned_data, 'response': response})
    else:
        form = device.form_settings()
        print('Изменение начальных данных в форме')
        form.update_initial_values(device.to_dict())
    return render(request, 'device/settings.html', {'devices': devices_list.get_dict(),
                                                    'device': device, 'idx': device_id,
                                                    'submenu': 0,
                                                    'form': form, 'response': ''})


@csrf_exempt
def device_statistics_view(request, device_id):
    """Статистика устройства"""
    # print("Индекс устройства в списке: ", device_id)
    device = devices_list.devices[device_id]
    # charts = device.return_values
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
                    relative_url = btn['url']
                    print(relative_url)
                    response_text = 'Нажата кнопка "' + btn['title'] + '" '
                    # TODO: послать запрос на устройстко на url
                    print('Отправить запрос на', device.ip_address)

                    # response = send_post(device.ip_address, relative_url, json=form.cleaned_data, protocol='http')
                    response = send_post('127.0.0.1:8000', relative_url, json=form.cleaned_data, protocol='http')

                    print(response.status_code)
                    if response.status_code == requests.codes.ok:
                        print('Запрос выполнен успешно')
                        response_text += 'Запрос выполнен успешно'
                        print(response.text)  # Принять с устройства строку, например "Устройство успешно запущено"
                    else:
                        # TODO: Обработать ошибку с утсройства, считать ее из ответа и вывести на экран
                        print(response.text)
                        print('Ошибка')
                if btn['type'] in RESERVED_BUTTONS:
                    if btn['id'] in request.POST:
                        btn['is_active'] = False
                    else:
                        btn['is_active'] = True

            if 'delete' in request.POST:
                print('Инициация удаления устройства')
                response_text = 'Нажата кнопка "Delete" \n'
                # response = send_post(device.ip_address, relative_url, json=form.cleaned_data, protocol='http')
                response = send_get('127.0.0.1:8000', '/delete', protocol='http')
                print(response.text)
                response_text += response.text
        else:
            response_text = 'Некорректный ввод'

    return render(request, 'device/control.html', {'devices': devices_list.get_dict(), 'device': device,
                                                   'idx': device_id, 'submenu': 2,
                                                   'form': form, 'buttons': buttons,
                                                   'response': response_text})


def add_device(request):
    """Добавление устройства"""
    if request.method == 'POST':
        form = AddDevice(request.POST)
        if form.is_valid():
            if devices_list.get_device(form.cleaned_data['ip_address']):
                return render(request, 'add_device.html', {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0,
                                                           'form': form, 'connection': 2,
                                                           'response': "Устройство уже добавлено"})
            # TODO: Послать запрос устройству для инициализации
            # response = send_get(form.cleaned_data['ip_address'], '/init', protocol='http')
            response = send_get('127.0.0.1:8000', '/init', protocol='http')
            print(response.status_code)
            print(response.text)
            # ожидаемый ответ:
            # {
            #   'name': "", 'ip_address': "",
            #   'wap_login': "", 'wap_password': "",
            #   'wifi_login': "", 'wifi_password': "",
            #   'settings': [], 'return_values': []
            # }
            if response.status_code == requests.codes.ok:
                connection = 1
                device = init_device(response.json())
                # print('Настройки: ', device.settings)

                # FIXME: Убрать
                # device.starting(0)
            else:
                connection = 0
            return render(request, 'add_device.html', {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0,
                                                       'form': form, 'connection': connection,
                                                       'response': response.text})
    else:
        form = AddDevice()
    return render(request, 'add_device.html', {'devices': devices_list.get_dict(), 'idx': 0, 'submenu': 0,
                                               'form': form, 'connection': 2, 'response': ""})


def init_device_http(request):
    """Функция приемник запросов, симуляция устройства"""
    # TODO: переосмыслить return_values, сделать как линии на графике
    print('Инициализация устройства (обработка на устройстве)')
    data = {'name': "устройство - GET",
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
def settings_test_view(request):
    data = {'saved': 1, 'message': 'Данные успешно сохранены'}
    if request.method == 'POST':
        print('Сохранение настроек (обработка на устройстве)')
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='application/json')


def delete_view(request):
    if request.method == 'GET':
        print('Удаление устройства (обработка на устройстве)')
        return HttpResponse('Устройство удалено')


@csrf_exempt
def pause_view(request):
    if request.method == 'POST':
        print(json.loads(request.body))
        print('Нажата кнопка Start (обработка на устройстве)')
        return HttpResponse('На устройстве установлена пауза')


@csrf_exempt
def stop_view(request):
    if request.method == 'POST':
        print(json.loads(request.body))
        print('Нажата кнопка Start (обработка на устройстве)')
        return HttpResponse('Работа устройства остановлена')

@csrf_exempt
def start_view(request):
    """Функция приемник запросов, симуляция устройства"""
    if request.method == 'POST':
        print('Нажата кнопка Start (обработка на устройстве)')
        # print('Запрос пишел на устройство')
        # print('request.body:', request.body)
        # print('request.POST:', request.POST)
        # print('Данные на утсройстве:', json.loads(request.body))
    return HttpResponse('Устройство успешно запущено')


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
