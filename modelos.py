import xml.etree.ElementTree as ET
import os

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._size = 0

    def append(self, dato):
        nodo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nodo
            self.cola = nodo
        else:
            self.cola.siguiente = nodo
            self.cola = nodo
        self._size += 1

    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def find(self, predicate):
        actual = self.cabeza
        while actual is not None:
            if predicate(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None

    def size(self):
        return self._size

class Estacion:
    def __init__(self, id_est, nombre):
        self.id = id_est
        self.nombre = nombre

class Frecuencia:
    def __init__(self, idEstacion, valor):
        self.idEstacion = idEstacion
        self.valor = int(valor)

class SensorSuelo:
    def __init__(self, id_s, nombre):
        self.id = id_s
        self.nombre = nombre
        self.frecuencias = ListaEnlazada()  

class SensorCultivo:
    def __init__(self, id_t, nombre):
        self.id = id_t
        self.nombre = nombre
        self.frecuencias = ListaEnlazada()  

class CampoAgricola:
    def __init__(self, id_c, nombre):
        self.id = id_c
        self.nombre = nombre
        self.estaciones = ListaEnlazada()      
        self.sensoresSuelo = ListaEnlazada()   
        self.sensoresCultivo = ListaEnlazada() 

class GrupoEstaciones:
    def __init__(self, patron_key):
        self.patron = patron_key
        self.estaciones = ListaEnlazada()  

def get_frecuencia_sensor(sensor, idEstacion):
    for freq in sensor.frecuencias:
        if freq.idEstacion == idEstacion:
            return freq.valor
    return 0

def construir_patron_para_estacion(campo, idEstacion):

    suelo_parts = ""
    
    for sensor in campo.sensoresSuelo:
        val = get_frecuencia_sensor(sensor, idEstacion)
        if suelo_parts == "":
            suelo_parts = str(val)
        else:
            suelo_parts = suelo_parts + "," + str(val)
    cultivo_parts = ""
    for sensor in campo.sensoresCultivo:
        val = get_frecuencia_sensor(sensor, idEstacion)
        if cultivo_parts == "":
            cultivo_parts = str(val)
        else:
            cultivo_parts = cultivo_parts + "," + str(val)
    return suelo_parts + "|" + cultivo_parts
