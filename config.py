import configparser

config = configparser.ConfigParser()

config.read('config.ini')

# settings
DEBUG_MODE = config.getboolean('settings', 'debug')
REUPLOAD_AGENT_SCHEME = config.getboolean('settings', 'reupload_agent_scheme')
MAX_NUMBER_OF_PF = config.getint('settings', 'max_number_of_pf')
CHECK_SURVEY_PERIOD = config.getint('settings', 'check_survey_period')
PARAMS_SURVEY_PERIOD = config.getint('settings', 'params_survey_period')

# files
AGENT_SCHEME_FILE_PATH = config.get('files', 'agent_scheme_file_path')
REG_INFO_FILE_PATH = config.get('files', 'reg_info_file_path')
METRIC_INFO_FILE_PATH = config.get('files', 'metric_info_file_path')

# network
AGENT_REG_ID = config.get('network', 'agent_reg_id')
HTTP_TIMEOUT_S = config.getint('network', 'http_timeout_s')
IP = config.get('network', 'ip')
PORT = config.get('network', 'port')

# storage
RETENTION_TIME_S = config.getint('storage', 'retention_time_s')

# freon
URL_FA = config.get('freon', 'url_fa')
URL_FB = config.get('freon', 'url_fb')

def update_config():
    config['settings']['reupload_agent_scheme'] = 'false'
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print('config.ini updated')