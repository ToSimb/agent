import random
import time
from config import (DEBUG_MODE)
from storage.sqlite_commands import (create_connection,
                                     check_db,
                                     insert_params
                                     )



def if_int(current_timestamp):
    return {"t": current_timestamp - 2, "v": str(random.randint(800, 1100))}

def if_double(current_timestamp):
    return {"t": current_timestamp - 1, "v": str(random.uniform(800, 1100))}

def if_state(current_timestamp):
    return {"t": current_timestamp, "v": "ERROR", "etmin": True, "comment": "Арбуз"}

def if_str(current_timestamp):
    return {"t": current_timestamp + 1, "v": "FAasdasTAL", "etmax": False, "etmin": True, "comment": "Test"}

def params_generator():
    params = []
    # for _ in range(random.randint(1,200)):
    for _ in range(10):
        print(time.time())
        current_timestamp = int(time.time())
        for item_id in range(1, 3):
            for metric_id in ['chassis.uptime',
                              'cpu.user.time',
                              'cpu.core.load',
                              'chassis.memory.total',
                              'chassis.memory.used',
                              'сompboard.voltage',
                              'сompboard.power',
                              'сompboard.state']:
                data = {}
                if metric_id == 'chassis.uptime':
                    data = if_double(current_timestamp)
                if metric_id == 'cpu.user.time':
                    data = if_double(current_timestamp)
                if metric_id == 'cpu.core.load':
                    data = if_double(current_timestamp)
                if metric_id == 'chassis.memory.total':
                    data = if_int(current_timestamp)
                if metric_id == 'chassis.memory.used':
                    data = if_int(current_timestamp)
                if metric_id == 'сompboard.voltage':
                    data = if_double(current_timestamp)
                if metric_id == 'сompboard.power':
                    data = if_double(current_timestamp)
                if metric_id == 'сompboard.state':
                    data = if_state(current_timestamp)
                params.append({ **{"item_id": item_id, "metric_id": metric_id}, **data })
        time.sleep(1)
    return params

if DEBUG_MODE and check_db():
    conn = create_connection()
    data = params_generator()
    insert_params(conn, data)
    conn.close()