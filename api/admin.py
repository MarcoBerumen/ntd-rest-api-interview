from django.contrib import admin
from .models import Planet

# Register your models here.
@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ('name', 'population', 'terrains', 'climates', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)