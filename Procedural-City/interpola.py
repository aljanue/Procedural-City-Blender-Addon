# Autores: Alberto Jativa, Jordi Beltran, Carlos Izquierdo, Enrique Alcover
# version ='1.0'
# --------------------------------------------------------------------------------------
""" Script que contiene las funciones de interpolación lineal, Hermite y Catmull-Rom """
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import numpy as np
# --------------------------------------------------------------------------------------

def interpola_lineal(t0, t1, x0, x1, t):
    """
    Algoritmo de interpolación lineal para estimar la posición en un punto de tiempo entre
    dos puntos conocidos y sus tiempos en una trayectoria.

    Args:
        t0: inicio del tramo
        t1: fin del tramo
        x0: posicion al inicio del tramo
        x1: posición al final del tramo
        t: tiempo entre t0 y t1 en el que queremos la posición

    Returns:
        x: Estimación de la posición en el tiempo t.

    """
    # Calcula la duración del tramo
    duracion = t1 - t0

    # Calcula la proporción de tiempo transcurrido entre t0 y t1 en el tiempo t.
    u = (t-t0) / duracion

    # Obtenemos una estimación de la posición dado el tiempo t utilizando interpolación lineal
    x = x0 + u*(x1-x0)
    return x


def interpola_hermite(t0, t1, x0, x1, v0, v1, t):
    """
    Algoritmo de interpolación Hermite, que estima la posición en un punto de tiempo entre dos puntos conocidos
    en una trayectoria, teniendo en cuenta las velocidades iniciales y finales.

    Args:
        t0: inicio del tramo
        t1: fin del tramo
        x0: posicion al inicio del tramo
        x1: posición al final del tramo
        v0: velocidad al inicio del tramo
        v1: velocidad al final del tramo
        t: tiempo entre t0 y t1 en el que queremos la posición

    Returns:
        pos: Estimación de la posición en el tiempo t.

    """
    # Calcula la duración del tramo
    duracion = t1 - t0

    # Calcula la proporción de tiempo transcurrido entre t0 y t1 en el tiempo t.
    u = (t - t0) / duracion

    # Calculo de los coeficientes del polinomio de Hermite
    H00 = 2 * u**3 - 3 * u**2 + 1
    H10 = u**3 - 2 * u**2 + u
    H01 = -2 * u**3 + 3 * u**2
    H11 = u**3 - u**2

    # Aplicamos el polinomio de Hermite para obtener una estimación de la posición dado el tiempo
    pos = x0 * H00 + x1 * H01 + v0 * H10 + v1 * H11

    return pos


def interpola_catmull_rom(tau, t1, t2, x0, x1, x2, x3, t):
    """
    Algoritmo de interpolación Catmull-Rom, el cual estima la posición en un punto de tiempo intermedio entre
    dos puntos de control teniendo en cuenta la tensión (tau) y cuatro puntos de control en una trayectoria.
    La suavidad de las curvas generadas por este algoritmo se ve influenciada por el valor de tensión (tau):
    a medida que el valor de tau aumenta, la suavidad de las curvas se incrementa, 
    mientras que un valor menor de tau resulta en curvas más abruptas.

    Args:
        tau: Parámetro que marca la tensión del tramo (tau > 0.5 aporta i)
        t0: tiempo del primer punto de control
        t1: tiempo del segundo punto de control
        t2: tiempo del tercer punto de control
        t3: tiempo del cuarto punto de control
        x0: posición del primer punto de control
        x1: posición del segundo punto de control
        x2: posición del tercer punto de control
        x3: posición del cuarto punto de control
        t: tiempo entre t1 y t2 en el que queremos la posición interpolada

    Returns:
        pos: Estimación de la posición en el tiempo t utilizando el algoritmo Catmull-Rom.

    """
    # Cálculo de las velocidades en los puntos de control
    v1 = tau*(x3 - x1)
    v0 = tau*(x2 - x0)

    # Estimación de la posición interpolada utilizando el algoritmo de Hermite con las velocidades calculadas.
    pos = interpola_hermite(t1, t2, x1, x2, v0, v1, t)

    return pos

# Casos de prueba para interpola_lineal
print(interpola_lineal(0, 1, 0, 1, 0.5))  # Debería imprimir 0.5
print(interpola_lineal(0, 2, 0, 1, 1))    # Debería imprimir 0.5
print(interpola_lineal(1, 2, 1, 2, 1.5))  # Debería imprimir 1.5

# Casos de prueba para interpola_hermite
print(interpola_hermite(0, 1, 0, 1, 0, 0, 0.5))  # Debería imprimir 0.5
print(interpola_hermite(0, 2, 0, 1, 0, 0, 1))    # Debería imprimir 0.5
print(interpola_hermite(1, 2, 1, 2, 1, 1, 1.5))  # Debería imprimir 1.5

# Casos de prueba para interpola_catmull_rom
# Debería imprimir un valor entre 1 y 2
print(interpola_catmull_rom(0.5, 0, 1, 0, 1, 2, 3, 0.5))
# Debería imprimir un valor entre 2 y 3
print(interpola_catmull_rom(0.5, 1, 2, 1, 2, 3, 4, 1.5))
print(interpola_catmull_rom(0.5, 0, 2, 0, 1, 2, 3, 1))    # Debería imprimir 1.0

print(interpola_lineal(0, 1.5, 0, 3, 0.5))