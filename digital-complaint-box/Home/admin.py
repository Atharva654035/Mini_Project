from django.contrib import admin
from .models import Complaint, ComplaintCategory, ComplaintUpdate
from django.utils.html import format_html

# Register your models here.

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'division', 'status', 'priority', 'complaint_date')
    list_filter = ('status', 'priority', 'complaint_date', 'category')
    search_fields = ('name', 'division', 'complaint', 'user__username')
    readonly_fields = ('complaint_date', 'user')
    list_editable = ('status', 'priority')
    
    fieldsets = (
        ('Complaint Information', {
            'fields': ('user', 'name', 'division', 'complaint', 'complaint_img', 'category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'admin_response')
        }),
        ('Dates', {
            'fields': ('complaint_date', 'resolved_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'old_status', 'new_status', 'updated_by', 'updated_at')
    list_filter = ('old_status', 'new_status', 'updated_at')
    readonly_fields = ('updated_at',)
