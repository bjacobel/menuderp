from django.contrib import admin
from models import Food, Alert, Profile

class FoodsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('More Info', {'fields': ['last_date', 'next_date'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'last_date', 'next_date')
    #list_filter = ['year', 'suffix']
    search_fields = ['name']

admin.site.register(Food, FoodsAdmin)

class AlertsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['food']}),
        ('More Info', {'fields': ['frequency'], 'classes': ['collapse']}),
    ]
    list_display = ('food', 'frequency')
    #list_filter = ['year', 'suffix']
    search_fields = ['food', 'frequency']

admin.site.register(Alert, AlertsAdmin)