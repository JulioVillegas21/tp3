/*
 * ============================================================================
 * UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
 * Asignatura : Análisis y Diseño de Algoritmos (2026)
 * Trabajo Práctico N° 3 : "Transforma y Conquista" (Transform and Conquer)
 * Archivo    : tp3_transforma_y_conquista.c
 * Lenguaje   : C Estándar (C99 / C11)
 * Compilación: gcc -O3 tp3_transforma_y_conquista.c -o tp3_c -lm
 * ============================================================================
 *
 * DOCUMENTACIÓN Y DECISIONES DE DISEÑO (Requisito h):
 * ---------------------------------------------------
 * 1. Generación y Manejo de Grandes Volúmenes (100.000.000 de enteros):
 *    - Se utiliza un generador pseudoaleatorio de 64 bits (Xorshift64* / LCG
 *      combinado) ya que RAND_MAX estándar en Windows es apenas 32.767 y no
 *      cubriría el rango [0, 100.000.000] de forma uniforme.
 *    - Se emplea buffering de flujo (setvbuf de 4 MB) para optimizar la
 *      lectura y escritura en disco de "Datos.txt".
 *
 * 2. Algoritmos de Ordenamiento:
 *    - Counting Sort O(n + k): Algoritmo no comparativo (Unidad 3). Utiliza un
 *      arreglo dinámico de frecuencias de tamaño k + 1. Es el método más
 *      rápido para ordenar 100.000.000 de enteros en [0, 100.000.000].
 *    - Selection Sort O(n^2): Algoritmo de Fuerza Bruta (Unidad 3). Realiza
 *      n(n - 1) / 2 comparaciones (Serie Aritmética, Unidad 2). Para grandes
 *      volúmenes permite ejecutar sobre una muestra representativa N y
 *      proyectar el tiempo cuadrático hacia N = 100.000.000.
 *    - Heap Sort O(n log n): Algoritmo de Transforma y Conquista por Cambio de
 *      Representación (Unidad 6). Fase 1 construye el Max-Heap en O(n) y
 *      Fase 2 extrae sucesivamente la raíz en O(n log n) in-place (memoria O(1)).
 *
 * 3. Estructuras de Datos (Transforma y Conquista - Cambio de Representación):
 *    - Árbol AVL (Adelson-Velskii y Landis, 1962 - Unidad 6):
 *      Definido mediante punteros (`struct NodoArbolAVL`) tal como se presenta
 *      en la Unidad 6 (diapositiva 18). Mantiene el Factor de Balance:
 *        FB = Altura(Izquierdo) - Altura(Derecho) en {-1, 0, +1}
 *      mediante Rotaciones Simples (Izquierda/Derecha) y Dobles (LR y RL).
 *    - Heap Binario (Montículo Máximo y Mínimo - Unidad 6):
 *      Árbol binario completo representado en un arreglo contiguo sin punteros:
 *        Padre(i) = (i - 1) / 2 | Izq(i) = 2*i + 1 | Der(i) = 2*i + 2.
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define ARCHIVO_DATOS     "Datos.txt"
#define ARCHIVO_COUNTING  "Datos_CountingSort.txt"
#define ARCHIVO_SELECTION "Datos_SelectionSort.txt"
#define ARCHIVO_HEAPSORT  "Datos_HeapSort.txt"

#define N_CONSIGNA        100000000LL
#define RANGO_MAX_DEF     100000000

/* Colores ANSI y utilidades visuales de consola */
#define C_RESET    "\033[0m"
#define C_BOLD     "\033[1m"
#define C_CYAN     "\033[96m"
#define C_AZUL     "\033[94m"
#define C_VERDE    "\033[92m"
#define C_AMARILLO "\033[93m"
#define C_MAGENTA  "\033[95m"
#define C_ROJO     "\033[91m"
#define C_BLANCO   "\033[97m"
#define C_GRIS     "\033[90m"

static void limpiar_pantalla(void) {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}

static void pausar_pantalla(void) {
    printf("\n  %s------------------------------------------------------------------------------%s\n", C_GRIS, C_RESET);
    printf("  %s%s>> Presione ENTER para volver al menu principal...%s", C_AMARILLO, C_BOLD, C_RESET);
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF) {}
    getchar();
}

static void cartel(const char* titulo, const char* subtitulo, const char* color) {
    printf("\n%s%s  +============================================================================+\n", color, C_BOLD);
    printf("  |  %-74s|\n", titulo);
    if (subtitulo && subtitulo[0] != '\0') {
        printf("  |%s  %-74s%s%s|\n", C_BLANCO, subtitulo, color, C_BOLD);
    }
    printf("  +============================================================================+%s\n\n", C_RESET);
}

