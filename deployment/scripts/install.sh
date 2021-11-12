#!/bin/bash
python_interpreter=""

read -p "┌────────────────────┐
| Python interpreter |
└────────────────────┘
Default: /usr/bin/python
(Сlick Enter for choose default)
If you wont to change, write: " python_interpreter


if [ -z "$python_interpreter" ]; then
    /usr/bin/python -m venv env
else
    $python_interpreter -m venv env
fi

source env/bin/activate
cd src/

pip install -U pip && pip install -r requirements.txt
