import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings_file = os.path.join(BASE_DIR, "my_settings.txt")

def check_settings():
    return os.path.exists(settings_file)

def update_settings(SV, UQIR, STAT):
    initial_settings = {
        'scheme_revision': SV,
        'user_query_interval_revision': UQIR,
        'rest_client_start': STAT
    }
    save_settings(initial_settings)

def save_settings(settings):
    with open(settings_file, 'w', encoding='utf-8') as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)

def get_file_mtime():
    try:
        timestamp = os.path.getmtime(settings_file)
        return int(timestamp)
    except FileNotFoundError:
        return -1

def get_settings():
    with open(settings_file, 'r') as file:
        content = json.load(file)
        return content['scheme_revision'], content['user_query_interval_revision'], content['rest_client_start']
