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

def agrupar_estaciones_por_patron(campo):
    grupos = ListaEnlazada()
    for estacion in campo.estaciones:
        key = construir_patron_para_estacion(campo, estacion.id)
        grupo = grupos.find(lambda g: g.patron == key)
        if grupo is None:
            nuevo = GrupoEstaciones(key)
            nuevo.estaciones.append(estacion)
            grupos.append(nuevo)
        else:
            grupo.estaciones.append(estacion)
    return grupos

def sumar_frecuencias_por_grupo(campo, grupo):
    representante = None
    for e in grupo.estaciones:
        representante = e
        break
    if representante is None:
        return None, "", ListaEnlazada(), ListaEnlazada()
    id_reducida = representante.id
    nombre_reducida = representante.nombre

    suma_por_suelo = ListaEnlazada()
    for sensor in campo.sensoresSuelo:
        suma = 0
        for est in grupo.estaciones:
            suma += get_frecuencia_sensor(sensor, est.id)
        if suma > 0:
            suma_por_suelo.append(Frecuencia(id_reducida, suma))

    suma_por_cultivo = ListaEnlazada()
    for sensor in campo.sensoresCultivo:
        suma = 0
        for est in grupo.estaciones:
            suma += get_frecuencia_sensor(sensor, est.id)
        if suma > 0:
            suma_por_cultivo.append(Frecuencia(id_reducida, suma))

    nombres_concat = nombre_reducida
    primera = True
    for e in grupo.estaciones:
        if primera:
            primera = False
            continue
        nombres_concat = nombres_concat + ", " + e.nombre

    return id_reducida, nombres_concat, suma_por_suelo, suma_por_cultivo

def cargar_archivo_xml(ruta_completa):
    if not os.path.isfile(ruta_completa):
        raise FileNotFoundError("Archivo no encontrado: " + ruta_completa)

    tree = ET.parse(ruta_completa)
    root = tree.getroot()
    campos = ListaEnlazada()

    for campo_elem in root:
        if campo_elem.tag != "campo":
            continue
        id_c = campo_elem.get("id", "")
        nombre_c = campo_elem.get("nombre", "")
        campo = CampoAgricola(id_c, nombre_c)

        for child in campo_elem:
            if child.tag == "estacionesBase":
                for est_elem in child:
                    if est_elem.tag == "estacion":
                        id_e = est_elem.get("id", "")
                        nom_e = est_elem.get("nombre", "")
                        campo.estaciones.append(Estacion(id_e, nom_e))
            elif child.tag == "sensoresSuelo":
                for sensor_elem in child:
                    if sensor_elem.tag == "sensorS":
                        id_s = sensor_elem.get("id", "")
                        nom_s = sensor_elem.get("nombre", "")
                        sensor = SensorSuelo(id_s, nom_s)
                        for freq_elem in sensor_elem:
                            if freq_elem.tag == "frecuencia":
                                idEst = freq_elem.get("idEstacion", "")
                                val_text = (freq_elem.text or "").strip()
                                if val_text == "":
                                    continue
                                sensor.frecuencias.append(Frecuencia(idEst, int(val_text)))
                        campo.sensoresSuelo.append(sensor)
            elif child.tag == "sensoresCultivo":
                for sensor_elem in child:
                    if sensor_elem.tag == "sensorT":
                        id_t = sensor_elem.get("id", "")
                        nom_t = sensor_elem.get("nombre", "")
                        sensor = SensorCultivo(id_t, nom_t)
                        for freq_elem in sensor_elem:
                            if freq_elem.tag == "frecuencia":
                                idEst = freq_elem.get("idEstacion", "")
                                val_text = (freq_elem.text or "").strip()
                                if val_text == "":
                                    continue
                                sensor.frecuencias.append(Frecuencia(idEst, int(val_text)))
                        campo.sensoresCultivo.append(sensor)

        campos.append(campo)
    return campos

def escribir_salida_xml(ruta_completa, campo, grupos):
    root = ET.Element("camposAgricolas")
    campo_elem = ET.SubElement(root, "campo", {"id": campo.id, "nombre": campo.nombre})
    est_red = ET.SubElement(campo_elem, "estacionesBaseReducidas")

    for grupo in grupos:
        id_repre, nombres_concat, _, _ = sumar_frecuencias_por_grupo(campo, grupo)
        if id_repre is None:
            continue
        ET.SubElement(est_red, "estacion", {"id": id_repre, "nombre": nombres_concat})

    sensores_s_elem = ET.SubElement(campo_elem, "sensoresSuelo")
    for sensor in campo.sensoresSuelo:
        sensor_elem = ET.SubElement(sensores_s_elem, "sensorS", {"id": sensor.id, "nombre": sensor.nombre})
        for grupo in grupos:
            id_repre, nombres_concat, suma_suelo, _ = sumar_frecuencias_por_grupo(campo, grupo)
            for f in suma_suelo:
                if f.idEstacion == id_repre:
                    freq_elem = ET.SubElement(sensor_elem, "frecuencia", {"idEstacion": id_repre})
                    freq_elem.text = str(f.valor)

    sensores_t_elem = ET.SubElement(campo_elem, "sensoresCultivo")
    for sensor in campo.sensoresCultivo:
        sensor_elem = ET.SubElement(sensores_t_elem, "sensorT", {"id": sensor.id, "nombre": sensor.nombre})
        for grupo in grupos:
            id_repre, nombres_concat, _, suma_cult = sumar_frecuencias_por_grupo(campo, grupo)
            for f in suma_cult:
                if f.idEstacion == id_repre:
                    freq_elem = ET.SubElement(sensor_elem, "frecuencia", {"idEstacion": id_repre})
                    freq_elem.text = str(f.valor)

    tree = ET.ElementTree(root)
    tree.write(ruta_completa, encoding="utf-8", xml_declaration=True)

def generar_dot_matriz_frecuencias(campo, grupos, ruta_dot):
    f = open(ruta_dot, "w", encoding="utf-8")
    f.write("digraph G {\n")
    f.write("  rankdir=LR;\n")
    f.write("  node [fontname=\"Arial\"];\n")

    for grupo in grupos:
        id_repre, nombres_concat, _, _ = sumar_frecuencias_por_grupo(campo, grupo)
        if id_repre is None:
            continue
        label = id_repre + "\\n" + nombres_concat
        f.write('  "{}" [shape=box];\n'.format(label))

    for sensor in campo.sensoresSuelo:
        lab = sensor.id + "\\n" + sensor.nombre
        f.write('  "{}" [shape=ellipse];\n'.format(lab))

    for sensor in campo.sensoresCultivo:
        lab = sensor.id + "\\n" + sensor.nombre
        f.write('  "{}" [shape=ellipse];\n'.format(lab))
