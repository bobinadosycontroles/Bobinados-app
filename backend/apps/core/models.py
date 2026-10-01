import uuid
from django.db import models
# JSONField compatibility: Django 3.1+ exposes models.JSONField; older versions
# require postgres JSONField from contrib.postgres. Import conditionally.
try:
    # Django 3.1+
    JSONField = models.JSONField
except AttributeError:
    from django.contrib.postgres.fields import JSONField
from model_utils.models import TimeStampedModel


class Inventario(TimeStampedModel):
    """
    Representa un producto en el inventario
    """
    ESTADO_ACTIVO = 'AC'
    ESTADO_INACTIVO = 'IN'
    ESTADOS = (
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    )
    
    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='código'
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name='nombre'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='descripción'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='observaciones'
    )
    proveedor = models.ForeignKey(
        'Proveedor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='productos',
        verbose_name='proveedor'
    )
    cantidad = models.IntegerField(
        default=0,
        verbose_name='cantidad'
    )
    valor_ingreso = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='valor de ingreso'
    )
    numero_factura = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='número de factura'
    )
    fecha = models.DateField(
        blank=True,
        null=True,
        verbose_name='fecha'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='precio unitario'
    )
    categoria = models.CharField(
        max_length=255,
        verbose_name='categoría'
    )
    estado = models.CharField(
        choices=ESTADOS,
        default=ESTADO_ACTIVO,
        max_length=2,
        verbose_name='estado'
    )

    class Meta:
        app_label = 'core'
        verbose_name = 'inventario'
        verbose_name_plural = 'inventarios'
        ordering = ['-created']
        default_permissions = ()

    def __str__(self):
        """
        Retorna la representación de la instancia del modelo
        """
        return f"{self.codigo} - {self.nombre}"

    @property
    def valor_total(self):
        """
        Calcula el valor total (cantidad * precio_unitario)
        """
        return self.cantidad * self.precio_unitario

    def agregar_ingreso(self, cantidad, fecha=None, numero_factura=None, valor_ingreso=0, proveedor=None, observaciones=None):
        """Crea un registro de IngresoInventario y actualiza la cantidad del producto"""
        from django.utils import timezone
        fecha = fecha or timezone.now().date()
        ingreso = IngresoInventario.objects.create(
            inventario=self,
            cantidad=cantidad,
            fecha=fecha,
            numero_factura=numero_factura,
            valor_ingreso=valor_ingreso,
            proveedor=proveedor,
            observaciones=observaciones
        )
        # Actualizar la cantidad en inventario
        self.cantidad = (self.cantidad or 0) + cantidad
        # Opcional: actualizar valor_ingreso y fecha de producto
        if valor_ingreso:
            self.valor_ingreso = valor_ingreso
        if numero_factura:
            self.numero_factura = numero_factura
        if fecha:
            self.fecha = fecha
        self.save()
        return ingreso


class Proveedor(models.Model):
    """Proveedor simple para usar en q-select más adelante"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=255, verbose_name='nombre')

    class Meta:
        app_label = 'core'
        verbose_name = 'proveedor'
        verbose_name_plural = 'proveedores'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Categoría de productos"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=255, verbose_name='nombre', unique=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    """Cliente para pedidos o ventas"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=255, verbose_name='nombre')
    documento = models.CharField(max_length=255, blank=True, null=True, verbose_name='documento')
    telefono = models.CharField(max_length=255, blank=True, null=True, verbose_name='teléfono')
    correo = models.CharField(max_length=255, blank=True, null=True, verbose_name='correo')
    ciudad = models.CharField(max_length=255, blank=True, null=True, verbose_name='ciudad')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name='dirección')
    contacto = models.CharField(max_length=255, blank=True, null=True, verbose_name='contacto')
    observacion = models.TextField(blank=True, null=True, verbose_name='observación')

    class Meta:
        app_label = 'core'
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    def __str__(self):
        return self.nombre


class IngresoInventario(TimeStampedModel):
    """Registro histórico de ingresos al inventario"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        related_name='ingresos'
    )
    cantidad = models.IntegerField(verbose_name='cantidad')
    fecha = models.DateField(verbose_name='fecha')
    numero_factura = models.CharField(max_length=255, blank=True, null=True, verbose_name='número de factura')
    valor_ingreso = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='valor de ingreso')
    proveedor = models.ForeignKey('Proveedor', null=True, blank=True, on_delete=models.SET_NULL, related_name='ingresos')
    observaciones = models.TextField(blank=True, null=True, verbose_name='observaciones')

    class Meta:
        app_label = 'core'
        verbose_name = 'ingreso inventario'
        verbose_name_plural = 'ingresos inventario'
        ordering = ['-created']

    def __str__(self):
        return f"Ingreso {self.cantidad} - {self.inventario.codigo} - {self.fecha}"


# NOTE: Programacion, ProgramacionInsumo, Corte, CorteDetalle, Presentacion and Lavanderia
# have been removed from the active data model as part of project cleanup.
# They were intentionally purged because these modules are not used in the current
# product scope. New `OrdenTaller` model is defined below to represent workshop orders.


# OrdenTaller: nuevo modelo que reemplaza el flujo antiguo de programacion/presentacion/corte/lavanderia
class OrdenTaller(TimeStampedModel):
    """Representa una orden de taller con sus etapas serializadas en JSON.

    Campos principales:
    - `order_number`: texto legible para la orden (ej. OT-10715)
    - `cliente`: FK opcional al modelo `Cliente`
    - `fecha`: fecha de la orden
    - `status`: etapa actual ('ingreso','revision','procedimiento','entrega','cerrada')
    - `ingreso`, `revision`, `procedimiento`, `entrega`: JSONFields con los datos de cada etapa
    """
    STATUS_INGRESO = 'ingreso'
    STATUS_REVISION = 'revision'
    STATUS_PROCEDIMIENTO = 'procedimiento'
    STATUS_ENTREGA = 'entrega'
    STATUS_CERRADA = 'cerrada'

    STATUS_CHOICES = (
        (STATUS_INGRESO, 'Ingreso'),
        (STATUS_REVISION, 'Revision'),
        (STATUS_PROCEDIMIENTO, 'Procedimiento'),
        (STATUS_ENTREGA, 'Entrega'),
        (STATUS_CERRADA, 'Cerrada'),
    )

    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    order_number = models.CharField(max_length=100, verbose_name='order_number', blank=True, null=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL, related_name='ordenes_taller')
    fecha = models.DateField(blank=True, null=True, verbose_name='fecha')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_INGRESO)

    ingreso = JSONField(default=dict, blank=True)
    revision = JSONField(default=dict, blank=True)
    procedimiento = JSONField(default=dict, blank=True)
    entrega = JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'orden taller'
        verbose_name_plural = 'ordenes taller'
        ordering = ['-created']

    def __str__(self):
        return f"{self.order_number or self.uuid} - {self.cliente or ''}"