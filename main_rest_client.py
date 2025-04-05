import requests
import threading
import time
import sys
import signal
import atexit

from logger.logger_rest_client import logger_rest_client
from config import (DEBUG_MODE,
                    REUPLOAD_AGENT_SCHEME,
                    CHECK_SURVEY_PERIOD,
                    PARAMS_SURVEY_PERIOD,
                    AGENT_SCHEME_FILE_PATH,
                    REG_INFO_FILE_PATH,
                    METRIC_INFO_FILE_PATH,
                    AGENT_REG_ID,
                    HTTP_TIMEOUT_S,
                    IP,
                    PORT,
                    update_config)
from rest_client.service import (open_file,
                                 save_file,
                                 collecting_params,
                                 filter_for_mil)
from storage.sqlite_commands import (create_connection,
                                     check_db,
                                     create_table,
                                     clear_table,
                                     delete_params)
from storage.settings_handler import (check_settings,
                                      update_settings,
                                      get_settings)

# _________________________
SERVER_URL = f"http://{IP}:{PORT}"
if DEBUG_MODE:
    SERVER_URL = "http://127.0.0.1:8080/at"

AGENT_ID = -1
USER_QUERY_INTERVAL_REVISION = 0

if not check_db():
    if create_table():
        logger_rest_client.info("Таблица в БД создана")
    else:
        logger_rest_client.error("Ошибка создания таблицы в БД")

CONN = create_connection()
if CONN is None:
    logger_rest_client.error("Ошибка подключения к БД")
    sys.exit(1)
logger_rest_client.info("Подключено к БД")

if not check_settings():
    logger_rest_client.info("Созданы начальные настройки")
    update_settings(AGENT_ID, USER_QUERY_INTERVAL_REVISION, True)

def signal_handler(sig, frame):
    cleanup_and_exit()

def cleanup_and_exit():
    try:
        update_settings(AGENT_ID, USER_QUERY_INTERVAL_REVISION, False)
    except Exception as e:
        logger_rest_client.warning(f"Не удалось обновить настройки при завершении: {e}")

    if CONN:
        CONN.close()
    logger_rest_client.info("Выход из системы (через atexit или interrupt)")
    sys.exit(0)

# возможно для виндовс придется переделать через ctypes !!!!
# либо переписать завершение программы через глобальный флаг, а не через поток-демон !!
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_and_exit)


def registration_agent(agent_data, agent_reg_response):
    params = {}
    if agent_reg_response is None:
        params['agent_reg_id'] = AGENT_REG_ID
        logger_rest_client.info(f"Регистрация агента {AGENT_REG_ID}")
    else:
        params['agent_id'] = agent_reg_response["agent_id"]
        logger_rest_client.info(f"Перерегистрация агента {agent_reg_response['agent_id']}")
    while True:
        try:
            response = requests.post(f"{SERVER_URL}/agent-scheme", json=agent_data, params=params, timeout=60)
            if response.status_code == 200:
                logger_rest_client.info(f"Регистрация/перерегистрация успешна")
                return response.json()
            elif response.status_code in [404, 422, 427, 428, 429]:
                logger_rest_client.error(f"Ошибка регистрации: {response.status_code} - {response.text}")
                logger_rest_client.error("Остановка приложения из-за ошибки.")
                sys.exit(1)
            elif response.status_code == 527:
                logger_rest_client.info("Сервер занят. Повтор через 10 секунд.")
                time.sleep(10)
            elif response.status_code == 528:
                logger_rest_client.error("Ошибка сервера. Повтор через 60 секунд.")
                time.sleep(60)
            else:
                logger_rest_client.error(f"Ошибка регистрации: {response.status_code} - {response.text}")
                sys.exit(1)
        except requests.exceptions.Timeout:
            logger_rest_client.error("Сервер недоступен. Таймаут при выполнении запроса.")
            time.sleep(60)
        except requests.exceptions.ConnectionError:
            logger_rest_client.info("Сервер недоступен. Повтор через 60 секунд.")
            time.sleep(60)
        except Exception as e:
            logger_rest_client.error(f"Ошибка: {e}")
            sys.exit(1)

def check_server():
    while True:
        try:
            global AGENT_ID
            global USER_QUERY_INTERVAL_REVISION
            if AGENT_ID > -1:
                params = {
                    'agent_id': AGENT_ID,
                    'user_query_interval_revision': USER_QUERY_INTERVAL_REVISION
                }
                response = requests.get(SERVER_URL + "/check", params=params, timeout=HTTP_TIMEOUT_S)
                if response.status_code == 200:
                    logger_rest_client.info(f"CHECK: {response.status_code}")
                elif response.status_code == 227:
                    # вызов функции изменения периода опроса !!!!
                    logger_rest_client.info(f"CHECK: {response.status_code}")
                    if227_server()
                else:
                    logger_rest_client.warning(f"CHECK: {response.status_code}")
        except requests.exceptions.Timeout:
            logger_rest_client.error("CHECK ERROR: Таймаут при выполнении запроса.")
        # подумать - надо ли вообще делать это исключение!
        except requests.exceptions.ConnectionError:
            logger_rest_client.error("CHECK ERROR: Сервер недоступен — ошибка подключения.")
        except Exception as e:
            logger_rest_client.error(f"CHECK ERROR: {e}")
        time.sleep(CHECK_SURVEY_PERIOD)