static void separador(const char* texto, const char* color) {
    if (!texto || texto[0] == '\0') {
        printf("  %s------------------------------------------------------------------------------%s\n", color, C_RESET);
    } else {
        printf("\n  %s--- %s%s%s %s----------------------------------------------------%s\n",
               color, C_BOLD, C_BLANCO, texto, color, C_RESET);
    }
}

/* Registro global de tiempos empíricos (Requisito g) */
typedef struct {
    double t_generacion;
    double t_max_min;
    double t_frecuencia;
    double t_counting_sort;
    double t_selection_sort;
    long long n_selection_sort;
    double t_heap_sort;
    double t_avl_construccion;
    double t_avl_insercion_us;
    double t_avl_busqueda_us;
    double t_avl_eliminacion_us;
    double t_heap_construccion;
    double t_heap_insercion_us;
    double t_heap_busqueda_us;
    double t_heap_elim_max_us;
    double t_heap_elim_min_us;
} RegistroTiempos;

static RegistroTiempos g_tiempos = {0};

/* ============================================================================
 * GENERADOR ALEATORIO UNIFORME EN [0, RANGO_MAX] (Soporta hasta > 100.000.000)
 * ============================================================================ */
static uint64_t estado_rng = 20260611ULL;

static uint32_t aleatorio_rango(uint32_t max_inclusive) {
    estado_rng ^= estado_rng >> 12;
    estado_rng ^= estado_rng << 25;
    estado_rng ^= estado_rng >> 27;
    uint64_t r = estado_rng * 2685821657736338717ULL;
    return (uint32_t)(r % (uint64_t)(max_inclusive + 1));
}

/* ============================================================================
 * CARGA Y ESCRITURA DE ARREGLOS EN ARCHIVO
 * ============================================================================ */
static int* cargar_datos(const char* nombre_archivo, long long limite, long long* n_leidos) {
    FILE* f = fopen(nombre_archivo, "r");
    if (!f) {
        printf("  [!] Error: No se pudo abrir '%s'. Ejecute primero la opcion a).\n", nombre_archivo);
        *n_leidos = 0;
        return NULL;
    }
    setvbuf(f, NULL, _IOFBF, 4 * 1024 * 1024);

    long long capacidad = (limite > 0) ? limite : 1000000;
    int* arr = (int*)malloc((size_t)capacidad * sizeof(int));
    if (!arr) {
        printf("  [!] Error de memoria al reservar arreglo.\n");
        fclose(f);
        *n_leidos = 0;
        return NULL;
    }

    long long cuenta = 0;
    int valor;
    while (fscanf(f, "%d", &valor) == 1) {
        if (cuenta >= capacidad) {
            capacidad *= 2;
            int* temp = (int*)realloc(arr, (size_t)capacidad * sizeof(int));
            if (!temp) {
                free(arr);
                fclose(f);
                *n_leidos = 0;
                return NULL;
            }
            arr = temp;
        }
        arr[cuenta++] = valor;
        if (limite > 0 && cuenta >= limite) break;
    }

    fclose(f);
    *n_leidos = cuenta;
    return arr;
}

static int guardar_datos(const char* nombre_archivo, const int* arr, long long n) {
    FILE* f = fopen(nombre_archivo, "w");
    if (!f) return 0;
    setvbuf(f, NULL, _IOFBF, 4 * 1024 * 1024);
    for (long long i = 0; i < n; i++) {
        fprintf(f, "%d\n", arr[i]);
    }
    fclose(f);
    return 1;
}

/* ============================================================================
 * a) GENERACIÓN DEL ARCHIVO DE DATOS ("Datos.txt")
 * ============================================================================ */
static void opcion_a_generar_datos(long long n_forzado) {
    printf("\n==============================================================================\n");
    printf("  a) GENERACION DEL ARCHIVO DE DATOS ('Datos.txt')\n");
    printf("==============================================================================\n");

    long long n = n_forzado;
    if (n <= 0) {
        printf("  Opciones de volumen de datos:\n");
        printf("    1) 100.000.000 de numeros (Volumen consigna completa)\n");
        printf("    2)   1.000.000 de numeros (Volumen intermedio agil)\n");
        printf("    3)     100.000 numeros    (Volumen rapido de prueba)\n");
        printf("  Seleccione [1-3, por defecto 2]: ");
        int op = 2;
        if (scanf("%d", &op) != 1) op = 2;
        if (op == 1) n = 100000000LL;
        else if (op == 3) n = 100000LL;
        else n = 1000000LL;
    }

    uint32_t rango_max = (n == 100000000LL) ? RANGO_MAX_DEF : (uint32_t)n;
    printf("  -> Generando '%s' con %lld numeros en [0, %u]...\n", ARCHIVO_DATOS, n, rango_max);

    clock_t t0 = clock();
    FILE* f = fopen(ARCHIVO_DATOS, "w");
    if (!f) {
        printf("  [!] Error al crear '%s'.\n", ARCHIVO_DATOS);
        return;
    }
    setvbuf(f, NULL, _IOFBF, 4 * 1024 * 1024);

    for (long long i = 0; i < n; i++) {
        fprintf(f, "%u\n", aleatorio_rango(rango_max));
    }
    fclose(f);

    double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_generacion = dt;
    printf("  [OK] Archivo '%s' generado en %.4f segundos.\n", ARCHIVO_DATOS, dt);
}

