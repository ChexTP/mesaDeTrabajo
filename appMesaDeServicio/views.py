from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from appMesaDeServicio.models import OficinaAmbiente,Solicitud
from random import randint
from .models import *
from django.db import Error,transaction


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
    
    
def registroSolicitud(request):
    
    try:
        with transaction.atomic():
            user=request,user
            descripcion=request.POST['descripcion']
            idOficinaAmbiente=int(request.POST('id_oficina_ambiente'))
            OficinaAmbiente=OficinaAmbiente.objects.get(pk=idOficinaAmbiente)
            solicitud = Solicitud(solsuario=user,
                                    solDescripcion=descripcion,
                                    solOficinaAmbiente=OficinaAmbiente)
            solicitud.save()
            consecutivoCaso=randint(1,10000)
            codigoCaso=f"REQ {str(consecutivoCaso).rjust(5,"0")}"
            userCaso=User.objects.filter(groups_name_in=['Administrador'])
            estado='Solicitada'
            caso=Caso(
                casoSolicitud=solicitud,
                casCodigo=codigoCaso,
                casUsuario=userCaso,
                casEstado=estado,
                )
            caso.save()
            
    except Error as error:
        transaction.rollback()
        print("errorrrrr")

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

def solicitud_view(request):
    if request.user.is_authenticated:
        ambientes = OficinaAmbiente.objects.all()
        session_data = {
            "user": request.user,
            "rol": request.user.groups.get().name,
            "oficinasAmbientes": ambientes
        }
        
        return render(request, "empleado/solicitud.html", session_data)
    else:
        mensaje = "iniciar sesion"
        return render(request, "login.html", { "mensaje": mensaje })
    

from random import randint
# registrando las solicitudes
def registro_solicitud(request):
    
    try:
        # valida que se guarde la informacon en ambas colecciones, no solamente en una
        with transaction.atomic():
            # guardando solicitud
            user = request.user
            descripcion = request.POST["descripcion"]
            id_ambiente = int(request.POST["id_ambiente"])
            ambiente = OficinaAmbiente.objects.get(pk=id_ambiente)
            solicitud = Solicitud(
                solicitudUsuario = user,
                solicitudAmbiente = ambiente,
                descripcion = descripcion
            )
            solicitud.save()
            
            # guardando caso
            consecutivo = randint(1,1000)
            codigo_caso = f"REQ {str(consecutivo).rjust(5, '0')}"
            caso_user = User.objects.filter(groups__name__in=['Administrador']).first()
            caso = Caso(
                solicitudCaso = solicitud,
                codigo = codigo_caso,
                estado = 'Solicitada',
                tecnicoAsignado = caso_user
            )
            caso.save()

            return render(request, 'empleado/solicitud.html');        
    # en caso de que hay algun error
    except Error as error:
        transaction.rollback()
        print("Error al registrar la solicitud")
        print(error)
        mensaje = error;
        return render(request, 'empleado/solicitud.html', {"message": mensaje})

def listarCasos(request):
    try:
        listarCasos= Caso.objects.filter(casEstado="Solicitada")
    except Error as error:
        mensaje = str(error)
    retorno= {"listarCasos":listarCasos}
    return render(request,"administrador/listaCasos.html",retorno)

