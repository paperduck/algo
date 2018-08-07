
"""
Run the daemon here.
"""

####################
import cmd
import curses
from threading import Thread
import sys
####################
from daemon import Daemon
####################

if __name__ == "__main__":
    curses.wrapper(Daemon.run)


