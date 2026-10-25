# CSV-configuration-parser

Ветка: `universal_parser`. Состояние: `41a0dcc`.

## Назначение и изменения относительно main

Ветка развивает чтение конфигурации и поиск файлов тестовых векторов. Входной и выходной каталоги задаются независимо. Добавлены объекты `ModuleInfo`, `InOutFields` и `BufferStream`, чтение секций по информационным строкам, колонка `__Type__` и поиск по имени сигнала математической модели.

Результат работы – описание модуля и отчёт о соответствии сигналов файлам. Конвертация содержимого и запись объединённых векторов появляются в `parser_with_collector`.

## Запуск

Для кода этой ветки нужен >= Python 3.12. Сторонние Python-пакеты не требуются.

```sh
python3 main.py -h
python3 main.py -c "OTU4_CONVERTER.csv" -i "no_errors/PCSTX/otu4_converter" -o "no_errors/PCSTX/otu4_converter/out_" -v
```

| Параметр | Назначение | По умолчанию |
| --- | --- | --- |
| `--config`, `-c` | Конфигурация CSV | `OTU4_CONVERTER.csv` |
| `--input-directory`, `-i` | Входные файлы | `.` |
| `--output-directory`, `-o` | Выходные файлы | `.` |
| `--verbose`, `-v` | Дополнительный вывод | Выключен |

Команда и описание аргументов основаны на исходном README; исправлено оформление переноса строк.

## Формат CSV

Конфигурация содержит заголовок модуля и секции `INPUTS` / `OUTPUTS` с общим количеством бит и байт. Для определения информационной строки проверяются слова inputs/outputs, bits и bytes в соответствующих ячейках.

Порядок колонок:

```csv
__Implementation__,__Dimension__,__TV_Offset__,__Bit_Position__,__Type__,__RTL_Signal__,__Model_Signal__,__Doc_Signal__
```

`BufferStream` позволяет вернуть последнюю прочитанную строку, чтобы начало следующей секции не потерялось. Поля хранят RTL-имя, имя модели, размерность и тип.

## Сопоставление файлов

Для входной секции код ищет подстроку `in_<__Model_Signal__>`, для выходной – `out_<__Model_Signal__>` в имени файла без расширения. Например:

```text
in_DATA_IN(32u).dat
out_DATA_VALID_OUT(1u).dat
```

В старом журнале исходного README встречались выходные имена без `out_`. Текущий код этой ветки ищет указанный префикс, поэтому старый журнал не следует использовать как точное описание правила поиска.

## Структура и ограничения

- `main.py` – класс `App`, генератор секций, поиск файлов и CLI.
- `classes.py` – модели конфигурации, поток с возвратом строки и проверка соответствий.
- `output.py` – информационные сообщения, предупреждения и ошибки.
- `exceptions.py` – ошибки парсера.

## Пример работы парсера

Пример вызова:
```shell
python3 main.py \
  \ -c "/home/truncheon/omo_testchamber/DOCs/Test Vectors/FRAMER_PCS_TX/DESCRAMBLER.csv"
  \ -i "/home/truncheon/no_errors/PCSTX/descrambler/" 
  \ -o "/home/truncheon/no_errors/PCSTX/descrambler/" 
  \ -s "./vectors" 
  \ --dump-size=2048
  \ -v

[v]: Working with .csv file at "/home/truncheon/omo_testchamber/DOCs/Test Vectors/FRAMER_PCS_TX/DESCRAMBLER.csv"
[v]: Checking presence of corresponding fields files at "/home/truncheon/no_errors/PCSTX/descrambler" for input vectors
[v]: Checking presence of corresponding fields files at "/home/truncheon/no_errors/PCSTX/descrambler" for output vectors

[!]: Warning at 1 row in a table
[!]: "" doesn't contain "module" and "id" susbstrings

[!]: "" value can't be interpreted as integer, when reading ModuleInfo

[v]: Module: DESCRAMBLER
[v]: Module ID: None

[i]: #Field - {
[i]:    .rtl_signal = "AIS_EN_IN",
[i]:    .model_signal = "AIS_EN_IN",
[i]:    .simulating = "False"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: "AIS_EN_IN" seems to be non-simulating, therefore skip this field

[i]: #Type - "INPUTS"
[i]: #Number of bits - 136
[i]: #Number of bytes - 17
[i]: #Field - {
[i]:    .rtl_signal = "DATA_IN",
[i]:    .model_signal = "DATA_IN",
[i]:    .simulating = "True"
[i]:    .implementation = "[127:0]",
[i]:    .dimension = "128"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "DATA_VALID",
[i]:    .model_signal = "DATA_VALID_IN",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "FRAME_BEGIN",
[i]:    .model_signal = "FRAME_BEGIN_IN",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "nHARD_RESET",
[i]:    .model_signal = "nHARD_RESET",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }

[i]: #Type - "OUTPUTS"
[i]: #Number of bits - 136
[i]: #Number of bytes - 17
[i]: #Field - {
[i]:    .rtl_signal = "DATA_OUT",
[i]:    .model_signal = "DATA_OUT",
[i]:    .simulating = "True"
[i]:    .implementation = "[127 : 0]",
[i]:    .dimension = "128"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "DATA_VALID_OUT",
[i]:    .model_signal = "DATA_VALID_OUT",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "FRAME_BEGIN_OUT",
[i]:    .model_signal = "FRAME_BEGIN_OUT",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }

=============== /home/truncheon/no_errors/PCSTX/descrambler ===============
[i]: INPUTS; "DATA_IN" - file "in_DATA_IN(1u).dat"
[i]: INPUTS; "DATA_VALID" - file "in_DATA_VALID_IN(1u).dat"
[i]: INPUTS; "FRAME_BEGIN" - file "in_FRAME_BEGIN_IN(1u).dat"
[i]: INPUTS; "nHARD_RESET" - file "in_nHARD_RESET(1u).dat"
[i]: INPUTS; Number of fields with files - 4; Total number of fields - 4

=============== /home/truncheon/no_errors/PCSTX/descrambler ===============
[i]: OUTPUTS; "DATA_OUT" - file "out_DATA_OUT(1u).dat"
[i]: OUTPUTS; "DATA_VALID_OUT" - file "out_DATA_VALID_OUT(1u).dat"
[i]: OUTPUTS; "FRAME_BEGIN_OUT" - file "out_FRAME_BEGIN_OUT(1u).dat"
[i]: OUTPUTS; Number of fields with files - 3; Total number of fields - 3

[v]: Total rows read - 14

[v]: "in_DATA_IN(1u).dat" seems to be BINARY

[v]: "in_DATA_VALID_IN(1u).dat" seems to be BINARY

[v]: "in_FRAME_BEGIN_IN(1u).dat" seems to be BINARY

[v]: "in_nHARD_RESET(1u).dat" seems to be BINARY

[v]: Vectores are stored at "/home/truncheon/CSV-configuration-parser/vectors/vectors_0.tv"

[v]: "out_DATA_OUT(1u).dat" seems to be BINARY

[v]: "out_DATA_VALID_OUT(1u).dat" seems to be BINARY

[v]: "out_FRAME_BEGIN_OUT(1u).dat" seems to be BINARY

[v]: Vectores are stored at "/home/truncheon/CSV-configuration-parser/vectors/vectors_1.tv"

Total time - 0:00:23.908457
```