/* ============================================================================
 * b) BÚSQUEDA DEL MÁXIMO Y MÍNIMO
 * ============================================================================ */
static void opcion_b_max_min(void) {
    printf("\n==============================================================================\n");
    printf("  b) BUSQUEDA DEL MAXIMO Y MINIMO EN 'Datos.txt'\n");
    printf("==============================================================================\n");

    FILE* f = fopen(ARCHIVO_DATOS, "r");
    if (!f) {
        printf("  [!] No existe '%s'. Ejecute primero la opcion a).\n", ARCHIVO_DATOS);
        return;
    }
    setvbuf(f, NULL, _IOFBF, 4 * 1024 * 1024);

    clock_t t0 = clock();
    int valor, minimo = 0, maximo = 0;
    long long n = 0;

    while (fscanf(f, "%d", &valor) == 1) {
        if (n == 0) {
            minimo = maximo = valor;
        } else {
            if (valor < minimo) minimo = valor;
            if (valor > maximo) maximo = valor;
        }
        n++;
    }
    fclose(f);

    double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_max_min = dt;

    printf("  Elementos leidos (n)  : %lld\n", n);
    printf("  Numero MENOR (Minimo) : %d\n", minimo);
    printf("  Numero MAYOR (Maximo) : %d\n", maximo);
    printf("  Complejidad           : Temporal O(n) | Espacial O(1)\n");
    printf("  Tiempo de ejecucion   : %.4f segundos\n", dt);
}

/* ============================================================================
 * c) ANÁLISIS DE FRECUENCIA (TOP 10 NÚMEROS QUE MÁS SE REPITEN)
 * ============================================================================ */
static void opcion_c_frecuencia(void) {
    printf("\n==============================================================================\n");
    printf("  c) ANALISIS DE FRECUENCIA (TOP 10 NUMEROS MAS REPETIDOS)\n");
    printf("==============================================================================\n");

    long long n = 0;
    clock_t t0 = clock();
    int* datos = cargar_datos(ARCHIVO_DATOS, 0, &n);
    if (!datos || n == 0) return;

    int max_val = 0;
    for (long long i = 0; i < n; i++) {
        if (datos[i] > max_val) max_val = datos[i];
    }

    int* frec = (int*)calloc((size_t)(max_val + 1), sizeof(int));
    if (!frec) {
        free(datos);
        return;
    }
    for (long long i = 0; i < n; i++) {
        frec[datos[i]]++;
    }

    int top_num[10] = {0};
    int top_cnt[10] = {0};

    for (int v = 0; v <= max_val; v++) {
        int c = frec[v];
        if (c > top_cnt[9]) {
            int pos = 9;
            while (pos > 0 && c > top_cnt[pos - 1]) {
                top_cnt[pos] = top_cnt[pos - 1];
                top_num[pos] = top_num[pos - 1];
                pos--;
            }
            top_cnt[pos] = c;
            top_num[pos] = v;
        }
    }

    double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_frecuencia = dt;

    printf("  PUESTO |        NUMERO |  REPETICIONES\n");
    printf("  --------------------------------------\n");
    for (int i = 0; i < 10; i++) {
        printf("  #%d     | %13d | %13d\n", i + 1, top_num[i], top_cnt[i]);
    }
    printf("  --------------------------------------\n");
    printf("  Tiempo de ejecucion: %.4f segundos\n", dt);

    free(frec);
    free(datos);
}

/* ============================================================================
 * d) ORDENAMIENTO MEDIANTE COUNTING SORT - O(n + k)
 * ============================================================================ */
