# -*- coding: utf-8 -*-
'''
Created on 8 nov. 2017

@author: Sergio
'''

import urllib
import sqlite3
from bs4 import BeautifulSoup
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

    
    

def guardar_bd():
    
    conn = sqlite3.connect('carnaval.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS LETRAS")
     
    conn.execute('''CREATE TABLE LETRAS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       FECHA           TEXT    NOT NULL,
       AUTOR           TEXT    NOT NULL,
       GRUPO           TEXT    NOT NULL,
       LETRA           TEXT    NOT NULL);''')
    
    l=extraer_fechas()
    for i in l:    
        print i
        
        rPrincipal = urllib.urlopen('http://letrasdcarnaval.blogspot.com.es/search/label/'+i).read()
#    rPrincipal = urllib.urlopen('http://letrasdcarnaval.blogspot.com.es/search/label/2018').read()
        
        soupPrincipal = BeautifulSoup(rPrincipal,"html.parser")
        soup2 = soupPrincipal.find(id="blog-pager-older-link")
        principal = 0
        while soup2 != None:
            if principal == 0:
                soup = soupPrincipal
                principal = principal+1
            else:
                link =soup2.a.get('href')
                r = urllib.urlopen(link).read()
                soup = BeautifulSoup(r,"html.parser")
            soup2 = soup.find(id="blog-pager-older-link")
            l=soup.find_all(class_='post-body entry-content') 
            for j in l:
                datos= j.select('div[style*="text-align: center;"]')
                        
                if datos != [] and (len(datos))>=5:
                            
                    #GRUPO
                    grupo=""
                    if len(datos[0].get_text())<2:#la linea puede estar vacia                         
                        grupo=datos[1].get_text().strip()
                    else:
                        grupo=datos[0].get_text().strip()   
                            
                    #AUTOR 
                    autor=""
                    x =1;
                        
                                
                    while len(datos[x].get_text())<6 :#elimina las lineas vacias o con años
                        x=x+1
                    while len(datos[x].get_text()) > 3 and len(datos[x].get_text().strip())<75:#cuando hay una linea en blanco o empieza enseguida la letra, para
                        if len(datos[x].get_text())<6 or (datos[x].get_text() is 'Vídeo aquí'):
                            autor = autor.strip()
                        elif autor== "":
                            autor = datos[x].get_text().strip()
                        else:
                            if datos[x].get_text().strip()[0] == '\'' or datos[x].get_text().strip()[0] == '\"' or datos[x].get_text().strip()[0] ==  '&':
                                autor = autor +" "+ datos[x].get_text().strip()
                            else:
                                autor = autor +", "+ datos[x].get_text().strip()
                        x=x+1
                    autor= autor.replace("2012", "").strip()
                    autor= autor.replace(grupo + "," , "")
                    video = "Vídeo aquí"
                    autor= autor.replace(video.decode('utf-8'), "").strip()
                            
                            
                    #LETRAS
                    datos2 = j.select('[style*="text-align: justify;"]' and '[style*="text-align: left;"]' and '[style*="color: white;"]' )
                    letra = ""
                    
                    for x in datos2:
                        
                        if letra == "":
                            letra = x.get_text().strip()
                        else:
                            letra = letra+" "+x.get_text().strip()
                            
                    if len(letra) is not 0:
                            #Con esto quitamos las tildes que pueden resultar molestas a la hora de hacer el procesado de textos
                            s = ''.join((c for c in unicodedata.normalize('NFD',unicode(letra)) if unicodedata.category(c) != 'Mn'))
                    
                            conn.execute("""INSERT INTO LETRAS (FECHA, AUTOR, GRUPO, LETRA) VALUES (?,?,?,?)""",
                                            (i,unicode(autor),unicode(grupo),unicode(s)))
                        
    conn.commit()
    conn.close()
    
    

    
def populateDatabaseLetras():
    guardar_bd()
    print("Finished database population")
    
if __name__ == '__main__':
    populateDatabaseLetras()