def post_params_server(AGENT_ID, result):
    while True:
        try:
            params = {
                'agent_id': AGENT_ID,
            }
            response = requests.post(SERVER_URL + "/params", params=params, json=result, timeout=HTTP_TIMEOUT_S)
            if response.status_code == 200:
                logger_rest_client.info(f"PARAMS: {response.status_code}")
                return True
            elif response.status_code == 227:
                # вызов функции изменения периода опроса !!!!
                logger_rest_client.info(f"PARAMS: {response.status_code}")
                if227_server()
                return True
            elif response.status_code in [404, 527]:
                logger_rest_client.info(f"PARAMS: {response.status_code}. Повтор через {PARAMS_SURVEY_PERIOD} сек.")
            elif response.status_code in [427, 528]:
                logger_rest_client.error(f"PARAMS: {response.status_code} - {response.text}.")
                raise
            else:
                logger_rest_client.warning(f"PARAMS: {response.status_code} - {response.text}")
                raise
        except requests.exceptions.Timeout:
            logger_rest_client.error("PARAMS ERROR: Таймаут при выполнении запроса.")
            return False
        # подумать - надо ли вообще делать это исключение!
        except requests.exceptions.ConnectionError:
            logger_rest_client.error("PARAMS ERROR: Сервер недоступен — ошибка подключения.")
            return False
        except Exception as e:
            logger_rest_client.error(f"PARAMS ERROR: {e}")
            raise

def if227_server():
    try:
        global USER_QUERY_INTERVAL_REVISION
        global AGENT_ID
        params = {
            'agent_id': AGENT_ID,
        }
        response = requests.get(SERVER_URL + "/metric-info-list", params=params, timeout=HTTP_TIMEOUT_S)
        if response.status_code == 200:
            result = response.json()
            mil_227 = filter_for_mil("agent_reg_response.json", result)
            save_file(mil_227, METRIC_INFO_FILE_PATH)
            USER_QUERY_INTERVAL_REVISION = result["user_query_interval_revision"]
            update_settings(AGENT_ID, USER_QUERY_INTERVAL_REVISION, True)
    except Exception as e:
        logger_rest_client.error(f"227 ERROR: {e}")
    return False

try:
    # инициализация
    if DEBUG_MODE:
        AGENT_SCHEME_FILE_PATH = 'create_scheme/agent_scheme.json'
    agent_scheme = open_file(AGENT_SCHEME_FILE_PATH)
    if agent_scheme is None:
        logger_rest_client.error("Файл схемы агента не найден. Завершение.")
        sys.exit(0)
    _, USER_QUERY_INTERVAL_REVISION, _ = get_settings()
    if agent_scheme is None:
        sys.exit(0)

    ## написать функцию проверки корректности схемы агента !! (приориетет: низкий)
    agent_reg_response = open_file(REG_INFO_FILE_PATH)

    # регистрация/перерегистрация
    if (agent_reg_response is None) or REUPLOAD_AGENT_SCHEME:
        print("регистрация/перерегистрация")
        agent_reg_response = registration_agent(agent_scheme, agent_reg_response)
        save_file(agent_reg_response, REG_INFO_FILE_PATH)
        update_config()
        if clear_table():
            logger_rest_client.info("Таблица очищена после регистрации/перерегистрации")
        else:
            logger_rest_client.error("Ошибка при очистке таблицы после регистрации/перерегистрации")
            sys.exit(1)

    AGENT_ID = agent_reg_response["agent_id"]

    update_settings(agent_scheme["scheme_revision"], USER_QUERY_INTERVAL_REVISION, True)

    # создания потока который будет производить чек сервера
    check_thread = threading.Thread(target=check_server)
    check_thread.daemon = True
    check_thread.start()

    # основной цикл передачи ПФ
    while True:
        ids_list, value = collecting_params(CONN)
        if len(value) > 0:
            result = {
                "scheme_revision": agent_scheme["scheme_revision"],
                "user_query_interval_revision": USER_QUERY_INTERVAL_REVISION,
                "value": value
            }
            if post_params_server(AGENT_ID, result):
                count_delete = delete_params(CONN, ids_list)
                logger_rest_client.info(f"DB: Удаленно {count_delete} отправленных данных")
        else:
            logger_rest_client.info("Нет данных в БД")
        time.sleep(PARAMS_SURVEY_PERIOD)

except Exception as e:
    logger_rest_client.error(e)
    try:
        update_settings(AGENT_ID, USER_QUERY_INTERVAL_REVISION, False)
    except Exception as e:
        logger_rest_client.warning(f"Не удалось обновить настройки при завершении: {e}")

finally:
    if CONN is not None:
        CONN.close()
    try:
        update_settings(AGENT_ID, USER_QUERY_INTERVAL_REVISION, False)
    except Exception as e:
        logger_rest_client.warning(f"Не удалось обновить настройки при завершении: {e}")
    logger_rest_client.info("Выход из системы")
    sys.exit(1)
