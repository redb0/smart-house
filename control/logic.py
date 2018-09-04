from typing import Tuple, Union

from control.forms import generate_am_form_class
from control.models import Device, devices_list, AlcoholMachine
from control.validators import control_field_is_valid


def init_device(data: dict) -> Tuple[Union[Device, None], str]:
    if not data:
        return None, "Нет данных"
    if not control_field_is_valid(data['control_protocol']['params']):
        return None, "Поля формы управления переданы некорректно"
    if data['type'] == "AM":
        device = AlcoholMachine.create(data['name'], data['type'], data['ip_address'],
                                       data['wifi_login'], data['wifi_password'],
                                       data['wap_login'], data['wap_password'],
                                       data['settings'], data['return_values'], data['control_protocol'])
        # device.settings = data['settings']
        # device.return_values = data['return_values']
        device.form_settings = generate_am_form_class(data)
        device.save()

    devices_list.add(device)

    return device, ""


def generate_form(device: Device):
    if device.device_type == "AM":
        pass



