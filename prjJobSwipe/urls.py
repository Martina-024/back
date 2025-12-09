from django.contrib import admin
from django.urls import path, include

# Importanciones para la API
from rest_framework import routers, viewsets
from jobswipe.models import OfertaDeEmpleo
from jobswipe.serializers import OfertaSerializer

# Config fde la vista
class OfertaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfertaDeEmpleo.objects.filter(estado='activa')
    serializer_class = OfertaSerializer

# Configdel router
router = routers.DefaultRouter()
router.register(r'ofertas', OfertaViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('django.contrib.auth.urls')),
    path('', include('jobswipe.urls')),
]