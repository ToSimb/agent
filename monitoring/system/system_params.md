# Описание параметров системы

Этот документ описывает параметры, используемые в классе для мониторинга состояния системы.

## Параметры

| Параметр                   | Описание                                                               | Тип данных | Величина     |
|----------------------------|------------------------------------------------------------------------|------------|--------------|
| `chassis.uptime`           | Время непрерывной работы системы.                                      | integer    | секунды      |
| `chassis.core.count`       | Количество физических ядер центральных процессоров в системе.          | integer    | -            |
| `chassis.logic.count`      | Количество логических ядер центральных процессоров в системе.          | integer    | -            |
| `chassis.load.avg`         | Средняя загрузка процессоров за определенный период времени (0.2 сек). | double     | -            |
| `chassis.irq`              | Количество прерываний (IRQ) в системе.                                 | integer    | -            |
| `chassis.memory.total`     | Объем общей оперативной памяти в системе.                              | integer    | байт         |
| `chassis.memory.used`      | Объем используемой оперативной памяти в системе.                       | integer    | байт         |
| `chassis.memory.available` | Объем доступной оперативной памяти в системе.                          | integer    | байт         |
| `chassis.swap.total`       | Объем общего пространства подкачки (swap) в системе.                   | integer    | байт         |
| `chassis.swap.used`        | Объем используемого пространства подкачки (swap) в системе.            | integer    | байт         |
| `chassis.swap.available`   | Объем доступного пространства подкачки (swap) в системе.               | integer    | байт         |

## Примечания

- Все параметры могут быть `None`, если данные еще не были собраны или недоступны.
