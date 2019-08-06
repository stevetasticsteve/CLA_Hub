from django.contrib import admin

from CE.models import CultureEvent, TextModel, PictureModel

class CEAdmin(admin.ModelAdmin):
    pass
    # prepopulated_fields = { 'slug': ('title',)}

class TextsAdmin(admin.ModelAdmin):
    pass

class PicturesAdmin(admin.ModelAdmin):
    pass

admin.site.register(CultureEvent, CEAdmin)
admin.site.register(TextModel, TextsAdmin)
admin.site.register(PictureModel, PicturesAdmin)

