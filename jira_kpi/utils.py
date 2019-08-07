import datetime

from collections import OrderedDict


interval_dict = OrderedDict(
    [
        ("Y", 365*86400),
        ("M", 30*86400),
        ("w", 7*86400),
        ("d", 86400),
        ("h", 3600),
        ("m", 60),
        ("s", 1)
    ]
)

def seconds_to_human(seconds, max_units=2):
    '''
    Convert seconds to human readable time
    '''
    seconds = int(seconds)
    units = []
    for unit, value in interval_dict.items():
        subres = int(seconds / value)
        if subres:
            seconds -= value * subres
            units.append('%s%s' % (subres, unit))
        if len(units) == max_units:
            break

    return ' '.join(units)

def str_to_date(dateStr):
    '''
    Parse date from string
    '''
    return datetime.datetime.strptime(dateStr,'%Y-%m-%dT%H:%M:%S.%f%z')

def pairwise(lst):
    '''
    Generate list of adjacent tuples from list.

    yield item i and item i+1 in list. e.g.
    (list[0], list[1]), (list[1], list[2]), ..., (list[-1], None)
    '''
    if not lst:
        return
    
    for i in range(len(lst)-1):
        yield lst[i], lst[i+1]
    
    yield lst[-1], None

def get_nested_key(d, nested_key, default_val=None):
    '''
    Get nested dictionary key value in a null-safe way
    '''
    keys = nested_key.split('.')
    val = d
    for index, key in enumerate(keys):
        val = val.get(key)
        if val == None and index != len(keys)-1:
            val = {}

    if val == None:
        return default_val

    return val

def title(text):
    '''
    Print title
    '''
    print('\n%s\n%s' % (text, '-' * len(text)))