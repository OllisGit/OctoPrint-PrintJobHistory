# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.BaseModel import BaseModel
# from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, BooleanField, ForeignKeyField


# Since V7
class CostModel(BaseModel):

	printJob = ForeignKeyField(PrintJobModel, backref='costs', on_delete='CASCADE', null=True, unique=True)

	# maybe later add costs-settings, like Purchase price, Maintenance costs...

	#             var costData = {
	#                 filename: filename,
	#                 filepath: filepath,
	#                 filamentCost: filamentCost,
	#                 electricityCost: electricityCost,
	#                 printerCost: printerCost,
	#                 otherCostLabel: otherCostLabel,
	#                 otherCost: otherCost,
	#             }

	totalCosts = FloatField(null=True)
	filamentCost = FloatField(null=True)
	electricityCost = FloatField(null=True)
	printerCost = FloatField(null=True)
	otherCostLabel = TextField(null=True)
	otherCost = FloatField(null=True)
	withDefaultSpoolValues = BooleanField(null=True)
