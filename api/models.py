from django.db import models

# Create your models here.
class Planet(models.Model):
    name = models.CharField(max_length=200, unique=True)
    population = models.CharField(max_length=50, null=True, blank=True)
    terrains = models.JSONField(null=True, blank=True) 
    climates = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']