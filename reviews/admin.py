from django.contrib import admin
from .models import Review


# Register your models here.
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','uname','review','rating','product')
admin.site.register(Review, ReviewAdmin)