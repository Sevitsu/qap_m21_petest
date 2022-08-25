import requests
import pytest
import json
import datetime
import logging
from settings import valid_email, valid_password


logging.basicConfig(format="%(asctime)s - %(levelname)s - "
                           "- %(lineno)d - %(message)s",
                    level=logging.INFO,
                    filename='log.txt'
                    )


@pytest.fixture()
def get_key_login(email=valid_email, password=valid_password):
    response = requests.post(url='https://petfriends.skillfactory.ru/login',
                             data={"email": email, "pass": password})
    assert response.status_code == 200, 'Запрос выполнен неуспешно'
    assert 'Cookie' in response.request.headers, 'В запросе не передан ключ авторизации'
    return response.request.headers.get('Cookie')


@pytest.fixture()
def get_key_api(email=valid_email, password=valid_password):
    headers = {
        'email': email,
        'password': password
    }
    res = requests.get(url='https://petfriends.skillfactory.ru/api/key', headers=headers)
    status = res.status_code

    try:
        result = res.json()
    except json.decoder.JSONDecodeError:
        result = res.text
    assert status == 200
    assert 'key' in result
    return result


@pytest.fixture(autouse=True)
def time_delta():
    start_time = datetime.datetime.now()
    yield
    end_time = datetime.datetime.now()
    print(f"\nТест шел: {end_time - start_time}")


@pytest.fixture(autouse=True)
def log_tests():
    logging.info('msg')
    yield
    logging.info('msg')
