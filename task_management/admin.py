from django.contrib import admin
from .models import Task

# Customize Admin Site Branding
admin.site.site_header = "Task Management"
admin.site.site_title = "Task Management Admin"
admin.site.index_title = "Administration Dashboard"

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')