# CSV-configuration-parser
```shell
python3 main.py -h 
usage: main.py [-h] [--config CONFIG] [--input-directory INPUT_DIRECTORY] [--output-directory OUTPUT_DIRECTORY] [--verbose]

.csv files format parser

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to .csv configuration file
  --input-directory INPUT_DIRECTORY, -i INPUT_DIRECTORY
                        Path to directory where input vectors are stored
  --output-directory OUTPUT_DIRECTORY, -o OUTPUT_DIRECTORY
                        Path to directory where output vectors are stored
  --verbose, -v         Switch to verbose mode
```
`--config` - путь до .csv файла с расписанной конфигурацией определенных структур (например `OTU4_CONVERTER.csv`).

`--input-directory` - путь до директории, в которой сохранены входные вектора (INPUTS).

`--output-directory` - путь до директории, в которой сохранены выходные вектора (OUTPUTS).

`-v` - вывод дополнительной информации. Например, полный птуть до директорий, в которых хранятся входные/выходные вектора.

Пример вызвова:
```shell
python3 main.py \
    \-c /tmp/no_errors/PCSTX/otu4_converter/1
    \-i /tmp/no_errors/PCSTX/otu4_converter
    \-o /tmp/no_errors/PCSTX/otu4_converter/out_
[!]: "" value can't be interpreted as integer, when reading ModuleInfo

[i]: Module: OTU4_CONVERTER
[i]: Module ID: None

[i]: #Type - "INPUTS"
[i]: #Number of bits - 434
[i]: #Number of bytes - 57
[i]: #Field - (DATA_IN, [9:0][31:0], 320)
[i]: #Field - (DATA_VALID_IN, None, 1)
[i]: #Field - (nHARD_RESET, None, 1)
[i]: #Field - (DEFAULT_LOGICAL_LANES_SEARCH_ORDER, [19:0][4:0], 104)
[i]: #Field - (FAS_MATCH_REQUIRED, [5:0], 8)
[i]: #Field - (OTL_10_UNLOCKS_TO_RESET, [4:0], 8)
[i]: #Field - (OTU4_CONVERTER_RESET, None, 1)
[i]: #Field - (-, -, -)

[i]: #Type - "OUTPUTS"
[i]: #Number of bits - 438
[i]: #Number of bytes - 62
[i]: #Field - (OTU4_OUTPUT, [127:0], 128)
[i]: #Field - (DATA_VALID_OUT, None, 1)
[i]: #Field - (FRAME_BEGIN, None, 1)
[i]: #Field - (LOGICAL_LANES_CHANNELS, [19:0][4:0], 104)
[i]: #Field - (LOGICAL_LANES_DETECTION_DEGREE, [19:0][2:0], 64)
[i]: #Field - (OTL_OOFLANE, [19:0] , 24)
[i]: #Field - (OTL_LOFLANE, [19:0] , 24)
[i]: #Field - (OTL_OOR, [19:0], 24)
[i]: #Field - (OTL_LOR, [19:0], 24)
[i]: #Field - (LAST_FAS_DISTANCE, [17:0], 24)
[i]: #Field - (INPUT_DATA_VALID_RATE, [16:0], 24)
[i]: #Field - (LAST_FAS_LLM, [7:0], 8)
[i]: #Field - (LAST_FAS_LOGICAL_LANE, [4:0] , 8)
[i]: #Field - (LAST_FAS_PHYSICAL_LANE, [4:0], 8)
[i]: #Field - (SEARCH_LANE_CHANNEL, [4:0], 8)
[i]: #Field - (LAST_FAS_DETECTION_DEGREE, [2:0], 8)
[i]: #Field - (OTL4_10_LOCK, None, 1)
[i]: #Field - (OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR, None, 1)
[i]: #Field - (OTU_OOM, None, 1)
[i]: #Field - (OTU_OOF, None, 1)
[i]: #Field - (OTU_LOM, None, 1)
[i]: #Field - (OTU_LOF, None, 1)
[i]: #Field - (OTL_LOL, None, 1)

=============== /tmp/no_errors/PCSTX/otu4_converter ===============
[i]: INPUTS; DATA_IN - file "in_DATA_IN(32u).dat"
[i]: INPUTS; DATA_VALID_IN - file "in_DATA_VALID_IN(1u).dat"
[i]: INPUTS; nHARD_RESET - file "in_nHARD_RESET(1u).dat"
[i]: INPUTS; DEFAULT_LOGICAL_LANES_SEARCH_ORDER - file "in_DEFAULT_LOGICAL_LANES_SEARCH_ORDER(5u).dat"
[i]: INPUTS; FAS_MATCH_REQUIRED - file "in_FAS_MATCH_REQUIRED(6u).dat"
[i]: INPUTS; OTL_10_UNLOCKS_TO_RESET - file "in_OTL_10_UNLOCKS_TO_RESET(5u).dat"
[i]: INPUTS; OTU4_CONVERTER_RESET - file "in_OTU4_CONVERTER_RESET(1u).dat"
[i]: INPUTS; Number of fields with files - 7; Total number of fields - 8
[i]: INPUTS; Fields without files - -

=============== /tmp/no_errors/PCSTX/otu4_converter/out_ ===============
[i]: OUTPUTS; OTU4_OUTPUT - file "OTU4_OUTPUT(1u).dat"
[i]: OUTPUTS; DATA_VALID_OUT - file "DATA_VALID_OUT_D(1u).dat"
[i]: OUTPUTS; FRAME_BEGIN - file "FRAME_BEGIN(1u).dat"
[i]: OUTPUTS; LOGICAL_LANES_CHANNELS - file "LOGICAL_LANES_CHANNELS_TO_LOGICAL_LANES_OUT(5u).dat"
[i]: OUTPUTS; LOGICAL_LANES_DETECTION_DEGREE - file "LOGICAL_LANES_DETECTION_DEGREE(3u).dat"
[i]: OUTPUTS; OTL_OOFLANE - file "OTL_OOFLANE(1u).dat"
[i]: OUTPUTS; OTL_LOFLANE - file "OTL_LOFLANE(1u).dat"
[i]: OUTPUTS; OTL_OOR - file "OTL_OOR(1u).dat"
[i]: OUTPUTS; OTL_LOR - file "OTL_LOR(1u).dat"
[i]: OUTPUTS; LAST_FAS_DISTANCE - file "LAST_FAS_DISTANCE_OUT(18u).dat"
[i]: OUTPUTS; INPUT_DATA_VALID_RATE - file "INPUT_DATA_VALID_RATE(17u).dat"
[i]: OUTPUTS; LAST_FAS_LLM - file "LAST_FAS_LLM(8u).dat"
[i]: OUTPUTS; LAST_FAS_LOGICAL_LANE - file "LAST_FAS_LOGICAL_LANE(5u).dat"
[i]: OUTPUTS; LAST_FAS_PHYSICAL_LANE - file "LAST_FAS_PHYSICAL_LANE(5u).dat"
[i]: OUTPUTS; LAST_FAS_DETECTION_DEGREE - file "LAST_FAS_DETECTION_DEGREE(4u).dat"
[i]: OUTPUTS; OTL4_10_LOCK - file "OTL4_10_LOCK(1u).dat"
[i]: OUTPUTS; OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR - file "OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR(1u).dat"
[i]: OUTPUTS; OTU_OOM - file "OTU_OOM(1u).dat"
[i]: OUTPUTS; OTU_OOF - file "OTU_OOF(1u).dat"
[i]: OUTPUTS; OTU_LOM - file "OTU_LOM(1u).dat"
[i]: OUTPUTS; OTU_LOF - file "OTU_LOF(1u).dat"
[i]: OUTPUTS; OTL_LOL - file "OTL_LOL(1u).dat"
[i]: OUTPUTS; Number of fields with files - 22; Total number of fields - 23
[i]: OUTPUTS; Fields without files - SEARCH_LANE_CHANNEL
```
