from django.contrib import admin
from .models import Empresa, Profile, Departamento, Ciudad
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class DepartamentoResource(resources.ModelResource):
    class Meta:
        model = Departamento

class CiudadResource(resources.ModelResource):
    class Meta:
        model = Ciudad

class DepartamentoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ('id', 'nombre',)
    list_display = ('id', 'nombre',)
    resourse_class = DepartamentoResource

class CiudadAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nombre', 'get_departamento', 'delivery', 'delivery_price', )
    search_fields = ('id', 'nombre', 'get_departamento', 'delivery', 'delivery_price', )
    resourse_class = CiudadResource

admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(Ciudad, CiudadAdmin)
admin.site.register(Profile)
admin.site.register(Empresa)
