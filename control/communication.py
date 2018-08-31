import requests
from requests.compat import urljoin


def send_get(ip_address: str, relative_url: str, protocol: str = 'http://'):
    if '://' in protocol:
        url = urljoin(protocol + ip_address, relative_url)
    else:
        url = urljoin(protocol + '://' + ip_address, relative_url)
    response = requests.get(url)
    return response


def send_post(ip_address: str, relative_url: str, data=None, json=None, protocol: str = 'http://'):
    if '://' in protocol:
        url = urljoin(protocol + ip_address, relative_url)
    else:
        url = urljoin(protocol + '://' + ip_address, relative_url)
    response = requests.post(url, data=data, json=json)
    return response
