#!/usr/bin/python3

from datetime import datetime

class o():
    d = ( datetime.now().strftime("%c") )

    @classmethod
    def go(cls):
        print ( cls.d )
