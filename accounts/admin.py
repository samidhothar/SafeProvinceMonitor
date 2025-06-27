"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """Extended user admin with profile inline."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)

    def get_role(self, instance):
        """Get user role from profile."""
        if hasattr(instance, 'profile'):
            return instance.profile.get_role_display()
        return 'No Profile'
    get_role.short_description = 'Role'

    def get_inline_instances(self, request, obj=None):
        """Return inline instances."""
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles."""
    list_display = ('user', 'role', 'department', 'district', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified', 'department', 'district')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'is_verified')
        }),
        ('Professional Details', {
            'fields': ('department', 'district', 'bio')
        }),
        ('Media', {
            'fields': ('avatar',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
