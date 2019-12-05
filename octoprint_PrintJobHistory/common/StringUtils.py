# coding=utf-8
from __future__ import absolute_import

import re

# see https://www.safaribooksonline.com/library/view/python-cookbook-2nd/0596007973/ch01s19.html


def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)

# see https://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days/4048773
def secondsToText(secs):
    days = secs // 86400
    hours = (secs - days * 86400) // 3600
    minutes = (secs - days * 86400 - hours * 3600) // 60
    seconds = secs - days * 86400 - hours * 3600 - minutes * 60

    result = ("{}d".format(days) if days else "") + \
             ("{}h".format(hours) if hours else "") + \
             ("{}m".format(minutes) if not days and minutes else "") + \
             ("{}s".format(seconds) if not days and not hours and seconds else "")
    return result


from string import Formatter
from datetime import timedelta

# see https://stackoverflow.com/questions/538666/python-format-timedelta-to-string
def formatTimeDelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    if type(tdelta) is not timedelta:
        return ''
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

def compactTimeDeltaFormatter(tdelta, inputtype='timedelta'):
	if type(tdelta) is not timedelta:
		return ''
	# Convert tdelta to integer seconds.
	if inputtype == 'timedelta':
		remainder = int(tdelta.total_seconds())
	elif inputtype in ['s', 'seconds']:
		remainder = int(tdelta)
	elif inputtype in ['m', 'minutes']:
		remainder = int(tdelta) * 60
	elif inputtype in ['h', 'hours']:
		remainder = int(tdelta) * 3600
	elif inputtype in ['d', 'days']:
		remainder = int(tdelta) * 86400
	elif inputtype in ['w', 'weeks']:
		remainder = int(tdelta) * 604800

	w = divmod(remainder, 604800)
	remainder = remainder - (w[0] * 604800)
	d = divmod(remainder, 86400)
	remainder = remainder - (d[0] * 86400)
	h = divmod(remainder, 3600)
	remainder = remainder - (h[0] * 3600)
	m = divmod(remainder, 60)
	remainder = remainder - (m[0] * 60)
	s = divmod(remainder, 1)

	result = ""
	if w[0] != 0:
		result = str(w[0]) +"w " + str(d[0]) + "d " + str(h[0])+"h " + str(m[0])+"m " + str(s[0])+"s"
	elif d[0] != 0:
		result = str(d[0]) + "d " + str(h[0]) + "h " + str(m[0]) + "m " + str(s[0]) + "s"
	elif h[0] != 0:
		result = str(h[0]) + "h " + str(m[0]) + "m " + str(s[0]) + "s"
	elif m[0] != 0:
		result = str(m[0]) + "m " + str(s[0]) + "s"
	elif s[0] != 0:
		result = str(s[0]) + "s"
	return result


def formatSave(pattern, value, defaultString):
	if (value == None or not isinstance(value, float)):
		return defaultString
	floatValue = float(value)
	return pattern.format(floatValue)


# bla = unicode('1')
#
# param = bla
# result = formatSave("{:.0f}", param, "unbekannt")
# print(result)

### TEST-ZONE
#day = 0
#hour = 0
#minute = 1
#second = 31

#seconds = day * 24 * 60 * 60 +  hour * 60 * 60 +  minute * 60  + second
#print(secondsToText(None, seconds) )
"""
from datetime import datetime
start_datetime_str = '09/10/18 13:55:26'
end_datetime_str = '09/20/18 14:56:35'
start_datetime_object = datetime.strptime(start_datetime_str, '%m/%d/%y %H:%M:%S')
end_datetime_object = datetime.strptime(end_datetime_str, '%m/%d/%y %H:%M:%S')

duration = end_datetime_object - start_datetime_object

print(compactTimeDeltaFormatter(duration))
print(formatTimeDelta(duration))
"""
