import json
from pprint import pprint as pp

SETTINGS_FILE = 'data/settings.json'


def print_debug(*args, sep=' ', end='\n', file=None, flush=True):
    if json.load(open(SETTINGS_FILE))['debug']:
        print(*args, sep=sep, end=end, file=file, flush=flush)


def pprint_debug(object, stream=None, indent=1, width=80, depth=None, *, compact=False):
    if json.load(open(SETTINGS_FILE))['debug']:
        pp(object, stream=stream, indent=indent, width=width, depth=depth, compact=compact)
