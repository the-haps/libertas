from django.contrib import admin
from .models import Ausgabe, Code

# Register your models here.


class AusgabeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Generell',               {
         'fields': ['name', 'number', 'publish_date']}),
        ('Dateien', {'fields': ['file', 'leseprobe', 'thumbnail']}),
    ]

    search_fields = ['name', 'number']
    list_display = ('name', 'number', 'publish_date')
    list_filter = ['publish_date']
    list_display_links = ['name']
    ordering = ['-number']


class CodeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,       {'fields': ['code', 'creation', 'ausgabe']}),
        ('Einlösung', {'fields': ['user', 'redeemed']})
    ]

    search_fields = ['code', 'user__username']
    autocomplete_fields = ('ausgabe', 'user')
    list_display = ('censored_code', 'ausgabe', 'creation', 'user', 'redeemed')
    readonly_fields = ['code', 'creation']

    def censored_code(self, obj):
        return "%s****" % (obj.code[:-4])
    censored_code.short_description = 'Code'


admin.site.register(Ausgabe, AusgabeAdmin)
admin.site.register(Code, CodeAdmin)
