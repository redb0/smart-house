import datetime
import json
import os

from django.db import models
from django.utils import timezone


# Create your models here.

def ensure_dir(file_path, subdir=''):
    if file_path:
        path = os.path.dirname(file_path)
    else:
        abs_path = os.path.abspath(__file__)
        rel_path = '/statistics/' + subdir
        path = os.path.join(abs_path, rel_path)
    if not os.path.exists(path):
        os.makedirs(path)


def get_datetime_str():
    now = datetime.datetime.now()
    return now.strftime('%d_%m_%Y_%H_%M_%S_%f')


class Devices:
    devices = []

    def __init__(self):
        pass

    def add(self, obj):
        self.devices.append(obj)

    def get_dict(self) -> dict:
        return {i: Devices.devices[i] for i in range(len(Devices.devices))}

    def get_device(self, ip_address):
        for obj in Devices.devices:
            if obj.ip_address == ip_address:
                return obj
        return None


devices_list = Devices()


class Device(models.Model):
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()
    wap_login = models.CharField(max_length=30)
    wap_password = models.CharField(max_length=50)
    wifi_login = models.CharField(max_length=30)
    wifi_password = models.CharField(max_length=50)
    device_settings = models.CharField(max_length=1024)

    # TODO: возможно ip адресс не будет меняться
    # def __init__(self, name: str, device_type: str, ip_address: str, wifi, wap) -> None:  # : Net
    #     self._name = name
    #     self._type = device_type
    #     self._ip_address = ip_address
    #     self._wifi_net = wifi
    #     self._WAP = wap  # Wireless Access Point - Беспроводная точка доступа
    #     self._settings = []  # {'design': '', 'name': '', 'value': 1} обознаение, значение
    #     self._return_values = []  # {'design': '', 'name': '', 'value': 1} обознаение, значение
    #     self._form_settings = None

    @classmethod
    def create(cls, name, d_type, ip_address,
               wap_login, wap_pass, wifi_login, wifi_pass,
               d_settings: list, return_values, control_protocol):
        device = cls(name=name, device_type=d_type, ip_address=ip_address,
                     wap_login=wap_login, wap_password=wap_pass,
                     wifi_login=wifi_login, wifi_password=wifi_pass,
                     device_settings=json.dumps(d_settings, ensure_ascii=False))
        device.__setattr__('return_values', return_values)
        device.__setattr__('settings', d_settings)  # TODO: зачем добавлять поле когда есть поле выше device_settings

        # Протокол управления, для рендеринга страници
        device.__setattr__('control_protocol', control_protocol)  # json.dumps(control_protocol, ensure_ascii=False)

        device.__setattr__('form_settings', None)
        device.__setattr__('current_launch', None)  # ссылка на историю текущего запуска
        # device.__setattr__('start_settings', None)  # стартовые настройки (json), из формы запуска (клавиши старт)

        device.__setattr__('title', '')
        device.__setattr__('subtitle', '')

        return device

    @classmethod
    def delete_everything(cls):
        cls.objects.all().delete()

    @classmethod
    def get_all_objects(cls):
        return cls.objects.all()

    def from_dict(self, data: dict):
        self.name = data['name']
        self.ip_address = data['ip_address']
        self.wifi_login = data['wifi_login'], data['wifi_password']
        self.wifi_password = data['wifi_password']
        self.wap_login = data['wap_login'], data['wap_password']
        self.wap_password = data['wap_password']

    def to_dict(self):
        return dict((key, self.__dict__[key]) for key in self.__dict__.keys() if not key.startswith('_'))

    def start(self, start_settings=None):  # , idx_settings=None
        # TODO: метод запуска устройства,
        # TODO: сгенерировать уникальное имя файла статистики
        # TODO: создать объект LaunchHistory(текущая дата время, девайс, запущенная программа, путь до файла статистики)
        # if idx_settings:
        #     setting = self.settings[idx_settings]
        # else:
        #     setting = self.settings

        date_str = get_datetime_str()
        abs_path = os.path.abspath(__file__)
        statistic_path = '../statistics/' + self.ip_address
        subdir = os.path.join(abs_path, statistic_path)
        if not os.path.exists(subdir):
            os.makedirs(subdir)

        file_name = date_str + '.json'
        path = os.path.join(subdir, file_name)

        try:
            print('попытка создать файл')
            file = open(path, 'x', encoding='utf-8')  # , os.O_WRONLY | os.O_CREAT | os.O_EXCL
        except IOError as e:
            print('не удалось открыть файл')
            print('файл существует')
        else:
            print('закрываем', path)
            file.close()

        self.current_launch = LaunchHistory(device=self, settings=self.settings,
                                            start_settings=start_settings, statistics=path)
        self.current_launch.save()

        return self.current_launch

    def stop(self):
        self.current_launch = None


