#!/usr/bin/python3

def btos(b):
    """
    Decode bytes to string using UTF8.
    Parameter `b' is assumed to have type of `bytes'.
    """
    if b == None:
        return None
    else:
        return b.decode('utf_8')


def stob(s):
    """
    """
    if s == None:
        return None
    else:
        return s.encode('utf_8')

