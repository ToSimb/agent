import json

def save_json_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)


def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None

def filter_metrics_by_templates(templates_data, metrics_data):
    template_metrics = set()
    if templates_data and "templates" in templates_data:
        for template in templates_data["templates"]:
            if "metrics" in template:
                template_metrics.update(template["metrics"])

    metrics_dict = {metric["metric_id"]: metric for metric in metrics_data["metrics"]} if metrics_data else {}

    filtered_metrics = []
    missing_metrics = []

    for metric_id in template_metrics:
        if metric_id in metrics_dict:
            filtered_metrics.append(metrics_dict[metric_id])
        else:
            missing_metrics.append(metric_id)

    if missing_metrics:
        raise ValueError(f"Отсутствуют метрики в файле metrics: {', '.join(missing_metrics)}")

    filtered_metrics.sort(key=lambda x: x["metric_id"])

    return filtered_metrics

def build_template_dict(templates):
    """Создает словарь шаблонов по template_id."""
    return {template["template_id"]: template for template in templates}

def collect_items(template_dict, template_id, path_prefix):
    """Рекурсивно строит item_id_list начиная с template_id и текущего path_prefix."""
    result = [{
        "full_path": path_prefix,
        "item_id": None
    }]

    template = template_dict.get(template_id)
    if not template:
        return result

    includes = template.get("includes", [])
    for include in includes:
        included_id = include["template_id"]
        count = include.get("count", 1)

        for i in range(count):
            child_path = f"{path_prefix}/{included_id}[{i}]"
            result.extend(collect_items(template_dict, included_id, child_path))

    return result

def find_root_templates(templates_data):
    if not templates_data or "templates" not in templates_data:
        return []

    all_templates = set()
    included_templates = set()

    for tmpl in templates_data["templates"]:
        tmpl_id = tmpl.get("template_id")
        if tmpl_id:
            all_templates.add(tmpl_id)

        for include in tmpl.get("includes", []):
            included_templates.add(include["template_id"])

    # Корни — это те, кто есть, но не включён никуда
    root_templates = all_templates - included_templates
    return sorted(root_templates)

def main():
    try:
        templates_path = 'templates.json'
        metrics_path = 'metrics.json'

        templates_data = load_json_file(templates_path)
        metrics_data = load_json_file(metrics_path)

        filtered_metrics = []
        filtered_metrics = filter_metrics_by_templates(templates_data, metrics_data)
        template_dict = build_template_dict(templates_data["templates"])

        root_ids = find_root_templates(templates_data)
        item_id_list = []

        for root_id in root_ids:
            path = f"{root_id}[0]"
            item_id_list.extend(collect_items(template_dict, root_id, path))

        agent_scheme = {
            "scheme_revision": 1,
            "scheme": {
                "metrics": filtered_metrics,
                "templates": templates_data.get("templates", []),
                "item_id_list": item_id_list,
                "join_id_list": [],
                "item_info_list": []
            }
        }

        save_json_file("agent_scheme.json", agent_scheme)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
