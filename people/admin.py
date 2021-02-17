from django.contrib import admin

import people.models


class PersonAdmin(admin.ModelAdmin):
    pass


class VillageAdmin(admin.ModelAdmin):
    pass


class MedicalAssessmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(people.models.Person, PersonAdmin)
admin.site.register(people.models.MedicalAssessment, MedicalAssessmentAdmin)
admin.site.register(people.models.Village, VillageAdmin)
