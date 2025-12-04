from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Perfil, OfertaDeEmpleo, Solicitud, Mensaje, CategoriaDeServicio

# Configuración para ver el Perfil dentro del Usuario
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline, )

# Re-registramos el User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registros simples
admin.site.register(CategoriaDeServicio)
admin.site.register(OfertaDeEmpleo)
admin.site.register(Solicitud)
admin.site.register(Mensaje)