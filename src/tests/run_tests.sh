# Run from /src/ like this:
#   $ bash tests/run_tests.sh
#   Do not run it from within /tests/. 
#   This is so the config_nonsecure.cfg path in config.py can be imported 
#   by the tests.

export PYTHONPATH=/home/user/raid/software_projects/algo/src
export PYTHONPATH=$PYTHONPATH:/home/user/raid/software_projects/algo/src/tests

python3 -m unittest test_oanda
python3 -m unittest test_daemon
python3 -m unittest test_instrument
python3 -m unittest test_chart
python3 -m unittest test_util_date
python3 -m unittest test_strategy


