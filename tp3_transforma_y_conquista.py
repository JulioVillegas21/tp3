#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
Asignatura: Análisis y Diseño de Algoritmos
Año: 2026
Trabajo Práctico N° 3: "Transforma y Conquista" (Transform and Conquer)
================================================================================

DESCRIPCIÓN GENERAL Y DECISIONES DE DISEÑO (Requisito h):
---------------------------------------------------------
Este programa implementa un menú interactivo completo que aborda todos los
puntos del Trabajo Práctico N° 3 (incisos a hasta l), integrando los conceptos
teóricos de las Unidades 1 a 6 de la cátedra:

1. PARADIGMA "TRANSFORMA Y CONQUISTA" (Unidad 6):
   Se descompone en tres etapas: Transformación -> Conquista -> Retransformación.
   En este trabajo se aplican dos de sus variantes fundamentales:
   a) Simplificación de la Instancia (Instance Simplification):
      - Presorting: Ordenar los datos previamente para facilitar el cálculo de
        frecuencias, detección de duplicados o búsquedas posteriores.
      - Agrupación de claves repetidas en el Árbol AVL mediante un contador de
        frecuencia por nodo, evitando degenerar o sobrecargar la memoria cuando
        existen millones de elementos repetidos.
   b) Cambio de Representación (Representation Change):
      - Árbol AVL (Adelson-Velskii y Landis, 1962): Árbol Binario de Búsqueda
        auto-balanceado donde cada nodo mantiene un Factor de Balance
        FB = Altura(Izquierdo) - Altura(Derecho) en el conjunto {-1, 0, +1}.
        Garantiza O(log n) en inserción, búsqueda y eliminación en el peor caso
        mediante Rotaciones Simples (Izquierda/Derecha) y Dobles (Izquierda-Derecha
        y Derecha-Izquierda).
      - Heap Binario (Montículo): Árbol binario completo representado de forma
        implícita sobre un arreglo contiguo (sin punteros), utilizando las
        fórmulas de indexación vistas en clase (base 0):
          * Padre(i)          = (i - 1) // 2
          * Hijo Izquierdo(i) = 2 * i + 1
          * Hijo Derecho(i)   = 2 * i + 2
        Se implementan tanto Max-Heap (padre >= hijos) como Min-Heap (padre <= hijos).
      - Heap Sort: Algoritmo de ordenamiento O(n log n) en todos los casos y
        memoria auxiliar O(1) (in-place), dividido en:
          * Fase 1: Construir el Max-Heap (Build-Heap con heapify desde el
            último nodo no-hoja hasta la raíz) en tiempo lineal O(n).
          * Fase 2: Extraer sucesivamente la raíz (máximo) intercambiándola con
            el último elemento activo del heap y restaurando la propiedad con
            heapify en O(n log n).

2. FUERZA BRUTA VS. ORDENAMIENTO NO COMPARATIVO (Unidades 2 y 3):
   - Selection Sort (Ordenamiento por Selección - Fuerza Bruta):
     Busca repetidamente el mínimo del subarreglo no ordenado y lo coloca en su
     posición final. Su número de comparaciones responde a la Serie Aritmética:
       n(n - 1) / 2  =>  Complejidad O(n^2) en Mejor, Promedio y Peor caso.
     Para n = 100.000.000, requiere ~5 x 10^15 comparaciones (inviable en la
     práctica completa), por lo que el programa permite ejecutarlo sobre una
     muestra configurable (ej. n = 15.000) y proyectar matemáticamente el tiempo
     exacto para 100.000.000 de elementos.
   - Counting Sort (Ordenamiento por Conteo - No Comparativo):
     Ordena sin comparar elementos entre sí, contando las ocurrencias de cada
     valor en un vector índice de tamaño k + 1. Alcanza complejidad lineal
     O(n + k) en Mejor y Peor caso, resultando el algoritmo más veloz para
     ordenar 100.000.000 de enteros acotados en el rango [0, 100.000.000].
