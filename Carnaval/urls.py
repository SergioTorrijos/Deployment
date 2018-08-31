#encoding:utf-8
from django.conf.urls import *
from django.contrib import admin
from main.views import index, populateDBLetras, populateDBNoticias, entrenarDatos, resultadoEntrenarDatos

admin.autodiscover()

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^populateLetras', populateDBLetras, name='populateDBLetras'),
    url(r'^populateNoticias',populateDBNoticias, name='populateDBNoticias'),
    url(r'^entrenarDatos',entrenarDatos, name='entrenarDatos'),
    url(r'^resultadoEntrenarDatos',resultadoEntrenarDatos, name='ResultadoEntrenarDatos'),]

