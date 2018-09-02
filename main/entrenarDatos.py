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

def nlp_clean(data):
    new_data = []
    for d in data:
        new_str = d.lower()
        dlist = tokenizer.tokenize(new_str)
        dlist = list(set(dlist).difference(stopword_set))
        new_data.append(dlist)
    return new_data

def guardarEntrenamiento(fechaPasada):
    
    
    conn = sqlite3.connect('carnaval.db')
    conn.text_factory = str  
    conn.execute('''DROP TABLE IF EXISTS ENTRENAMIENTO''')
     
    conn.execute('''CREATE TABLE ENTRENAMIENTO
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
	   FECHA			TEXT NOT NULL,
       NOTICIA           TEXT    NOT NULL,
       REPETICIONES           TEXT    NOT NULL,
       VECTOR           TEXT    NOT NULL);''')
    
    try:
        
        cursorLetras= conn.execute('''SELECT LETRA FROM LETRAS WHERE FECHA ='''+fechaPasada)
        letrasNoticias = []
        
        noticiasSeleccionadas = []
        noticiasSeleccionadasNombre = []
        noticiasRepetidas = []
        noticiasRepetidasFin = []
        suma=0
		
        for j in cursorLetras.fetchall():
            
			if suma != 15:
				
				
				suma+=1
				
				letrasNoticias= []
				letrasNoticias.append(j[0])
				
				cursorNoticias = conn.execute('''SELECT TITULAR FROM NOTICIAS WHERE FECHA='''+str(int(fechaPasada) - 1))
				for i in cursorNoticias.fetchall():
					letrasNoticias.append(i[0])
			 
				letras_fin = nlp_clean(letrasNoticias)
				
				it = LabeledLineSentence(letras_fin, letrasNoticias)
				
				model = gensim.models.Doc2Vec(vector_size=15, window=2, min_count=1, workers=4)
				model.build_vocab(it)
				
				iterator_size=2
				for epoch in range(iterator_size):
					model.train(it,total_examples=model.corpus_count,epochs=model.epochs)
					model.alpha -= 0.00002
					model.min_alpha = model.alpha
				model.save('doc2vec.model')
				d2v_model = gensim.models.doc2vec.Doc2Vec.load('doc2vec.model')
				model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
				similar_doc = d2v_model.docvecs.most_similar(0) 
				for index in similar_doc:
					
					noticiasSeleccionadas.append(index)
					
					if index[0] in noticiasSeleccionadasNombre: 
						if index[0] not in noticiasRepetidas:
							noticiasRepetidas.append(index[0])
							 
						
					noticiasSeleccionadasNombre.append(index[0])
				
            
        controlRepetidasFin =[]
        for index2 in noticiasRepetidas: 
            numerito = noticiasSeleccionadasNombre.count(index2)
            if index2 not in controlRepetidasFin:
                controlRepetidasFin.append(index2)
                noticiasRepetidasFin.append([index2,numerito])
        noticiasSeleccionadas.sort(key=lambda x: x[1], reverse=True)
        noticiasRepetidasFin.sort(key=lambda x: x[1], reverse=True)
                
        if len(noticiasRepetidasFin) < 5:
            
            
            fin = noticiasSeleccionadas[:(5-len(noticiasRepetidasFin))]
            for f in noticiasRepetidasFin:
                conn.execute("""INSERT INTO ENTRENAMIENTO (FECHA,NOTICIA, REPETICIONES, VECTOR) VALUES (?,?,?,?)""",
                            (fechaPasada,f[0],f[1],"0"))
                
            for fi in fin:
                conn.execute("""INSERT INTO ENTRENAMIENTO (FECHA,NOTICIA, REPETICIONES, VECTOR) VALUES (?,?,?,?)""",
                            (fechaPasada,fi[0],"0",fi[1]))
            

            conn.commit()
            conn.close()
            
            
        else:
            for f in noticiasRepetidasFin:
                conn.execute("""INSERT INTO ENTRENAMIENTO (FECHA,NOTICIA, REPETICIONES, VECTOR) VALUES (?,?,?,?)""",
                            (fechaPasada,f[0],f[1],"0"))
                
            conn.commit()
            conn.close()
            
    except:
        res= []
        res.append("No se encuentran datos para la fecha seleccionada")
        return res

def resultadoEntrenamiento():
    conn = sqlite3.connect('carnaval.db')
    	
	
    
class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield gensim.models.doc2vec.LabeledSentence(doc,[self.labels_list[idx]])     


    
    
if __name__ == '__main__':
    guardarEntrenamiento()