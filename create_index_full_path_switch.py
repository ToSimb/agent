import json
import re
from pathlib import Path

SCHEMA_PATH = Path("agent_scheme.json")      # где лежит файл со схемой
SRC_DIR     = Path("_settings_file/raw")     # папка с «пустыми» файлами
DST_DIR     = Path("_settings_file/proc")     # куда сохранять результат
# ──────────────────────────────────────────────────────────────────────────────

SPECIAL_MAPPING = {
    "connection": "device_connection[0]",
    "agent":      "agent_connection[0]",
}

ROOT_RE = re.compile(r"^(?P<base>[^\[]+)\[(?P<idx>\d+)]$")
FILE_RE = re.compile(r"^(?P<base>.+?)_(?P<idx>\d+)\.txt$", re.I)
KEY_RE  = re.compile(r"^switch:(?P<idx>\d+):(?P<tag>.+)$")


def load_schema(schema_path: Path):
    """Строим словарь (base, idx) → root_path."""
    with schema_path.open(encoding="utf-8-sig") as f:
        raw = json.load(f)
    items = raw["scheme"]["item_id_list"] if isinstance(raw, dict) else raw
    roots = {}

    for it in items:
        fp = it["full_path"]
        root = fp.split("/")[0]
        m = ROOT_RE.match(root)
        if not m:
            continue
        base, idx = m.group("base"), int(m.group("idx"))
        roots[(base, idx)] = root
    return roots


def fill_one_file(src: Path, dst: Path, roots):
    m_file = FILE_RE.match(src.name)
    if not m_file:
        raise RuntimeError(f"Имя файла '{src.name}' не соответствует шаблону <base>_<idx>.json")
    base, idx = m_file.group("base"), int(m_file.group("idx"))

    root_path = roots.get((base, idx))
    if root_path is None:
        raise RuntimeError(f"В схеме нет элемента '{base}[{idx}]' — проверьте файл {src}")

    with src.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    for k in list(data.keys()):
        m_key = KEY_RE.match(k)
        if not m_key:
            raise RuntimeError(f"Ключ '{k}' не распознан (файл {src})")
        tag = m_key.group("tag")

        if tag.isdigit():
            data[k] = f"{root_path}/if_switch[{int(tag)}]"
        else:
            tail = SPECIAL_MAPPING.get(tag)
            if tail is None:
                raise RuntimeError(f"Неизвестный тэг '{tag}' в файле {src} — добавьте в SPECIAL_MAPPING")
            data[k] = f"{root_path}/{tail}"

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8-sig") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    roots = load_schema(SCHEMA_PATH)

    for src_file in SRC_DIR.glob("*.txt"):
        dst_file = DST_DIR / src_file.name
        try:
            fill_one_file(src_file, dst_file, roots)
            print(f"[OK]   {src_file.name}")
        except Exception as exc:
            print(f"[FAIL] {src_file.name}: {exc}")

    print("\nГотово.")


if __name__ == "__main__":
    main()
