#!/bin/sh

python --version | grep -q 3.5 || {
        echo You need python 3.5.
        echo Sorry.
        exit 1
}

virtualenv --no-site-packages --distribute .env && source .env/bin/activate && pip install -r requirements.txt

echo "Now run source .env/bin/activate to activate"