static void opcion_d_counting_sort(void) {
    printf("\n==============================================================================\n");
    printf("  d) ORDENAMIENTO MEDIANTE COUNTING SORT -> 'Datos_CountingSort.txt'\n");
    printf("==============================================================================\n");

    long long n = 0;
    int* datos = cargar_datos(ARCHIVO_DATOS, 0, &n);
    if (!datos || n == 0) return;

    clock_t t0 = clock();
    int k = 0;
    for (long long i = 0; i < n; i++) {
        if (datos[i] > k) k = datos[i];
    }

    int* conteo = (int*)calloc((size_t)(k + 1), sizeof(int));
    if (!conteo) {
        free(datos);
        return;
    }

    /* Paso 1: Contar apariciones de cada clave */
    for (long long i = 0; i < n; i++) {
        conteo[datos[i]]++;
    }

    /* Paso 2: Reconstruir el arreglo ordenado sin comparaciones entre datos */
    long long idx = 0;
    for (int valor = 0; valor <= k; valor++) {
        int c = conteo[valor];
        while (c-- > 0) {
            datos[idx++] = valor;
        }
    }

    double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_counting_sort = dt;

    guardar_datos(ARCHIVO_COUNTING, datos, n);
    printf("  [OK] Counting Sort completado sobre n = %lld (k = %d).\n", n, k);
    printf("       Complejidad        : O(n + k) en Mejor y Peor Caso\n");
    printf("       Tiempo de ejecucion: %.6f segundos\n", dt);

    free(conteo);
    free(datos);
}

/* ============================================================================
 * e) ORDENAMIENTO MEDIANTE SELECTION SORT - O(n^2)
 * ============================================================================ */
static void opcion_e_selection_sort(long long limite_muestra) {
    printf("\n==============================================================================\n");
    printf("  e) ORDENAMIENTO MEDIANTE SELECTION SORT -> 'Datos_SelectionSort.txt'\n");
    printf("==============================================================================\n");

    long long n = 0;
    long long lim = (limite_muestra > 0) ? limite_muestra : 20000;
    int* datos = cargar_datos(ARCHIVO_DATOS, lim, &n);
    if (!datos || n == 0) return;

    clock_t t0 = clock();
    for (long long i = 0; i < n - 1; i++) {
        long long min_idx = i;
        for (long long j = i + 1; j < n; j++) {
            if (datos[j] < datos[min_idx]) {
                min_idx = j;
            }
        }
        if (min_idx != i) {
            int temp = datos[i];
            datos[i] = datos[min_idx];
            datos[min_idx] = temp;
        }
    }
    double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_selection_sort = dt;
    g_tiempos.n_selection_sort = n;

    guardar_datos(ARCHIVO_SELECTION, datos, n);
    double escala = (double)N_CONSIGNA / (double)n;
    double proyectado = dt * escala * escala;

    printf("  [OK] Selection Sort completado sobre muestra n = %lld.\n", n);
    printf("       Comparaciones realizadas : %lld  [n(n-1)/2 - Serie Aritmetica]\n", n * (n - 1) / 2);
    printf("       Tiempo medido (n=%lld)  : %.6f segundos\n", n, dt);
    printf("       Proyeccion n=100.000.000 : %.1f segundos (~%.1f dias)\n", proyectado, proyectado / 86400.0);

    free(datos);
}

/* ============================================================================
 * f) VERIFICACIÓN DEL ORDENAMIENTO ASCENDENTE - O(n)
 * ============================================================================ */
static int verificar_archivo(const char* ruta, long long* total_elem) {
    FILE* f = fopen(ruta, "r");
    if (!f) return -1;
    setvbuf(f, NULL, _IOFBF, 4 * 1024 * 1024);

    int ant = 0, act = 0;
    long long cnt = 0;
    int ordenado = 1;

    while (fscanf(f, "%d", &act) == 1) {
        if (cnt > 0 && act < ant) {
            ordenado = 0;
            break;
        }
        ant = act;
        cnt++;
    }
    fclose(f);
    *total_elem = cnt;
    return ordenado;
}

static void opcion_f_verificar(void) {
    printf("\n==============================================================================\n");
    printf("  f) VERIFICACION DEL ORDENAMIENTO ASCENDENTE\n");
    printf("==============================================================================\n");

    const char* archivos[3] = {ARCHIVO_COUNTING, ARCHIVO_SELECTION, ARCHIVO_HEAPSORT};
    const char* nombres[3]  = {"Counting Sort", "Selection Sort", "Heap Sort"};

    for (int i = 0; i < 3; i++) {
        long long cnt = 0;
        int res = verificar_archivo(archivos[i], &cnt);
        if (res == 1) {
            printf("  * %-15s (%s): CORRECTO - %lld elementos en orden ascendente.\n",
                   nombres[i], archivos[i], cnt);
        } else if (res == 0) {
            printf("  * %-15s (%s): ERROR - Desorden detectado.\n", nombres[i], archivos[i]);
        } else {
            printf("  * %-15s (%s): Archivo aun no generado.\n", nombres[i], archivos[i]);
        }
    }
}

/* ============================================================================
 * i) IMPLEMENTACIÓN DE ÁRBOL AVL (Unidad 6, diapositivas 9-18)
 * ============================================================================ */
struct NodoArbolAVL {
    int dato;
    int frecuencia;
    int altura;
    struct NodoArbolAVL* izquierdo;
    struct NodoArbolAVL* derecho;
};

