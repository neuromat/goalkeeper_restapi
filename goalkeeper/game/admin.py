from django.contrib import admin
from .models import Institution, GameConfig, GoalkeeperGame, MemoryGame, WarmUp, Level, States


class StatesInline(admin.TabularInline):
    model = States
    extra = 3


class GoalkeeperGameAdmin(admin.ModelAdmin):
    list_display = ('config', 'phase', 'depth', 'sequence',)
    list_display_links = ('phase', 'sequence')
    exclude = ('game_type',)
    inlines = [StatesInline]


class MemoryGameAdmin(admin.ModelAdmin):
    list_display = ('config', 'level', 'phase', 'sequence')
    list_display_links = ('phase', 'sequence')
    exclude = ('game_type',)


class WarmUpAdmin(admin.ModelAdmin):
    list_display = ('config', 'level', 'sequence',)
    list_display_links = ('sequence',)
    exclude = ('game_type',)


admin.site.register(Institution)
admin.site.register(GameConfig)
admin.site.register(Level)
admin.site.register(GoalkeeperGame, GoalkeeperGameAdmin)
admin.site.register(MemoryGame, MemoryGameAdmin)
admin.site.register(WarmUp, WarmUpAdmin)
