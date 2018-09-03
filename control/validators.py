from typing import List

from .models import devices_list
from .control_settings import FIELD_TYPES, RESERVED_BUTTONS, KEYS


def device_id_is_correct(device_id: int) -> bool:
    if 0 <= device_id < len(devices_list.devices):
        return True
    return False


def control_field_is_valid(fields_list: List[dict]) -> bool:
    for field in fields_list:
        if not availability_keys(field, KEYS['common']):
            return False
        if (field['type'] in FIELD_TYPES) or (field['type'] in RESERVED_BUTTONS):
            if (field['type'] == 'button') or (field['type'] in RESERVED_BUTTONS):
                if not availability_keys(field, KEYS['button']):
                    return False
            else:
                if not availability_keys(field, KEYS['other']):
                    return False
        else:
            return False
    return True


def availability_keys(verifiable_dict, keys_list):
    set_keys = set(keys_list)
    set_keys_dict = set(verifiable_dict.keys())
    if set_keys.issubset(set_keys_dict) or set_keys_dict.issubset(set_keys):
        return True
    return False


