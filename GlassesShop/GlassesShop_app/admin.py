from django.contrib import admin
from .models import  GlassesOrder, Lens, MToM

admin.site.register(GlassesOrder)
admin.site.register(Lens)
admin.site.register(MToM)