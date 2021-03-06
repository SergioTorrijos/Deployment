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
			if int(a.get_text()) > 2017:
				res.append(str(a.get_text()))
    
    return res

    
    

def guardar_bd():
    
    conn = sqlite3.connect('carnaval.db')
    conn.text_factory = str 
    conn.execute("DELETE FROM LETRAS WHERE FECHA=" + "2018")
     
    
    l=extraer_fechas()
    for i in l:    
        
        rPrincipal = urllib.urlopen('http://letrasdcarnaval.blogspot.com.es/search/label/'+i).read()
        
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
                            
                    grupo=""
                    if len(datos[0].get_text())<2:                    
                        grupo=datos[1].get_text().strip()
                    else:
                        grupo=datos[0].get_text().strip()   
                            
                    autor=""
                    x =1;
                        
                                
                    while len(datos[x].get_text())<6 :
                        x=x+1
                    while len(datos[x].get_text()) > 3 and len(datos[x].get_text().strip())<75:
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
                            
                            
                    datos2 = j.select('[style*="text-align: justify;"]' and '[style*="text-align: left;"]' and '[style*="color: white;"]' )
                    letra = ""
                    
                    for x in datos2:
                        
                        if letra == "":
                            letra = x.get_text().strip()
                        else:
                            letra = letra+" "+x.get_text().strip()
                            
                    if len(letra) is not 0:
                            s = ''.join((c for c in unicodedata.normalize('NFD',unicode(letra)) if unicodedata.category(c) != 'Mn'))
                    
                            conn.execute("""INSERT INTO LETRAS (FECHA, AUTOR, GRUPO, LETRA) VALUES (?,?,?,?)""",
                                            (i,unicode(autor),unicode(grupo),unicode(s)))
                        
							
    conn.commit()
    conn.close()
    
    

    
def populateDatabaseLetras():
    guardar_bd()
    
if __name__ == '__main__':
    populateDatabaseLetras()