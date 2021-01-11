from django.contrib import admin

from .models import *
# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("categories",)

class WatchListAdmin(admin.ModelAdmin):
    filter_horizontal = ("listings",)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(WatchList, WatchListAdmin)