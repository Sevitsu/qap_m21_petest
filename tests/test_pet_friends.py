import logging

from api import PetFriends
from settings import valid_email, valid_password
import os
import requests
import pytest

pf = PetFriends()


@pytest.mark.positive
@pytest.mark.get
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


@pytest.mark.positive
@pytest.mark.get
def test_get_all_pets(get_key_login):
    response = requests.get(url='https://petfriends.skillfactory.ru/api/pets',
                            headers={'Cookie': get_key_login})
    assert response.status_code == 200, 'Запрос выполнен неуспешно'
    assert len(response.json().get('pets')) > 0, 'Количество питомцев не соответствует ожиданиям'


@pytest.mark.positive
@pytest.mark.get
def test_get_all_pets_with_valid_key(get_key_api, filter=''):
    status, result = pf.get_list_of_pets(get_key_api, filter)
    assert status == 200
    assert len(result['pets']) > 0


@pytest.mark.positive
@pytest.mark.post
def test_add_new_pet_simple(get_key_api, name='Kotya', animal_type='Catt', age='1'):
    status, result = pf.add_new_pet_simple(get_key_api, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


@pytest.mark.positive
@pytest.mark.post
def test_add_new_pet_with_valid_data(get_key_api, name='Kotya', animal_type='Catt', age='1', pet_photo='images/Kotya.jpeg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.add_new_pet(get_key_api, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


@pytest.mark.positive
@pytest.mark.delete
def test_successful_delete_self_pet(get_key_api):
    _, my_pets = pf.get_list_of_pets(get_key_api, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(get_key_api, "Supets", "mmm", "2", "images/kotya.jpeg")
        _, my_pets = pf.get_list_of_pets(get_key_api, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(get_key_api, pet_id)

    _, my_pets = pf.get_list_of_pets(get_key_api, "my_pets")

    assert status == 200
    assert pet_id not in my_pets.values()


@pytest.mark.positive
@pytest.mark.put
def test_successful_update_self_pet_info(get_key_api, name='Murz', animal_type='CatDog', age=3):
    _, my_pets = pf.get_list_of_pets(get_key_api, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(get_key_api, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception('Empty list of my_pets')


@pytest.mark.positive
@pytest.mark.post
def test_add_new_pet_photo(get_key_api, pet_photo='images/Kotya.jpeg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, my_pets = pf.get_list_of_pets(get_key_api, "my_pets")
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.add_pet_photo(get_key_api, pet_id, pet_photo)

        assert status == 200
        assert 'pet_photo' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_api_key_for_invalid_user(email='invalid@mmm.ru', password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_api_key_for_empty_user(email='', password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_api_key_for_invalid_pswrd(email=valid_email, password='678'):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_api_key_for_empty_pswrd(email=valid_email, password=''):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_api_key_for_incorrect_userdata(email='23', password='password'):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_all_pets_with_outdated_auth_key(filter=''):
    auth_key = {'key': 'd3c1355cc3c551acbebe5b58ead5d09897aa6ff03ce448554d40987d'}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_all_pets_with_symbols_in_auth_key(filter=''):
    auth_key = {'key': '!@#$%^&*!@#$%^&*!@#$%^&*!@#$%^&!@#$%^&*!@#$%^&*!@#$%^&*@'}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403
    assert 'Forbidden' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_all_pets_with_incorrect_filter(get_key_api, filter='pets'):
    auth_key = get_key_api
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 500
    assert 'Internal Server Error' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_my_pets_with_cyrillic_in_filter(get_key_api, filter='ьн_зуеы'):
    auth_key = get_key_api
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 500
    assert 'Internal Server Error' in result


@pytest.mark.negative
@pytest.mark.get
# Negative test below
def test_get_all_pets_with_255_characters_in_filter(get_key_api, filter='123456789123456789123456789123456789123456789123456789123456789123456789123123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789'):
    auth_key = get_key_api
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 500
    assert 'Internal Server Error' in result


@pytest.mark.negative
@pytest.mark.delete
# Negative test below
def test_unsuccessful_delete_self_pet_with_empty_pet_id(get_key_api):
    auth_key = get_key_api
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Supets", "mmm", "2", "images/kotya.jpeg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = ''
    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 404
    assert pet_id not in my_pets.values()
