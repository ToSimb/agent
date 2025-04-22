import json
import os
from typing import Dict, Optional, Iterable

from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd,
    bulkCmd,
)
from monitoring.base import BaseObject, SubObject
from logger.logger_monitoring import logger_monitoring

class Switch(BaseObject):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip

        self.connection_value: Optional[str] = "FATAL"
        self.interfaces: Dict[str, "Interface"] = {}
        self.interfaces_info: Dict[str, str] = {}
        self.item_index: Dict[str, "Interface"] = {}
        self.connection_id: int = -1

        self._oids_map: Dict[str, str] = {}
        self._index_interface: Dict[str, str] = {}
        self._model: str = ""
        self._system_id: str = ""

        self._engine = SnmpEngine()
        self._target = None
        self._community = "public"
        self._load_config()
        self._refresh_state(first_run=True)

    def update(self) -> None:
        self._refresh_state()

    def get_objects_description(self):
        return self.interfaces_info

    def create_index(self, switch_dict):
        for index, idx_val in switch_dict.items():
            if idx_val is None:
                logger_monitoring.debug(f"Для индекса {index} нет значения")
                continue

            if "connection" in index:
                self.connection_id = idx_val
                continue

            for key, value in self.interfaces_info.items():
                if value == index:
                    self.item_index[str(idx_val)] = self.interfaces[key]
                    break

        logger_monitoring.info("Индексы для коммутаторов обновлены")

    def get_all(self):
        return [{i: iface.get_params_all()} for i, iface in self.interfaces.items()]

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            if item_id == str(self.connection_id) and metric_id == "connection.state":
                return self.connection_value
            return self.item_index[item_id].get_metric(metric_id)
        except Exception as err:
            logger_monitoring.error(f"Ошибка при вызове item_id - {item_id}:{metric_id} — {err}")
            return None

    def _load_config(self):
        cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "switches.json")
        try:
            with open(cfg_path, encoding="utf‑8‑sig") as fp:
                data = json.load(fp)
        except FileNotFoundError:
            logger_monitoring.error(f"Файл конфигурации не найден: {cfg_path}. Коммутатор: {self.ip}")
            return
        except json.JSONDecodeError as e:
            logger_monitoring.error(f"Ошибка JSON в {cfg_path}: {e}. Коммутатор: {self.ip}")
            return

        cfg = next((d for d in data.get("switches", []) if d.get("ip") == self.ip), {})
        if not cfg:
            logger_monitoring.error(f"Коммутатор {self.ip} отсутствует в конфигурации")
            return

        self._model = cfg.get("model", "")
        iface_cnt = cfg.get("port_count", 0)
        self._oids_map = cfg.get("OIDs", {})
        self._community = cfg.get("community", "public")
        self._system_id = cfg.get("scheme_number", "")
        snmp_port = cfg.get("snmp_port", 161)
        self._target = UdpTransportTarget((self.ip, snmp_port), timeout=1, retries=1)

        if len(self._oids_map) != 6:
            logger_monitoring.debug(f"В конфигурации {self.ip}: OID‑ов {len(self._oids_map)}, а не 6")

        for idx in range(iface_cnt):
            self.interfaces[str(idx)] = Interface()
            self.interfaces_info[str(idx)] = f"switch:{self._system_id}:{idx}"
        self.interfaces_info["connection"] = "switch:0:connection"
        logger_monitoring.info(f"Порядковый номер коммутатора в системе {self._system_id}")

    def _snmp_get(self, oid: str):
        """Безопасный однократный GET."""
        try:
            error_ind, error_stat, _, var_binds = next(
                getCmd(
                    self._engine,
                    CommunityData(self._community, mpModel=1),
                    self._target,
                    ContextData(),
                    ObjectType(ObjectIdentity(oid)),
                )
            )
            if error_ind or error_stat:
                raise RuntimeError(error_ind or error_stat.prettyPrint())
            return var_binds[0][1]
        except Exception as e:
            return None

    def _snmp_bulk(self, oid: str, max_reps=25) -> Iterable:
        """
        GETBULK‑обход под‑дерева. На ошибке даёт пустой результат.
        """
        try:
            for err_ind, err_stat, _, var_binds in bulkCmd(
                self._engine,
                CommunityData(self._community, mpModel=1),
                self._target,
                ContextData(),
                0,
                max_reps,
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
            ):
                if err_ind or err_stat:
                    raise RuntimeError(err_ind or err_stat.prettyPrint())
                yield from var_binds
        except Exception:
            return

    def _refresh_state(self, *, first_run=False):

        if self._snmp_get("1.3.6.1.2.1.1.3.0") is not None:
            self.connection_value = "OK"
        else:
            self.connection_value = "FATAL"
        if self.connection_value == "FATAL":
            for iface in self.interfaces.values():
                iface.reset()
            return

        if (first_run or not self._index_interface) and self.connection_value == "OK":
            self._index_interface = self._discover_indices()

        aggregated: Dict[str, Dict[str, str]] = {}
        for base_oid, metric in self._oids_map.items():
            for oid, val in self._snmp_bulk(base_oid):
                idx_snmp = str(oid).split(".")[-1]
                idx_iface = self._index_interface.get(idx_snmp)
                if idx_iface is None:
                    continue
                aggregated.setdefault(idx_iface, {})[metric] = val.prettyPrint()

        for i, iface in self.interfaces.items():
            iface.update(aggregated.get(i, {}))

    def _discover_indices(self) -> Dict[str, str]:
        """Строим соответствие «SNMP‑index ⇢ порт коммутатора»."""
        mapping: Dict[str, str] = {}
        for oid, val in self._snmp_bulk("1.3.6.1.2.1.2.2.1.2"):  # ifDescr
            idx = str(oid).split(".")[-1]
            port = self._normalize_descr(str(val))
            if port is not None:
                mapping[idx] = port
        return mapping

    def _normalize_descr(self, descr: str) -> Optional[str]:
        try:
            if self._model in {"Mellanox SX6700", "Mellanox MSX6012F-2BFS"}:
                if "IB" in descr:
                    return str(int(descr.split("/")[-1]) - 1)
            elif self._model in {"D-Link DGS-1210-28X/ME", "D-Link DGS-1210-52/ME"}:
                if "D-Link" in descr:
                    return str(int(descr.split()[-1]) - 1)
            elif self._model == "MIKROTIK CRS312-4C+8XG-RM":
                if "ether" in descr:
                    return str(int(descr.replace("ether", "")) - 1)
                elif "combo" in descr:
                    return str(int(descr.replace("combo", "")) + 8)
        except Exception:
            pass
        return None


class Interface(SubObject):
    __slots__ = ("_params",)

    def __init__(self):
        super().__init__()
        self._params: Dict[str, Optional[str]] = {
            "if.in.bytes": None,
            "if.in.packets": None,
            "if.out.errors": None,
            "if.out.bytes": None,
            "if.out.packets": None,
            "if.in.errors": None,
        }

    def update(self, fresh: Dict[str, str]):
        """Добавляем (или обновляем) только полученные сегодня значения."""
        self._params.update({k: v for k, v in fresh.items() if v is not None})

    def reset(self):
        """Обнуляем всё (вызывается при потере связи)."""
        for k in self._params:
            self._params[k] = None

    def get_params_all(self):
        return self._params.copy()

    def get_metric(self, metric_id: str):
        try:
            val = self._params[metric_id]
            if val is not None:
                self._params[metric_id] = None
                val = self.validate_integer(val)
            return val
        except KeyError:
            logger_monitoring.error(f"Метрика {metric_id} отсутствует")
            return None
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None