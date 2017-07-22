import urllib2
import os
import subprocess
import random
import time
import argparse

class colores:
	morado = '\033[1;95m'
	azul = '\033[1;94m'
	verde = '\033[1;92m'
	amarillo = '\033[1;93m'
	rojo = '\033[1;91m'
	cian = '\033[1;96m'
	reset = '\033[0m'
	
def agregaraarchivo(archivo, linea):
	if not os.path.exists(archivo):
		open(archivo,'w')
	if len(linea):
		with open(archivo,'a') as myfile:
			myfile.write(linea + '\n')

def contenidoarchivo(archivo):
	contenido=[]
	linea=''
	if not os.path.exists(archivo):
		open(archivo,'w')	
	with open(archivo,'r') as myfile:
		for linea in myfile.readlines():
			if len(linea.rstrip('\n')):
				contenido.append(linea.rstrip('\n'))
	return contenido 

def quitardearchivo(archivo,linea):
	lineas=contenidoarchivo(archivo)
	with open(archivo,'w') as myfile:
		for l in lineas:
			if len(l):
				if l <> linea:
					myfile.write(l + '\n')
	
def randlist(num):
	lista=[]
	aleatorio=0
	while len(lista) < num:
		aleatorio=random.randrange(num)
		if not aleatorio in lista:
			lista.append(aleatorio)
	return lista
	
def crawl(url,taginicio,tagfin):
	try:
		contenido=urllib2.urlopen(url).read()
		return cortar(contenido,taginicio,tagfin)
	except:
		print colores.rojo + '\nPagina no encontrada: ' + colores.azul + url + colores.reset
		agregaraarchivo('errores.txt', 'Pagina no encontrada: '+ url)
		return ['']
	
def cortar(contenido,taginicio,tagfin):
	lista=[]
	inicio=0
	fin=0
	inicioant=0
	temp=contenido
	i=0
	while (taginicio in temp) and (tagfin in temp):
		i=i+1
		inicio=temp.find(taginicio)
		temp=temp[inicio+len(taginicio):]
		fin=temp.find(tagfin)
		if not temp[0:fin] in lista:
			lista.append(temp[0:fin])
		temp=temp[fin+len(tagfin):]
	return lista

def continuardescargas(max=0):
	contador=0
	if not opt.nocontinue:
		for continuar in contenidoarchivo('descargando.txt'):
			contador=contador+1
			if (contador > max) and (max>0):
				break
			print colores.amarillo + 'Continuar descarga: ' + colores.azul + continuar + colores.reset
			descargar(continuar,False)

def pausa(min=0):
	if min==0:
		min=random.randrange(30) + 1
	for i in range(min,0,-1):
		print colores.morado + 'Esperando: ' + colores.azul + str(i) + ' minutos' + colores.reset 
		time.sleep(60)
		
def descargar(url,continuar=True):
	if url in contenidoarchivo('descargados.txt'):
		print colores.morado + 'Ya descargado: ' + colores.azul + url + colores.reset
		quitardearchivo('descargando.txt',url)
	else:
		print colores.verde + 'Descargando: ' + colores.azul + url + colores.verde + '...' + colores.reset 
		try:
			if not url in contenidoarchivo('descargando.txt'):
				agregaraarchivo('descargando.txt',url)
			subprocess.check_call(['wget','-c',url])
		except:
			print colores.rojo + '\nError descargando: ' + colores.azul + url + colores.rojo + '!' + colores.reset 
			agregaraarchivo('errores.txt','Error descargando: ' + url)
		else:
			quitardearchivo('descargando.txt',url)
			agregaraarchivo('descargados.txt',url)
			if not opt.pause is None:
				pausa(opt.pause)
			if continuar:
				continuardescargas(1)

paginas=0
parser = argparse.ArgumentParser(prog='download-allitebooks')
parser.add_argument('-search', default='')
parser.add_argument('-random', action="store_true", default=False)
parser.add_argument('-pause', required=False, type=int)
parser.add_argument('-norelated', action="store_true", default=False)
parser.add_argument('-nocontinue', action="store_true", default=False)
opt = parser.parse_args()

if len(opt.search):
	sbusqueda='?s=' + str(opt.search).replace(' ','+')
else:
	sbusqueda=''
	
continuardescargas(1)
for p in crawl('http://www.allitebooks.com/' + sbusqueda ,'<span class="pages">','</span>'):
	for q in cortar(p,'/','Pages'):
		paginas = int(q)
if paginas==0:
	for p in crawl('http://www.allitebooks.com/' + sbusqueda ,'Search results for','</span>'):
		paginas=1
print colores.morado + 'Paginas: ' + colores.azul + str(paginas) + colores.reset

listapaginas=[]
if opt.random:
	listapaginas=randlist(paginas)
else:
	listapaginas=range(paginas)
for i in listapaginas:
	u1=0
	u2=0
	for s in crawl('http://www.allitebooks.com/page/' + str(i+1) + '/' + sbusqueda,'<div class="entry-thumbnail hover-thumb">','rel='):
		for t in cortar(s,'href="','"'):
			for u in  crawl(t,'<span class="download-links">','<span class="download-size">'):
				for v in cortar(u,'href="','"'):
					u1=u1+1
					u2=0
					print colores.amarillo + 'Pagina: ' + colores.azul + str(i+1) + '.' + str(u1).zfill(2)+ '.' + str(u2).zfill(2) + colores.reset
					descargar(v)
			if not opt.norelated:
				for u in crawl(t,'<ul class="related_post wp_rp">','</article>'):
					for v in cortar(u,'href="','"'):
						for w in  crawl(v,'<span class="download-links">','<span class="download-size">'):
							for x in cortar(w,'href="','"'):
								u2=u2+1
								print colores.amarillo + 'Pagina: ' + colores.azul + str(i+1) + '.' + str(u1).zfill(2)+ '.' + str(u2).zfill(2) + colores.reset
								descargar(x)
