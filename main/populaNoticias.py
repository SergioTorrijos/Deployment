# -*- coding: utf-8 -*-
'''
Created on 8 nov. 2017

@author: Sergio
'''

import sqlite3
from bs4 import BeautifulSoup
import urllib
import unicodedata

def extraer_fechas():
    r = urllib.urlopen('http://letrasdcarnaval.blogspot.com.es/').read()
    soup = BeautifulSoup(r,"html.parser")
    l=soup.find(class_='widget-content list-label-widget-content')
    m = l.find_all('li')
    res=[]
    for i in m:
        a= i.find('a')
        if (len(a.get_text()) ==4 and (a.get_text()).isdigit()):
            res.append(str(a.get_text()))
    
    return res

def extraer_fechas_Noticias():
    conn = sqlite3.connect('carnaval.db')
    cursor = conn.cursor()
   
    #Asi se ve si en la base de datos existe la columna FECHA o la tabla LETRAS
    try :
        #Es más rapido coger los datos de la base de datos que hacer Scrapping, por eso usamos este primer método
        cursor.execute("SELECT distinct FECHA FROM LETRAS")
        res=[]
        for registro in cursor:
            res.append(str(registro[0]))
        
        #Si en la base de datos hay letras, coge las fechas guardadas en la base de datos, si las hubiera
        if res != []: 
            res = res
            
        #Si en la base de datos no hay fechas aún, coge los años de la misma manera que se realiza a la hora de coger las letras
        #Este metodo tarda más, pero evita errores en la pagina.
        else: 
            res = extraer_fechas()
    
    #Si no existe alguna de las anteriores, se usa el método habitual para obtener las fechas 
    except :
        res = extraer_fechas()
    
    return res

def guardar_bd():
    
    conn = sqlite3.connect('carnaval.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS NOTICIAS")
     
    conn.execute('''CREATE TABLE NOTICIAS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       FECHA           TEXT    NOT NULL,
       TITULAR           TEXT    NOT NULL);''')
    
    l=extraer_fechas_Noticias()
    for i in l:    
        print i
        
        rPrincipal = urllib.urlopen('https://es.wikipedia.org/wiki/'+i).read()
        
        soupPrincipal = BeautifulSoup(rPrincipal,"html.parser")
        inicio = soupPrincipal.find(class_='mw-parser-output')
        #Esto se hace porque hay años que no toman bien el valor decompose y otros años que lo necesitan para que las noticias
        #no tomen valores extraños
        try:
            inicio.find(class_='listaref').decompose()
        except:
            inicio.find(class_='listaref')
        
        for continuacion in inicio.find_all('ul'):
            for noticia in continuacion.find_all('li'):
                if len(noticia.get_text()) >20 and ((" Acontecimientos" not in noticia.get_text()) and (" Fecha desconocida" not in noticia.get_text()) and (" Fecha desconocido" not in noticia.get_text()) and (" Wikimedia" not in noticia.get_text()) and (" Fechas desconocidas" not in noticia.get_text()) and (" Fallecimientos" not in noticia.get_text()) and (" Lucha Libre Profesional" not in noticia.get_text()) and (" Lucha Libre Profesional" not in noticia.get_text()) and (" Ciencia y tecnolog" not in noticia.get_text()) and (" Astron" not in noticia.get_text()) and (" Deporte" not in noticia.get_text()) and (" Nacimientos" not in noticia.get_text()) and (" Internacionales" not in noticia.get_text()) and (" Videojuegos" not in noticia.get_text())):
                    s = ''.join((c for c in unicodedata.normalize('NFD',unicode(noticia.get_text().strip())) if unicodedata.category(c) != 'Mn'))
                    
                    conn.execute("""INSERT INTO NOTICIAS (FECHA,TITULAR) VALUES (?,?)""",
                                        (i,unicode(s)))
    conn.commit()
    conn.close()
    
def populateDatabaseNoticias():
    guardar_bd()
    print("Finished database population")
    
if __name__ == '__main__':
    populateDatabaseNoticias()