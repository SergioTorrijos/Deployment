from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator


class Letras(models.Model):
    fecha = models.IntegerField(max_length=4)
    autor = models.CharField(max_length=50) 
    grupo = models.CharField(max_length=50) 
    letra = models.TextField()
    def __unicode__(self):
        return unicode(self.autor)
    
class Noticias(models.Model):
    fecha = models.IntegerField(max_length=4)
    titular = models.TextField()
    def __unicode__(self):
        return unicode(self.titular)
 
class UserInformation(models.Model):
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    gender = models.CharField(max_length=1, choices=(('F', 'Female'),('M','Male'),))
    zipCode = models.CharField(max_length=8)
    def __unicode__(self):
        return unicode(self.gender+self.zipCode)