static int altura_avl(struct NodoArbolAVL* n) {
    return n ? n->altura : 0;
}

static int max_int(int a, int b) {
    return (a > b) ? a : b;
}

/* Factor de Balance FB = Altura(Subárbol Izquierdo) - Altura(Subárbol Derecho) */
static int factor_balance(struct NodoArbolAVL* n) {
    return n ? (altura_avl(n->izquierdo) - altura_avl(n->derecho)) : 0;
}

static struct NodoArbolAVL* crear_nodo_avl(int dato) {
    struct NodoArbolAVL* nodo = (struct NodoArbolAVL*)malloc(sizeof(struct NodoArbolAVL));
    nodo->dato = dato;
    nodo->frecuencia = 1;
    nodo->altura = 1;
    nodo->izquierdo = NULL;
    nodo->derecho = NULL;
    return nodo;
}

/* Rotación Simple Derecha (RSD) */
static struct NodoArbolAVL* rotacion_derecha(struct NodoArbolAVL* y) {
    struct NodoArbolAVL* x = y->izquierdo;
    struct NodoArbolAVL* T2 = x->derecho;

    x->derecho = y;
    y->izquierdo = T2;

    y->altura = 1 + max_int(altura_avl(y->izquierdo), altura_avl(y->derecho));
    x->altura = 1 + max_int(altura_avl(x->izquierdo), altura_avl(x->derecho));
    return x;
}

/* Rotación Simple Izquierda (RSI - Unidad 6, diapositiva 12) */
static struct NodoArbolAVL* rotacion_izquierda(struct NodoArbolAVL* x) {
    struct NodoArbolAVL* y = x->derecho;
    struct NodoArbolAVL* T2 = y->izquierdo;

    y->izquierdo = x;
    x->derecho = T2;

    x->altura = 1 + max_int(altura_avl(x->izquierdo), altura_avl(x->derecho));
    y->altura = 1 + max_int(altura_avl(y->izquierdo), altura_avl(y->derecho));
    return y;
}

static struct NodoArbolAVL* balancear_nodo_avl(struct NodoArbolAVL* nodo) {
    if (!nodo) return NULL;
    nodo->altura = 1 + max_int(altura_avl(nodo->izquierdo), altura_avl(nodo->derecho));
    int fb = factor_balance(nodo);

    /* Desequilibrio Izquierdo (FB > 1) */
    if (fb > 1) {
        if (factor_balance(nodo->izquierdo) < 0) {
            /* Rotación Doble Izquierda-Derecha */
            nodo->izquierdo = rotacion_izquierda(nodo->izquierdo);
        }
        return rotacion_derecha(nodo);
    }
    /* Desequilibrio Derecho (FB < -1) */
    if (fb < -1) {
        if (factor_balance(nodo->derecho) > 0) {
            /* Rotación Doble Derecha-Izquierda */
            nodo->derecho = rotacion_derecha(nodo->derecho);
        }
        return rotacion_izquierda(nodo);
    }
    return nodo;
}

static struct NodoArbolAVL* insertar_avl(struct NodoArbolAVL* nodo, int dato, long long* nuevos_nodos) {
    if (!nodo) {
        (*nuevos_nodos)++;
        return crear_nodo_avl(dato);
    }
    if (dato < nodo->dato) {
        nodo->izquierdo = insertar_avl(nodo->izquierdo, dato, nuevos_nodos);
    } else if (dato > nodo->dato) {
        nodo->derecho = insertar_avl(nodo->derecho, dato, nuevos_nodos);
    } else {
        nodo->frecuencia++;
        return nodo;
    }
    return balancear_nodo_avl(nodo);
}

static struct NodoArbolAVL* buscar_avl(struct NodoArbolAVL* raiz, int dato, int* pasos) {
    struct NodoArbolAVL* actual = raiz;
    *pasos = 0;
    while (actual) {
        (*pasos)++;
        if (dato == actual->dato) return actual;
        actual = (dato < actual->dato) ? actual->izquierdo : actual->derecho;
    }
    return NULL;
}

static struct NodoArbolAVL* nodo_minimo_avl(struct NodoArbolAVL* n) {
    struct NodoArbolAVL* act = n;
    while (act && act->izquierdo) act = act->izquierdo;
    return act;
}

