# Описание параметров системы

Этот документ описывает параметры, используемые для мониторинга сетевых интерфейсов сервера.

## Параметры

| Параметр         | Описание                                                        | Тип данных | Величина |
|------------------|-----------------------------------------------------------------|------------|----------|
| `if.in.errors`   | Количество ошибок при приёме на каждом сетевом интерфейсе.      | integer    | -        |
| `if.in.bytes`    | Количество полученных байт через каждый сетевой интерфейс.      | integer    | -        |
| `if.in.packets`  | Количество полученных пакетов через каждый сетевой интерфейс.   | integer    | -        |
| `if.in.speed`    | Скорость входящего трафика на каждом сетевом интерфейсе.        | double     | байт/сек |
| `if.in.load`     | Загрузка интерфейса входящим трафиком.                          | double     | %        |
| `if.out.errors`  | Количество ошибок при отправке на каждом сетевом интерфейсе.    | integer    | -        |
| `if.out.bytes `  | Количество отправленных байт через каждый сетевой интерфейс.    | integer    | -        |
| `if.out.packets` | Количество отправленных пакетов через каждый сетевой интерфейс. | integer    | -        |
| `if.out.speed`   | Скорость исходящего трафика на каждом сетевом интерфейсе.       | double     | байт/сек |
| `if.out.load`    | Загрузка интерфейса исходящим трафиком.                         | double     | %        |

## Примечание

- Все параметры могут быть `None`, если данные еще не были собраны или недоступны.