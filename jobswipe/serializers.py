from rest_framework import serializers
from .models import OfertaDeEmpleo

class OfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfertaDeEmpleo
        fields = ['id', 'titulo', 'descripcion', 'categoria', 'fecha_publicacion', 'es_inclusion']