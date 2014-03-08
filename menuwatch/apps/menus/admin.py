from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db import models
from models import Food, Watch, Profile


# classes for filtering FoodsAdmin
class UpcomingDatesFilter(SimpleListFilter):
    title = ('Has Upcoming Dates?')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'hasupcoming'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('0', ('False')),
            ('1', ('True')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(next_dates__exact=None)
        return queryset.exclude(next_dates__exact=None)

class FoodsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['name', 'attrs']}),
        ('Up Next',       {'fields': ['location', 'meal', 'foodgroup']}),
        ('More',       {'fields': ['last_date']}),
    ]
    list_display = ('name', 'meal', 'location', 'foodgroup', 'attrs', 'watched_by', 'last_date', 'peek_next_date')
    list_filter = ['meal', 'foodgroup', 'location', 'attrs', UpcomingDatesFilter]
    search_fields = ['name']

    def queryset(self, request):
        return Food.objects.annotate(watch_count=models.Count('watch'))

    def watched_by(self, inst):
        return inst.watch_count

    watched_by.admin_order_field = 'watch_count'

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
        (None,                  {'fields': ['user', 'pro', 'onboarded', 'frequency']}),
    ]
    list_display = ('fullname', 'email', 'used_watches', 'pro', 'onboarded', 'frequency_name', 'can_create_new_watches')
    list_filter = ['pro', 'onboarded', 'frequency']
    search_fields = ['firstname', 'lastname', 'email']

admin.site.register(Profile, ProfilesAdmin)
