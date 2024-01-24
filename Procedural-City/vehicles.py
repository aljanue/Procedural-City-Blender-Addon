# Autores: Alberto Jativa, Jordi Beltran, Carlos Izquierdo, Enrique Alcover
# version ='1.0'
# -------------------------------------------------------------------------------
""" Script que contiene el código para generar los vehiculos de nuestra ciudad"""
# -------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------
import bpy
import math
import random
import os
import sys
import numpy as np
import mathutils

from city import Materials
from interpola import interpola_catmull_rom, interpola_hermite, interpola_lineal

dir = os.path.dirname(os.path.realpath(__file__))
if not dir in sys.path:
    sys.path.append(dir)
# -------------------------------------------------------------------------------

def setVehicleProperties(obj, pos_ini, tam_coche, material):
    """
    Función para asignar las propiedades de los vehiculos de la escena.
    Estas propiedades son: posición inicial, tamaño, material y movimiento.
    
    Args:
        obj (object): Objeto del que se estan modificando las propiedades
        pos_ini (float): Posición en la que se encuentra el vehiculo inicialmente
        tam_coche (int): Tamaño del vehiculo
        material (mat): Material del vehiculo
    """
    # Propiedades del objeto
    A = bpy.context.scene.a_desplazamiento
    freq = bpy.context.scene.f_desplazamiento
    v_coches = bpy.context.scene.v_coches
    calles_x = bpy.context.scene.calles_x
    calles_y = bpy.context.scene.calles_y
    tam_manzana = bpy.context.scene.tam_manzana
    tam_calles = bpy.context.scene.tam_calles
    p = bpy.context.scene.cursor.location
    
    n_giros = bpy.context.scene.n_giros
    
    # Creación del vehículo
    obj.location = pos_ini
    obj.scale = (tam_coche*10, tam_coche*10, tam_coche*10)

    # Asignación del material
    if material != -1:
        obj.data.materials.pop()
        obj.data.materials.append(material)

    aux_z = obj.location.z

    # Si la frecuencia es distinta de 0 se calcula la cantidad de fotogramas que
    # deben insertarse en la animación para completar un ciclo de movimiento en
    # función de la frecuencia
    if freq != 0:
        paso_kf = int(24/freq)
    else:
        paso_kf = 0

    # Creamos el primer fotograma de la escena
    start = bpy.context.scene.frame_start
    frm = start
    # Insertamos un fotograma clave en la posición del objeto en el eje X (index = 0) en el fotograma de la escena (frame = start)
    obj.keyframe_insert(data_path="location", index=0, frame=start)
    obj.keyframe_insert(data_path="location", index=1, frame=start)
    
    pos_ini_x = obj.location.x

    # Calculamos el inicio y final de la ciudad en el eje X
    ini_ciudad_x = p[0] - tam_calles/2
    fin_ciudad_x = p[0] + ((calles_x + 1) * (tam_manzana + tam_calles))
    
    # Si en el panel de las propiedades asignamos un numero de giros igual a 0, los coches se moverán en linea recta
    if n_giros == 0:
        #Los que están fuera de la ciudad que entren y la crucen por ambos lados (if y elif)
        if pos_ini_x > fin_ciudad_x:
            # Establecemos la posición final del vehiculo en 
            obj.location.x = pos_ini_x-(fin_ciudad_x - ini_ciudad_x)*1.25
            # Calculamos donde tenemos que insertar el último fotograma de la animación. 
            # Se calcula usando la fórmula de la velocidad en el MRU (x/t)
            frm += calles_x*1.25/v_coches*24
            # Insertamos un fotograma clave en la posición del objeto en el eje X (index = 0) en el fotograma de la escena (frame = end)
            obj.keyframe_insert(data_path="location", index=0, frame=frm)
        elif pos_ini_x < ini_ciudad_x:
            obj.location.x = pos_ini_x+(fin_ciudad_x - ini_ciudad_x)*1.25
            frm += calles_x*1.25/v_coches*24
            obj.keyframe_insert(data_path="location", index=0, frame=frm)
        # Los que están dentro de la ciudad, que se muevan a uno de los lados
        else:
            # Decidir a que lado moverse de forma aleatoria
            band = random.randint(1, 2)
            #Derecha
            if band == 1:
                obj.location.x = pos_ini_x+(fin_ciudad_x - ini_ciudad_x)*1.25
                frm += calles_x*1.25/v_coches*24
                obj.keyframe_insert(data_path="location", index=0, frame=frm)

            #Izquierda
            else:
                obj.location.x = pos_ini_x-(fin_ciudad_x - ini_ciudad_x)*1.25
                frm += calles_x*1.25/v_coches*24

    # Si el número de giros es distinto de 0, los coches se moveran realizando giros
    else:
        #Si no están dentro de la ciudad, les hacemos entrar antes de que giren
        if ini_ciudad_x > pos_ini_x:
            obj.location.x = ini_ciudad_x
            calles_recorridas = (ini_ciudad_x - pos_ini_x)/(tam_calles+tam_manzana)
            frm+=  calles_recorridas / v_coches * 24
            obj.keyframe_insert(data_path="location", index=0, frame=frm)
            obj.keyframe_insert(data_path="location", index=1, frame=frm)
            
        if fin_ciudad_x < pos_ini_x:
            obj.location.x = fin_ciudad_x
            calles_recorridas = (pos_ini_x - fin_ciudad_x)/(tam_calles+tam_manzana)
            frm+=  calles_recorridas / v_coches * 24
            obj.keyframe_insert(data_path="location", index=0, frame=frm)
            obj.keyframe_insert(data_path="location", index=1, frame=frm)
        
        giro = 0    # Contador de giros

        while(giro <= n_giros): 
            band = random.randint(1, 2)      # bandera para decidir a que lado moverse de forma aleatoria
            
            # Este condicional permitirá realizar 1 giro 
            # en cada eje de forma repetitiva
            
            #Movimiento en el eje x
            if giro%2!=0:
                # Girar en una calle aleatoria
                dist_rand = random.randint(1, calles_x)
                # Se mueven de izquierda a derecha
                if band == 1:
                    obj.location.x+=dist_rand*(tam_calles+tam_manzana)
                # Se mueven de derecha a izquierda
                else:
                    obj.location.x-=dist_rand*(tam_calles+tam_manzana)
                frm += (dist_rand/v_coches)*24
                obj.keyframe_insert(data_path="location", index=0, frame=frm)
                obj.keyframe_insert(data_path="location", index=1, frame=frm)
                
            #Giros en el eje y
            else:
                dist_rand = random.randint(1, calles_y)
                if band == 1:
                    obj.location.y+=dist_rand*(tam_calles+tam_manzana)
                else:
                    obj.location.y-=dist_rand*(tam_calles+tam_manzana)
                frm += (dist_rand/v_coches)*24
                obj.keyframe_insert(data_path="location", index=0, frame=frm)
                obj.keyframe_insert(data_path="location", index=1, frame=frm)
            giro+=1
      
    
    # Si el paso de keyframes y la frecuencia son distintos de cero, se producirá movimiento vertical (eje Z)
    if paso_kf != 0 and freq !=0:
        for i in range(start, int(frm), paso_kf):
            obj.location.z = aux_z + A 
            obj.keyframe_insert(data_path="location", index=2, frame=i)
        for i in range(start+int(paso_kf/2), int(frm), paso_kf):
            obj.location.z = aux_z 
            obj.keyframe_insert(data_path="location", index=2, frame=i)
    else:
        obj.keyframe_insert(data_path="location", index=2, frame=start)
        obj.keyframe_insert(data_path="location", index=2, frame=frm)
    
    ObtenerCurvaDistancia_Recorrida(obj)
                    
    InicializarDistancia_Deseada(obj)

