# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models

class Outbox(models.Model):
    updatedindb = models.DateTimeField(db_column='UpdatedInDB') # Field name made lowercase.
    insertintodb = models.DateTimeField(db_column='InsertIntoDB') # Field name made lowercase.
    sendingdatetime = models.DateTimeField(db_column='SendingDateTime') # Field name made lowercase.
    sendbefore = models.TimeField(db_column='SendBefore') # Field name made lowercase.
    sendafter = models.TimeField(db_column='SendAfter') # Field name made lowercase.
    text = models.TextField(db_column='Text', blank=True, null=True) # Field name made lowercase.
    destinationnumber = models.CharField(max_length=20, db_column='DestinationNumber') # Field name made lowercase.
    coding = models.CharField(max_length=255, db_column='Coding', blank=True, null=True) # Field name made lowercase.
    udh = models.TextField(db_column='UDH', blank=True, null=True) # Field name made lowercase.
    class_field = models.IntegerField(db_column='Class', blank=True, null=True) # Field name made lowercase. Field renamed because it was a Python reserved word.
    textdecoded = models.TextField(db_column='TextDecoded') # Field name made lowercase.
    multipart = models.BooleanField(db_column='MultiPart') # Field name made lowercase.
    relativevalidity = models.IntegerField(db_column='RelativeValidity', blank=True, null=True) # Field name made lowercase.
    senderid = models.CharField(max_length=255, db_column='SenderID', blank=True, null=True) # Field name made lowercase.
    sendingtimeout = models.DateTimeField(db_column='SendingTimeOut') # Field name made lowercase.
    deliveryreport = models.CharField(max_length=10, db_column='DeliveryReport', blank=True, null=True) # Field name made lowercase.
    creatorid = models.TextField(db_column='CreatorID') # Field name made lowercase.
    class Meta:
        db_table = u'outbox'

class Inbox(models.Model):
    updatedindb = models.DateTimeField(db_column='UpdatedInDB') # Field name made lowercase.
    receivingdatetime = models.DateTimeField(db_column='ReceivingDateTime') # Field name made lowercase.
    text = models.TextField(db_column='Text') # Field name made lowercase.
    sendernumber = models.CharField(max_length=20, db_column='SenderNumber') # Field name made lowercase.
    coding = models.CharField(max_length=255, db_column='Coding') # Field name made lowercase.
    udh = models.TextField(db_column='UDH') # Field name made lowercase.
    smscnumber = models.CharField(max_length=20, db_column='SMSCNumber') # Field name made lowercase.
    class_field = models.IntegerField(db_column='Class') # Field name made lowercase. Field renamed because it was a Python reserved word.
    textdecoded = models.TextField(db_column='TextDecoded') # Field name made lowercase.
    recipientid = models.TextField(db_column='RecipientID') # Field name made lowercase.
    processed = models.BooleanField(db_column='Processed') # Field name made lowercase.
    class Meta:
        db_table = u'inbox'
