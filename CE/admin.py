from django.contrib import admin

from CE.models import CultureEvent, Text, Picture, Visit


class CEAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_modified', 'last_modified_by')
    exclude = ('description',)


class TextsAdmin(admin.ModelAdmin):
    list_display = ('text_title', 'ce', 'phonetic_standard', 'valid_for_DA', 'discourse_type')
    list_filter = ('phonetic_standard', 'valid_for_DA', 'discourse_type')


class PicturesAdmin(admin.ModelAdmin):
    pass


class VisitsAdmin(admin.ModelAdmin):
    list_display = ('ce', 'date', 'team_present')


admin.site.register(CultureEvent, CEAdmin)
admin.site.register(Text, TextsAdmin)
admin.site.register(Picture, PicturesAdmin)
admin.site.register(Visit, VisitsAdmin)
