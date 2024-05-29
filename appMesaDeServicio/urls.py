from django.urls import path
from . import views

urlpatterns = [
    path("",views.index),
    path("login/",views.login),
    path("administrador/",views.inicioAdministrador),
    path("tecnico/",views.inicioTecnico),
    path("empleado/",views.inicioEmpleado),
    path("vistaSolicitud/",views.vistaSolicitud),
    path("solicitud/", views.solicitud_view),
    path("registro-solicitud/", views.registro_solicitud),
    path("listarCasosParaAsignar/",views.listarCasos),
    path("salir/",views.salir),
]