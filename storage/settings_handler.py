import json
import os

settings_file = "storage/my_settings.db"

def check_settings():
    return os.path.exists(settings_file)

def create_settings():
    initial_settings = {
        'scheme_revision': 0,
        'user_query_interval_revision': 0,
    }
    save_settings(initial_settings)

def save_settings(settings):
    with open(settings_file, 'w', encoding='utf-8') as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)

def get_settings():
    with open(settings_file, 'r') as file:
        content = json.load(file)
        return content['scheme_revision'], content['user_query_interval_revision']
