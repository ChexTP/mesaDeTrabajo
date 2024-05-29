from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from appMesaDeServicio.models import OficinaAmbiente,Solicitud,Caso
from random import randint
from .models import *
from django.db import Error,transaction

from datetime import datetime
# para correo
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException


# Create your views here.

def index(request):
    return render(request, "login.html")

def inicioAdministrador(request):
    if request.user.is_authenticated:
        datoSesion = {"user": request.user,
                      "rol": request.user.groups.get().name
                      }
        return render(request,"administrador/index.html",datoSesion)
    else:
        mensaje="debe iniciar sesion primero"
        return render(request,"login.html",{"mensaje":mensaje})

def inicioTecnico(request):
    if request.user.is_authenticated:
        datoSesion = {"user": request.user,
                      "rol": request.user.groups.get().name
                      }
        return render(request,"tecnico/index.html",datoSesion)
    else:
        mensaje="debe iniciar sesion primero"
        return render(request,"login.html")
    
def inicioEmpleado(request):
    if request.user.is_authenticated:
        datoSesion = {"user": request.user,
                      "rol": request.user.groups.get().name
                      }
        return render(request,"empleado/index.html",datoSesion)
    else:
        mensaje="debe iniciar sesion primero"
        return render(request,"login.html")
    
def salir(request):
    auth.logout(request)
    return render(request,"login.html")

@csrf_exempt
def login(request):
    username= request.POST["user"]
    password=request.POST["password"]
    user = authenticate(username=username,password=password)
    if user is not None:
        #registrar la variable de sesion
        auth.login(request, user)
        if user.groups.filter(name="Administrador").exists():
            return redirect('/administrador')
        elif user.groups.filter(name='Tecnico').exists():
            return redirect('/tecnico')
        else:
            return redirect('/empleado')
    else:
        mensaje="ususario o contraseña incorrecta"
        return render(request,"login.html",{"mensaje":mensaje})
    
    
def registrarSolicitud(request):
    try:
        with transaction.atomic():
            user = request.user
            descripcion = request.POST['descripcion']
            idOficinaAmbiente = int(request.POST['id_ambiente'])
            oficinaAmbiente = OficinaAmbiente.objects.get(pk=idOficinaAmbiente)
            solicitud = Solicitud(solUsuario=user, 
                                  solDescripcion=descripcion,
                                  solOficinaAmbiente=oficinaAmbiente)
            solicitud.save()
            # obtener año para en el consecutivo agregar el año.
            fecha = datetime.now()
            year = fecha.year
            # obtener el número de solicitudes hechas por año actual
            consecutivoCaso = Solicitud.objects.filter(
                fechaHoraCreacion__year=year).count()
            
            consecutivo = randint(1, 1000)
            codigo_caso = f"REQ {str(consecutivo).rjust(5, '0')}"
            caso_user = User.objects.filter(groups__name__in=['Administrador']).first()
            caso = Caso(
                casSolicitud=solicitud,
                casCodigo=codigo_caso,
                casEstado='Solicitada',
                casUsuario=caso_user
            )
            caso.save()

            return render(request, 'empleado/solicitud.html')
            # enviar el correo al empleado
            # asunto = 'Registro Solicitud - Mesa de Servicio'
            # mensajeCorreo = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
            #     informarle que su solicitud fue registrada en nuestro sistema con el número de caso \
            #     <b>{codigoCaso}</b>. <br><br> Su caso será gestionado en el menor tiempo posible, \
            #     según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
            #     <br><br>Lo invitamos a ingresar a nuestro sistema en la siguiente url:\
            #     http://mesadeservicioctpicauca.sena.edu.co.'
            # # crear el hilo para el envío del correo
            # thread = threading.Thread(
            #     target=enviarCorreo, args=(asunto, mensajeCorreo, [user.email]))
            # # ejecutar el hilo
            # thread.start()
            mensaje = "Se ha registrado su solicitud de manera exitosa"
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"

    oficinaAmbientes = OficinaAmbiente.objects.all()
    retorno = {"mensaje": mensaje, "oficinasAmbientes": oficinaAmbientes}
    return render(request, "empleado/solicitud.html", retorno)

    

from random import randint
# registrando las solicitudes
def registro_solicitud(request):
    try:
        # valida que se guarde la información en ambas colecciones, no solamente en una
        with transaction.atomic():
            # guardando solicitud
            user = request.user
            descripcion = request.POST['descripcion']
            idOficinaAmbiente = int(request.POST['id_oficina_ambiente'])  # Aquí estaba el error, cambiar paréntesis por corchetes
            oficinaAmbiente = OficinaAmbiente.objects.get(pk=idOficinaAmbiente)
            
            solicitud = Solicitud(
                solsuario=user,
                solDescripcion=descripcion,
                solOficinaAmbiente=oficinaAmbiente
            )
            solicitud.save()

            # guardando caso
            consecutivo = randint(1, 1000)
            codigo_caso = f"REQ {str(consecutivo).rjust(5, '0')}"
            caso_user = User.objects.filter(groups__name__in=['Administrador']).first()
            caso = Caso(
                solicitudCaso=solicitud,
                codigo=codigo_caso,
                estado='Solicitada',
                tecnicoAsignado=caso_user
            )
            caso.save()

            return render(request, 'empleado/solicitud.html')

    # en caso de que haya algún error
    except Exception as error:  # Cambié Error por Exception
        transaction.rollback()
        print("Error al registrar la solicitud")
        print(error)
        mensaje = str(error)  # Asegúrate de convertir el error a cadena si planeas pasarlo a la plantilla
        return render(request, 'empleado/solicitud.html', {"message": mensaje})


def vistaSolicitud(request):
    if request.user.is_authenticated:
        oficinaAmbiente=OficinaAmbiente.objects.all()
        datoSesion = {"user": request.user,
                      "rol": request.user.groups.get().name,
                      'oficinasAmbientes': oficinaAmbiente,
                      }
        return render(request,"empleado/solicitud.html",datoSesion)
    else:
        mensaje="debe iniciar sesion"
        return render(request,"login.html",{"mensaje":mensaje})   
    
def listarCasos(request):
    mensaje=''
    try:
        listarCasos= Caso.objects.filter(casEstado="Solicitada")
        tecnicos=User.objects.filter(groups__name__in=["Tecnicos"])
    except Error as error:
        mensaje = str(error)
    retorno= {"listarCasos":listarCasos,
              "tecnicos":tecnicos,
              'mensaje':mensaje}
    return render(request,"administrador/listaCasos.html",retorno)

def asignarTecnicoCaso(request):
    if request.user.is_autenthicated:
        try:
            idTecnico = int(request.POST['cbTecnico'])
            userTecnico = User.objects.get(pk=idTecnico)
            idCaso= int(request.POST['idCaso'])
            caso= Caso.objects.get(pk=idCaso)
            caso.casEstado=userTecnico
            caso.save()
            mensaje="caso asignado"
        #auiq se debe poner el codigo para enviar el correo de notificacion  al tecnico
        except Error as error:
            mensaje=str(error)
        
        return redirect('/listarCasos/')
    else:
        mensaje='Debe iniciar sesion primero'
        return render(request,"login.html",{'mensaje':mensaje})

