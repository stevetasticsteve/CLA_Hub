from django.contrib import admin

import lexicon.models


class VerbAdmin(admin.ModelAdmin):
    pass


class MatatVerbAdmin(admin.ModelAdmin):
    pass


class WordAdmin(admin.ModelAdmin):
    list_display = ("kgu", "eng")
    search_fields = ("kgu",)


admin.site.register(lexicon.models.ImengisVerb, VerbAdmin)
admin.site.register(lexicon.models.KovolWord, WordAdmin)
admin.site.register(lexicon.models.MatatVerb, MatatVerbAdmin)