static struct NodoArbolAVL* eliminar_avl(struct NodoArbolAVL* raiz, int dato, int* exito) {
    if (!raiz) return NULL;
    if (dato < raiz->dato) {
        raiz->izquierdo = eliminar_avl(raiz->izquierdo, dato, exito);
    } else if (dato > raiz->dato) {
        raiz->derecho = eliminar_avl(raiz->derecho, dato, exito);
    } else {
        *exito = 1;
        if (!raiz->izquierdo || !raiz->derecho) {
            struct NodoArbolAVL* temp = raiz->izquierdo ? raiz->izquierdo : raiz->derecho;
            free(raiz);
            return temp;
        } else {
            struct NodoArbolAVL* suc = nodo_minimo_avl(raiz->derecho);
            raiz->dato = suc->dato;
            raiz->frecuencia = suc->frecuencia;
            int dummy = 0;
            raiz->derecho = eliminar_avl(raiz->derecho, suc->dato, &dummy);
        }
    }
    return balancear_nodo_avl(raiz);
}

static void inorden_muestra_avl(struct NodoArbolAVL* nodo, int* contador, int limite) {
    if (!nodo || *contador >= limite) return;
    inorden_muestra_avl(nodo->izquierdo, contador, limite);
    if (*contador < limite) {
        printf("%d ", nodo->dato);
        (*contador)++;
    }
    inorden_muestra_avl(nodo->derecho, contador, limite);
}

static void liberar_avl(struct NodoArbolAVL* nodo) {
    if (!nodo) return;
    liberar_avl(nodo->izquierdo);
    liberar_avl(nodo->derecho);
    free(nodo);
}

static void opcion_i_avl(long long limite) {
    printf("\n==============================================================================\n");
    printf("  i) IMPLEMENTACION DE ARBOL AVL (Cambio de Representacion)\n");
    printf("==============================================================================\n");

    long long n = 0;
    long long lim = (limite > 0) ? limite : 100000;
    int* datos = cargar_datos(ARCHIVO_DATOS, lim, &n);
    if (!datos || n == 0) return;

    struct NodoArbolAVL* raiz = NULL;
    long long nodos_unicos = 0;

    clock_t t0 = clock();
    for (long long i = 0; i < n; i++) {
        raiz = insertar_avl(raiz, datos[i], &nodos_unicos);
    }
    double dt_build = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_avl_construccion = dt_build;

    printf("  Altura del Arbol AVL         : %d\n", altura_avl(raiz));
    printf("  Cantidad total de nodos (un.): %lld (de %lld elementos leidos)\n", nodos_unicos, n);
    printf("  Tiempo de construccion       : %.4f segundos\n", dt_build);
    printf("  Recorrido InOrden (primeros 20 elementos): ");
    int mostrados = 0;
    inorden_muestra_avl(raiz, &mostrados, 20);
    printf("\n");

    int val_ins = 99999999;
    int val_bus = datos[n / 2];
    int pasos = 0, elim_ok = 0;

    clock_t ti = clock();
    raiz = insertar_avl(raiz, val_ins, &nodos_unicos);
    g_tiempos.t_avl_insercion_us = ((double)(clock() - ti) / CLOCKS_PER_SEC) * 1e6;

    clock_t tb = clock();
    struct NodoArbolAVL* hallado = buscar_avl(raiz, val_bus, &pasos);
    g_tiempos.t_avl_busqueda_us = ((double)(clock() - tb) / CLOCKS_PER_SEC) * 1e6;

    clock_t te = clock();
    raiz = eliminar_avl(raiz, val_bus, &elim_ok);
    g_tiempos.t_avl_eliminacion_us = ((double)(clock() - te) / CLOCKS_PER_SEC) * 1e6;

    printf("  * Insercion (%d)   : %.2f us\n", val_ins, g_tiempos.t_avl_insercion_us);
    printf("  * Busqueda (%d)    : %s en %d pasos (%.2f us)\n",
           val_bus, hallado ? "ENCONTRADO" : "NO ENCONTRADO", pasos, g_tiempos.t_avl_busqueda_us);
    printf("  * Eliminacion (%d) : %s (%.2f us)\n",
           val_bus, elim_ok ? "ELIMINADO" : "NO EXISTIA", g_tiempos.t_avl_eliminacion_us);

    liberar_avl(raiz);
    free(datos);
}

/* ============================================================================
 * j) Y k) HEAP BINARIO (MAX-HEAP / MIN-HEAP) Y HEAP SORT (Unidad 6, pág. 20-29)
 *    Relaciones padre-hijo en el arreglo:
 *      Padre(i) = (i - 1) / 2  |  Izq(i) = 2*i + 1  |  Der(i) = 2*i + 2
 * ============================================================================ */
static void heapify_max(int* arr, long long n, long long i) {
    while (1) {
        long long mayor = i;
        long long izq = 2 * i + 1;
        long long der = 2 * i + 2;

        if (izq < n && arr[izq] > arr[mayor]) mayor = izq;
        if (der < n && arr[der] > arr[mayor]) mayor = der;

        if (mayor != i) {
            int tmp = arr[i];
            arr[i] = arr[mayor];
            arr[mayor] = tmp;
            i = mayor;
        } else {
            break;
        }
    }
}

