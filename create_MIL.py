from monitoring.service import open_file, save_file_data

agent_scheme = open_file("agent_scheme.json")
agent_reg_reg = open_file("agent_reg_response.json")

def build_metric_tuples(agent_scheme: dict, agent_reg_reg: dict) -> list:
    """
    Возвращает список (item_id, metric_id, query_interval), построенный по шаблонам.
    """
    result = []

    # 1. Собираем словарь: metric_id - значение query_interval
    metric_intervals = {
        metric["metric_id"]: metric["query_interval"]
        for metric in agent_scheme["scheme"].get("metrics", [])
    }
    print(metric_intervals)

    # 2. Собираем словарь: template_id - список metric_id
    template_metrics = {
        template["template_id"]: template.get("metrics", [])
        for template in agent_scheme["scheme"].get("templates", [])
    }
    print(template_metrics)

    # 3. Обработка item_id_list из ответа сервера
    for item in agent_reg_reg.get("item_id_list", []):
        item_id = item.get("item_id")
        full_path = item.get("full_path")

        # Получаем последний шаблон из full_path, например: cpu_v1[0] -> cpu_v1
        template_with_index = full_path.split("/")[-1]
        template_id = template_with_index.split("[")[0]

        # Получаем метрики, связанные с шаблоном
        metrics = template_metrics.get(template_id, None)
        if metrics is None:
            print(f"Не найден шаблон {template_id}")
            return None
        for metric_id in metrics:
            query_interval = metric_intervals.get(metric_id)
            if query_interval is not None:
                result.append((item_id, metric_id, query_interval))
            else:
                print(f"Не найден interval для метрики {metric_id}")
                return None

    return result

metrics_list = build_metric_tuples(agent_scheme, agent_reg_reg)
print(metrics_list)

save_file_data("metric_interval.json", metrics_list)


xxxx = open_file("metric_interval.json")
