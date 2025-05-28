from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.District)

# class CustomAdmin(admin.ModelAdmin):
#     def save_model(self, request, obj, form, change):
#         if not obj.name:
#             obj.name = None
       
#         super().save_model(request, obj, form, change)
    
admin.site.register(models.State)
    
admin.site.register(models.Country_Codes)
admin.site.register(models.TaskModel)
admin.site.register(models.Workers)
admin.site.register(models.UserTaskResponse)