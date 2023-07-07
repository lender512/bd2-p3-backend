from django.db import models

# Create your models here.
class FaceVector(models.Model):
    vector = models.TextField()
    name = models.CharField(max_length=1000)
    distance = models.FloatField(default=0.0)
