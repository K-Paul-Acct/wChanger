#!/bin/bash
python_interpreter=""

read -p "----------------------
| Python interpreter |
----------------------
Default: /usr/bin/python3
(Сlick Enter for choose default)
If you wont to change, write: " python_interpreter


if [ -z "$python_interpreter" ]; then
    1 0,18 * * 1,6 *  /usr/bin/python3 test.py
else
    `1 0,18 * * 1,6 *  $python_interpreter test.py`
fi