static void heapify_min(int* arr, long long n, long long i) {
    while (1) {
        long long menor = i;
        long long izq = 2 * i + 1;
        long long der = 2 * i + 2;

        if (izq < n && arr[izq] < arr[menor]) menor = izq;
        if (der < n && arr[der] < arr[menor]) menor = der;

        if (menor != i) {
            int tmp = arr[i];
            arr[i] = arr[menor];
            arr[menor] = tmp;
            i = menor;
        } else {
            break;
        }
    }
}

static void opcion_j_heap(void) {
    printf("\n==============================================================================\n");
    printf("  j) IMPLEMENTACION DE HEAP BINARIO (MAX-HEAP Y MIN-HEAP)\n");
    printf("==============================================================================\n");

    long long n = 0;
    int* max_h = cargar_datos(ARCHIVO_DATOS, 0, &n);
    if (!max_h || n == 0) return;

    int* min_h = (int*)malloc((size_t)(n + 1) * sizeof(int));
    memcpy(min_h, max_h, (size_t)n * sizeof(int));

    clock_t t0 = clock();
    for (long long i = (n / 2) - 1; i >= 0; i--) heapify_max(max_h, n, i);
    for (long long i = (n / 2) - 1; i >= 0; i--) heapify_min(min_h, n, i);
    g_tiempos.t_heap_construccion = (double)(clock() - t0) / CLOCKS_PER_SEC;

    int altura_aprox = (int)floor(log2((double)n)) + 1;
    printf("  Cantidad de elementos      : %lld\n", n);
    printf("  Elemento raiz en Max-Heap  : %d\n", max_h[0]);
    printf("  Elemento raiz en Min-Heap  : %d\n", min_h[0]);
    printf("  Altura aproximada del Heap : %d niveles\n", altura_aprox);
    printf("  Tiempo Build-Heap O(n)     : %.4f segundos\n", g_tiempos.t_heap_construccion);

    /* Eliminar máximo en Max-Heap y mínimo en Min-Heap */
    int max_extraido = max_h[0];
    max_h[0] = max_h[n - 1];
    heapify_max(max_h, n - 1, 0);

    int min_extraido = min_h[0];
    min_h[0] = min_h[n - 1];
    heapify_min(min_h, n - 1, 0);

    printf("  * Max-Heap tras eliminar maximo (%d) -> Nueva raiz: %d\n", max_extraido, max_h[0]);
    printf("  * Min-Heap tras eliminar minimo (%d) -> Nueva raiz: %d\n", min_extraido, min_h[0]);

    free(max_h);
    free(min_h);
}

static void opcion_k_heap_sort(void) {
    printf("\n==============================================================================\n");
    printf("  k) ORDENAMIENTO MEDIANTE HEAP SORT -> 'Datos_HeapSort.txt'\n");
    printf("==============================================================================\n");

    long long n = 0;
    int* datos = cargar_datos(ARCHIVO_DATOS, 0, &n);
    if (!datos || n == 0) return;

    clock_t t0 = clock();
    /* Fase 1: Construir el Max-Heap desde el último nodo no-hoja hasta la raíz */
    for (long long i = (n / 2) - 1; i >= 0; i--) {
        heapify_max(datos, n, i);
    }

    /* Fase 2: Extraer sucesivamente la raíz e invocar heapify en el subárbol restante */
    for (long long fin = n - 1; fin > 0; fin--) {
        int temp = datos[0];
        datos[0] = datos[fin];
        datos[fin] = temp;
        heapify_max(datos, fin, 0);
    }
    double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
    g_tiempos.t_heap_sort = dt;

    guardar_datos(ARCHIVO_HEAPSORT, datos, n);
    long long verificados = 0;
    int ok = verificar_archivo(ARCHIVO_HEAPSORT, &verificados);

    printf("  [OK] Heap Sort finalizado sobre n = %lld elementos.\n", n);
    printf("       Complejidad        : O(n log n) en Mejor y Peor Caso | Memoria O(1)\n");
    printf("       Tiempo de ejecucion: %.6f segundos\n", dt);
    printf("       Verificacion       : %s (%lld elementos)\n", ok == 1 ? "ORDENADO CORRECTAMENTE" : "ERROR", verificados);

    free(datos);
}

/* ============================================================================
 * l) COMPARACIÓN DE ESTRUCTURAS Y ALGORITMOS
 * ============================================================================ */