def CreateVehicles():
    """
    Función que genera todos los vehiculos que estarán en la escena de Blender. Esta función obtiene los valores
    de las variables de la interfaz implementada.

    Mediante un bucle for creamos cada vehiculo individualmente. De forma aleatoria seleccionamos la calle en la
    que se ubicará el coche, calculamos el tamaño del coche según el tamaño de las calles y calculamos una altura
    aleatoria para cada coche en función del tamaño del vehiculo y la altura máxima que puede tener un edificio.
    """
    #Propiedades del panel
    calles_y = bpy.context.scene.calles_y
    calles_x = bpy.context.scene.calles_x
    tam_manzana = bpy.context.scene.tam_manzana
    tam_calles = bpy.context.scene.tam_calles
    p = bpy.context.scene.cursor.location
    n_vehicles = bpy.context.scene.n_coches
    
    #Creacion objeto vacio
    bpy.ops.object.empty_add(location=[0, 0, 0])
    vehicles = bpy.context.active_object
    vehicles.name = 'coches'

    # Buscar coleccion 'ciudad'
    city = bpy.data.collections.get('ciudad')
    
    # Enlazar a coleccion ciudad
    city.objects.link(vehicles)
    bpy.context.collection.objects.unlink(vehicles)
    
    # Creacion de materiales
    vehicles_materials = Materials('vehicle')
    
    # Obtencion de la coleccion de las copias de los coches
    vehiclesCollection = bpy.data.collections.get('copias_ModeloCoche')

    # Bucle for para crear los coches, calculamos la posición inicial y el tamaño del coche y llamamos a CreateVehicle
    i = 0 # Contador de coches
    for obj in vehiclesCollection.objects:
        # Si el objeto es un coche, lo guardamos en la variable car
        if obj.name.startswith('ModeloCoche'):
            car = obj
            car.name = 'coche.{:03d}'.format(i)

            # Enlazamos al objeto vacío
            bpy.context.view_layer.objects.active = vehicles
            vehicles.select_set(True)
            bpy.ops.object.parent_set(type='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            car.select_set(True)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            # Enlazamos el coche a la colección de la ciudad
            city.objects.link(car)
            vehiclesCollection.objects.unlink(car)

            # Calculamos la posición inicial del coche, tamaño y altura de vuelo
            calle_ini = random.randint(-calles_y//4, calles_y+calles_y//2)
            tam_coche = (tam_calles * 0.4) / 2
            h_vuelo = random.uniform(tam_coche / 2, bpy.context.scene.alt_edificios_max)
            
            if(len(vehicles_materials) > 0):
                material = vehicles_materials[random.randint(0, len(vehicles_materials)-1)]
            else:
                material=-1
                
            rand_calle_ini=random.randint(-calles_x//4, calles_x+calles_x//4)
            pos_x = p[0]+(rand_calle_ini-1)*(tam_calles+tam_manzana)+(tam_calles/2+tam_manzana)
            pos_ini = [pos_x, p[1] + (calle_ini - 0.5) * tam_calles + tam_manzana * calle_ini, p[2] + h_vuelo]
            setVehicleProperties(car, pos_ini, tam_coche, material)
            i += 1
        
def get_posicion(self, frame, ind):
    """
    Calcula la posición de nuestro objeto en un fotograma especifico de la animación,
    dados unos fotogramas clave, utilizando el algoritmo de interpolación lineal implementado
    
    Args:
        self (Object): Referencia al objeto desde el que se llama el método.
        frame (int): Número del fotograma en el que estamos calculando la posición del objeto
        ind (int): Índice del eje que queramos tratar (0 para X, 1 para Y, 2 para Z).
    Returns:
        pos (float): Posición en que se encuentra el objeto en el frame deseado.
    """
    interpolation_method = bpy.context.scene.interpolation_method
    
    obj = self

    # Si quieren reparametrizar
    if obj.utilizar:
        if obj.animation_data and obj.animation_data.action:
            # Obtenemos la curva del fotograma que contiene la información del eje especificado con
            # la variable ind. Location indica que estamos buscando información sobre la ubicación del objeto.
            curva_recorrida = obj.animation_data.action.fcurves.find('dist_recorrida')
            curva_deseada = obj.animation_data.action.fcurves.find('dist_deseada')
            #Obtenemos la distancia deseada
            distancia = curva_deseada.evaluate(frame)
            iterator = 0
            while (iterator < len(curva_recorrida.keyframe_points) and curva_recorrida.keyframe_points[iterator].co[1] < distancia):
                iterator = iterator + 1

            if iterator < len(curva_recorrida.keyframe_points):
                #Obtenemos el frame donde se encuentra la distancia en la curva de distancia recorrida 
                frame = interpola_lineal(curva_recorrida.keyframe_points[iterator-1].co[1],
                             curva_recorrida.keyframe_points[iterator].co[1], 
                             curva_recorrida.keyframe_points[iterator-1].co[0],
                             curva_recorrida.keyframe_points[iterator].co[0], distancia)
            else:
                frame = curva_recorrida.keyframe_points[-1].co[0]
            
            
    # Obtenemos la curva del fotograma que contiene la información del eje especificado con
    # la variable ind. Location indica que estamos buscando información sobre la ubicación del objeto.
    curva = obj.animation_data.action.fcurves.find('location', index=ind)
    
    i = 0 # Empezamos a mirar desde el fotograma principal
    # Bucle para encontrar el par de fotogramas entre los que se encuentra el fotograma deseado
    while i < len(curva.keyframe_points) and curva.keyframe_points[i].co[0] < frame:
        i = i + 1
    
    if interpolation_method == 'CATMULL':
        # Si solo hay dos keyframes
        if len(curva.keyframe_points) == 2:
            if i<=0:
                # Caso 1: El fotograma deseado esta antes que el primer fotograma clave y se toma la posición del primer fotograma clave
                pos = curva.keyframe_points[0].co[1] 
            elif i >= len(curva.keyframe_points):
                # Caso 2: El fotograma deseado esta después del ultimo fotograma clave y se toma la posición del último fotograma clave
                pos = curva.keyframe_points[i-1].co[1]
            else:
                pos = interpola_catmull_rom(
                    bpy.context.scene.tau_value,      # Tensión de la curva
                    curva.keyframe_points[i-1].co[0], # Tiempo del fotograma anterior
                    curva.keyframe_points[i].co[0],   # Tiempo del fotograma siguiente
                    curva.keyframe_points[i-1].co[1], # Posición del fotograma anterior (no hay otro previo)
                    curva.keyframe_points[i-1].co[1], # Posición del fotograma anterior
                    curva.keyframe_points[i].co[1],   # Posición del fotograma siguiente
                    curva.keyframe_points[i].co[1],   # Posición del fotograma siguiente (no hay otro después)
                    frame                             # El fotograma deseado para el cálculo
                    )
        else:
            if i<=0:
                # Caso 1: El fotograma deseado esta antes que el primer fotograma clave y se toma la posición del primer fotograma clave
                pos = curva.keyframe_points[0].co[1] 
            elif i >= len(curva.keyframe_points):
                # Caso 2: El fotograma deseado esta después del ultimo fotograma clave y se toma la posición del último fotograma clave
                pos = curva.keyframe_points[i-1].co[1] 
            elif i < 2:
                # Caso 3: Como no hay fotograma previo al anterior, se coge el anterior
                pos = interpola_catmull_rom(
                    bpy.context.scene.tau_value,      # Valor de la tensión
                    curva.keyframe_points[i-1].co[0], # Tiempo del fotograma anterior
                    curva.keyframe_points[i].co[0],   # Tiempo del fotograma siguiente
                    curva.keyframe_points[i-1].co[1], # Posición del fotograma anterior (no hay otro previo)
                    curva.keyframe_points[i-1].co[1], # Posición del fotograma anterior
                    curva.keyframe_points[i].co[1],   # Posición del fotograma siguiente
                    curva.keyframe_points[i+1].co[1], # Posición del fotograma siguiente siguiente
                    frame                             # El fotograma deseado para el cálculo
                    )
            elif i > len(curva.keyframe_points)-3:
                # Caso 4: Como no hay fotograma posterior al siguiente, se utiliza el siguiente
                pos = interpola_catmull_rom(
                    bpy.context.scene.tau_value,      # Tensión de la curva
                    curva.keyframe_points[i-1].co[0], # Tiempo del fotograma anterior
                    curva.keyframe_points[i].co[0],   # Tiempo del fotograma siguiente
                    curva.keyframe_points[i-2].co[1], # Posición del fotograma anterior del anterior
                    curva.keyframe_points[i-1].co[1], # Posición del fotograma anterior
                    curva.keyframe_points[i].co[1],   # Posición del fotograma siguiente 
                    curva.keyframe_points[i].co[1],   # Posición del fotograma siguiente (no hay otro después)
                    frame                             # El fotograma deseado para el cálculo
                    )
            else:
                # Caso general: Se calcula con interpolación Catmull-Rom la posición del fotograma
                pos = interpola_catmull_rom(
                    bpy.context.scene.tau_value,      # Tensión de la curva
                    curva.keyframe_points[i-1].co[0], # Tiempo del fotograma anterior
                    curva.keyframe_points[i].co[0],   # Tiempo del fotograma siguiente
                    curva.keyframe_points[i-2].co[1], # Posición del fotograma anterior del anterior
                    curva.keyframe_points[i-1].co[1], # Posición del fotograma anterior
                    curva.keyframe_points[i].co[1],   # Posición del fotograma siguiente
                    curva.keyframe_points[i+1].co[1], # Posición del fotograma siguiente del siguiente
                    frame                             # El fotograma deseado para el cálculo
                    )
    elif interpolation_method == 'HERMITE':
        if i==0:
            pos = curva.keyframe_points[0].co[1]
        elif i == len(curva.keyframe_points):
            pos = curva.keyframe_points[i-1].co[1]
        else:
            v1 = 15*(curva.keyframe_points[i-1].handle_right[1] - curva.keyframe_points[i-1].handle_left[1])
            v2 = 15*(curva.keyframe_points[i].handle_right[1] - curva.keyframe_points[i].handle_left[1])

            pos = interpola_hermite(curva.keyframe_points[i-1].co[0], curva.keyframe_points[i].co[0], curva.keyframe_points[i-1].co[1], curva.keyframe_points[i].co[1], v1, v2, frame)    
    elif interpolation_method == 'LINEAL':
        if i==0:
            pos = curva.keyframe_points[0].co[1]
        elif i == len(curva.keyframe_points):
            pos = curva.keyframe_points[i-1].co[1]
        else:
            pos = interpola_lineal(curva.keyframe_points[i-1].co[0], curva.keyframe_points[i].co[0], curva.keyframe_points[i-1].co[1], curva.keyframe_points[i].co[1], frame)
    return pos

def get_quaternion(self, frame, axis):
    """
    Calcula el quaternion de rotación del objeto determinando un vector con las posiciones actual
    y anterior del objeto y otro vector con la dirección tangente deseada.
    Args:
        self (Object): Referencia al objeto desde el que se llama el método.
        frame (int): Número del fotograma en el que estamos calculando la posición del objeto
        axis (int): Índice del eje que queramos tratar (0 para X, 1 para Y, 2 para Z).
    Returns:
        qFinal (float): Quaternion de rotación del objeto en el frame deseado.
    """
    # Vector que marca la dirección inicial del objeto vehículo
    vDirector = mathutils.Vector(bpy.context.scene.v_director)

    ## Obtención de las posiciones que forman el vector tangente
    # Para el primer fotograma se calcula la trayectoria entre el primer keyframe y el siguiente (ya que no hay keyframe anterior)
    if frame == bpy.context.scene.frame_start:
        v1 = mathutils.Vector([get_posicion(self, frame+1, 0), get_posicion(self, frame+1, 1), get_posicion(self, frame+1, 2)])
        v0 = mathutils.Vector([get_posicion(self, frame, 0), get_posicion(self, frame, 1), get_posicion(self, frame, 2)])
    # Para el resto de fotogramas la trayectoria se calcula con el keyframe anterior y el actual.
    else:
        v0 = mathutils.Vector([get_posicion(self, frame-1, 0), get_posicion(self, frame-1, 1), get_posicion(self, frame-1, 2)])
        v1 = mathutils.Vector([get_posicion(self, frame, 0), get_posicion(self, frame, 1), get_posicion(self, frame, 2)])

    # Vector tangente de la trayectoria
    vTangente = v1 - v0
    vTangenteSinNormalizar = vTangente # Necesitamos el vector tangente sin normalizar para el alabeo
    vTangente.normalize()

    ## Alineación con el tangente
    qAlineacion = get_quat_from_vecs(vDirector, vTangente)

    ## Ajuste de la dirección lateral
    vLateral = get_lat_vec(vTangente) # Obtener el vector lateral de la trayectoria
    el = get_lat_vec(vDirector) # Obtener el vector lateral inicial del vehículo
    qRot = get_quat_rot(vTangente, vDirector, el)

    # Cuaternion final (sin aplicar las correcciones de eje z e y, ademas del alabeo)
    qFinal = qRot @ qAlineacion
    
    # Corrección para que el eje z sea siempre positivo
    z = mathutils.Vector([0, 0, 1])
    z.rotate(qFinal)
    if z[2] < 0:
        q180z = mathutils.Quaternion((0, 1, 0), math.radians(180))
        qFinal =  qFinal @ q180z

    # Corrección para que el eje y este alineado
    if vTangente[1] == -1 and (bpy.context.scene.a_desplazamiento == 0 or bpy.context.scene.f_desplazamiento == 0):
        q180y = mathutils.Quaternion((0, 0, 1), math.radians(180))
        qFinal =  q180y @ qFinal
    
    ## Aplicación de una rotación adicional
    if self.utilizar_alabeo == True or bpy.context.scene.activar_alabeo == True:
            
        # Calculo del vector tangente anterior (necesario para el cuaternion de alabeo)
        if frame == bpy.context.scene.frame_start or frame == bpy.context.scene.frame_start + 1:
            vTangenteAnterior = mathutils.Vector([0, 0, 0])
        else:
            v0 = mathutils.Vector([get_posicion(self, frame-2, 0), get_posicion(self, frame-2, 1), get_posicion(self, frame-2, 2)])
            v1 = mathutils.Vector([get_posicion(self, frame-1, 0), get_posicion(self, frame-1, 1), get_posicion(self, frame-1, 2)])
            vTangenteAnterior = v1 - v0
        
        qAlabeo = get_quat_alabeo(vTangenteSinNormalizar, vTangenteAnterior)
        qFinal = qAlabeo @ qFinal

    return qFinal[axis]

def get_quat_from_vecs(e, t):
    """
    Función que calcula el cuaternion que alinea los vectores e y t.
    Args:
        e (Vector): Vector director del objeto
        t (Vector): Vector tangente del objeto
    Returns:
        q (float): Quaternion de rotación del objeto en el frame deseado.
    """
    v = e.cross(t)
    v.normalize()
    angle = math.acos(max(-1, min(1, e.dot(t))))

    return mathutils.Quaternion(v, angle)

def get_lat_vec(t):
    """
    Calcula el vector lateral del objeto determinando un vector con la dirección tangente deseada.
    Args:
        t (Vector): Vector tangente del objeto
    Returns:
        l (Vector): Vector lateral del objeto en el frame deseado.
    """
    # Vector up
    z = mathutils.Vector([0, 0, 1])
    
    l = z.cross(t)
    l.normalize()
    return l

def get_quat_rot(t, e, el):
    """
    Función que que recibe el vector t, el vector e para alinearlo con t y el vector el para
    controlar la orientación lateral. 
    Args:
        t (Vector): Vector tangente del objeto
        e (Vector): Vector director del objeto
        el (Vector): Vector lateral que tiene el objeto inicialmente
    Returns:
        q (float): Quaternion de rotación del objeto en el frame deseado.
    """
    # Obtenemos el vector e'l (aplicandole el cuaternion de alineacion)
    el.rotate(get_quat_from_vecs(e, t))

    # Obtenemos el vector lateral de la trayectoria
    l = get_lat_vec(t)

    # Obtenemos el cuaternion de rotación
    q = get_quat_from_vecs(el, l)

    return q

def get_quat_alabeo(t, tAnt):
    """
    Función que recibe los vectores tangentes actual y anterior para calcular el cuaternion de alabeo.
    Los vectores deben estar sin normalizar ya que sino el angulo de alabeo no se calcula correctamente.
    Args:
        t (Vector): Vector tangente del objeto
        tAnt (Vector): Vector tangente anterior del objeto
    Returns:
        q (float): Quaternion de alabeo del objeto en el frame deseado.
    """
    # Obtenemos el vector lateral de la trayectoria
    l = get_lat_vec(t)

    # Obtenemos el vector normal de la curva
    deltaT = 1 / 24
    n = ( t - tAnt ) / deltaT

    # Calculamos el ángulo de inclinacion
    angle = n.length

    # Cálculo del signo de inclinación del vehiculo
    if l.dot(n.normalized()) > 0:
        angle = -angle

    # Limitamos el ángulo de inclinación
    angle = min(max(-45, angle), 45)
    
    # Convertimos el ángulo a radianes
    angle = math.radians(angle)

    # Calculamos el cuaternion de alabeo
    q = mathutils.Quaternion(t, angle)
    return q

def ObtenerCurvaDistancia_Recorrida(obj):
    """
    Función que crea la curva con la distancia total recorrida del objeto
    Args:
        obj (Object): Objeto del que se estan modificando las propiedades
    """
    # Cuando quieren recalcular, borramos la curva
    if obj.animation_data.action.fcurves.find('dist_recorrida'):
        obj.animation_data.action.fcurves.remove(obj.animation_data.action.fcurves.find('dist_recorrida'))    

    distancia = 0

    #Insertamos kf en frame = 0
    obj.dist_recorrida = distancia
    obj.keyframe_insert(data_path="dist_recorrida", frame=0)
    
    #Para el resto de frames calculamos la distancia recorrida
    for i in range(1, bpy.context.scene.frame_end+1):
        #Obtenemos un vector con la distancia entre puntos por coordenadas
        p = mathutils.Vector([get_posicion(obj, i, j) - get_posicion(obj, i-1, j) for j in range(3)])
        #Hacemos el modulo para sacar la distancia y la sumamos
        distancia += p.length
        obj.dist_recorrida = distancia
        obj.keyframe_insert(data_path="dist_recorrida", frame=i)

    # Convertimos la interpolacion de blender a lineal
    set_interpolation_to_linear(obj, 'dist_recorrida')

        
    

def InicializarDistancia_Deseada(obj):
    """
    Función que inicializa la distancia deseada del objeto en cada fotograma de la animación.
    Args:
        obj (Object): Objeto del que se estan modificando las propiedades
    """
    # Asegúrate de que el objeto tiene datos de animación y una acción
    if obj.animation_data and obj.animation_data.action:
        # Obtenemos la curva del fotograma que contiene la información del eje especificado con
        # la variable ind. Location indica que estamos buscando información sobre la ubicación del objeto.
        curva = obj.animation_data.action.fcurves.find('dist_recorrida')
        # Cuando quieren recalcular, borramos la curva
        if obj.animation_data.action.fcurves.find('dist_deseada'):
            obj.animation_data.action.fcurves.remove(obj.animation_data.action.fcurves.find('dist_deseada'))

        if curva:
            #Insertamos 2 kf para inicializar la curva
            bpy.context.object.dist_deseada = curva.keyframe_points[0].co[1]
            obj.keyframe_insert(data_path="dist_deseada", frame=curva.keyframe_points[0].co[0])
            obj.dist_deseada = curva.keyframe_points[bpy.context.scene.frame_end].co[1]
            obj.keyframe_insert(data_path="dist_deseada", frame=bpy.context.scene.frame_end)

            # Convertimos la interpolacion de blender a lineal
            set_interpolation_to_linear(obj, 'dist_deseada')

def set_interpolation_to_linear(obj, data_path):
    """
    Función que convierte la interpolacion de Blender a lineal
    Args:
        obj (Object): Objeto del que se estan modificando las propiedades
        data_path: Propiedad cuya curva se convierte a lineal
    """
    if obj.animation_data and obj.animation_data.action:
        fcurve = obj.animation_data.action.fcurves.find(data_path)
        if fcurve:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'
    
    