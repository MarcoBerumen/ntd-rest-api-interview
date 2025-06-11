from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Planet(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    population = models.CharField(max_length=50, null=True, blank=True)
    terrains = models.ManyToManyField('Terrain', blank=True)
    climates = models.ManyToManyField('Climate', blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Terrain(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
class Climate(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']