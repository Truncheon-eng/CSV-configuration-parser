# CSV-configuration-parser

Ветка: `parser_with_collector`. Состояние: `7c67c82`.

## Назначение и этап разработки

К чтению конфигурации добавлен `Collector`, который построчно объединяет файлы отдельных сигналов и переводит значения в текстовое шестнадцатеричное представление. Это этап формирования унифицированных тестовых векторов для дальнейшей проверки аппаратных моделей.

В математических моделях данные представлены отдельными битами, последовательностями битов либо десятичными элементами массивов. Конфигурация связывает эти файлы с сигналами и задаёт размерности.

## Запуск

Нужен Python 3.12 или новее; внешние пакеты не используются. Каталог результата необходимо создать заранее.

```sh
mkdir -p vectors
python3 main.py -c "DESCRAMBLER.csv" -i "no_errors/PCSTX/descrambler" -o "no_errors/PCSTX/descrambler" -s "vectors" --dump-size 2048 -v
```

Это пример для Linux shell; в Windows пути можно передать в кавычках той же командой Python, предварительно создав каталог `vectors`.

| Параметр | Назначение | По умолчанию |
| --- | --- | --- |
| `--config`, `-c` | CSV с описанием полей | `OTU4_CONVERTER.csv` |
| `--input-directory`, `-i` | Входные файлы | `.` |
| `--output-directory`, `-o` | Выходные файлы | `.` |
| `--store`, `-s` | Каталог результата | `.` |
| `--dump-size`, `-d` | Число символов для распознавания системы счисления, 1024–8192 | 1024 |
| `--verbose`, `-v` | Расширенный журнал | Выключен |

В справке CLI для dump-size написано bits, но код вызывает `read(dump_size)` у текстового файла: фактически это число символов. Пример запуска и назначение параметров сохранены из исходного README.

## Конфигурация и имена файлов

Порядок колонок:

```csv
__Implementation__,__Dimension__,__TV_Offset__,__Bit_Position__,__Type__,__RTL_Signal__,__Model_Signal__,__Doc_Signal__
```

Секции `INPUTS` и `OUTPUTS` содержат сведения об общем размере вектора и строки полей. `__Type__=S` включает поле в обработку, `R` исключает его как регистровое; другие значения вызывают ошибку.

Имя файла ищется регулярным выражением с префиксом направления, именем модели и суффиксом размерности. Поддерживаются формы `in_DATA_IN(32u).dat`, `in_DATA_IN[32].dat` и аналогичные имена с `out_`. Размерность преобразования берётся из CSV, а не из суффикса имени файла.

## Обработка данных

1. `Parser.run()` читает секции и возвращает словари соответствий полей и файлов.
2. `Collector` просматривает начало каждого файла и выбирает двоичный либо десятичный обработчик.
3. Одна строка результата собирается из соответствующих строк файлов. Разное количество строк приводит к ошибке благодаря `zip(..., strict=True)`.
4. Создаются `vectors_0.tv`, `vectors_1.tv` и далее по порядку обработанных секций. Для обычного CSV с INPUTS перед OUTPUTS это входные и выходные векторы соответственно.

Однобитное значение записывается одним символом. Многобитный двоичный вход ожидается как отдельные биты через одиночные пробелы, например `1 0 1 0`, а не как слитная строка `1010`. Десятичные элементы разделяются пробельными символами. Для `[9:0][31:0]` ожидается десять чисел в строке; каждый элемент форматируется отдельно и отделяется пробелом.

Выход не содержит заголовков, префиксов `0x` и запятых. Пример структуры строки:

```text
<шестнадцатеричные данные> <data_valid> <frame_begin> <reset>
```

Поля следуют порядку найденных соответствий, формируемых обходом полей CSV. Смещения `__TV_Offset__` и `__Bit_Position__` не используются для упаковки бинарного блока.

## Ограничения текущей реализации

- Автоопределение неоднозначно для десятичных данных, начало которых состоит только из 0 и 1. Увеличение dump-size может помочь, но не гарантирует правильного выбора.
- В наборе десятичных цифр распознавателя отсутствует `8`: если она встретится раньше цифры, определившей десятичный формат, возникает ошибка.
- В двоичном обработчике округление длины добавляет восемь бит и при исходной кратности восьми. Например, для восьми входных единиц текущий алгоритм формирует `00` вместо `ff`. Поэтому широкие двоичные данные требуют исправления и повторной проверки.
- Проверка переполнения десятичного элемента использует ширину, округлённую до байта, а не всегда исходную битовую ширину.
- Для ненайденного файла выдаётся предупреждение; сборка может продолжиться с неполным набором полей.
- Результат открывается в режиме перезаписи. При ошибке возможен частично записанный файл.

Эти ограничения описывают проверенную логику исходников; приведённые команды не являются протоколом успешного запуска.

## Файлы проекта

`main.py` отвечает за конфигурацию и запуск; `classes.py` – за поля и сопоставления; `collector.py` – за чтение, преобразование и сборку; `exceptions.py` и `output.py` – за ошибки и сообщения. В `DSP_TX/` сохранены примеры данных.

## Пример работы парсера

