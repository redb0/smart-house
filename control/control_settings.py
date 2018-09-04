# 'button-delete' - пока не описал стили, она присутвтсвует всегда на странице ее не нужно указывать в списке полей
FIELD_TYPES = ['select', 'button']
RESERVED_BUTTONS = ['button-start', 'button-pause', 'button-stop', 'button-delete']

KEYS = {
    'common': ['title', 'id', 'type'],
    'button': ['url', 'is_active'],
    'other': ['field', 'options']
}

# TODO: Написать валидатор списка полей, чтобы зарезервированных кнопок было только по 1 штуке
