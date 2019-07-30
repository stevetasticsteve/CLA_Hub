from django.contrib import admin

from CE.models import CultureEvent, Texts, Pictures

class CEAdmin(admin.ModelAdmin):
    pass

class TextsAdmin(admin.ModelAdmin):
    pass

class PicturesAdmin(admin.ModelAdmin):
    pass

admin.site.register(CultureEvent, CEAdmin)
admin.site.register(Texts, TextsAdmin)
admin.site.register(Pictures, PicturesAdmin)

