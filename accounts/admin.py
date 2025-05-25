from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Customer

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Tell DjangoAdmin to use email for ordering and list display
    ordering = ('email',)
    list_display = ('email', 'full_name', 'user_type', 'is_staff')
    search_fields = ('email', 'full_name')

    # Redefine which fields show up on the “change” page
    fieldsets = (
        (None,               {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'user_type')}),
        (_('Permissions'),   {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Redefine which fields show up when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'user_type', 'password1', 'password2'),
        }),
    )

    # Remove username (it no longer exists)
    # You don't need to override `username` since we set USERNAME_FIELD = 'email'
    model = User


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('boards', 'wishlist', 'cart', 'saved_items')

