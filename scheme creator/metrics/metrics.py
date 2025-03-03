def get_cpu_metrics():
    cpu_metrics = [
            {
                "dimension": "none",
                "metric_id": "cpu.core.countlogical",
                "name": "Общее количество логических ядер центральных процессоров в системе",
                "comment": "Общее количество логических ядер центральных процессоров в системе",
                "query_interval": 500,
                "type": "integer"
            },
            {
                "dimension": "none",
                "metric_id": "cpu.core.physicalcount",
                "name": "Общее количество физических ядер центральных процессоров в системе",
                "comment": "Общее количество физических ядер центральных процессоров в системе",
                "query_interval": 500,
                "type": "integer"
            },
			{
				"dimension": "%",
				"metric_id": "cpu.core.load",
				"name": "Загрузка логического процессора",
				"query_interval": 10,
				"type": "double"
			},
            {
                "dimension": "none",
                "metric_id": "cpu.intercount",
                "name": "Количество прерываний в системе",
                "query_interval": 10,
                "type": "integer"
            },
            {
                "dimension": "%",
                "metric_id": "cpu.user.time",
                "name": "% времени польз. операций",
                "comment": "% времени, кот. ЦП тратит на пользоват.",
                "query_interval": 10,
                "type": "double"
            },
            {
                "dimension": "%",
                "metric_id": "cpu.system.time",
                "name": "% времени прог. прерываний",
                "comment": "% времени, кот. ЦП тратит на систему",
                "query_interval": 10,
                "type": "double"
            },
            {
                "dimension": "%",
                "metric_id": "cpu.hardinter.time",
                "name": "% времени аппар. прерываний",
                "comment": "% времени, кот. ЦП тратит на аппар. прерывания",
                "query_interval": 10,
                "type": "double"
            },
            {
                "dimension": "%",
                "metric_id": "cpu.softinter.time",
                "name": "% времени программ. прерываний",
                "comment": "% времени, кот. ЦП тратит на программ. прерывания",
                "query_interval": 10,
                "type": "double"
            },

            {
                "dimension": "%",
                "metric_id": "cpu.idle.time",
                "name": "% времени простоя",
                "comment": "% времени, кот. ЦП простаивает",
                "query_interval": 10,
                "type": "double"
            },
            {
                "dimension": "%",
                "metric_id": "cpu.io.time",
                "name": "% времени операций ввода/вывода",
                "comment": "% времени, кот. ЦП тратит на ввод/вывод",
                "query_interval": 10,
                "type": "double"
            }
        ]
    return cpu_metrics

def get_disk_metrics():
    disk_metrics = [
            {
                "dimension": "none",
                "metric_id": "cpu..core.count",
                "name": "Общее количество логических ядер центральных процессоров в системе",
                "comment": "Общее количество логических ядер центральных процессоров в системе",
                "query_interval": 500,
                "type": "integer"
            }
        ]
    return disk_metrics