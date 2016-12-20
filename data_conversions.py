#!/usr/bin/python3

@classmethod
def btos(cls, b):
    """
    Decode bytes to string using UTF8.
    Parameter `b' is assumed to have type of `bytes'.
    """
    return b.decode('utf_8')


@classmethod
def stob(cls, s):
    """
    """
    return s.encode('utf_8')

