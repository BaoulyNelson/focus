from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model  = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('role', 'bio', 'avatar', 'site_web', 'twitter')


class UserAdminEtendu(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, obj):
        try:
            return obj.userprofile.get_role_display()
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, UserAdminEtendu)
