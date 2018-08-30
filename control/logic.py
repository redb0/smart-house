from control.forms import generate_am_form_class
from control.models import Device, devices_list, AlcoholMachine


def init_device(data: dict) -> Device:
    # device = Device(data['name'], data['type'], data['ip_address'],
    #                 Net(data['wifi_login'], data['wifi_password']),
    #                 Net(data['wap_login'], data['wap_password']))
    # device.settings = data['settings']
    # device.return_values = data['return_values']
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

    return device


def generate_form(device: Device):
    if device.device_type == "AM":
        pass