Пример вызова:
```shell
python3 main.py -c /home/kali/CSV-configuration-parser/OTU4_CONVERTER.csv
  \-d /mnt/hgfs/kali_shared/vector_unification/no_errors/PCSTX/otu4_converter/ -v
[Verbose] Read strings: 37
[Input] Field name: DATA_IN, Implementation: [9:0][31:0], Dimension: 320
[Input] Field name: DATA_VALID_IN, Implementation: None, Dimension: 1
[Input] Field name: nHARD_RESET, Implementation: None, Dimension: 1
[Input] Field name: DEFAULT_LOGICAL_LANES_SEARCH_ORDER, Implementation: [19:0][4:0], Dimension: 104
[Input] Field name: FAS_MATCH_REQUIRED, Implementation: [5:0], Dimension: 8
[Input] Field name: OTL_10_UNLOCKS_TO_RESET, Implementation: [4:0], Dimension: 8
[Input] Field name: OTU4_CONVERTER_RESET, Implementation: None, Dimension: 1


[Output] Field name: DATA_IN, Implementation: [9:0][31:0], Dimension: 320
[Output] Field name: DATA_VALID_IN, Implementation: None, Dimension: 1
[Output] Field name: nHARD_RESET, Implementation: None, Dimension: 1
[Output] Field name: DEFAULT_LOGICAL_LANES_SEARCH_ORDER, Implementation: [19:0][4:0], Dimension: 104
[Output] Field name: FAS_MATCH_REQUIRED, Implementation: [5:0], Dimension: 8
[Output] Field name: OTL_10_UNLOCKS_TO_RESET, Implementation: [4:0], Dimension: 8
[Output] Field name: OTU4_CONVERTER_RESET, Implementation: None, Dimension: 1


Working with input vectors in /mnt/hgfs/kali_shared/vector_unification/no_errors/PCSTX/otu4_converter
[Input] DATA_IN: file "in_DATA_IN(32u).dat"
[Input] DATA_VALID_IN: file "in_DATA_VALID_IN(1u).dat"
[Input] DEFAULT_LOGICAL_LANES_SEARCH_ORDER: file "in_DEFAULT_LOGICAL_LANES_SEARCH_ORDER(5u).dat"
[Input] FAS_MATCH_REQUIRED: file "in_FAS_MATCH_REQUIRED(6u).dat"
[Input] nHARD_RESET: file "in_nHARD_RESET(1u).dat"
[Input] OTL_10_UNLOCKS_TO_RESET: file "in_OTL_10_UNLOCKS_TO_RESET(5u).dat"
[Input] OTU4_CONVERTER_RESET: file "in_OTU4_CONVERTER_RESET(1u).dat"
[Input] Total fields: 7, Fields with file: 7


Working with output vectors in /mnt/hgfs/kali_shared/vector_unification/no_errors/PCSTX/otu4_converter/out_
[Output] DATA_VALID_OUT: file "DATA_VALID_OUT_D(1u).dat"
[Output] FRAME_BEGIN: file "FRAME_BEGIN(1u).dat"
[Output] INPUT_DATA_VALID_RATE: file "INPUT_DATA_VALID_RATE(17u).dat"
[Output] LAST_FAS_DETECTION_DEGREE: file "LAST_FAS_DETECTION_DEGREE(4u).dat"
[Output] LAST_FAS_DISTANCE: file "LAST_FAS_DISTANCE_OUT(18u).dat"
[Output] LAST_FAS_LLM: file "LAST_FAS_LLM(8u).dat"
[Output] LAST_FAS_LOGICAL_LANE: file "LAST_FAS_LOGICAL_LANE(5u).dat"
[Output] LAST_FAS_PHYSICAL_LANE: file "LAST_FAS_PHYSICAL_LANE(5u).dat"
[Output] LOGICAL_LANES_CHANNELS: file "LOGICAL_LANES_CHANNELS_TO_LOGICAL_LANES_OUT(5u).dat"
[Output] LOGICAL_LANES_DETECTION_DEGREE: file "LOGICAL_LANES_DETECTION_DEGREE(3u).dat"
[Output] OTL4_10_LOCK: file "OTL4_10_LOCK(1u).dat"
[Output] OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR: file "OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR(1u).dat"
[Output] OTL_LOFLANE: file "OTL_LOFLANE(1u).dat"
[Output] OTL_LOL: file "OTL_LOL(1u).dat"
[Output] OTL_LOR: file "OTL_LOR(1u).dat"
[Output] OTL_OOFLANE: file "OTL_OOFLANE(1u).dat"
[Output] OTL_OOR: file "OTL_OOR(1u).dat"
[Output] OTU4_OUTPUT: file "OTU4_OUTPUT(1u).dat"
[Output] OTU_LOF: file "OTU_LOF(1u).dat"
[Output] OTU_LOM: file "OTU_LOM(1u).dat"
[Output] OTU_OOF: file "OTU_OOF(1u).dat"
[Output] OTU_OOM: file "OTU_OOM(1u).dat"
[Output] Fields without files: SEARCH_LANE_CHANNEL
[Output] Total fields: 23, Fields with file: 22
```