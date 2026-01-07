from django.contrib import admin
from .models import Task

# Customize Admin Site Branding
admin.site.site_header = "Task Management"
admin.site.site_title = "Task Management Admin"
admin.site.index_title = "Administration Dashboard"

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        """RBAC: Ensure normal users only see their own tasks."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_readonly_fields(self, request, obj=None):
        """RBAC: Prevent normal users from changing the task owner."""
        if not request.user.is_superuser:
            return ('user',)
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        """RBAC: Automatically assign the task to the current user if not admin."""
        if not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)