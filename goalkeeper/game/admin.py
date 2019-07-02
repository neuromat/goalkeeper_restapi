from django.contrib import admin
from .models import Level, WarmUp


class WarmUpAdmin(admin.ModelAdmin):
    list_display = ('config', 'sequence',)
    list_display_links = ('sequence',)
    exclude = ('game_type',)


admin.site.register(Level)
admin.site.register(WarmUp, WarmUpAdmin)
