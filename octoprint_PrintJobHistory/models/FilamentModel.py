# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.models.BaseModel import BaseModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, ForeignKeyField


class FilamentModel(BaseModel):

	printJob = ForeignKeyField(PrintJobModel, related_name='filaments', on_delete='CASCADE')

	profileVendor = CharField(null=True)
	diameter = FloatField(null=True)
	density = FloatField(null=True)
	material = CharField(null=True)
	spoolName = DateTimeField(null=True)
	spoolCost = DateTimeField(null=True)
	spoolCostUnit = CharField(null=True)
	spoolWeight = CharField(null=True)
	usedLength = FloatField(null=True)
	calculatedLength = FloatField(null=True)
	usedWeight = FloatField(null=True)
	usedCost = FloatField(null=True)