================================================================================
"""

import os
import sys
import math
import time
import random
import webbrowser
from collections import Counter

# Intentar importar numpy para acelerar operaciones masivas de 100 millones
try:
    import numpy as np
    TIENE_NUMPY = True
except ImportError:
    TIENE_NUMPY = False


# ==============================================================================
# UTILIDADES VISUALES DE CONSOLA: COLORES ANSI, CARTELES Y LIMPIEZA
# ==============================================================================
def habilitar_colores_windows():
    """Activa soporte ANSI y codificación UTF-8 en terminales de Windows."""
    if os.name == "nt":
        os.system("")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


habilitar_colores_windows()


class C:
    """Paleta de colores ANSI para una salida clara, ordenada y legible."""
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"

    CYAN     = "\033[96m"
    AZUL     = "\033[94m"
    VERDE    = "\033[92m"
    AMARILLO = "\033[93m"
    MAGENTA  = "\033[95m"
    ROJO     = "\033[91m"
    BLANCO   = "\033[97m"
    GRIS     = "\033[90m"


ANCHO_CAJA = 78


def limpiar_pantalla():
    """Borra la consola para evitar acumulación de texto entre opciones."""
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")
    else:
        print("\n" * 2)


def cartel(titulo, subtitulo="", color=C.CYAN):
    """Dibuja un cartel encabezado con bordes dobles y centrado."""
    borde = "═" * (ANCHO_CAJA - 2)
    print(f"\n{color}{C.BOLD}  ╔{borde}╗")
    print(f"  ║{titulo.center(ANCHO_CAJA - 2)}║")
    if subtitulo:
        print(f"  ║{C.RESET}{C.BLANCO}{subtitulo.center(ANCHO_CAJA - 2)}{color}{C.BOLD}║")
    print(f"  ╚{borde}╝{C.RESET}\n")


def separador(texto="", color=C.GRIS):
    """Imprime un separador visual limpio entre bloques o subsecciones."""
    if not texto:
        print(f"  {color}{'─' * ANCHO_CAJA}{C.RESET}")
    else:
        etiqueta = f" {texto} "
        restante = max(4, ANCHO_CAJA - len(etiqueta) - 3)
        print(f"\n  {color}───{C.BOLD}{C.BLANCO}{etiqueta}{C.RESET}{color}{'─' * restante}{C.RESET}")


def msg_ok(texto):
    print(f"  {C.VERDE}{C.BOLD}[OK]{C.RESET} {C.VERDE}{texto}{C.RESET}")


def msg_info(texto):
    print(f"  {C.CYAN}{C.BOLD}[i]{C.RESET}  {texto}")


def msg_alerta(texto):
    print(f"  {C.AMARILLO}{C.BOLD}[!]{C.RESET}  {C.AMARILLO}{texto}{C.RESET}")


def msg_error(texto):
    print(f"  {C.ROJO}{C.BOLD}[X]{C.RESET}  {C.ROJO}{texto}{C.RESET}")


def dato_linea(etiqueta, valor, color_valor=C.BLANCO):
    print(f"       {C.GRIS}•{C.RESET} {etiqueta:<31}: {color_valor}{C.BOLD}{valor}{C.RESET}")


def pausar(mensaje="Presione ENTER para volver al menú principal..."):
    print()
    separador("", C.GRIS)
    input(f"  {C.AMARILLO}{C.BOLD}>> {mensaje}{C.RESET}")


# ==============================================================================
# CONFIGURACIÓN GLOBAL Y REGISTRO DE TIEMPOS (Requisito g)
# ==============================================================================
ARCHIVO_DATOS = "Datos.txt"
ARCHIVO_COUNTING = "Datos_CountingSort.txt"
ARCHIVO_SELECTION = "Datos_SelectionSort.txt"
ARCHIVO_HEAPSORT = "Datos_HeapSort.txt"

CANTIDAD_CONSIGNA = 100_000_000
RANGO_MAXIMO = 100_000_000

registro_tiempos = {
    "generacion_archivo": None,
    "busqueda_max_min": None,
    "analisis_frecuencia": None,
    "counting_sort": None,
    "selection_sort": None,
    "selection_sort_n": None,
    "selection_sort_proyectado_100M": None,
    "heap_sort": None,
    "avl_construccion": None,
    "avl_n_cargados": None,
    "avl_insercion": None,
    "avl_busqueda": None,
    "avl_eliminacion": None,
    "heap_construccion": None,
    "heap_n_cargados": None,
    "heap_insercion": None,
    "heap_busqueda": None,
    "heap_eliminacion_max": None,
    "heap_eliminacion_min": None,
}


# ==============================================================================
# UTILIDADES DE LECTURA Y ESCRITURA DE ARCHIVOS
# ==============================================================================
def cargar_numeros_desde_archivo(ruta_archivo, limite=None):
    """
    Lee los números enteros almacenados en un archivo de texto (uno por línea
    o separados por espacios). Si se especifica 'limite', carga únicamente los
    primeros N números para pruebas sobre estructuras en memoria.
    """
    if not os.path.exists(ruta_archivo):
        msg_error(f"El archivo '{ruta_archivo}' no existe. Ejecute primero la opción a).")
        return []

    numeros = []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.split()
            for p in partes:
                numeros.append(int(p))
                if limite is not None and len(numeros) >= limite:
                    return numeros
    return numeros


def guardar_numeros_en_archivo(ruta_archivo, iterable_numeros):
    """
    Guarda una secuencia de números enteros en un archivo de texto utilizando
    escritura por bloques (buffering) para maximizar el rendimiento de E/S.
    """
    TAM_BLOQUE = 100_000
    buffer_lineas = []
    contador = 0

    with open(ruta_archivo, "w", encoding="utf-8", buffering=8 * 1024 * 1024) as f:
        for num in iterable_numeros:
            buffer_lineas.append(f"{num}\n")
            contador += 1
            if len(buffer_lineas) >= TAM_BLOQUE:
                f.writelines(buffer_lineas)
                buffer_lineas.clear()
        if buffer_lineas:
            f.writelines(buffer_lineas)
            buffer_lineas.clear()
    return contador


# ==============================================================================
# OPCIÓN a) GENERACIÓN DEL ARCHIVO DE DATOS ("Datos.txt")
# ==============================================================================
def opcion_a_generar_datos(cantidad_forzada=None, rango_max_forzado=None):
    """
    a) Generación del archivo de datos:
       Genera el archivo 'Datos.txt' con números aleatorios en el rango
       [0, 100.000.000]. Por defecto propone los 100.000.000 de la consigna
       o permite seleccionar un volumen menor para pruebas rápidas en PC.
    """
    cartel("a) GENERACIÓN DEL ARCHIVO DE DATOS", "Archivo destino: Datos.txt  |  Complejidad: O(n)", C.CYAN)

    if cantidad_forzada is not None:
        n = cantidad_forzada
        rango_max = rango_max_forzado if rango_max_forzado is not None else RANGO_MAXIMO
    else:
        msg_info(f"Consigna: N = {CANTIDAD_CONSIGNA:,} números en [0, {RANGO_MAXIMO:,}] (~880 MB en disco).")
        separador("Seleccione el volumen de datos a generar", C.CYAN)
        print(f"    {C.AMARILLO}[1]{C.RESET} {C.BLANCO}100.000.000{C.RESET} de números  {C.GRIS}(Volumen completo de la consigna){C.RESET}")
        print(f"    {C.AMARILLO}[2]{C.RESET}   {C.BLANCO}1.000.000{C.RESET} de números  {C.GRIS}(Volumen intermedio ágil ~8.8 MB){C.RESET}")
        print(f"    {C.AMARILLO}[3]{C.RESET}     {C.BLANCO}100.000{C.RESET} números     {C.GRIS}(Volumen rápido de prueba ~680 KB){C.RESET}")
        print(f"    {C.AMARILLO}[4]{C.RESET} Cantidad personalizada")
        print()
        eleccion = input(f"  {C.AMARILLO}>> Elija una opción [1-4, Enter=3 (100.000)]: {C.RESET}").strip()

        if eleccion == "1":
            n = 100_000_000
        elif eleccion == "2":
            n = 1_000_000
        elif eleccion == "4":
            try:
                n = int(input(f"  {C.AMARILLO}>> Ingrese cantidad N de números: {C.RESET}").strip())
            except ValueError:
                n = 100_000
        else:
            n = 100_000

        rango_max = RANGO_MAXIMO
        resp_rango = input(
            f"  {C.AMARILLO}>> Rango de valores: [1] Proporcional [0, {n:,}]  [2] Completo [0, 100M] (Enter=1): {C.RESET}"
        ).strip()
        if resp_rango != "2":
            rango_max = n

    separador("Progreso de generación", C.VERDE)
    msg_info(f"Generando '{ARCHIVO_DATOS}' con {n:,} números aleatorios en [0, {rango_max:,}]...")
    t_inicio = time.perf_counter()

    TAM_LOTE = 1_000_000
    generados = 0

    with open(ARCHIVO_DATOS, "w", encoding="utf-8", buffering=16 * 1024 * 1024) as f:
        if TIENE_NUMPY:
            rng = np.random.default_rng(seed=2026)
            while generados < n:
                lote = min(TAM_LOTE, n - generados)
                arr = rng.integers(0, rango_max + 1, size=lote, dtype=np.int64)
                f.write("\n".join(map(str, arr.tolist())) + "\n")
                generados += lote
                porcentaje = (generados / n) * 100
                print(f"\r       {C.CYAN}Progreso:{C.RESET} {generados:,} / {n:,} ({C.VERDE}{porcentaje:5.1f}%{C.RESET})", end="", flush=True)
        else:
            random.seed(2026)
            lote_peq = 100_000
            while generados < n:
                actual = min(lote_peq, n - generados)
                bloque = [str(random.randint(0, rango_max)) for _ in range(actual)]
                f.write("\n".join(bloque) + "\n")
                generados += actual
                porcentaje = (generados / n) * 100
                print(f"\r       {C.CYAN}Progreso:{C.RESET} {generados:,} / {n:,} ({C.VERDE}{porcentaje:5.1f}%{C.RESET})", end="", flush=True)

    t_fin = time.perf_counter()
    duracion = t_fin - t_inicio
    registro_tiempos["generacion_archivo"] = duracion
    tam_mb = os.path.getsize(ARCHIVO_DATOS) / (1024 * 1024)

    print("\n")
    msg_ok(f"Archivo '{ARCHIVO_DATOS}' generado exitosamente.")
    dato_linea("Cantidad de elementos (n)", f"{n:,}", C.CYAN)
    dato_linea("Rango de valores", f"[0, {rango_max:,}]", C.BLANCO)
    dato_linea("Tamaño en disco", f"{tam_mb:.2f} MB", C.BLANCO)
    dato_linea("Tiempo de ejecución", f"{duracion:.4f} segundos", C.VERDE)
    return n, rango_max


# ==============================================================================
# OPCIÓN b) BÚSQUEDA DEL MÁXIMO Y MÍNIMO
# ==============================================================================
def opcion_b_buscar_max_min():
    """
    b) Búsqueda del máximo y mínimo:
       Recorre secuencialmente 'Datos.txt' en O(n) temporal y O(1) espacial.
    """
    cartel("b) BÚSQUEDA DEL MÁXIMO Y MÍNIMO", "Recorrido secuencial: Tiempo O(n)  |  Memoria O(1)", C.AZUL)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    msg_info(f"Analizando '{ARCHIVO_DATOS}' en una sola pasada...")
    t_inicio = time.perf_counter()
    minimo = None
    maximo = None
    cantidad = 0

    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        for linea in f:
            for token in linea.split():
                val = int(token)
                if minimo is None or val < minimo:
                    minimo = val
                if maximo is None or val > maximo:
                    maximo = val
                cantidad += 1

    duracion = time.perf_counter() - t_inicio
    registro_tiempos["busqueda_max_min"] = duracion

    separador("Resultados Obtenidos", C.AZUL)
    msg_ok("Búsqueda finalizada correctamente.")
    dato_linea("Elementos analizados (n)", f"{cantidad:,}", C.CYAN)
    dato_linea("Número MENOR (Mínimo)", f"{minimo:,}", C.AMARILLO)
    dato_linea("Número MAYOR (Máximo)", f"{maximo:,}", C.VERDE)
    dato_linea("Complejidad Temporal", "O(n)  [Mejor, Promedio y Peor Caso]", C.BLANCO)
    dato_linea("Complejidad Espacial", "O(1)  [Memoria auxiliar constante]", C.BLANCO)
    dato_linea("Tiempo de ejecución", f"{duracion:.4f} segundos", C.VERDE)
    return minimo, maximo, cantidad


# ==============================================================================
# OPCIÓN c) ANÁLISIS DE FRECUENCIA (TOP 10 NÚMEROS MÁS REPETIDOS)
# ==============================================================================
def opcion_c_analisis_frecuencia():
    """
    c) Análisis de frecuencia:
       Determina los 10 números que más se repiten dentro de 'Datos.txt'.
    """
    cartel("c) ANÁLISIS DE FRECUENCIA (TOP 10)", "Conteo de ocurrencias en 'Datos.txt'  |  Complejidad: O(n)", C.MAGENTA)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    msg_info("Contabilizando apariciones de cada número...")
    t_inicio = time.perf_counter()
    contador = Counter()
    total_leidos = 0

    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        for linea in f:
            partes = [int(x) for x in linea.split()]
            contador.update(partes)
            total_leidos += len(partes)

    top_10 = contador.most_common(10)
    duracion = time.perf_counter() - t_inicio
    registro_tiempos["analisis_frecuencia"] = duracion

    separador("Ranking Top 10 Más Repetidos", C.MAGENTA)
    dato_linea("Total de números procesados", f"{total_leidos:,}", C.CYAN)
    dato_linea("Valores únicos distintos", f"{len(contador):,}", C.BLANCO)
    print()
    print(f"  {C.MAGENTA}┌──────────┬────────────────────┬──────────────────┐{C.RESET}")
    print(f"  {C.MAGENTA}│{C.BOLD}{C.BLANCO}  PUESTO  {C.MAGENTA}│{C.BLANCO}       NÚMERO       {C.MAGENTA}│{C.BLANCO}   REPETICIONES   {C.MAGENTA}│{C.RESET}")
    print(f"  {C.MAGENTA}├──────────┼────────────────────┼──────────────────┤{C.RESET}")
    for idx, (numero, frec) in enumerate(top_10, start=1):
        col = C.AMARILLO if idx <= 3 else C.BLANCO
        print(f"  {C.MAGENTA}│{C.RESET}  {col}{C.BOLD}#{idx:<7}{C.RESET}{C.MAGENTA}│{C.RESET} {col}{numero:>18,}{C.RESET} {C.MAGENTA}│{C.RESET} {C.VERDE}{frec:>16,}{C.RESET} {C.MAGENTA}│{C.RESET}")
    print(f"  {C.MAGENTA}└──────────┴────────────────────┴──────────────────┘{C.RESET}")
    print()
    dato_linea("Tiempo de ejecución", f"{duracion:.4f} segundos", C.VERDE)
    return top_10


# ==============================================================================
# OPCIÓN d) ORDENAMIENTO MEDIANTE COUNTING SORT
# ==============================================================================
def algoritmo_counting_sort(datos):
    """
    Implementación pura de Counting Sort (Unidad 3 - Algoritmo No Comparativo):
      - Complejidad Temporal: O(n + k) en Mejor, Promedio y Peor Caso.
      - Complejidad Espacial: O(k) para el vector de conteo.
    """
    if not datos:
        return []

    k = max(datos)
    conteo = [0] * (k + 1)

    for num in datos:
        conteo[num] += 1

    resultado = []
    for valor, cantidad in enumerate(conteo):
        if cantidad > 0:
            resultado.extend([valor] * cantidad)

    return resultado


def opcion_d_counting_sort():
    """
    d) Ordenamiento mediante Counting Sort -> 'Datos_CountingSort.txt'
    """
    cartel("d) ORDENAMIENTO MEDIANTE COUNTING SORT", "Algoritmo No Comparativo (Unidad 3)  |  Complejidad: O(n + k)", C.VERDE)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    msg_info(f"Paso 1/3: Cargando datos desde '{ARCHIVO_DATOS}'...")
    datos = cargar_numeros_desde_archivo(ARCHIVO_DATOS)
    n = len(datos)
    if n == 0:
        return None

    k = max(datos)
    msg_info(f"Paso 2/3: Ejecutando Counting Sort sobre n = {n:,} elementos (k_max = {k:,})...")
    t_inicio = time.perf_counter()
    ordenados = algoritmo_counting_sort(datos)
    duracion_sort = time.perf_counter() - t_inicio
    registro_tiempos["counting_sort"] = duracion_sort

    msg_info(f"Paso 3/3: Guardando resultado en '{ARCHIVO_COUNTING}'...")
    t_io_ini = time.perf_counter()
    guardar_numeros_en_archivo(ARCHIVO_COUNTING, ordenados)
    duracion_io = time.perf_counter() - t_io_ini

    separador("Resumen de Counting Sort", C.VERDE)
    msg_ok("Ordenamiento Counting Sort finalizado con éxito.")
    dato_linea("Elementos ordenados (n)", f"{n:,}", C.CYAN)
    dato_linea("Valor máximo (k)", f"{k:,}", C.BLANCO)
    dato_linea("Complejidad Temporal", "O(n + k)  [Mejor y Peor Caso]", C.AMARILLO)
    dato_linea("Complejidad Espacial", "O(k)  [Vector índice de frecuencias]", C.BLANCO)
    dato_linea("Tiempo de ordenamiento", f"{duracion_sort:.6f} segundos", C.VERDE)
    dato_linea("Tiempo de escritura disco", f"{duracion_io:.4f} segundos", C.GRIS)
    dato_linea("Archivo generado", ARCHIVO_COUNTING, C.CYAN)
    return duracion_sort


# ==============================================================================
# OPCIÓN e) ORDENAMIENTO MEDIANTE SELECTION SORT
# ==============================================================================
def algoritmo_selection_sort(arr):
    """
    Implementación pura de Selection Sort (Unidad 3 - Fuerza Bruta):
      - Serie Aritmética: C(n) = n(n - 1) / 2 comparaciones -> O(n^2).
      - Memoria auxiliar: O(1) (in-place).
    """
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        val_min = arr[i]
        for j in range(i + 1, n):
            if arr[j] < val_min:
                val_min = arr[j]
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def opcion_e_selection_sort(limite_muestra=None):
    """
    e) Ordenamiento mediante Selection Sort -> 'Datos_SelectionSort.txt'
    """
    cartel("e) ORDENAMIENTO MEDIANTE SELECTION SORT", "Fuerza Bruta (Unidad 3)  |  Complejidad: O(n²)  |  Memoria: O(1)", C.ROJO)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    if limite_muestra is not None:
        datos = cargar_numeros_desde_archivo(ARCHIVO_DATOS, limite=limite_muestra)
    else:
        datos_totales = cargar_numeros_desde_archivo(ARCHIVO_DATOS)
        n_total = len(datos_totales)
        if n_total > 30_000:
            comp_totales = n_total * (n_total - 1) // 2
            msg_alerta(f"Aviso de Complejidad Cuadrática O(n²) sobre n = {n_total:,} números:")
            print(f"       Por Serie Aritmética requiere n(n-1)/2 = {C.ROJO}{comp_totales:,}{C.RESET} comparaciones.")
            print(f"       Para n = 100.000.000 serían ~5 × 10^15 comparaciones (semanas/meses).")
            print()
            resp = input(f"  {C.AMARILLO}>> Ingrese tamaño de muestra N [Enter=10000, 0=Todos]: {C.RESET}").strip()
            if resp == "0":
                datos = datos_totales
            else:
                try:
                    n_muestra = int(resp) if resp else 10_000
                except ValueError:
                    n_muestra = 10_000
                datos = datos_totales[:n_muestra]
        else:
            datos = datos_totales

    n = len(datos)
    comparaciones = n * (n - 1) // 2
    msg_info(f"Ejecutando Selection Sort sobre n = {n:,} elementos ({comparaciones:,} comparaciones)...")

    t_inicio = time.perf_counter()
    algoritmo_selection_sort(datos)
    duracion = time.perf_counter() - t_inicio

    factor_escala = (CANTIDAD_CONSIGNA / n) ** 2
    tiempo_proyectado_seg = duracion * factor_escala
    tiempo_proyectado_dias = tiempo_proyectado_seg / 86400.0

    registro_tiempos["selection_sort"] = duracion
    registro_tiempos["selection_sort_n"] = n
    registro_tiempos["selection_sort_proyectado_100M"] = tiempo_proyectado_seg

    guardar_numeros_en_archivo(ARCHIVO_SELECTION, datos)

    separador("Resumen de Selection Sort", C.ROJO)
    msg_ok("Ordenamiento Selection Sort finalizado.")
    dato_linea("Elementos ordenados (n)", f"{n:,}", C.CYAN)
    dato_linea("Comparaciones [n(n-1)/2]", f"{comparaciones:,}", C.AMARILLO)
    dato_linea("Complejidad Temporal", "O(n²)  [Mejor, Medio y Peor Caso]", C.ROJO)
    dato_linea("Tiempo real medido", f"{duracion:.6f} segundos", C.VERDE)
    dato_linea("Proyección para 100.000.000", f"{tiempo_proyectado_seg:,.1f} s (~{tiempo_proyectado_dias:,.1f} días)", C.ROJO)
    dato_linea("Archivo generado", ARCHIVO_SELECTION, C.CYAN)
    return duracion


# ==============================================================================
# OPCIÓN f) VERIFICACIÓN DEL ORDENAMIENTO
# ==============================================================================
def verificar_archivo_ordenado(ruta_archivo):
    """
    Verifica en tiempo lineal O(n) y espacio O(1) que el archivo cumpla
    orden ascendente estricto/no decreciente (anterior <= actual).
    """
    if not os.path.exists(ruta_archivo):
        return False, 0, None, None, "Archivo no encontrado (aún no generado)"

    anterior = None
    primero = None
    cantidad = 0

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            for token in linea.split():
                actual = int(token)
                if primero is None:
                    primero = actual
                if anterior is not None and actual < anterior:
                    return False, cantidad, primero, actual, f"Desorden en pos {cantidad}: {anterior} > {actual}"
                anterior = actual
                cantidad += 1

    if cantidad == 0:
        return False, 0, None, None, "Archivo vacío"
    return True, cantidad, primero, anterior, "Orden ascendente verificado (a[i] <= a[i+1])"


def opcion_f_verificar_ordenamiento():
    """
    f) Verificación del ordenamiento ascendente de los archivos d), e) y k).
    """
    cartel("f) VERIFICACIÓN DEL ORDENAMIENTO ASCENDENTE", "Comprobación lineal O(n) de A[i] <= A[i+1]", C.CYAN)

    archivos_a_verificar = [
        ("Opción d) Counting Sort", ARCHIVO_COUNTING),
        ("Opción e) Selection Sort", ARCHIVO_SELECTION),
        ("Opción k) Heap Sort", ARCHIVO_HEAPSORT),
    ]

    for etiqueta, ruta in archivos_a_verificar:
        t0 = time.perf_counter()
        ok, cant, prim, ult, msg = verificar_archivo_ordenado(ruta)
        dt = time.perf_counter() - t0

        separador(f"{etiqueta} ({ruta})", C.VERDE if ok else C.AMARILLO)
        if ok:
            msg_ok("CORRECTO — Ordenado de manera ascendente.")
            dato_linea("Elementos verificados", f"{cant:,}", C.CYAN)
            dato_linea("Primer -> Último valor", f"{prim:,}  --->  {ult:,}", C.BLANCO)
            dato_linea("Tiempo de verificación", f"{dt:.4f} segundos [O(n)]", C.VERDE)
        else:
            msg_alerta(msg)


# ==============================================================================
# OPCIÓN i) IMPLEMENTACIÓN DE ÁRBOL AVL (Unidad 6 - Transforma y Conquista)
# ==============================================================================
class NodoAVL:
    """Nodo de un Árbol AVL con contador de frecuencia para duplicados."""
    __slots__ = ("dato", "frecuencia", "altura", "izquierdo", "derecho")

    def __init__(self, dato):
        self.dato = dato
        self.frecuencia = 1
        self.altura = 1
        self.izquierdo = None
        self.derecho = None


class ArbolAVL:
    """
    Árbol AVL (Adelson-Velskii y Landis, 1962 - Unidad 6):
      FB = Altura(Subárbol Izquierdo) - Altura(Subárbol Derecho) en {-1, 0, +1}.
      Implementa Rotaciones Simples (RSD/RSI) y Dobles (RDD/RDI).
    """
    def __init__(self):
        self.raiz = None
        self.cantidad_nodos_unicos = 0
        self.cantidad_elementos_totales = 0
        self.rotaciones_realizadas = 0

    @staticmethod
    def obtener_altura(nodo):
        return nodo.altura if nodo is not None else 0

    def obtener_factor_balance(self, nodo):
        if nodo is None:
            return 0
        return self.obtener_altura(nodo.izquierdo) - self.obtener_altura(nodo.derecho)

    def _actualizar_altura(self, nodo):
        h_izq = self.obtener_altura(nodo.izquierdo)
        h_der = self.obtener_altura(nodo.derecho)
        nodo.altura = 1 + (h_izq if h_izq > h_der else h_der)

    def _rotacion_derecha(self, y):
        self.rotaciones_realizadas += 1
        x = y.izquierdo
        T2 = x.derecho
        x.derecho = y
        y.izquierdo = T2
        self._actualizar_altura(y)
        self._actualizar_altura(x)
        return x

    def _rotacion_izquierda(self, x):
        self.rotaciones_realizadas += 1
        y = x.derecho
        T2 = y.izquierdo
        y.izquierdo = x
        x.derecho = T2
        self._actualizar_altura(x)
        self._actualizar_altura(y)
        return y

    def _balancear(self, nodo):
        self._actualizar_altura(nodo)
        fb = self.obtener_factor_balance(nodo)

        if fb > 1:
            if self.obtener_factor_balance(nodo.izquierdo) < 0:
                nodo.izquierdo = self._rotacion_izquierda(nodo.izquierdo)
            return self._rotacion_derecha(nodo)

        if fb < -1:
            if self.obtener_factor_balance(nodo.derecho) > 0:
                nodo.derecho = self._rotacion_derecha(nodo.derecho)
            return self._rotacion_izquierda(nodo)

        return nodo

    def insertar(self, valor):
        self.raiz = self._insertar_rec(self.raiz, valor)

    def _insertar_rec(self, nodo, valor):
        if nodo is None:
            self.cantidad_nodos_unicos += 1
            self.cantidad_elementos_totales += 1
            return NodoAVL(valor)

        if valor < nodo.dato:
            nodo.izquierdo = self._insertar_rec(nodo.izquierdo, valor)
        elif valor > nodo.dato:
            nodo.derecho = self._insertar_rec(nodo.derecho, valor)
        else:
            nodo.frecuencia += 1
            self.cantidad_elementos_totales += 1
            return nodo

        return self._balancear(nodo)

    def buscar(self, valor):
        actual = self.raiz
        pasos = 0
        while actual is not None:
            pasos += 1
            if valor == actual.dato:
                return actual, pasos
            elif valor < actual.dato:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        return None, pasos

    def eliminar(self, valor):
        eliminado = [False]
        self.raiz = self._eliminar_rec(self.raiz, valor, eliminado)
        return eliminado[0]

    def _obtener_nodo_minimo(self, nodo):
        actual = nodo
        while actual.izquierdo is not None:
            actual = actual.izquierdo
        return actual

    def _eliminar_rec(self, nodo, valor, eliminado):
        if nodo is None:
            return None

        if valor < nodo.dato:
            nodo.izquierdo = self._eliminar_rec(nodo.izquierdo, valor, eliminado)
        elif valor > nodo.dato:
            nodo.derecho = self._eliminar_rec(nodo.derecho, valor, eliminado)
        else:
            eliminado[0] = True
            self.cantidad_elementos_totales -= nodo.frecuencia
            self.cantidad_nodos_unicos -= 1

            if nodo.izquierdo is None:
                return nodo.derecho
            elif nodo.derecho is None:
                return nodo.izquierdo

            sucesor = self._obtener_nodo_minimo(nodo.derecho)
            nodo.dato = sucesor.dato
            nodo.frecuencia = sucesor.frecuencia

            self.cantidad_elementos_totales += sucesor.frecuencia
            self.cantidad_nodos_unicos += 1
            eliminado_suc = [False]
            nodo.derecho = self._eliminar_rec(nodo.derecho, sucesor.dato, eliminado_suc)

        return self._balancear(nodo)

    def recorrido_inorden_muestra(self, limite_muestra=20):
        """Recorrido InOrden (Izquierda -> Nodo -> Derecha) -> Orden ascendente."""
        muestra = []
        pila = []
        actual = self.raiz
        while (actual is not None or pila) and len(muestra) < limite_muestra:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo
            actual = pila.pop()
            muestra.append(actual.dato)
            actual = actual.derecho
        return muestra


def opcion_i_arbol_avl(limite_carga=None, valor_insertar=None, valor_buscar=None, valor_eliminar=None):
    """
    i) Implementación de Árbol AVL: construcción, InOrden, inserción, búsqueda y eliminación.
    """
    cartel("i) IMPLEMENTACIÓN DE ÁRBOL AVL", "Transforma y Conquista: Cambio de Representación  |  O(log n)", C.AZUL)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    modo_interactivo = (limite_carga is None)
    if modo_interactivo:
        resp = input(f"  {C.AMARILLO}>> Cantidad de elementos a insertar en el AVL [Enter=50000, 0=Todos]: {C.RESET}").strip()
        if resp == "0":
            limite_carga = None
        else:
            try:
                limite_carga = int(resp) if resp else 50_000
            except ValueError:
                limite_carga = 50_000

    datos = cargar_numeros_desde_archivo(ARCHIVO_DATOS, limite=limite_carga)
    n_cargados = len(datos)
    msg_info(f"Construyendo Árbol AVL con {n_cargados:,} números del archivo...")

    avl = ArbolAVL()
    t0 = time.perf_counter()
    for num in datos:
        avl.insertar(num)
    t_construccion = time.perf_counter() - t0

    registro_tiempos["avl_construccion"] = t_construccion
    registro_tiempos["avl_n_cargados"] = n_cargados

    altura_teorica_min = math.floor(math.log2(max(1, avl.cantidad_nodos_unicos))) + 1
    altura_teorica_max = int(1.44 * math.log2(max(2, avl.cantidad_nodos_unicos)))

    separador("1. Propiedades del Árbol AVL Construido", C.AZUL)
    msg_ok("Árbol AVL balanceado correctamente.")
    dato_linea("Elementos insertados totales", f"{avl.cantidad_elementos_totales:,}", C.CYAN)
    dato_linea("Cantidad total de nodos (ún.)", f"{avl.cantidad_nodos_unicos:,}", C.BLANCO)
    dato_linea("Altura del árbol", f"{avl.obtener_altura(avl.raiz)} niveles (Cota AVL: [{altura_teorica_min}, {altura_teorica_max}])", C.AMARILLO)
    dato_linea("Factor de Balance en raíz", f"{avl.obtener_factor_balance(avl.raiz)} (Raíz = {avl.raiz.dato if avl.raiz else 'N/A'})", C.VERDE)
    dato_linea("Rotaciones aplicadas", f"{avl.rotaciones_realizadas:,} (Simples + Dobles)", C.BLANCO)
    dato_linea("Tiempo de construcción", f"{t_construccion:.4f} segundos", C.VERDE)

    separador("2. Recorrido InOrden (Izquierda -> Nodo -> Derecha)", C.CYAN)
    muestra_inorden = avl.recorrido_inorden_muestra(20)
    print(f"  {C.CYAN}Primeros 20 valores ordenados:{C.RESET}")
    print(f"  {C.BLANCO}{muestra_inorden}{C.RESET}")

    separador("3. Operaciones Individuales Cronometradas [O(log n)]", C.MAGENTA)
    if modo_interactivo:
        try:
            inp_ins = input(f"  {C.AMARILLO}>> Ingrese un nuevo valor a INSERTAR [Enter=99999999]: {C.RESET}").strip()
            valor_insertar = int(inp_ins) if inp_ins else 99_999_999
        except ValueError:
            valor_insertar = 99_999_999

        sugerido = datos[len(datos) // 2] if datos else valor_insertar
        try:
            inp_bus = input(f"  {C.AMARILLO}>> Ingrese un valor a BUSCAR [Enter={sugerido}]: {C.RESET}").strip()
            valor_buscar = int(inp_bus) if inp_bus else sugerido
        except ValueError:
            valor_buscar = sugerido

        try:
            inp_eli = input(f"  {C.AMARILLO}>> Ingrese un valor a ELIMINAR [Enter={valor_buscar}]: {C.RESET}").strip()
            valor_eliminar = int(inp_eli) if inp_eli else valor_buscar
        except ValueError:
            valor_eliminar = valor_buscar
    else:
        if valor_insertar is None:
            valor_insertar = 99_999_999
        if valor_buscar is None:
            valor_buscar = datos[len(datos) // 2] if datos else valor_insertar
        if valor_eliminar is None:
            valor_eliminar = valor_buscar

    t_ins_ini = time.perf_counter()
    avl.insertar(valor_insertar)
    t_ins = time.perf_counter() - t_ins_ini
    registro_tiempos["avl_insercion"] = t_ins

    t_bus_ini = time.perf_counter()
    nodo_hallado, pasos_bus = avl.buscar(valor_buscar)
    t_bus = time.perf_counter() - t_bus_ini
    registro_tiempos["avl_busqueda"] = t_bus

    t_eli_ini = time.perf_counter()
    fue_eliminado = avl.eliminar(valor_eliminar)
    t_eli = time.perf_counter() - t_eli_ini
    registro_tiempos["avl_eliminacion"] = t_eli

    print()
    print(f"  {C.CYAN}{C.BOLD}• INSERCIÓN ({valor_insertar:,}):{C.RESET}")
    dato_linea("Tiempo de ejecución", f"{t_ins * 1e6:.2f} µs ({t_ins:.8f} s)", C.VERDE)
    dato_linea("Nodos / Altura actual", f"{avl.cantidad_nodos_unicos:,} nodos | Altura {avl.obtener_altura(avl.raiz)}", C.BLANCO)

    print(f"\n  {C.CYAN}{C.BOLD}• BÚSQUEDA ({valor_buscar:,}):{C.RESET}")
    if nodo_hallado:
        dato_linea("Resultado", f"ENCONTRADO (Frec={nodo_hallado.frecuencia}) en {pasos_bus} pasos", C.VERDE)
    else:
        dato_linea("Resultado", f"NO ENCONTRADO tras {pasos_bus} pasos", C.ROJO)
    dato_linea("Tiempo de ejecución", f"{t_bus * 1e6:.2f} µs ({t_bus:.8f} s)", C.VERDE)

    print(f"\n  {C.CYAN}{C.BOLD}• ELIMINACIÓN ({valor_eliminar:,}):{C.RESET}")
    dato_linea("Resultado", "ELIMINADO Y REBALANCEADO" if fue_eliminado else "NO EXISTÍA", C.VERDE if fue_eliminado else C.AMARILLO)
    dato_linea("Tiempo de ejecución", f"{t_eli * 1e6:.2f} µs ({t_eli:.8f} s)", C.VERDE)
    dato_linea("Nodos tras eliminar", f"{avl.cantidad_nodos_unicos:,} nodos | Altura {avl.obtener_altura(avl.raiz)}", C.BLANCO)
    return avl


# ==============================================================================
# OPCIÓN j) IMPLEMENTACIÓN DE HEAP / MONTÍCULO BINARIO (Unidad 6)
# ==============================================================================
class HeapBinario:
    """
    Montículo Binario (Max-Heap o Min-Heap) en arreglo contiguo (Unidad 6):
      Padre(i) = (i - 1) // 2  |  Izq(i) = 2*i + 1  |  Der(i) = 2*i + 2.
    """
    def __init__(self, datos_iniciales=None, es_max_heap=True):
        self.es_max_heap = es_max_heap
        self.arreglo = list(datos_iniciales) if datos_iniciales is not None else []
        if self.arreglo:
            self.construir_heap()

    def _comparar(self, a, b):
        return (a > b) if self.es_max_heap else (a < b)

    def construir_heap(self):
        """Build-Heap en tiempo lineal O(n)."""
        n = len(self.arreglo)
        for i in range((n // 2) - 1, -1, -1):
            self._heapify_down(i, n)

    def _heapify_up(self, idx):
        """Heapify Up / Sift Up en O(log n)."""
        arr = self.arreglo
        while idx > 0:
            padre = (idx - 1) // 2
            if self._comparar(arr[idx], arr[padre]):
                arr[idx], arr[padre] = arr[padre], arr[idx]
                idx = padre
            else:
                break

    def _heapify_down(self, idx, n):
        """Heapify Down / Sift Down en O(log n)."""
        arr = self.arreglo
        es_max = self.es_max_heap
        while True:
            mejor = idx
            izq = 2 * idx + 1
            der = 2 * idx + 2

            if es_max:
                if izq < n and arr[izq] > arr[mejor]:
                    mejor = izq
                if der < n and arr[der] > arr[mejor]:
                    mejor = der
            else:
                if izq < n and arr[izq] < arr[mejor]:
                    mejor = izq
                if der < n and arr[der] < arr[mejor]:
                    mejor = der

            if mejor != idx:
                arr[idx], arr[mejor] = arr[mejor], arr[idx]
                idx = mejor
            else:
                break

    def insertar(self, valor):
        self.arreglo.append(valor)
        self._heapify_up(len(self.arreglo) - 1)

    def buscar(self, valor):
        for idx, elem in enumerate(self.arreglo):
            if elem == valor:
                return idx
        return -1

    def eliminar_raiz(self):
        n = len(self.arreglo)
        if n == 0:
            return None
        raiz = self.arreglo[0]
        ultimo = self.arreglo.pop()
        if self.arreglo:
            self.arreglo[0] = ultimo
            self._heapify_down(0, len(self.arreglo))
        return raiz

    def cantidad_elementos(self):
        return len(self.arreglo)

    def obtener_raiz(self):
        return self.arreglo[0] if self.arreglo else None

    def altura_aproximada(self):
        n = len(self.arreglo)
        return 0 if n == 0 else math.floor(math.log2(n)) + 1


def opcion_j_implementacion_heap(limite_carga=None, valor_insertar=None, valor_buscar=None):
    """
    j) Implementación de Heap Binario (Max-Heap y Min-Heap).
    """
    cartel("j) IMPLEMENTACIÓN DE HEAP BINARIO", "Max-Heap y Min-Heap sobre Arreglo  |  Padre=(i-1)//2, Hijos=2i+1, 2i+2", C.AMARILLO)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    modo_interactivo = (limite_carga is None)
    if modo_interactivo:
        resp = input(f"  {C.AMARILLO}>> Cantidad de elementos a cargar en el Heap [Enter=Todos]: {C.RESET}").strip()
        try:
            limite_carga = int(resp) if resp else None
        except ValueError:
            limite_carga = None

    datos = cargar_numeros_desde_archivo(ARCHIVO_DATOS, limite=limite_carga)
    n_datos = len(datos)

    msg_info(f"Construyendo Max-Heap y Min-Heap con {n_datos:,} elementos (Build-Heap O(n))...")
    t0 = time.perf_counter()
    max_heap = HeapBinario(datos, es_max_heap=True)
    t_build_max = time.perf_counter() - t0

    t1 = time.perf_counter()
    min_heap = HeapBinario(datos, es_max_heap=False)
    t_build_min = time.perf_counter() - t1

    registro_tiempos["heap_construccion"] = t_build_max
    registro_tiempos["heap_n_cargados"] = n_datos

    separador("1. Estado Inicial de Max-Heap y Min-Heap", C.AMARILLO)
    print(f"  {C.AMARILLO}┌────────────────────────────────┬──────────────────────┬──────────────────────┐{C.RESET}")
    print(f"  {C.AMARILLO}│{C.BOLD}{C.BLANCO} Propiedad                      {C.AMARILLO}│{C.CYAN}       MAX-HEAP       {C.AMARILLO}│{C.VERDE}       MIN-HEAP       {C.AMARILLO}│{C.RESET}")
    print(f"  {C.AMARILLO}├────────────────────────────────┼──────────────────────┼──────────────────────┤{C.RESET}")
    print(f"  {C.AMARILLO}│{C.RESET} Cantidad de elementos          {C.AMARILLO}│{C.BLANCO} {max_heap.cantidad_elementos():>20,} {C.AMARILLO}│{C.BLANCO} {min_heap.cantidad_elementos():>20,} {C.AMARILLO}│{C.RESET}")
    print(f"  {C.AMARILLO}│{C.RESET} Elemento raíz (índice 0)       {C.AMARILLO}│{C.CYAN}{C.BOLD} {max_heap.obtener_raiz():>20,} {C.RESET}{C.AMARILLO}│{C.VERDE}{C.BOLD} {min_heap.obtener_raiz():>20,} {C.RESET}{C.AMARILLO}│{C.RESET}")
    print(f"  {C.AMARILLO}│{C.RESET} Altura aproximada (niveles)    {C.AMARILLO}│{C.BLANCO} {max_heap.altura_aproximada():>20} {C.AMARILLO}│{C.BLANCO} {min_heap.altura_aproximada():>20} {C.AMARILLO}│{C.RESET}")
    print(f"  {C.AMARILLO}│{C.RESET} Tiempo Build-Heap O(n)         {C.AMARILLO}│{C.VERDE} {t_build_max:>18.4f} s {C.AMARILLO}│{C.VERDE} {t_build_min:>18.4f} s {C.AMARILLO}│{C.RESET}")
    print(f"  {C.AMARILLO}└────────────────────────────────┴──────────────────────┴──────────────────────┘{C.RESET}")
    print(f"  {C.GRIS}Primeros 10 del arreglo Max-Heap:{C.RESET} {max_heap.arreglo[:10]}")
    print(f"  {C.GRIS}Primeros 10 del arreglo Min-Heap:{C.RESET} {min_heap.arreglo[:10]}")

    separador("2. Operaciones Requeridas Cronometradas", C.CYAN)
    if modo_interactivo:
        try:
            inp_ins = input(f"  {C.AMARILLO}>> Ingrese nuevo elemento a INSERTAR [Enter=99999999]: {C.RESET}").strip()
            valor_insertar = int(inp_ins) if inp_ins else 99_999_999
        except ValueError:
            valor_insertar = 99_999_999

        sugerido = datos[len(datos) // 2] if datos else valor_insertar
        try:
            inp_bus = input(f"  {C.AMARILLO}>> Ingrese un valor a BUSCAR [Enter={sugerido}]: {C.RESET}").strip()
            valor_buscar = int(inp_bus) if inp_bus else sugerido
        except ValueError:
            valor_buscar = sugerido
    else:
        if valor_insertar is None:
            valor_insertar = 99_999_999
        if valor_buscar is None:
            valor_buscar = datos[len(datos) // 2] if datos else valor_insertar

    t_ins_0 = time.perf_counter()
    max_heap.insertar(valor_insertar)
    t_ins_max = time.perf_counter() - t_ins_0
    min_heap.insertar(valor_insertar)
    registro_tiempos["heap_insercion"] = t_ins_max

    t_bus_0 = time.perf_counter()
    idx_hallado = max_heap.buscar(valor_buscar)
    t_bus_heap = time.perf_counter() - t_bus_0
    registro_tiempos["heap_busqueda"] = t_bus_heap

    t_del_max_0 = time.perf_counter()
    max_eliminado = max_heap.eliminar_raiz()
    t_del_max = time.perf_counter() - t_del_max_0
    registro_tiempos["heap_eliminacion_max"] = t_del_max

    t_del_min_0 = time.perf_counter()
    min_eliminado = min_heap.eliminar_raiz()
    t_del_min = time.perf_counter() - t_del_min_0
    registro_tiempos["heap_eliminacion_min"] = t_del_min

    print()
    print(f"  {C.CYAN}{C.BOLD}• INSERCIÓN de {valor_insertar:,} [Heapify Up - O(log n)]:{C.RESET}")
    dato_linea("Tiempo de ejecución", f"{t_ins_max * 1e6:.2f} µs ({t_ins_max:.8f} s)", C.VERDE)

    print(f"\n  {C.CYAN}{C.BOLD}• BÚSQUEDA de {valor_buscar:,} [Recorrido lineal - O(n)]:{C.RESET}")
    if idx_hallado != -1:
        dato_linea("Resultado", f"ENCONTRADO en el índice {idx_hallado:,} del arreglo", C.VERDE)
    else:
        dato_linea("Resultado", "NO ENCONTRADO", C.ROJO)
    dato_linea("Tiempo de ejecución", f"{t_bus_heap * 1e6:.2f} µs ({t_bus_heap:.8f} s)", C.AMARILLO)

    print(f"\n  {C.CYAN}{C.BOLD}• ELIMINAR MÁXIMO EN MAX-HEAP [Heapify Down - O(log n)]:{C.RESET}")
    dato_linea("Máximo extraído / Nueva raíz", f"{max_eliminado:,}  --->  Nueva raíz: {max_heap.obtener_raiz():,}", C.BLANCO)
    dato_linea("Tiempo de ejecución", f"{t_del_max * 1e6:.2f} µs ({t_del_max:.8f} s)", C.VERDE)

    print(f"\n  {C.CYAN}{C.BOLD}• ELIMINAR MÍNIMO EN MIN-HEAP [Heapify Down - O(log n)]:{C.RESET}")
    dato_linea("Mínimo extraído / Nueva raíz", f"{min_eliminado:,}  --->  Nueva raíz: {min_heap.obtener_raiz():,}", C.BLANCO)
    dato_linea("Tiempo de ejecución", f"{t_del_min * 1e6:.2f} µs ({t_del_min:.8f} s)", C.VERDE)
    return max_heap, min_heap


# ==============================================================================
# OPCIÓN k) ORDENAMIENTO MEDIANTE HEAP SORT (Unidad 6)
# ==============================================================================
def _heapify_max_inplace(arr, n, i):
    """Restaura la propiedad de Max-Heap en el subárbol con raíz en 'i'."""
    while True:
        mayor = i
        izq = 2 * i + 1
        der = 2 * i + 2

        if izq < n and arr[izq] > arr[mayor]:
            mayor = izq
        if der < n and arr[der] > arr[mayor]:
            mayor = der

        if mayor != i:
            arr[i], arr[mayor] = arr[mayor], arr[i]
            i = mayor
        else:
            break


def algoritmo_heap_sort(arr):
    """
    Heap Sort en 2 Fases (Unidad 6, diapositiva 25):
      - Fase 1: Construir Max-Heap desde el último no-hoja hasta la raíz -> O(n).
      - Fase 2: Intercambiar raíz con el final y aplicar Heapify -> O(n log n).
      - Memoria auxiliar: O(1) (In-place).
    """
    n = len(arr)

    t_f1_ini = time.perf_counter()
    for i in range((n // 2) - 1, -1, -1):
        _heapify_max_inplace(arr, n, i)
    t_fase1 = time.perf_counter() - t_f1_ini

    t_f2_ini = time.perf_counter()
    for fin in range(n - 1, 0, -1):
        arr[0], arr[fin] = arr[fin], arr[0]
        _heapify_max_inplace(arr, fin, 0)
    t_fase2 = time.perf_counter() - t_f2_ini

    return t_fase1, t_fase2


def opcion_k_heap_sort():
    """
    k) Ordenamiento mediante Heap Sort -> 'Datos_HeapSort.txt'
    """
    cartel("k) ORDENAMIENTO MEDIANTE HEAP SORT", "Transforma y Conquista (Unidad 6)  |  O(n log n)  |  Memoria O(1)", C.VERDE)

    if not os.path.exists(ARCHIVO_DATOS):
        msg_error(f"No se encontró '{ARCHIVO_DATOS}'. Ejecute primero la opción a).")
        return None

    msg_info(f"Paso 1/4: Cargando datos desde '{ARCHIVO_DATOS}'...")
    datos = cargar_numeros_desde_archivo(ARCHIVO_DATOS)
    n = len(datos)
    if n == 0:
        return None

    msg_info(f"Paso 2/4: Ejecutando Heap Sort (Fase 1 Max-Heap + Fase 2 Extracción) sobre n = {n:,}...")
    t_total_ini = time.perf_counter()
    t_fase1, t_fase2 = algoritmo_heap_sort(datos)
    duracion_total = time.perf_counter() - t_total_ini
    registro_tiempos["heap_sort"] = duracion_total

    msg_info(f"Paso 3/4: Guardando resultados en '{ARCHIVO_HEAPSORT}'...")
    guardar_numeros_en_archivo(ARCHIVO_HEAPSORT, datos)

    msg_info(f"Paso 4/4: Verificando ordenamiento ascendente de '{ARCHIVO_HEAPSORT}'...")
    ok, cant, prim, ult, msg = verificar_archivo_ordenado(ARCHIVO_HEAPSORT)

    separador("Resumen de Heap Sort", C.VERDE)
    msg_ok("Ordenamiento Heap Sort finalizado con éxito.")
    dato_linea("Cantidad de elementos (n)", f"{n:,}", C.CYAN)
    dato_linea("Fase 1 (Construir Max-Heap)", f"{t_fase1:.6f} s  [O(n)]", C.BLANCO)
    dato_linea("Fase 2 (Extracción + Heapify)", f"{t_fase2:.6f} s  [O(n log n)]", C.BLANCO)
    dato_linea("Tiempo Total de Ordenamiento", f"{duracion_total:.6f} s  [O(n log n)]", C.VERDE)
    dato_linea("Memoria Auxiliar", "O(1)  [Ordenamiento In-Place]", C.AMARILLO)
    dato_linea("Archivo generado", ARCHIVO_HEAPSORT, C.CYAN)
    dato_linea("Verificación de Orden", f"{'EXITOSA' if ok else 'FALLIDA'} ({prim:,} ---> {ult:,})", C.VERDE if ok else C.ROJO)
    return duracion_total


# ==============================================================================
# OPCIONES g), h) Y l) MEDICIÓN DE TIEMPOS, DOCUMENTACIÓN Y COMPARACIÓN FINAL
# ==============================================================================
def opcion_g_mostrar_tiempos(mostrar_banner=True):
    """g) Muestra el tablero consolidado de tiempos de la sesión."""
    if mostrar_banner:
        cartel("g) REGISTRO Y MEDICIÓN DE TIEMPOS", "Análisis Empírico de la Sesión (Unidad 2)", C.CYAN)

    def fmt_s(val):
        return f"{C.VERDE}{val:.6f} s{C.RESET}" if val is not None else f"{C.GRIS}Pendiente de ejecutar{C.RESET}"

    def fmt_us(val):
        return f"{C.VERDE}{val * 1e6:.2f} µs{C.RESET} {C.GRIS}({val:.8f} s){C.RESET}" if val is not None else f"{C.GRIS}Pendiente de ejecutar{C.RESET}"

    separador("1. Operaciones sobre Archivos", C.CYAN)
    print(f"    • a) Generación de 'Datos.txt'       : {fmt_s(registro_tiempos['generacion_archivo'])}")
    print(f"    • b) Búsqueda de Máximo y Mínimo     : {fmt_s(registro_tiempos['busqueda_max_min'])}")
    print(f"    • c) Análisis de Frecuencia (Top 10) : {fmt_s(registro_tiempos['analisis_frecuencia'])}")

    separador("2. Algoritmos de Ordenamiento", C.VERDE)
    print(f"    • d) Counting Sort   [O(n + k)]      : {fmt_s(registro_tiempos['counting_sort'])}")
    if registro_tiempos["selection_sort"] is not None:
        n_sel = registro_tiempos["selection_sort_n"]
        proy = registro_tiempos["selection_sort_proyectado_100M"]
        print(f"    • e) Selection Sort  [O(n²)] (n={n_sel:,}): {fmt_s(registro_tiempos['selection_sort'])}  {C.ROJO}(Proy. 100M: {proy:,.1f} s){C.RESET}")
    else:
        print(f"    • e) Selection Sort  [O(n²)]         : {C.GRIS}Pendiente de ejecutar{C.RESET}")
    print(f"    • k) Heap Sort       [O(n log n)]    : {fmt_s(registro_tiempos['heap_sort'])}")

    separador("3. Estructuras (Árbol AVL vs. Heap Binario)", C.AMARILLO)
    print(f"    • i) Árbol AVL - Construcción        : {fmt_s(registro_tiempos['avl_construccion'])}")
    print(f"    • i) Árbol AVL - Inserción O(log n)  : {fmt_us(registro_tiempos['avl_insercion'])}")
    print(f"    • i) Árbol AVL - Búsqueda O(log n)   : {fmt_us(registro_tiempos['avl_busqueda'])}")
    print(f"    • i) Árbol AVL - Eliminación O(log n): {fmt_us(registro_tiempos['avl_eliminacion'])}")
    print(f"    • j) Heap      - Construcción O(n)   : {fmt_s(registro_tiempos['heap_construccion'])}")
    print(f"    • j) Heap      - Inserción O(log n)  : {fmt_us(registro_tiempos['heap_insercion'])}")
    print(f"    • j) Heap      - Búsqueda O(n)       : {fmt_us(registro_tiempos['heap_busqueda'])}")
    print(f"    • j) Max-Heap  - Eliminar Máx O(logn): {fmt_us(registro_tiempos['heap_eliminacion_max'])}")
    print(f"    • j) Min-Heap  - Eliminar Mín O(logn): {fmt_us(registro_tiempos['heap_eliminacion_min'])}")


def opcion_h_documentacion():
    """h) Muestra en pantalla la documentación técnica integrada."""
    cartel("h) DOCUMENTACIÓN TÉCNICA Y DECISIONES DE DISEÑO", "Fundamentación teórica basada en Unidades 1 a 6", C.MAGENTA)
    print(f"{C.BLANCO}{__doc__}{C.RESET}")


def opcion_l_comparacion_estructuras_y_algoritmos():
    """
    l) Comparación de Estructuras (AVL vs Heap) y Algoritmos de Ordenamiento.
    """
    cartel("l) COMPARACIÓN DE ESTRUCTURAS Y ALGORITMOS", "Análisis Teórico, Empírico y Conclusiones para Grandes Volúmenes", C.MAGENTA)

    separador("PARTE 1: ÁRBOL AVL vs. HEAP BINARIO", C.CYAN)
    print(f"  {C.CYAN}┌────────────────────────┬────────────────────────────┬────────────────────────────┐{C.RESET}")
    print(f"  {C.CYAN}│{C.BOLD}{C.BLANCO} Operación / Criterio   {C.CYAN}│{C.AZUL} Árbol AVL (Equilibrado)    {C.CYAN}│{C.AMARILLO} Heap Binario (Montículo)   {C.CYAN}│{C.RESET}")
    print(f"  {C.CYAN}├────────────────────────┼────────────────────────────┼────────────────────────────┤{C.RESET}")
    filas_est = [
        ("Enfoque (Unidad 6)",     "Cambio de Representación",   "Cambio de Representación"),
        ("Representación física",  "Nodos enlazados (punteros)", "Arreglo contiguo (fórmulas)"),
        ("Construcción inicial",   "O(n log n)",                 "O(n) (con Build-Heap)"),
        ("Inserción",              "O(log n) + rotaciones",      "O(log n) (heapify up)"),
        ("Búsqueda arbitraria",    "O(log n) (búsqueda binaria)","O(n) (recorrido secuencial)"),
        ("Consultar Máx / Mín",    "O(log n)",                   "O(1) (acceso a raíz idx 0)"),
        ("Eliminación",            "O(log n) (cualquier clave)", "O(log n) (raíz máx o mín)"),
        ("Recorrido ordenado",     "O(n) mediante InOrden",      "O(n log n) extrayendo raíz"),
    ]
    for crit, v_avl, v_heap in filas_est:
        print(f"  {C.CYAN}│{C.RESET} {crit:<22} {C.CYAN}│{C.RESET} {v_avl:<26} {C.CYAN}│{C.RESET} {v_heap:<26} {C.CYAN}│{C.RESET}")
    print(f"  {C.CYAN}└────────────────────────┴────────────────────────────┴────────────────────────────┘{C.RESET}")

    separador("PARTE 2: ALGORITMOS DE ORDENAMIENTO", C.VERDE)
    print(f"  {C.VERDE}┌────────────────┬──────────────┬──────────────┬──────────────────┬────────────────────┐{C.RESET}")
    print(f"  {C.VERDE}│{C.BOLD}{C.BLANCO} Algoritmo      {C.VERDE}│{C.BLANCO} Mejor Caso   {C.VERDE}│{C.BLANCO} Peor Caso    {C.VERDE}│{C.BLANCO} Memoria Auxiliar {C.VERDE}│{C.BLANCO} Técnica / Enfoque  {C.VERDE}│{C.RESET}")
    print(f"  {C.VERDE}├────────────────┼──────────────┼──────────────┼──────────────────┼────────────────────┤{C.RESET}")
    print(f"  {C.VERDE}│{C.RESET} {C.VERDE}{C.BOLD}Counting Sort {C.RESET} {C.VERDE}│{C.RESET} O(n + k)     {C.VERDE}│{C.RESET} O(n + k)     {C.VERDE}│{C.RESET} O(k) / O(n + k)  {C.VERDE}│{C.RESET} No comparativo     {C.VERDE}│{C.RESET}")
    print(f"  {C.VERDE}│{C.RESET} {C.ROJO}{C.BOLD}Selection Sort{C.RESET} {C.VERDE}│{C.RESET} O(n²)        {C.VERDE}│{C.RESET} O(n²)        {C.VERDE}│{C.RESET} O(1) (In-place)  {C.VERDE}│{C.RESET} Fuerza Bruta       {C.VERDE}│{C.RESET}")
    print(f"  {C.VERDE}│{C.RESET} {C.CYAN}{C.BOLD}Heap Sort     {C.RESET} {C.VERDE}│{C.RESET} O(n log n)   {C.VERDE}│{C.RESET} O(n log n)   {C.VERDE}│{C.RESET} O(1) (In-place)  {C.VERDE}│{C.RESET} Transforma y Conq. {C.VERDE}│{C.RESET}")
    print(f"  {C.VERDE}└────────────────┴──────────────┴──────────────┴──────────────────┴────────────────────┘{C.RESET}")

    opcion_g_mostrar_tiempos(mostrar_banner=False)

    separador("CONCLUSIONES PARA GRANDES VOLÚMENES (100.000.000 DE DATOS)", C.AMARILLO)
    print(f"  {C.VERDE}{C.BOLD}1. COUNTING SORT O(n + k):{C.RESET} Más rápido para enteros acotados (k ≈ n).")
    print(f"     Al no realizar comparaciones supera el límite O(n log n), pero gasta O(k) RAM.")
    print(f"  {C.CYAN}{C.BOLD}2. HEAP SORT O(n log n):{C.RESET} El más equilibrado y escalable de uso general.")
    print(f"     Ordena In-Place con memoria constante O(1) y garantiza O(n log n) en el peor caso.")
    print(f"  {C.ROJO}{C.BOLD}3. SELECTION SORT O(n²):{C.RESET} Inviable para millones de datos (~5×10^15 comparaciones).")
    print(f"  {C.AMARILLO}{C.BOLD}4. ÁRBOL AVL vs. HEAP:{C.RESET} AVL gana en búsquedas arbitrarias O(log n) y orden InOrden;")
    print(f"     Heap gana en acceso O(1) al máximo/mínimo, construcción O(n) y ahorro de memoria.")


# ==============================================================================
# EJECUCIÓN AUTOMÁTICA INTEGRAL Y MENÚ INTERACTIVO PRINCIPAL
# ==============================================================================
# ==============================================================================
# OPCIÓN v) MODO VISUAL PASO A PASO EN CONSOLA (ÁRBOL AVL, HEAP Y HEAP SORT)
# ==============================================================================
def imprimir_arbol_avl_ascii(avl, nodo=None, prefijo="", es_izq=True, es_raiz=True, destacado=None):
    """Dibuja el Árbol AVL de forma gráfica en consola mostrando dato, altura y FB."""
    if es_raiz:
        nodo = avl.raiz
        if nodo is None:
            print(f"  {C.GRIS}(Árbol vacío){C.RESET}")
            return

    if nodo.derecho is not None:
        nuevo_pref = prefijo + ("    " if es_raiz else ("│   " if es_izq else "    "))
        imprimir_arbol_avl_ascii(avl, nodo.derecho, nuevo_pref, False, False, destacado)

    fb = avl.obtener_factor_balance(nodo)
    fb_str = f"+{fb}" if fb > 0 else f"{fb}"
    color_fb = C.ROJO if abs(fb) > 1 else C.VERDE
    color_nodo = C.AMARILLO if (destacado is not None and nodo.dato == destacado) else C.CYAN

    rama = "──► " if es_raiz else ("└── " if es_izq else "┌── ")
    print(f"  {C.GRIS}{prefijo}{rama}{C.RESET}{color_nodo}{C.BOLD}[{nodo.dato}]{C.RESET} {C.GRIS}(h={nodo.altura}, {color_fb}FB={fb_str}{C.GRIS}){C.RESET}")

    if nodo.izquierdo is not None:
        nuevo_pref = prefijo + ("    " if es_raiz else ("    " if es_izq else "│   "))
        imprimir_arbol_avl_ascii(avl, nodo.izquierdo, nuevo_pref, True, False, destacado)


def imprimir_heap_ascii(arr, n_activo=None, idx_swap=(), idx_activo=None):
    """Dibuja el Heap Binario como árbol jerárquico + su arreglo sincronizado debajo."""
    if not arr:
        print(f"  {C.GRIS}(Heap vacío){C.RESET}")
        return
    if n_activo is None:
        n_activo = len(arr)

    def _dibujar(i, prefijo, es_izq, es_raiz):
        if i >= len(arr):
            return
        der = 2 * i + 2
        izq = 2 * i + 1
        if der < len(arr):
            _dibujar(der, prefijo + ("    " if es_raiz else ("│   " if es_izq else "    ")), False, False)

        if i >= n_activo:
            col = C.VERDE
            tag = " (ORDENADO)"
        elif i in idx_swap:
            col = C.AMARILLO
            tag = " ◄ SWAP"
        elif idx_activo is not None and i == idx_activo:
            col = C.MAGENTA
            tag = " ◄ ACTIVO"
        else:
            col = C.CYAN
            tag = ""

        rama = "──► " if es_raiz else ("└── " if es_izq else "┌── ")
        print(f"  {C.GRIS}{prefijo}{rama}{C.RESET}{col}{C.BOLD}[{arr[i]}]{C.RESET} {C.GRIS}idx={i}{col}{tag}{C.RESET}")

        if izq < len(arr):
            _dibujar(izq, prefijo + ("    " if es_raiz else ("    " if es_izq else "│   ")), True, False)

    _dibujar(0, "", True, True)
    print()
    # Mostrar el arreglo debajo sincronizado
    celdas = []
    for idx, val in enumerate(arr):
        if idx >= n_activo:
            celdas.append(f"{C.VERDE}{C.BOLD}[{idx}:{val}]{C.RESET}")
        elif idx in idx_swap:
            celdas.append(f"{C.AMARILLO}{C.BOLD}[{idx}:{val}]{C.RESET}")
        elif idx_activo is not None and idx == idx_activo:
            celdas.append(f"{C.MAGENTA}{C.BOLD}[{idx}:{val}]{C.RESET}")
        else:
            celdas.append(f"{C.CYAN}[{idx}:{val}]{C.RESET}")
    print("  Arreglo: " + " ".join(celdas))


def visual_avl_consola():
    """Demostración paso a paso en consola de inserciones y rotaciones en Árbol AVL."""
    limpiar_pantalla()
    cartel("VISUALIZADOR EN CONSOLA: ÁRBOL AVL PASO A PASO", "Muestra altura (h), Factor de Balance (FB) y cada rotación", C.AZUL)
    print(f"    {C.AMARILLO}[1]{C.RESET} Rotación Simple Izquierda       {C.GRIS}[10, 20, 30]{C.RESET}")
    print(f"    {C.AMARILLO}[2]{C.RESET} Rotación Doble Izq+Der (Diap.13){C.GRIS}[20, 10, 15]{C.RESET}")
    print(f"    {C.AMARILLO}[3]{C.RESET} Ejercicio Profe (Diap. 13)      {C.GRIS}[60, 40, 70, 30, 45, 50]{C.RESET}")
    print(f"    {C.AMARILLO}[4]{C.RESET} Ingresar mis propios números uno por uno")
    op = input(f"\n  {C.AMARILLO}>> Elija opción [1-4, Enter=3]: {C.RESET}").strip()

    avl = ArbolAVL()
    if op == "4":
        while True:
            limpiar_pantalla()
            cartel("ÁRBOL AVL INTERACTIVO EN VIVO", "Arriba = Subárbol Derecho  |  Abajo = Subárbol Izquierdo", C.AZUL)
            imprimir_arbol_avl_ascii(avl)
            print(f"\n  {C.GRIS}InOrden actual:{C.RESET} {C.VERDE}{avl.recorrido_inorden_muestra(50)}{C.RESET}")
            print(f"  {C.GRIS}Altura: {avl.obtener_altura(avl.raiz)} | Nodos: {avl.cantidad_nodos_unicos} | Rotaciones: {avl.rotaciones_realizadas}{C.RESET}")
            val_txt = input(f"\n  {C.AMARILLO}>> Ingrese un número para INSERTAR (o 'fin' para salir): {C.RESET}").strip().lower()
            if val_txt in ("fin", "s", "q", ""):
                break
            try:
                v = int(val_txt)
                rot_antes = avl.rotaciones_realizadas
                avl.insertar(v)
                if avl.rotaciones_realizadas > rot_antes:
                    msg_alerta(f"¡Se disparó una rotación de rebalanceo al insertar {v}!")
                    time.sleep(0.8)
            except ValueError:
                msg_error("Ingrese un número entero válido.")
                time.sleep(0.8)
        return

    secuencias = {
        "1": [10, 20, 30],
        "2": [20, 10, 15],
        "3": [60, 40, 70, 30, 45, 50],
    }
    datos = secuencias.get(op, secuencias["3"])

    for paso, val in enumerate(datos, start=1):
        limpiar_pantalla()
        cartel(f"ÁRBOL AVL — PASO {paso}/{len(datos)}: INSERTANDO [{val}]", "Arriba = Rama Derecha  |  Abajo = Rama Izquierda", C.AZUL)
        rot_antes = avl.rotaciones_realizadas
        avl.insertar(val)
        rot_delta = avl.rotaciones_realizadas - rot_antes
        if rot_delta > 0:
            tipo = "ROTACIÓN DOBLE" if rot_delta >= 2 else "ROTACIÓN SIMPLE"
            msg_alerta(f"Al insertar {val} el árbol se desequilibró (|FB|=2) y aplicó: {tipo} ({rot_delta} giro/s).")
        else:
            msg_ok(f"Se insertó {val}. Todos los nodos mantienen FB en {{-1, 0, +1}}.")
        print()
        imprimir_arbol_avl_ascii(avl, destacado=val)
        print(f"\n  {C.GRIS}Recorrido InOrden:{C.RESET} {C.VERDE}{avl.recorrido_inorden_muestra(50)}{C.RESET}")
        if paso < len(datos):
            pausar(f"Presione ENTER para insertar el siguiente número ({datos[paso]})...")


def visual_heap_y_heapsort_consola():
    """Demostración paso a paso en consola de Heap Sort (Fase 1 + Fase 2) con árbol + arreglo."""
    limpiar_pantalla()
    cartel("VISUALIZADOR EN CONSOLA: HEAP Y HEAP SORT PASO A PASO", "Ejemplo de las Diapositivas 24-29: [2, 5, 4, 8, 9, 10, 11]", C.AMARILLO)
    arr = [2, 5, 4, 8, 9, 10, 11]
    n = len(arr)

    def mostrar_estado(fase, desc, n_act, swap_idx=(), act_idx=None):
        limpiar_pantalla()
        cartel(fase, desc, C.AMARILLO if "FASE 1" in fase else C.VERDE)
        imprimir_heap_ascii(arr, n_activo=n_act, idx_swap=swap_idx, idx_activo=act_idx)
        pausar("Presione ENTER para ver el siguiente paso...")

    def heapify_vis(size, i, fase_lbl):
        while True:
            mayor = i
            izq = 2 * i + 1
            der = 2 * i + 2
            if izq < size and arr[izq] > arr[mayor]:
                mayor = izq
            if der < size and arr[der] > arr[mayor]:
                mayor = der
            if mayor != i:
                mostrar_estado(fase_lbl, f"Heapify: padre [{i}]={arr[i]} intercambia con hijo mayor [{mayor}]={arr[mayor]}", size, swap_idx=(i, mayor))
                arr[i], arr[mayor] = arr[mayor], arr[i]
                i = mayor
            else:
                break

    mostrar_estado("FASE 1: CONSTRUIR MAX-HEAP O(n)", "Arreglo inicial desordenado antes de aplicar Heapify", n)
    for i in range((n // 2) - 1, -1, -1):
        heapify_vis(n, i, "FASE 1: CONSTRUIR MAX-HEAP O(n)")

    mostrar_estado("FASE 1 COMPLETADA: MAX-HEAP LISTO", f"El máximo ({arr[0]}) ya está en la raíz [0]. Comienza Fase 2.", n, act_idx=0)

    for fin in range(n - 1, 0, -1):
        mostrar_estado("FASE 2: EXTRACCIÓN Y ORDENAMIENTO O(n log n)", f"SWAP raíz máxima [0]={arr[0]} con último activo [{fin}]={arr[fin]}", fin + 1, swap_idx=(0, fin))
        arr[0], arr[fin] = arr[fin], arr[0]
        mostrar_estado("FASE 2: EXTRACCIÓN Y ORDENAMIENTO O(n log n)", f"El {arr[fin]} quedó ORDENADO (verde) en [{fin}]. Ahora Heapify en raíz [0].", fin, act_idx=0)
        heapify_vis(fin, 0, "FASE 2: EXTRACCIÓN Y ORDENAMIENTO O(n log n)")

    limpiar_pantalla()
    cartel("HEAP SORT FINALIZADO", f"Arreglo completamente ordenado: {arr}", C.VERDE)
    imprimir_heap_ascii(arr, n_activo=0)


def opcion_v_modo_visual():
    """Submenú visual interactivo (en consola y en navegador web gráfico)."""
    cartel("v) MODO VISUAL PASO A PASO (AVL, HEAP Y HEAP SORT)", "Observá cómo cambian los árboles al agregar datos y rotar", C.MAGENTA)
    print(f"    {C.VERDE}{C.BOLD}[1]{C.RESET} {C.VERDE}Abrir Visualizador Gráfico Interactivo en el Navegador Web{C.RESET} {C.GRIS}(visualizador_avl_heap.html){C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}[2]{C.RESET} Visualizador paso a paso en Consola: {C.AZUL}Árbol AVL (FB y Rotaciones){C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}[3]{C.RESET} Visualizador paso a paso en Consola: {C.AMARILLO}Heap y Heap Sort (Árbol + Arreglo){C.RESET}")
    print()
    op = input(f"  {C.AMARILLO}>> Seleccione una opción [1-3, Enter=1]: {C.RESET}").strip()

    if op == "2":
        visual_avl_consola()
    elif op == "3":
        visual_heap_y_heapsort_consola()
    else:
        ruta_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizador_avl_heap.html")
        if os.path.exists(ruta_html):
            msg_ok(f"Abriendo visualizador gráfico interactivo: {ruta_html}")
            webbrowser.open("file:///" + ruta_html.replace("\\", "/"))
        else:
            msg_error("No se encontró 'visualizador_avl_heap.html' en esta carpeta.")


def ejecutar_flujo_completo_demostracion(n_datos=100_000, n_selection=10_000, n_avl=50_000, interactivo=False):
    """Ejecuta secuencialmente todas las opciones con pausas limpias opcionales."""
    pasos = [
        lambda: opcion_a_generar_datos(cantidad_forzada=n_datos, rango_max_forzado=n_datos),
        lambda: opcion_b_buscar_max_min(),
        lambda: opcion_c_analisis_frecuencia(),
        lambda: opcion_d_counting_sort(),
        lambda: opcion_e_selection_sort(limite_muestra=n_selection),
        lambda: opcion_k_heap_sort(),
        lambda: opcion_f_verificar_ordenamiento(),
        lambda: opcion_i_arbol_avl(limite_carga=n_avl),
        lambda: opcion_j_implementacion_heap(limite_carga=n_datos),
        lambda: opcion_l_comparacion_estructuras_y_algoritmos(),
    ]
    for idx, paso in enumerate(pasos, start=1):
        if interactivo:
            limpiar_pantalla()
        paso()
        if interactivo and idx < len(pasos):
            pausar(f"Paso {idx}/{len(pasos)} completado. Presione ENTER para continuar al siguiente punto...")


def mostrar_menu():
    limpiar_pantalla()
    cartel(
        "UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)",
        "Análisis y Diseño de Algoritmos  |  TP N° 3: Transforma y Conquista (2026)",
        C.CYAN,
    )

    estado_archivo = (
        f"{C.VERDE}Detectado ({os.path.getsize(ARCHIVO_DATOS) / (1024*1024):.2f} MB){C.RESET}"
        if os.path.exists(ARCHIVO_DATOS)
        else f"{C.AMARILLO}Aún no generado (ejecute opción a){C.RESET}"
    )
    print(f"  {C.GRIS}Estado de '{ARCHIVO_DATOS}':{C.RESET} {estado_archivo}")

    separador("1. GESTIÓN DE ARCHIVO Y ANÁLISIS INICIAL", C.CYAN)
    print(f"    {C.AMARILLO}{C.BOLD}a){C.RESET} Generación del archivo de datos ({C.CYAN}'Datos.txt'{C.RESET})")
    print(f"    {C.AMARILLO}{C.BOLD}b){C.RESET} Búsqueda del máximo y mínimo  {C.GRIS}[O(n) / Memoria O(1)]{C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}c){C.RESET} Análisis de frecuencia        {C.GRIS}[Top 10 más repetidos]{C.RESET}")

    separador("2. ALGORITMOS DE ORDENAMIENTO Y VERIFICACIÓN", C.VERDE)
    print(f"    {C.AMARILLO}{C.BOLD}d){C.RESET} Ordenamiento mediante {C.VERDE}Counting Sort{C.RESET}  {C.GRIS}[O(n + k) -> Datos_CountingSort.txt]{C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}e){C.RESET} Ordenamiento mediante {C.ROJO}Selection Sort{C.RESET} {C.GRIS}[O(n²)    -> Datos_SelectionSort.txt]{C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}k){C.RESET} Ordenamiento mediante {C.CYAN}Heap Sort{C.RESET}      {C.GRIS}[O(n log n)-> Datos_HeapSort.txt]{C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}f){C.RESET} Verificación del ordenamiento ascendente {C.GRIS}[Comprueba d, e y k]{C.RESET}")

    separador("3. ESTRUCTURAS DE 'TRANSFORMA Y CONQUISTA' (UNIDAD 6)", C.AZUL)
    print(f"    {C.AMARILLO}{C.BOLD}i){C.RESET} Implementación de {C.AZUL}Árbol AVL{C.RESET}            {C.GRIS}[Inserción, Búsqueda, Elim., InOrden]{C.RESET}")
    print(f"    {C.AMARILLO}{C.BOLD}j){C.RESET} Implementación de {C.AMARILLO}Heap Binario{C.RESET}         {C.GRIS}[Max-Heap y Min-Heap sobre arreglo]{C.RESET}")
    print(f"    {C.MAGENTA}{C.BOLD}v){C.RESET} {C.MAGENTA}{C.BOLD}MODO VISUAL PASO A PASO{C.RESET}               {C.GRIS}[Gráfico Web + Árbol ASCII en vivo]{C.RESET}")

    separador("4. TIEMPOS, DOCUMENTACIÓN Y COMPARACIÓN FINAL", C.MAGENTA)
    print(f"    {C.AMARILLO}{C.BOLD}g){C.RESET} Medición y resumen de tiempos de ejecución")
    print(f"    {C.AMARILLO}{C.BOLD}h){C.RESET} Documentación técnica y decisiones de diseño")
    print(f"    {C.AMARILLO}{C.BOLD}l){C.RESET} Comparación final: Estructuras (AVL vs Heap) y Algoritmos")
    print(f"    {C.VERDE}{C.BOLD}m){C.RESET} {C.VERDE}Ejecutar demostración completa paso a paso (a -> l){C.RESET}")
    print(f"    {C.ROJO}{C.BOLD}s){C.RESET} Salir del programa")
    separador("", C.GRIS)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--auto-demo":
        n_datos = int(sys.argv[2]) if len(sys.argv) > 2 else 100_000
        n_sel = int(sys.argv[3]) if len(sys.argv) > 3 else 10_000
        n_avl = int(sys.argv[4]) if len(sys.argv) > 4 else 50_000
        ejecutar_flujo_completo_demostracion(n_datos=n_datos, n_selection=n_sel, n_avl=n_avl, interactivo=False)
        return

    while True:
        mostrar_menu()
        opcion = input(f"\n  {C.AMARILLO}{C.BOLD}>> Seleccione una opción [a-m / s para salir]: {C.RESET}").strip().lower()

        if opcion in ("s", "salir", "0", "q"):
            limpiar_pantalla()
            cartel("PROGRAMA FINALIZADO", "Gracias por utilizar el sistema del TP N° 3 - UNViMe 2026", C.VERDE)
            break

        # Limpiar consola al presionar una opción para que cada punto se vea solo y limpio
        limpiar_pantalla()

        if opcion == "a":
            opcion_a_generar_datos()
        elif opcion == "b":
            opcion_b_buscar_max_min()
        elif opcion == "c":
            opcion_c_analisis_frecuencia()
        elif opcion == "d":
            opcion_d_counting_sort()
        elif opcion == "e":
            opcion_e_selection_sort()
        elif opcion == "f":
            opcion_f_verificar_ordenamiento()
        elif opcion == "g":
            opcion_g_mostrar_tiempos()
        elif opcion == "h":
            opcion_h_documentacion()
        elif opcion == "i":
            opcion_i_arbol_avl()
        elif opcion == "j":
            opcion_j_implementacion_heap()
        elif opcion == "k":
            opcion_k_heap_sort()
        elif opcion == "l":
            opcion_l_comparacion_estructuras_y_algoritmos()
        elif opcion == "m":
            ejecutar_flujo_completo_demostracion(interactivo=True)
        elif opcion == "v":
            opcion_v_modo_visual()
        else:
            msg_error(f"Opción '{opcion}' no válida. Seleccione una letra entre 'a' y 'm', 'v' para modo visual, o 's' para salir.")

        pausar()


if __name__ == "__main__":
    main()
