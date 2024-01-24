import bpy


def crea_copias(obj, context, copy_action = False):
    """ Crea varias copias de un objeto y elimina las fcurves de posición

    Devuelve: colección con las copias creadas
    """

    scene = bpy.context.scene
    n = scene.n_coches

    base_collection = scene.collection

    # En lugar de dejar los objetos nuevos directamente en la colección básica,
    # creamos una. Esto facilitará el trabajo posterior
    # Si ya existe, creará otra.
    # Puede ser interesante eliminar los objetos que se crearon la última vez
    collection_name = "copias_"+obj.name
    copies_collection = bpy.data.collections.new(collection_name)
    base_collection.children.link(copies_collection)

    if obj.animation_data is not None:
        original_action = obj.animation_data.action
    else:
        original_action = None

    for i in range (n):

        # Creamos una copia del objeto obj
        # Hay que añadirlo a la colección. De lo contrario no
        # lo veremos en la escena
        new_obj = obj.copy()
        copies_collection.objects.link(new_obj)

        # La acción (con los fotogramas clave) no se copia. Se crea
        # una referencia. Si modificamos los fotogramas clave de
        # una copia, cambiarán todos, incluído el original
        # Si no queremos que ocurra esto, copiamos la acción, creando
        # una nueva.
        if copy_action and original_action is not None:
            new_obj.animation_data.action = original_action.copy()
        #
    #

    return copies_collection
#

if __name__ == "__main__":

    bpy.types.Object.n_copias = bpy.props.IntProperty(name="Num Copias")

    obj_a_copiar = bpy.context.object
    obj_a_copiar.n_copias = 2

    # Cuando lo llamemos desde un operador, le pasamos el context
    # que recibe el método invoke/execute
    crea_copias(obj_a_copiar,bpy.context)

#