class AlcoholMachine(Device):
    class Meta:
        proxy = True
    # data = {'name': "Самогонный аппарат - GET",
    #         'type': "AM",
    #         'ip_address': "127.0.0.1",
    #         'wap_login': "login",
    #         'wap_password': "password",
    #         'wifi_login': "login",
    #         'wifi_password': "password",
    #         'settings': [{'name': 'Программа 1',
    #                       'modes': [{'name': 'Режим 1', 'temp': 75, 'time': 30},
    #                                 {'name': 'Режим 2', 'temp': 95, 'time': 240},
    #                                 {'name': 'Режим 3', 'temp': 100, 'time': 30},
    #                                 {'name': 'Режим 4', 'temp': 30, 'time': 0},
    #                                 {'name': 'Режим 5', 'temp': 30, 'time': 0}],
    #                       'pid': {'p': 1, 'i': 1, 'd': 1}}],
    #         'return_values': [{'design': 'temp', 'name': 'Температура', 'value': 35.5},
    #                           {'design': 'time', 'name': 'Время', 'value': 10},
    #                           {'design': 'container', 'name': 'Сосуд', 'value': 1}]
    #         }

    def from_dict(self, data: dict):
        # {'name': 'Самогонный аппарат - GET',
        #  'ip_address': '127.0.0.1',
        #  'wap_login': 'login', 'wap_password': 'password',
        #  'wifi_login': 'login', 'wifi_password': 'password',
        #
        #  '0_name': 'Программа 1',
        #  '0_0_modes_name': 'Режим 1', '0_0_modes_temp': '75', '0_0_modes_time': '30',
        #  '0_1_modes_name': 'Режим 2', '0_1_modes_temp': '95', '0_1_modes_time': '240',
        #  '0_2_modes_name': 'Режим 3', '0_2_modes_temp': '100', '0_2_modes_time': '30',
        #  '0_3_modes_name': 'Режим 4', '0_3_modes_temp': '30', '0_3_modes_time': '0',
        #  '0_4_modes_name': 'Режим 5', '0_4_modes_temp': '30', '0_4_modes_time': '0',
        #
        #  '0_pid_p': 1.0, '0_pid_i': 1.0, '0_pid_d': 1.0
        # }
        self.name = data['name']
        self.ip_address = data['ip_address']
        self.wap_login = data['wifi_login']
        self.wifi_password = data['wifi_password']
        self.wap_login = data['wap_login']
        self.wap_password = data['wap_password']
        for key in data.keys():
            constituents = key.split('_')
            if (len(constituents) == 2) and constituents[0].isdigit() and (constituents[1] == 'name'):
                idx = int(constituents[0])
                self.settings[idx]['name'] = data[key]
            if (len(constituents) == 4) and constituents[0].isdigit() and constituents[1].isdigit() and (constituents[2] == 'modes'):
                idx_program = int(constituents[0])
                idx_mode = int(constituents[1])
                self.settings[idx_program]['modes'][idx_mode][constituents[3]] = data[key]
            if (len(constituents) == 3) and constituents[0].isdigit() and (constituents[1] == 'pid') and (constituents[2] in ['p', 'i', 'd']):
                idx_program = int(constituents[0])
                self.settings[idx_program]['pid'][constituents[2]] = data[key]
        print('Новые настройки ', self.settings)

    def to_dict(self):
        d = {'name': self.name,
             'ip_address': self.ip_address,
             'wap_login': self.wap_login, 'wap_password': self.wap_password,
             'wifi_login': self.wifi_login, 'wifi_password': self.wifi_password,
             'settings': self.settings}
        return d


class LaunchHistory(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey('Device', blank=True, null=True, on_delete=models.SET_NULL)
    settings = models.CharField(max_length=1024)
    start_settings = models.CharField(max_length=1024, default='')
    statistics = models.CharField(max_length=100)  # путь до файла json со статистикой

    @classmethod
    def get_last_launch(cls, devise):
        # obj = cls.objects.filter(device__device_type=devise.device_type, date__lte=timezone.now()).order_by('-date')
        obj = cls.objects.filter(device__device_type=devise.device_type).order_by('-date')
        print(obj)
        if obj:
            for ob in obj:
                print(ob.statistics)
            return obj[0]
        else:
            return None

    @classmethod
    def delete_everything(cls):
        cls.objects.all().delete()

    @classmethod
    def get_all_objects(cls):
        return cls.objects.all()

    def update_statistics(self, json_data):
        with open(self.statistics, encoding='utf-8') as f:
            data_from_file = json.load(f)

        for key, item in json_data.items():
            if key in data_from_file:
                data_from_file[key]['data'].append(item)

        with open(self.statistics, 'w', encoding='utf-8') as f:
            json.dump(data_from_file, f, ensure_ascii=False)

    def file_is_empty(self):
        return os.stat(self.statistics).st_size == 0

    def set_format(self, json_format):
        if os.stat(self.statistics).st_size == 0:
            with open(self.statistics, 'w', encoding='utf-8') as f:
                # f.write(json_format)
                json.dump(json_format, f, ensure_ascii=False)

    def get_statistic(self):
        with open(self.statistics, encoding='utf-8') as f:
            return json.load(f)


