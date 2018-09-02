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
			if int(a.get_text()) > 2017:
				res.append(str(a.get_text()))
    
    return res


def guardar_bd():
    
    conn = sqlite3.connect('carnaval.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DELETE FROM NOTICIAS WHERE FECHA=" + "2018")
     
    
    l=extraer_fechas()
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
                    if ("enero" in noticia.get_text()) or ("febrero" in noticia.get_text()) or ("marzo" in noticia.get_text()) or ("abril" in noticia.get_text()) or ("mayo" in noticia.get_text()) or ("junio" in noticia.get_text()) or ("julio" in noticia.get_text()) or ("agosto" in noticia.get_text()) or ("septiembre" in noticia.get_text()) or ("octubre" in noticia.get_text()) or ("noviembre" in noticia.get_text()) or ("diciembre" in noticia.get_text()): 
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