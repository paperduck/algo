# run from /src/ like this:
#   $ bash tests/run_tests.sh
# for the sake of the config_nonsecure.cfg path in config.py.

export PYTHONPATH=/home/user/raid/software_projects/algo/src
export PYTHONPATH=$PYTHONPATH:/home/user/raid/software_projects/algo/src/tests

python3 -m unittest test_daemon
python3 -m unittest test_instrument

