from cryptography.fernet import Fernet

from db_service.app.config import HASHING_SECRET_KEY


def merge_dicts(*dicts):
    merged_dict = {}
    for dictionary in dicts:
        if dictionary:
            merged_dict.update(dictionary)
    return merged_dict


def encrypt_password(password, key=HASHING_SECRET_KEY):
    f = Fernet(key)
    encrypted_value = f.encrypt(password.encode('utf-8')).decode('utf-8')
    return encrypted_value


def decrypt_password(password, key=HASHING_SECRET_KEY):
    f = Fernet(key)
    decrypted_value = f.decrypt(password).decode('utf-8')
    return decrypted_value


def draw_linaege_from_json(json_data, model_name):
    markdown = ''
    markdown = find_children(json_data, model_name, markdown)
    markdown = find_parents(json_data, model_name, markdown)
    if not markdown:
        markdown = f"{model_name};"
    return markdown


def find_children(json_data, model, markdown, exclude=None):
    if json_data.get(model):
        if children := json_data.get(model).get('children'):
            for child in children:
                markdown += f'{model} --> {child};'
                if children := json_data.get(child).get('children'):
                    for child in children:
                        find_children(json_data, child, markdown, model)
                        find_parents(json_data, child, markdown, model)

    return markdown


def find_parents(json_data, model, markdown, exclude=None):
    if json_data.get(model):
        if parents := json_data.get(model).get('parents'):
            for parent in parents:
                markdown += f'{parent} --> {model};'
                if json_data.get(parent):
                    if parents := json_data.get(parent).get('parents'):
                        for parent in parents:
                            find_parents(json_data, parent, markdown, model)
                            find_children(json_data, parent, markdown, model)

    return markdown


def cast_value(value, type):
    new_value = None
    if type == 'integer':
        new_value = int(value)
    if type == 'string':
        new_value = str(value)

    return new_value


def construct_profile_dict(profile_model):
    return {
        "id": profile_model.id,
        "username": profile_model.username,
        "email": profile_model.email,
        "first_name": profile_model.first_name,
        "last_name": profile_model.last_name
    }



def is_all_lower_case(input_str):
    return input_str.islower()
