import configparser

config = configparser.ConfigParser()

config.read('config.ini')

# settings
DEBUG_MODE = config.getboolean('settings', 'debug')
REUPLOAD_AGENT_SCHEME = config.get('settings', 'reupload_agent_scheme')
MAX_NUMBER_OF_PF = config.getint('settings', 'max_number_of_pf')

# log
LOG_LEVEL = config['log']['log_level']

# files
AGENT_SCHEME_FILE_PATH = config.get('files', 'agent_scheme_file_path')
REG_INFO_FILE_PATH = config.get('files', 'reg_info_file_path')
METRIC_INFO_FILE_PATH = config.get('files', 'metric_info_file_path')

# network
AGENT_REG_ID = config.get('network', 'agent_reg_id')
HTTP_TIMEOUT_S = config.get('network', 'http_timeout_s')
IP = config.get('network', 'ip')
PORT = config.get('network', 'port')

# storage
RETENTION_TIME_S = config.get('network', 'retention_time_s')