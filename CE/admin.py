from django.contrib import admin

from CE.models import CultureEvent, Text, Picture, Visit, Question


class CEAdmin(admin.ModelAdmin):
    list_display = ("title", "last_modified", "last_modified_by")
    exclude = ("description",)


class TextsAdmin(admin.ModelAdmin):
    list_display = ("text_title", "ce", "phonetic_standard", "discourse_type")
    list_filter = ("phonetic_standard", "discourse_type")


class PicturesAdmin(admin.ModelAdmin):
    pass


class VisitsAdmin(admin.ModelAdmin):
    list_display = ("ce", "date", "team_present")


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "answer", "ce")


admin.site.register(CultureEvent, CEAdmin)
admin.site.register(Text, TextsAdmin)
admin.site.register(Picture, PicturesAdmin)
admin.site.register(Visit, VisitsAdmin)
admin.site.register(Question, QuestionAdmin)
