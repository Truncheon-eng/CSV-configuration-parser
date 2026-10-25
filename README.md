# CSV-configuration-parser

Ветка: `main`. Состояние: `983e204`.

## Назначение и этап разработки

Начальный этап унификации тестовых векторов математических моделей. Программа читает CSV с описанием сигналов и проверяет, какие файлы векторов доступны для входных и выходных полей. На этом этапе содержимое файлов не преобразуется в шестнадцатеричный вид, объединённые файлы не создаются.

## Запуск

Нужен Python3; используются модули стандартной библиотеки. Команды выполняются из корня проекта.

```sh
python3 main.py -h
python3 main.py -c "OTU4_CONVERTER.csv" -d "no_errors/PCSTX/otu4_converter" -v
```

| Параметр | Назначение | По умолчанию |
| --- | --- | --- |
| `--config`, `-c` | CSV с конфигурацией | `OTU4_CONVERTER.csv` |
| `--dir`, `-d` | Каталог входных файлов | Текущий каталог |
| `--verbose`, `-v` | Дополнительная информация о полях и обработке | Выключен |

Выходные файлы ищутся в подкаталоге `out_` выбранного каталога. Отдельного параметра для него в этой ветке нет.

## Формат конфигурации

Сохранена схема исходного README: первая строка содержит метаданные модуля, вторая описывает размер входного вектора, третья содержит заголовки. Далее идут входные поля, разделитель, служебные строки и выходные поля. Разделителем считается строка, в которой все ячейки пустые либо равны `-`. Положение служебных строк существенно: после входной секции код пропускает две записи перед чтением выходных полей.

Заголовки должны идти в следующем порядке:

```csv
__Implementation__,__Dimension__,__TV_Offset__,__Bit_Position__,__RTL_Signal__,__Model_Signal__,__Doc_Signal__
```

Для объекта `Field` используются RTL-имя, описание размерности и размер поля. Например, `[9:0][31:0]` описывает десять 32-битных элементов.

## Порядок работы и результат

1. `App` проверяет путь к CSV и читает входные и выходные поля.
2. Для каждого каталога программа сопоставляет имя поля с подстрокой имени файла.
3. `FieldValidator` выводит найденные соответствия, количество найденных файлов и поля без файлов.

Поиск по подстроке не гарантирует однозначного соответствия, если имена сигналов пересекаются.

## Файлы проекта

- `main.py` – класс `App`, чтение CSV, обход каталогов и CLI.
- `classes.py` – описание поля и отчёт о найденных файлах.
- `exceptions.py` – исключение `ParserException`.

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

Следующий этап – ветка `universal_parser`: раздельные пути к входным и выходным векторам и более общее чтение секций.