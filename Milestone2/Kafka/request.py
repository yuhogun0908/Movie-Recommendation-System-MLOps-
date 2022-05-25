import requests
from time import sleep

def http_request(name, info_type):    
    """
    name(str) : user / movie
    info_type(str) : specific information
    """

    response = requests.get('http://128.2.204.215:8080/{}/{}'.format(name, info_type), timeout=None)
    return response.json()


if __name__ == "__main__":
    http_request('user','889871')