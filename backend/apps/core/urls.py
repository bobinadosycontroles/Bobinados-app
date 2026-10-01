from django.urls import path

from .views import (
    InventarioListCreateAPIView,
    InventarioRetrieveUpdateDestroyAPIView,
    IngresoListCreateAPIView,
    ProveedorListCreateAPIView,
    ProveedorRetrieveUpdateDestroyAPIView,
    CategoriaListCreateAPIView,
    CategoriaRetrieveUpdateDestroyAPIView,
    ClienteListCreateAPIView,
    ClienteRetrieveUpdateDestroyAPIView,
    OrdenTallerListCreateAPIView,
    OrdenTallerRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path('inventario/', InventarioListCreateAPIView.as_view(), name='core-inventario-api'),
    path('inventario/<uuid:uuid>/', InventarioRetrieveUpdateDestroyAPIView.as_view(), name='core-inventario-detail-api'),
    path('inventario/<uuid:uuid>/ingresos/', IngresoListCreateAPIView.as_view(), name='core-inventario-ingresos-api'),
    path('proveedor/', ProveedorListCreateAPIView.as_view(), name='core-proveedor-api'),
    path('proveedor/<uuid:uuid>/', ProveedorRetrieveUpdateDestroyAPIView.as_view(), name='core-proveedor-detail-api'),
    path('categoria/', CategoriaListCreateAPIView.as_view(), name='core-categoria-api'),
    path('categoria/<uuid:uuid>/', CategoriaRetrieveUpdateDestroyAPIView.as_view(), name='core-categoria-detail-api'),
    path('cliente/', ClienteListCreateAPIView.as_view(), name='core-cliente-api'),
    path('cliente/<uuid:uuid>/', ClienteRetrieveUpdateDestroyAPIView.as_view(), name='core-cliente-detail-api'),
    path('taller/', OrdenTallerListCreateAPIView.as_view(), name='core-taller-api'),
    path('taller/<uuid:uuid>/', OrdenTallerRetrieveUpdateDestroyAPIView.as_view(), name='core-taller-detail-api'),
    
]
