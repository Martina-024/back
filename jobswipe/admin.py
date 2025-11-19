from django.contrib import admin
from .models import Perfil, CategoriaDeServicio, OfertaDeEmpleo, Solicitud, Mensaje

# Registrar los modelos simples
admin.site.register(CategoriaDeServicio)

# Personalizar el admin para Perfil
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'telefono')
    search_fields = ('user__username', 'telefono')
    list_filter = ('tipo',)

# Personalizar el admin para OfertaDeEmpleo
@admin.register(OfertaDeEmpleo)
class OfertaDeEmpleoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'perfil_empleador', 'categoria', 'estado', 'es_inclusion', 'fecha_publicacion')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('estado', 'categoria', 'es_inclusion')

# Personalizar el admin para Solicitud
@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('User_candidato', 'oferta', 'estado', 'fecha_postulacion')
    search_fields = ('User_candidato__username', 'oferta__titulo')
    list_filter = ('estado',)

# Personalizar el admin para Mensaje
@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    # --- ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
    # Cambiamos 'oferta' (que ya no existe) por 'solicitud'
    list_display = ('User_origen', 'User_destino', 'solicitud', 'fecha', 'leido')
    # ---------------------------------
    
    list_filter = ('fecha', 'leido')
    search_fields = ('contenido', 'User_origen__username', 'User_destino__username')
    
    # Hacemos que los campos de solo lectura se muestren en el admin
    readonly_fields = ('fecha',)