static void opcion_l_comparacion(void) {
    printf("\n==============================================================================\n");
    printf("  l) COMPARACION DE ESTRUCTURAS Y ALGORITMOS\n");
    printf("==============================================================================\n");
    printf("  Algoritmo      | Mejor Caso | Peor Caso  | Memoria Aux | Tiempo Medido (s)\n");
    printf("  ---------------+------------+------------+-------------+-------------------\n");
    printf("  Counting Sort  | O(n + k)   | O(n + k)   | O(k)        | %.6f s\n", g_tiempos.t_counting_sort);
    printf("  Selection Sort | O(n^2)     | O(n^2)     | O(1)        | %.6f s (n=%lld)\n",
           g_tiempos.t_selection_sort, g_tiempos.n_selection_sort);
    printf("  Heap Sort      | O(n log n) | O(n log n) | O(1)        | %.6f s\n", g_tiempos.t_heap_sort);
    printf("==============================================================================\n");
}

int main(void) {
#ifdef _WIN32
    system(""); /* Habilita secuencias de colores ANSI en consolas de Windows 10/11 */
#endif
    char opcion[16];
    while (1) {
        limpiar_pantalla();
        cartel("UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)",
               "Analisis y Diseno de Algoritmos | TP N 3: Transforma y Conquista (2026)", C_CYAN);

        separador("1. ARCHIVO DE DATOS Y ANALISIS INICIAL", C_CYAN);
        printf("    %s%sa)%s Generacion del archivo de datos ('Datos.txt')\n", C_AMARILLO, C_BOLD, C_RESET);
        printf("    %s%sb)%s Busqueda del maximo y minimo       %s[O(n) / Memoria O(1)]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_GRIS, C_RESET);
        printf("    %s%sc)%s Analisis de frecuencia             %s[Top 10 mas repetidos]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_GRIS, C_RESET);

        separador("2. ORDENAMIENTO Y VERIFICACION", C_VERDE);
        printf("    %s%sd)%s Ordenamiento mediante %sCounting Sort%s  %s[O(n + k)]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_VERDE, C_RESET, C_GRIS, C_RESET);
        printf("    %s%se)%s Ordenamiento mediante %sSelection Sort%s %s[O(n^2)]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_ROJO, C_RESET, C_GRIS, C_RESET);
        printf("    %s%sk)%s Ordenamiento mediante %sHeap Sort%s      %s[O(n log n) / O(1)]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_CYAN, C_RESET, C_GRIS, C_RESET);
        printf("    %s%sf)%s Verificacion del ordenamiento ascendente\n", C_AMARILLO, C_BOLD, C_RESET);

        separador("3. ESTRUCTURAS DE 'TRANSFORMA Y CONQUISTA' (UNIDAD 6)", C_AZUL);
        printf("    %s%si)%s Implementacion de %sArbol AVL%s        %s[Insercion, Busqueda, Elim., InOrden]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_AZUL, C_RESET, C_GRIS, C_RESET);
        printf("    %s%sj)%s Implementacion de %sHeap Binario%s     %s[Max-Heap y Min-Heap]%s\n", C_AMARILLO, C_BOLD, C_RESET, C_AMARILLO, C_RESET, C_GRIS, C_RESET);

        separador("4. TIEMPOS, COMPARACION Y SALIDA", C_MAGENTA);
        printf("    %s%sl)%s Comparacion de Estructuras y Algoritmos (incluye g y h)\n", C_AMARILLO, C_BOLD, C_RESET);
        printf("    %s%ss)%s Salir del programa\n", C_ROJO, C_BOLD, C_RESET);
        separador("", C_GRIS);
        printf("\n  %s%s>> Seleccione una opcion [a-l / s para salir]: %s", C_AMARILLO, C_BOLD, C_RESET);

        if (scanf("%15s", opcion) != 1) break;
        char c = opcion[0];
        if (c == 's' || c == 'S' || c == '0') {
            limpiar_pantalla();
            cartel("PROGRAMA FINALIZADO", "TP N 3 - Analisis y Diseno de Algoritmos (UNViMe 2026)", C_VERDE);
            break;
        }

        limpiar_pantalla();
        if (c == 'a' || c == 'A') opcion_a_generar_datos(0);
        else if (c == 'b' || c == 'B') opcion_b_max_min();
        else if (c == 'c' || c == 'C') opcion_c_frecuencia();
        else if (c == 'd' || c == 'D') opcion_d_counting_sort();
        else if (c == 'e' || c == 'E') opcion_e_selection_sort(0);
        else if (c == 'f' || c == 'F') opcion_f_verificar();
        else if (c == 'i' || c == 'I') opcion_i_avl(0);
        else if (c == 'j' || c == 'J') opcion_j_heap();
        else if (c == 'k' || c == 'K') opcion_k_heap_sort();
        else if (c == 'l' || c == 'L' || c == 'g' || c == 'h') opcion_l_comparacion();
        else printf("  %s[X] Opcion '%s' no valida.%s\n", C_ROJO, opcion, C_RESET);

        pausar_pantalla();
    }
    return 0;
}
