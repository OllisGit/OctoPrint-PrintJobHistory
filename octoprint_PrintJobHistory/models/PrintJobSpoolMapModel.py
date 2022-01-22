# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.models.BaseModel import BaseModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, ForeignKeyField, \
	IntegerField


class PrintJobSpoolMapModel(BaseModel):

	printJob = ForeignKeyField(PrintJobModel, related_name='spoolMap', on_delete='CASCADE')

	spoolManagerId = IntegerField()
