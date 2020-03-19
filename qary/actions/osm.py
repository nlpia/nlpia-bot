"""Open Street Maps -- GIS search, edit, scrape, parse

>>> txt = '''
... Wednesday, 3-9pm
... Thursday, 3-9pm
... Friday 3-10pm
...
... Saturday, 12-10pm
... Sunday, 12-6pmThursday, 3-9pm
... '''
>>> extract_opening_hours(txt)
We-Th 15:00-21:00; Fr 15:00-22:00; Sa 12:00-22:00; Su 15:00-21:00
"""
from datetime import time


def extract_opening_hours(s):
    # FIXME: parse s
    return dict(
        We=(time(15), time(21)),
        Th=(time(15), time(21)),
        Fr=(time(15), time(22)),
        Sa=(time(12), time(22)),
        Su=(time(12), time(21)))


def to_osm_format(data):
    """ OSM "opening_hours" tag field format

    SEE: https://wiki.openstreetmap.org/wiki/Key:opening_hours
    """
    txt = ''
    for dow in 'Su Mo Tu We Th Fr Sa'.split():
        day_hours = data.get(dow, None)
        if day_hours is not None:
            txt += f'{dow} {day_hours[0].hour}:{day_hours[0].minute}-{day_hours[2].hour}:{day_hours[1].minute}; '
    return txt.rstrip().rstrip(';')
