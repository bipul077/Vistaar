from django.contrib import admin
from .models import Category,Products,Subcategory,Review

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    #list_display = ['product_name', 'slug', 'description', 'available', 'created', 'updated']
    prepopulated_fields = {'slug': ('product_name',)}
    
    
@admin.register(Subcategory)
class ProductAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title',)}

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','uname','subject', 'created_at', 'updated_at')
admin.site.register(Review, ReviewAdmin)



