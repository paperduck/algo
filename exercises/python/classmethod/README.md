

PURPOSE:

Making sure the `@classmethod` decorator can be used to prevent the strategy
modules from having their own individual connections to a broker.
Only want one connection that is shared by all strategies.

