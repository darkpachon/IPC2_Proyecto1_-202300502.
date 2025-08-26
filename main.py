
from modelos import (
    cargar_archivo_xml,
    agrupar_estaciones_por_patron,
    sumar_frecuencias_por_grupo,
    escribir_salida_xml,
    generar_dot_matriz_frecuencias
)

import os

def mostrar_menu():
    print("\n----- Menú principal -----")
    print("1. Cargar archivo")
    print("2. Procesar archivo (agrupar estaciones)")
    print("3. Escribir archivo de salida (XML reducido)")
    print("4. Mostrar datos del estudiante (ejemplo)")
    print("5. Generar gráfica (DOT)")
    print("6. Salir")
    print("--------------------------")

def main():
    campos_cargados = None
    campo_procesado = None
    grupos_procesados = None

    while True:
        mostrar_menu()
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            ruta = input("Ingrese la ruta del archivo XML (ej: ./entrada.xml): ").strip()
            if not os.path.isfile(ruta):
                print("Archivo no encontrado:", ruta)
                continue
            try:
                campos_cargados = cargar_archivo_xml(ruta)
                print("Archivo cargado correctamente.")
            except Exception as e:
                print("Error al cargar archivo:", e)
        elif opc == "2":
            if not campos_cargados:
                print("Debe cargar un archivo primero (opción 1).")
                continue
            # tomamos el primer campo cargado
            primer_campo = None
            for c in campos_cargados:
                primer_campo = c
                break
            if primer_campo is None:
                print("No se encontró ningún campo en el archivo.")
                continue
            campo_procesado = primer_campo
            grupos_procesados = agrupar_estaciones_por_patron(campo_procesado)
            print("Procesamiento completado. Grupos formados:", grupos_procesados.size())
            # mostrar resumen
            idx = 1
            for g in grupos_procesados:
                est_nombres = ""
                primera = True
                for e in g.estaciones:
                    if primera:
                        est_nombres = e.nombre
                        primera = False
                    else:
                        est_nombres = est_nombres + ", " + e.nombre
                print(" Grupo", idx, "->", est_nombres)
                idx += 1
        elif opc == "3":
            if campo_procesado is None or grupos_procesados is None:
                print("Debe procesar un archivo primero (opción 2).")
                continue
            ruta_out = input("Ingrese ruta y nombre para archivo de salida XML (ej: ./salida.xml): ").strip()
            try:
                escribir_salida_xml(ruta_out, campo_procesado, grupos_procesados)
                print("Archivo de salida escrito en:", ruta_out)
            except Exception as e:
                print("Error al escribir archivo:", e)
        elif opc == "4":
            print("\n--- Datos del estudiante (ejemplo) ---")
            print("Nombre: Tu Nombre Aquí")
            print("Carnet: 2023xxxx")
            print("Curso: Introducción a la Programación y Computación 2")
            print("Carrera: Ingeniería")
            print("Semestre: 2do")
            print("-------------------------------------")
        elif opc == "5":
            if campo_procesado is None or grupos_procesados is None:
                print("Debe procesar un archivo primero (opción 2).")
                continue
            ruta_dot = input("Ingrese ruta y nombre para archivo DOT (ej: ./grafica.dot): ").strip()
            try:
                generar_dot_matriz_frecuencias(campo_procesado, grupos_procesados, ruta_dot)
                print("DOT generado en:", ruta_dot)
                print("Para convertir a imagen: dot -Tpng {} -o grafica.png".format(ruta_dot))
            except Exception as e:
                print("Error al generar DOT:", e)
        elif opc == "6":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
