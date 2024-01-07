import os
import uuid

from api import PetFriends
from settings import valid_email, valid_password
from settings import failed_email, failed_password


pf = PetFriends()


def test_get_api_key_for_failed_user():
    status, result = pf.get_api_key(failed_email, failed_password)
    assert status == 403


def test_creat_pet_simple_with_valid_data(name="Коппер", animal_type="Бладхаунд", age="4"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    assert result["name"] == name


def test_get_my_pets_with_valid_key(filter_="my_pets"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, my_pets = pf.get_list_of_pets(auth_key, filter_)

    assert status == 200
    assert len(my_pets["pets"]) > 0


def test_get_my_all_pets_with_valid_key(filter_="my_all_pets"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter_)

    assert status == 500


def add_photo_of_pet(pet_photo: str):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets["pets"]) == 0:
        pf.create_pet_simple(auth_key, "Коппер", "Бладхаунд", "4")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    _pet = [pet for pet in my_pets["pets"] if pet["name"] == "Коппер"][0]
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.add_photo_of_pet(auth_key, _pet["id"], pet_photo)
    return status


def test_add_photo_of_pet_with_valid_data(pet_photo="images/copper.jpg"):
    try:
        status = add_photo_of_pet(pet_photo)
        assert status == 200
    except IndexError:
        raise Exception("Not found copper.")


def test_add_photo_png_of_pet_with_valid_data(pet_photo="images/copper.png"):
    try:
        status = add_photo_of_pet(pet_photo)
        assert status == 500
    except IndexError:
        raise Exception("Not found copper.")


def test_delete_non_existent_pet_with_valid_data():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets["pets"]) == 0:
        pf.create_pet_simple(auth_key, "Коппер", "Бладхаунд", "4")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = str(uuid.uuid4())
    assert pet_id not in [my_pet["id"] for my_pet in my_pets["pets"]]

    status, _ = pf.delete_pet(auth_key, pet_id)
    assert status == 200


def test_successful_update_not_existent_pet_info_w(name="Коппер", animal_type="Бладхаунд", age=4):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = str(uuid.uuid4())
    assert pet_id not in [my_pet["id"] for my_pet in my_pets["pets"]]

    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)
    assert status == 400


def test_add_new_pet_png_photo_with_valid_data(name="Коппер", animal_type="Бладхаунд", age="4", pet_photo="images/copper.png"):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result["name"] == name
    assert result["pet_photo"] == ""


def test_delete_all_my_pet_with_valid_data():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.get_list_of_pets(auth_key, "my_pets")

    for pet in result["pets"]:
        pf.delete_pet(auth_key, pet["id"])

    status, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert len(my_pets["pets"]) == 0
