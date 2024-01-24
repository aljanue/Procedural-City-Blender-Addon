# Autores: Alberto Jativa, Jordi Beltran, Carlos Izquierdo, Enrique Alcover
# version ='1.0'
# --------------------------------------------------------------------------------
""" Script que contiene el código para generar los edificios de nuestra ciudad"""
# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import bpy
import math
import random
# --------------------------------------------------------------------------------

def CreateBuilding(pos_x, pos_y, pos_z, l, h, material, city):
    """
    Función que toma 7 valores para generar un edificio en nuestra ciudad. Para generar un edificio utilizamos 
    un cubo sobre el que aplicamos la posición y tamaño calculados según las opciones seleccionadas por el usuario.
    También le pasamos el material y la colección donde lo almacenaremos.

    Args:
        pos_x (float): Coordenada x del edificio
        pos_y (float): Coordenada y del edificio
        pos_z (float): Coordenada z del edificio
        l (float): Ancho del edificio
        h (float): Largo del edificio
        material (material): Material
        city ('bpy_types.Collection'): Colección a la que se añade el edificio
    """
    # Creación del edificio
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(pos_x, pos_y, pos_z), scale=(l/2, l/2, h))
    obj = bpy.context.active_object
    obj.name = 'edificio'

    # Asignación del material
    if material != -1:
        obj.data.materials.append(material)
    
    # Enlazar objeto a objeto vacío
    buildings = bpy.data.objects.get('edificios')
    bpy.context.view_layer.objects.active = buildings
    buildings.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    # Enlazar objeto a coleccion
    city.objects.link(obj)
    bpy.context.collection.objects.unlink(obj)


def Materials(tipo):
    """
    Función para obtener una lista de los materiales cuyo nombre empiezan
    por el contenido de la variable tipo

    Args:
        tipo (String): nombre de los materiales

    Returns:
        mat (List): vector con los materiales cuyo nombre empieza por tipo
    """
    mat = []
    for all_materials in bpy.data.materials:
        if (all_materials.name.startswith(tipo)):
            mat.append(all_materials)
    return mat


def probabilidad_edificio(x, y):
    """
    Función que calcula la probabilidad de que un edificio aparezca dada la proximidad de dicho edificio al centro de la ciudad

    Args:
        x (float): Coordenada x del punto del que queremos calcular una probabilidad
        y (float): Coordenada y del punto del que queremos calcular una probabilidad

    Returns:
        prob (float): Probabilidad calculada
    """
    # Calculamos la distancia al origen del punto (x,y)
    dist = math.sqrt(x**2 + y**2)

    # Calculamos y devolvemos la probabilidad de aparición del edificio para ese punto
    prob = math.tanh(-0.4 * (dist-12)) * 0.45 + 0.5
    return prob


def CreateCity():
    """
    Función para crear una ciudad procedural en Blender. Esta función obtiene los valores
    de las variables de la interfaz del usuario.

    Calcula el centro de nuestra matriz de edificios para realizar el control de densidad
    de los edificios, cuanto mas alejados estemos del centro, habrá menos probabilidad de 
    que aparezca un edificio.

    Mediante bucles for, ubicamos los edificios y llamamos a la función CreateBuilding con
    los parámetros necesarios. Creamos la matriz de edificios comprobando su probabilidad de
    aparición, en el caso de que se cree el edificio por estar dentro de los valores de variación
    calculamos una altura acorde con su distancia al centro.
    """
    # Asignación de variables desde la interfaz
    nx = bpy.context.scene.calles_x
    ny = bpy.context.scene.calles_y
    l = bpy.context.scene.tam_manzana
    w = bpy.context.scene.tam_calles
    p = bpy.context.scene.cursor.location

    # Creacion de un objeto vacio para agrupar los objetos y tener la escena organizada
    bpy.ops.object.empty_add(location=p)
    obj = bpy.context.active_object
    obj.name = 'edificios'

    # Creacion de coleccion para agrupar los objetos y tener la escena organizada
    city = bpy.data.collections.new('ciudad')
    bpy.context.scene.collection.children.link(city)

    # Asignacion de objeto vacio a coleccion
    city.objects.link(obj)
    bpy.context.collection.objects.unlink(obj)

    # Posición inicial de la matriz de edificios
    pos_x = p[0] + l/2
    pos_y = p[1] + l/2

    # Cálculo del centro de la matriz de edificios
    cx = p[0]+ ( (nx + 1) * l + nx * w) / 2
    cy = p[1]+ ((ny + 1) * l + ny * w) / 2

    # Obtención de materiales a aplicar a los edificios (deben existir con anterioridad en la escena materiales cuyo nombre empiece con 'edificio')
    building_materials = Materials('building')

    # Bucles for para la creación de la matriz de edificios
    for row in range(nx+1):
        for col in range(ny+1):
            # Filtramos edificios por probabilidad
            if random.uniform(bpy.context.scene.var_edificios_min, bpy.context.scene.var_edificios_max) < probabilidad_edificio(pos_x - cx, pos_y - cy):

                # Asignamos altura por posición respectiva al centro
                if 0.94 < probabilidad_edificio(pos_x - cx, pos_y - cy):
                    h = random.uniform((bpy.context.scene.alt_edificios_min+bpy.context.scene.alt_edificios_max) / 2, bpy.context.scene.alt_edificios_max)  # 10.0, 16.0
                else:
                    h = random.uniform(bpy.context.scene.alt_edificios_min, (bpy.context.scene.alt_edificios_min+bpy.context.scene.alt_edificios_max) / 2)

                # Desplazamos los edificios un poco por debajo del suelo
                pos_z = p[2]+h-1

                # Asignamos material si existe
                if (len(building_materials) > 0):
                    material = building_materials[random.randint(0, len(building_materials) - 1)]
                else:
                    material = -1

                CreateBuilding(pos_x, pos_y, pos_z, l, h, material, city)

            pos_y += l + w

        pos_y = p[1] + l / 2
        pos_x += l + w