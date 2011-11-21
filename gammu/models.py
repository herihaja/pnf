# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models

class Outbox(models.Model):
    updatedindb = models.DateTimeField()
    insertintodb = models.DateTimeField()
    sendingdatetime = models.DateTimeField()
    sendbefore = models.TimeField()
    sendafter = models.TimeField()
    text = models.TextField(blank=True, null=True)
    destinationnumber = models.CharField(max_length=20)
    coding = models.CharField(max_length=255, blank=True, null=True)
    udh = models.TextField(blank=True, null=True)
    class_field = models.IntegerField(blank=True, null=True)
    textdecoded = models.TextField()
    multipart = models.BooleanField()
    relativevalidity = models.IntegerField(blank=True, null=True)
    senderid = models.CharField(max_length=255, blank=True, null=True)
    sendingtimeout = models.DateTimeField()
    deliveryreport = models.CharField(max_length=10, blank=True, null=True)
    creatorid = models.TextField()
    class Meta:
        db_table = u'outbox'

class Inbox(models.Model):
    updatedindb = models.DateTimeField()
    receivingdatetime = models.DateTimeField()
    text = models.TextField()
    sendernumber = models.CharField(max_length=20)
    coding = models.CharField(max_length=255)
    udh = models.TextField()
    smscnumber = models.CharField(max_length=20)
    class_field = models.IntegerField()
    textdecoded = models.TextField()
    recipientid = models.TextField()
    processed = models.BooleanField()
    class Meta:
        db_table = u'inbox'
