from rest_framework import serializers
from django.db.models import Sum
from .models import Inventario, IngresoInventario, Proveedor, Categoria, Cliente, OrdenTaller


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['uuid', 'nombre']
        read_only_fields = ['uuid']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['uuid', 'nombre']
        read_only_fields = ['uuid']


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['uuid', 'nombre', 'documento', 'telefono', 'correo', 'ciudad', 'direccion', 'contacto', 'observacion']
        read_only_fields = ['uuid']


# Corte / Presentacion / Lavanderia related serializers removed as these models
# were intentionally purged during cleanup. OrdenTaller serializer is provided
# below to support the new workshop order API.


class IngresoInventarioListSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        model = IngresoInventario
        fields = ['uuid', 'inventario', 'cantidad', 'fecha', 'numero_factura', 'valor_ingreso', 'proveedor', 'observaciones', 'created']
        read_only_fields = ['uuid', 'created']


class IngresoInventarioCreateSerializer(serializers.ModelSerializer):
    proveedor = serializers.SlugRelatedField(queryset=Proveedor.objects.all(), slug_field='uuid', allow_null=True, required=False)

    class Meta:
        model = IngresoInventario
        fields = ['uuid', 'cantidad', 'fecha', 'numero_factura', 'valor_ingreso', 'proveedor', 'observaciones']
        read_only_fields = ['uuid']


class InventarioListRetrieveSerializer(serializers.ModelSerializer):
    valor_total = serializers.SerializerMethodField()
    proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        model = Inventario
        fields = ['uuid', 'codigo', 'nombre', 'descripcion', 'observaciones', 'proveedor', 'cantidad', 'valor_ingreso', 'numero_factura', 'fecha', 'precio_unitario', 'valor_total', 'categoria', 'estado', 'created', 'modified']
        read_only_fields = ['uuid', 'valor_total', 'created', 'modified']

    def get_valor_total(self, obj):
        return float(obj.valor_total)


class InventarioCreateUpdateSerializer(serializers.ModelSerializer):
    proveedor = serializers.SlugRelatedField(queryset=Proveedor.objects.all(), slug_field='uuid', allow_null=True, required=False)

    class Meta:
        model = Inventario
        fields = ['uuid', 'codigo', 'nombre', 'descripcion', 'observaciones', 'proveedor', 'cantidad', 'valor_ingreso', 'numero_factura', 'fecha', 'precio_unitario', 'categoria', 'estado']
        read_only_fields = ['uuid']


class OrdenTallerSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_uuid = serializers.SlugRelatedField(queryset=Cliente.objects.all(), slug_field='uuid', write_only=True, source='cliente', allow_null=True, required=False)

    class Meta:
        model = OrdenTaller
        fields = ['uuid', 'order_number', 'cliente', 'cliente_uuid', 'fecha', 'status', 'ingreso', 'revision', 'procedimiento', 'entrega', 'created', 'modified']
        read_only_fields = ['uuid', 'created', 'modified']

