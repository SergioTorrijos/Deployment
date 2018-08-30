# -*- coding: utf-8 -*-
'''
Created on 8 nov. 2017

@author: Sergio
'''


#Import all the dependencies
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='nltk')
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
import sqlite3

tokenizer = RegexpTokenizer(r'\w+')
stopword_set = set(stopwords.words('spanish'))
#This function does all cleaning of data using two objects above
def nlp_clean(data):
    new_data = []
    for d in data:
        new_str = d.lower()
        dlist = tokenizer.tokenize(new_str)
        dlist = list(set(dlist).difference(stopword_set))
        new_data.append(dlist)
    return new_data

#Método principal del Doc2Vec
def guardarEntrenamiento(fechaPasada):
    
    
    conn = sqlite3.connect('carnaval.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS ENTRENAMIENTO")
     
    conn.execute('''CREATE TABLE ENTRENAMIENTO
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       NOTICIA           TEXT    NOT NULL,
       REPETICIONES           TEXT    NOT NULL,
       VECTOR           TEXT    NOT NULL);''')
    
    try:
        
        cursorLetras= conn.execute("SELECT LETRA FROM LETRAS WHERE FECHA ="+fechaPasada)
        letrasNoticias = []
        suma=0
        noticiasSeleccionadas = []
        noticiasSeleccionadasNombre = []
        noticiasRepetidas = []
        noticiasRepetidasFin = []
        
        for j in cursorLetras.fetchall():
            
            print suma
            print unicode(j[0])
            suma+=1
            
            letrasNoticias= []
            letrasNoticias.append(unicode(j[0]))
            
            cursorNoticias = conn.execute("SELECT TITULAR FROM NOTICIAS WHERE FECHA="+fechaPasada+" or FECHA="+ str(int(fechaPasada) - 1))
            for i in cursorNoticias.fetchall():
                letrasNoticias.append(unicode(i[0]))
         
            letras_fin = nlp_clean(letrasNoticias)
            
            it = LabeledLineSentence(letras_fin, letrasNoticias)
            
    #         model = gensim.models.Doc2Vec( vector_size=1, min_count=1, alpha=0.05, min_alpha=0.00025, dm=2)
            model = gensim.models.Doc2Vec(vector_size=15, window=2, min_count=1, workers=4)
            model.build_vocab(it)
            
            iterator_size=100
            #training of model
            for epoch in range(iterator_size):
    #             print 'iteration '+str(epoch+1)
                model.train(it,total_examples=model.corpus_count,epochs=model.epochs)
                model.alpha -= 0.00002
                model.min_alpha = model.alpha
             
            #saving the created model
            model.save('doc2vec.model')
            
            
            #loading the model
            d2v_model = gensim.models.doc2vec.Doc2Vec.load('doc2vec.model')
            model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
            #start testing
            #to get most similar document with similarity scores using document-index
            similar_doc = d2v_model.docvecs.most_similar(0) 
            print similar_doc
            for index in similar_doc:
                
                noticiasSeleccionadas.append(index)#Noticias con vectores
                
                if index[0] in noticiasSeleccionadasNombre: #Se comprueba si se repite alguna noticia, si no se repite se añade
                    if index[0] not in noticiasRepetidas: #Vemos que noticias se repiten tras el entrenamiento, si no esta en noticias repetidas se añade
                        noticiasRepetidas.append(index[0])
                         
                    
                    #print noticiasRepetidas
                noticiasSeleccionadasNombre.append(index[0])
            
            #print "NOTICIA REPETIDA !!!!!"
            #print noticiasRepetidas
            
            
        controlRepetidasFin =[]
        for index2 in noticiasRepetidas: #Vemos cuantas veces se repite las noticias
            numerito = noticiasSeleccionadasNombre.count(index2)
            if index2 not in controlRepetidasFin:
                controlRepetidasFin.append(index2)
                noticiasRepetidasFin.append([index2,numerito])
        #print noticiasSeleccionadas
        noticiasSeleccionadas.sort(key=lambda x: x[1], reverse=True)
        noticiasRepetidasFin.sort(key=lambda x: x[1], reverse=True)
        #print noticiasSeleccionadas
        #print noticiasSeleccionadasNombre
        
        #print "SOLO LOS PRIMEROS 5"
        #print noticiasSeleccionadas[:(5-len(noticiasRepetidas))] #Se cogen las primeras 5 noticias más destacadas
                
        if len(noticiasRepetidasFin) < 5: #Si hay más de 5 noticias repetidas, cogemos las noticias que más se repitan.
            
            
            fin = noticiasSeleccionadas[:(5-len(noticiasRepetidasFin))]
            #Noticias que se repiten junto a sus repeticiones
            for f in noticiasRepetidasFin:
                conn.execute("""INSERT INTO ENTRENAMIENTO (NOTICIA, REPETICIONES, VECTOR) VALUES (?,?,?)""",
                            (f[0],f[1],"0"))
                
            #Noticias que no se repiten junto a su vector
            for fi in fin:
                conn.execute("""INSERT INTO ENTRENAMIENTO (NOTICIA, REPETICIONES, VECTOR) VALUES (?,?,?)""",
                            (fi[0],"0",fi[1]))
            
            conn.commit()
            conn.close()
            
            
        else:
            #Noticias repetidas junto a las veces que se repite
            for f in noticiasRepetidasFin:
                conn.execute("""INSERT INTO ENTRENAMIENTO (NOTICIA, REPETICIONES, VECTOR) VALUES (?,?,?)""",
                            (f[0],f[1],"0"))
                
            conn.commit()
            conn.close()
            
    except:
        res= []
        res.append("No se encuentran datos para la fecha seleccionada")
        return res
    
    
    
class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield gensim.models.doc2vec.LabeledSentence(doc,[self.labels_list[idx]])     


    
def entrenamientoDatos(fechaPasada):
    guardarEntrenamiento(fechaPasada)
    print("Finished database population")
    
if __name__ == '__main__':
    entrenamientoDatos()