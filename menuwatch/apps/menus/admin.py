from django.contrib import admin
from models import Food, Watch, Profile


class FoodsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['name', 'attrs']}),
        ('Up Next',       {'fields': ['next_date', 'location', 'meal', 'foodgroup']}),
        ('More',       {'fields': ['last_date']}),
    ]
    list_display = ('name', 'next_date', 'meal', 'location', 'foodgroup', 'attrs', 'num_watches', 'last_date', )
    list_filter = ['meal', 'foodgroup', 'location', 'attrs']
    search_fields = ['name']

admin.site.register(Food, FoodsAdmin)


class WatchesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['food', 'owner']}),
    ]
    list_display = ('food',  'owner')
    search_fields = ['food', 'owner']

admin.site.register(Watch, WatchesAdmin)


class ProfilesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['user', 'pro', 'frequency']}),
    ]
    list_display = ('fullname', 'email', 'used_watches', 'pro', 'frequency_name', 'can_create_new_watches')
    list_filter = ['pro', 'frequency']
    search_fields = ['firstname', 'lastname', 'email']

admin.site.register(Profile, ProfilesAdmin)
