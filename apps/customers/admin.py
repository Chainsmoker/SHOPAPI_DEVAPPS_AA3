from django.contrib import admin
from .models import Customer

admin.site.register(Customer)

admin.site.site_header = 'E-commerce Admin'
admin.site.site_title = 'E-commerce Admin Portal'
admin.site.index_title = 'E-commerce Admin Portal'
