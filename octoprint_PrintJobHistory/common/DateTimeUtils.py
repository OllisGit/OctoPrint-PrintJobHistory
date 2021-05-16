# coding=utf-8
from __future__ import absolute_import

import datetime

def calcDurationInSeconds(endDateTime, startDateTime):
	duration = (endDateTime - startDateTime).total_seconds()
	return duration
