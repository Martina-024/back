from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. URLs del panel de Admin
    path('admin/', admin.site.urls),
    
    # 2. URLs de autenticación de Django (para /login/, /logout/)
    # Las ponemos aquí para que se carguen correctamente
    path('', include('django.contrib.auth.urls')),
    
    # 3. URLs de tu aplicación (para la página de inicio '/', /register/, etc.)
    # Esta debe ir DESPUÉS de las de auth para que las intercepte correctamente.
    path('', include('jobswipe.urls')),
]

# NO DEBE HABER NADA MÁS AQUÍ
# (Especialmente no debe haber líneas con "re_path", "static.serve" o "^(?P<path>.*)$")