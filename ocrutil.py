import base64
import json
import os

import requests

filename = 'data/key.json'

if os.path.exists(filename):
    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        app_id = data['App_ID']
        api_key = data['API_Key']
        secret_key = data['Secret_Key']
else:
    print('Baidu-Aip读取失败')


def get_file_content(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()


def __get_access_token():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=' \
           'client_credentials&client_id={}&client_secret={}'\
        .format(api_key, secret_key)
    response = requests.get(host)
    if response:
        return response.json()['access_token']


def get_license_plate_number() -> str:
    request_url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/license_plate'
    image = base64.b64encode(get_file_content('img/test.jpg'))
    params = {'image': image}
    access_token = __get_access_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        json = response.json()
        if 'words_result' in json:
            return json["words_result"]["number"]
        else:
            print(json['error_msg'])
            return ""
