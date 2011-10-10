from django.db import models

class Province(models.Model):
    nom = models.CharField(max_length=20)
    code = models.CharField(max_length=6)

    def __unicode__(self):
        return self.nom

class Region(models.Model):
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=20)
    code = models.CharField(max_length=6)

    def __unicode__(self):
        return self.nom

class District(models.Model):
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=40)
    code = models.CharField(max_length=6)

    def __unicode__(self):
        return self.nom

class Commune(models.Model):
    district = models.ForeignKey(District, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=40)
    code = models.CharField(max_length=6)

    def __unicode__(self):
        return self.nom
