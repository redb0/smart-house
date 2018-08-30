import json
from collections import namedtuple


class ToDict:
    def to_dict(self):
        d = {}
        datas = dict((key, self.__dict__[key]) for key in self.__dict__.keys() if not key.startswith('_'))

        for data in datas:
            if isinstance(datas[data], tuple):
                d[data] = (reqursive_to_json_1(datas[data]))
            elif isinstance(datas[data], list):
                if data not in d:
                    d[data] = []
                for item in datas[data]:
                    d[data].append(reqursive_to_json_1(item))
            elif hasattr(data, '__dict__'):
                d[data] = (reqursive_to_json_1(datas[data]))
            else:
                d[data] = (datas[data])
        return d


class AlcoholMachineSettings(ToDict):
    def __init__(self, settings):
        self._Mode = namedtuple('Mode', ['name', 'temp', 'time'])
        self._Pid = namedtuple('Pid', ['p', 'i', 'd'])

        self.program_name = ''
        self.modes = []
        self.pid = None

        self.program_name = settings['name']

        for mode in settings['modes']:
            self.modes.append(self._Mode(**mode))

        self.pid = self._Pid(**settings['pid'])


def reqursive_to_json_1(obj):
    d = {}
    if isinstance(obj, tuple):
        datas = obj._asdict()
        for data in datas:
            if isinstance(datas[data], tuple):
                d[data] = (reqursive_to_json_1(datas[data]))  # , key=key
            elif isinstance(datas[data], list):
                if data not in d:
                    d[data] = []
                for item in datas[data]:
                    d[data].append(reqursive_to_json_1(item))  # , key=key
            elif hasattr(data, '__dict__'):
                d[data] = (reqursive_to_json_1(datas[data]))  # , key=key
            else:
                d[data] = (datas[data])
    elif hasattr(obj, '__dict__'):
        datas = obj.__dict__
        for data in datas:
            if isinstance(datas[data], tuple):
                d[data] = (reqursive_to_json_1(datas[data]))  # , key=key
            elif isinstance(datas[data], list):
                if data not in d:
                    d[data] = []
                for item in datas[data]:
                    d[data].append(reqursive_to_json_1(item))  # , key=key
            elif hasattr(data, '__dict__'):
                d[data] = (reqursive_to_json_1(datas[data]))  # , key=key
            else:
                d[data] = (datas[data])

    return d  # dict(d) json.dumps(d)


Mode = namedtuple('Mode', ['name', 'temp', 'time'])


class A:
    def __init__(self):
        self.name = 'name'
        self.modes = []
        for i in range(5):
            self.modes.append(Mode('name_' + str(i), i, i + 5))
        Pid = namedtuple('Pid', ['p', 'i', 'd'])
        self.pid = Pid(1, 2, 3)


def main():
    # a = A()
    # d = reqursive_to_json_1(a)
    # print(a.__dict__)
    # print(d)
    # print(json.dumps(d))

    settings = {'name': 'Программа 1',
                'modes': [{'name': 'Режим 1', 'temp': 75, 'time': 30},
                          {'name': 'Режим 2', 'temp': 95, 'time': 240},
                          {'name': 'Режим 3', 'temp': 100, 'time': 30},
                          {'name': 'Режим 4', 'temp': 30, 'time': 0},
                          {'name': 'Режим 5', 'temp': 30, 'time': 0}],
                'pid': {'p': 1, 'i': 1, 'd': 1}}

    a = AlcoholMachineSettings(settings)
    print(a.__dict__)
    print(a.to_dict())
    print(json.dumps(a.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
