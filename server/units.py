"""
Functions to convert between units and create human-readable strings from times
and lengths.
"""

from math import floor

second = 1
minute = second * 60
hour = minute * 60
day = hour * 24
week = day * 7
year = day * 365.25

ft = 1 / 3.28084
km = 1000
mi = 1609.34

def format_distance(x: float, metric: bool) -> str:
	"""Describes a distance in either kilometres or miles"""
	if metric:
		return f'{x / km:.1f} km'
	else:
		return f'{x / mi:.1f} mi'

def format_elevation(x: float, metric: bool) -> str:
	"""Describes an elevation in either metres or feet"""
	if metric:
		return f'{x:.0f} m'
	else:
		return f'{x / ft:.0f} ft'

def format_time(x: float, detail: int = 2) -> str:
	"""Describes a time duration in seconds, minutes, etc. to the specified level of precision"""
	units = [ 'years', 'weeks', 'days', 'hours', 'minutes', 'seconds' ]
	values = [
		x / year,
		(x % year) / week,
		(x % week) / day,
		(x % day) / hour,
		(x % hour) / minute,
		(x % minute) / second,
	]
	return ' '.join([
		f'{floor(value)} {unit}' for value, unit in zip(values, units) if value >= 1
	][:detail]) or '0 seconds'
