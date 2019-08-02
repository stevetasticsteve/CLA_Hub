from django.contrib import admin

from CE.models import CultureEvent, Texts, PictureModel

class CEAdmin(admin.ModelAdmin):
    pass

class TextsAdmin(admin.ModelAdmin):
    pass

class PicturesAdmin(admin.ModelAdmin):
    pass

admin.site.register(CultureEvent, CEAdmin)
admin.site.register(Texts, TextsAdmin)
admin.site.register(PictureModel, PicturesAdmin)

