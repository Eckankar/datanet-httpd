import os

# Automagically import all handlers in the directory.
modules = [pyfile[:-3]
           for pyfile in os.listdir(os.path.dirname(__file__))
           if pyfile[-3:] == '.py' and pyfile != '__init__.py']

HANDLERS = [getattr(__import__(module, globals(), locals(), []), module)()
            for module in modules]

__all__ = ['HANDLERS'] + modules


