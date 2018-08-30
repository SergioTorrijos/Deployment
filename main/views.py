from main.models import UserInformation
from django.shortcuts import render_to_response, get_object_or_404
from main.populaLetras import populateDatabaseLetras
from main.populaNoticias import populateDatabaseNoticias
from main.entrenarDatos import entrenamientoDatos
from main.forms import UserForm
import sqlite3
from django.template.context import RequestContext
from botocore.vendored.requests.api import request
    
#  CONJUNTO DE VISTAS

def index(request): 
    return render_to_response('index.html')

def populateDBLetras(request):
    populateDatabaseLetras()
    conn = sqlite3.connect('carnaval.db')
    cursor = conn.execute("SELECT COUNT(*) FROM LETRAS")
    numeroLetras =str(cursor.fetchone()[0])
    return render_to_response('populateLetras.html',{'numeroLetras':numeroLetras},context_instance=RequestContext(request))

def populateDBNoticias(request):
    populateDatabaseNoticias()
    conn = sqlite3.connect('carnaval.db')
    cursor = conn.execute("SELECT COUNT(*) FROM NOTICIAS")
    numeroNoticias =str(cursor.fetchone()[0])
    return render_to_response('populateNoticias.html',{'numeroNoticias':numeroNoticias},context_instance=RequestContext(request))


def entrenarDatos(request):
    if request.method=='GET':
        form = UserForm(request.GET, request.FILES)
        if form.is_valid():
            entrenamientoDatos(str(form.cleaned_data['id']))
            
            conn = sqlite3.connect('carnaval.db')
            cursor = conn.execute("SELECT distinct NOTICIA FROM ENTRENAMIENTO")
            res=[]
            for registro in cursor:
                res.append(registro[0])
                
            return render_to_response('entreno.html', {'noticiasssss':res}, context_instance=RequestContext(request))
    else:
        form=UserForm()
    return render_to_response('entrenarDatos.html', {'form':form}, context_instance=RequestContext(request))

    
    