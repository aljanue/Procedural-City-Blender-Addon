# Autores: Alberto Jativa, Jordi Beltran, Carlos Izquierdo, Enrique Alcover
# version ='1.0'
# ---------------------------------------------------------------------------------------------
""" Script que contiene el código para eliminar objetos, colecciones y acciones de la escena"""
# ---------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------
import bpy
# ---------------------------------------------------------------------------------------------

def DeleteObjects(nameObject):
    """
    Función para eliminar todos los objetos con un nombre determinado

    Args:
        nameObject (String): nombre de los objetos a eliminar
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(nameObject):
            bpy.data.objects.remove(obj, do_unlink=True)


def DeleteCollections(nameCollection):
    """
    Función para eliminar una colección con un nombre determinado

    Args:
        nameCollection (String): nombre de la colección
    """
    for collection in bpy.data.collections:
        if collection.name.startswith(nameCollection):
            bpy.data.collections.remove(collection)


def DeleteActions():
    """
    Función para eliminar las acciones tras cada ejecución de crearVehiculos
    """
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)