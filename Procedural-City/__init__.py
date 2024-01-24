# Autores: Alberto Jativa, Jordi Beltran
# version ='3.0'
# ----------------------------------------------------------------------------------------------
""" 
Script que implementa la interfaz para crear la ciudad y los vehiculos, ademas de configurar 
el movimiento de los coches.
"""
# ----------------------------------------------------------------------------------------------
# Información del addon
# ----------------------------------------------------------------------------------------------
bl_info = {
    "name": "Procedural City",
    "author": "aljanue, jorbel3",
    "version": (3, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Properties > Procedural City",
    "description": "Create a procedural city",
    "category": "Properties",
}
# ----------------------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------------------
import bpy
import os
import sys
import math

dir = os.path.dirname(os.path.realpath(__file__))
if not dir in sys.path:
    sys.path.append(dir)

from . import delete
from . import city
from . import vehicles
from crea_copias import crea_copias
from importlib import reload
from bpy_extras.io_utils import ImportHelper

# ------------------------------------------------------------------------------------------------------
# Reloads (recargar los módulos cada vez que ejecutamos el script user_interface.py que es el principal)
# ------------------------------------------------------------------------------------------------------
reload(delete)
reload(city)
reload(vehicles)

# Clase para crear un panel con los diferentes ajustes para la generación de la ciudad desde el viewport 3D
class ProceduralCityPanel(bpy.types.Panel):
    """
    Crea un panel para generar una ciudad procedural desde el 3D viewport
    """
    bl_label = "Procedural City"
    bl_idname = "OBJECT_PT_ProceduralCity"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Procedural City"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        scene = context.scene
        

        # Sección para la creación del terreno
        row = layout.row()
        row.label(text="Creation of terrain", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(scene, "calles_x")
        row.prop(scene, "calles_y")
        
        row = layout.row()
        row.prop(scene, "tam_manzana")
        row.prop(scene, "tam_calles")
        
        # Sección para la configuración de los edificios
        row = layout.row()
        row.label(text="Creation of buildings", icon='HOME')
        
        row = layout.row()
        row.prop(scene, "alt_edificios_min")
        row.prop(scene, "alt_edificios_max")

        row = layout.row()
        row.prop(scene, "var_edificios_min")
        row.prop(scene, "var_edificios_max")
        
        # Sección para la configuración de los vehiculos
        row = layout.row()
        row.label(text="Creation of vehicles", icon='AUTO')

        row = layout.row()
        row.prop(scene, "n_coches")
        row.prop(scene, "v_coches")

        row = layout.row()
        row.prop(scene, "a_desplazamiento")
        row.prop(scene, "f_desplazamiento")
        
        row = layout.row() 
        row.prop(scene, "n_giros")
        
        # Sección para la configuración del vector director
        row = layout.row()
        row.label(text="Vector director", icon='EMPTY_AXIS')

        row = layout.row()
        row.operator("object.director_x")
        row.operator("object.director_y")
        row.operator("object.director_z")
        
        # Botón para la generación de la ciudad
        row = layout.row()
        row.operator("object.generar_city")

        row = layout.row()
        row.label(text="Bank angle (all vehicles)", icon = 'DRIVER_ROTATIONAL_DIFFERENCE')
        row = layout.row()
        row.prop(scene, "activar_alabeo")
        
        box = layout.box()
        row = box.row()
        row.label(text="INTERPOLATION", icon = 'DRIVER_DISTANCE')
        
        row = box.row()
        row.prop(scene, "interpolation_method")
        
        row = box.row()
        row.prop(scene, "tau_value")
        
class AlabeoPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Bank Angle"
    bl_idname = "OBJECT_PT_alabeo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.name.startswith('coche')


    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Bank Angle", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        row = layout.row()
        row.prop(obj, "utilizar_alabeo")


class ReparametrizacionPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Reparametrization"
    bl_idname = "OBJECT_PT_reparam"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.name.startswith('coche')

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Distance", icon='ANIM')

        
        
        row = layout.row()
        row.prop(obj, "utilizar")

        row = layout.row()
        row.label(text="Desired distance")
        row.prop(obj, "dist_deseada")

        row = layout.row()
        row.operator("object.recalc_dist_rec")

        row = layout.row()
        row.operator("object.recalc_dist_des")
        
class DirectorXOperator(bpy.types.Operator):
    
    bl_idname = "object.director_x"
    bl_label = "X Axis"

    def execute(self, context):
        scene = context.scene
        scene.v_director = [1,0,0]
        return {'FINISHED'}
    
class DirectorYOperator(bpy.types.Operator):
    bl_idname = "object.director_y"
    bl_label = "Y Axis"

    def execute(self, context):
        scene = context.scene
        scene.v_director = [0,1,0]
        return {'FINISHED'}
    
class DirectorZOperator(bpy.types.Operator):
    bl_idname = "object.director_z"
    bl_label = "Z Axis"

    def execute(self, context):
        scene = context.scene
        scene.v_director = [0,0,1]
        return {'FINISHED'}


# Clase del operador para generar la ciudad
class GenerateCityOperator(bpy.types.Operator, ImportHelper):
    """
    Genera un grid con deformaciones aleatorias
    """
    bl_idname = "object.generar_city"
    bl_label = "Create city!"

    filter_glob: bpy.props.StringProperty(default="*.obj", options={'HIDDEN'})
    
    def execute(self, context):
        # Utilizamos una variable para la escena
        scene = context.scene

        # Eliminamos los objetos y acciones generados con la anterior generación de la ciudad y los vehiculos
        delete.DeleteCollections('ciudad')
        delete.DeleteActions()
        delete.DeleteCollections('copias_ModeloCoche')
        delete.DeleteObjects('ModeloCoche')
        
        # Importamos el fichero .obj
        bpy.ops.import_scene.obj(filepath=self.filepath, axis_forward='-Y', axis_up='Z')
        obj = bpy.context.selected_objects[0]
        obj.name = "ModeloCoche"
        
        # Llamamos a la función crearCiudad con las variables del menu.
        city.CreateCity()

        # Creamos las copias de los coches
        crea_copias(obj, context)

        # Llamamos a la función crearVehiculos con las variables del menu
        vehicles.CreateVehicles()

        # Eliminamos las colecciones de las copias de los coches y el coche original
        delete.DeleteCollections('copias_ModeloCoche')
        delete.DeleteObjects('ModeloCoche') 
                
        for obj in bpy.data.objects:
                if obj.name.startswith('coche') and obj.type!='EMPTY':
                    
                    drv_z = obj.driver_add('location', 2).driver
                    drv_z.use_self = True
                    drv_z.expression = "get_pos(self, frame, 2)"
                    
                    drv_y = obj.driver_add('location', 1).driver
                    drv_y.use_self = True
                    drv_y.expression = "get_pos(self, frame, 1)"
                    
                    drv_x = obj.driver_add('location', 0).driver
                    drv_x.use_self = True
                    drv_x.expression = "get_pos(self, frame, 0)"
                    obj.rotation_mode = 'QUATERNION'
                
                    drv_r_0 = obj.driver_add('rotation_quaternion', 0).driver
                    drv_r_0.use_self = True
                    drv_r_0.expression = "get_quat(self, frame, 0)"
                    
                    drv_r_1 = obj.driver_add('rotation_quaternion', 1).driver
                    drv_r_1.use_self = True
                    drv_r_1.expression = "get_quat(self, frame, 1)"
                    
                    drv_r_2 = obj.driver_add('rotation_quaternion', 2).driver
                    drv_r_2.use_self = True
                    drv_r_2.expression = "get_quat(self, frame, 2)"
                    
                    drv_r_3 = obj.driver_add('rotation_quaternion', 3).driver
                    drv_r_3.use_self = True
                    drv_r_3.expression = "get_quat(self, frame, 3)"
        
        return{'FINISHED'}
    
class Recalc_Dist_RecOperator(bpy.types.Operator):
    bl_idname = "object.recalc_dist_rec"
    bl_label = "Recalculate distance traveled"

    def execute(self, context):
        obj = bpy.context.active_object
        obj.utilizar = False
        vehicles.ObtenerCurvaDistancia_Recorrida(obj)
        return {'FINISHED'}
    
class Recalc_Dist_DesOperator(bpy.types.Operator):
    bl_idname = "object.recalc_dist_des"
    bl_label = "Recalculate desired distance"

    def execute(self, context):
        obj = bpy.context.active_object
        vehicles.InicializarDistancia_Deseada(obj)
        return {'FINISHED'}

# Estas funciones deben declararse al final del script.
def register():
    """
    Función de Blender que se utiliza para registrar y habilitar todas las clases, propiedades
    personalizadas, operadores y paneles que forman parte de la ciudad procedural.
    Esta función es llamada cuando se activa el complemento desde Blender.
    """
    # Se registran las propiedades en la escena
    bpy.types.Scene.v_director = bpy.props.IntVectorProperty(name="Vec. director", default=(0, 1, 0))

    bpy.types.Scene.calles_x = bpy.props.IntProperty(name = "Streets in x",
                                                     description="Number of streets in x",
                                                     min = 1,
                                                     default = 40)
                                                        
    bpy.types.Scene.calles_y = bpy.props.IntProperty(name = "Streets in y",
                                                     description="Number of streets in y",
                                                     min = 1, 
                                                     default = 40)
                                                   
    bpy.types.Scene.tam_manzana = bpy.props.FloatProperty(name= "Building size",
                                                          description="Building size",
                                                          min = 0,
                                                          default = 4)   
                                                                                                           
    bpy.types.Scene.alt_edificios_min = bpy.props.FloatProperty(name = "Minimum height",
                                                                description="Minimum height of buildings",
                                                                min = 1,
                                                                default = 2)
                                                            
    bpy.types.Scene.alt_edificios_max = bpy.props.FloatProperty(name = "Maximum height of",
                                                                description="Maximum height of buildings",
                                                                min = 1,
                                                                default = 40)
                                                            
    bpy.types.Scene.var_edificios_min = bpy.props.FloatProperty(name = "Minimum building variability",
                                                                description="Minimum probability that a building appears relative to the center",
                                                                min = 0,
                                                                default = 0,
                                                                max=1)
                                                            
    bpy.types.Scene.var_edificios_max = bpy.props.FloatProperty(name = "Maximum building variability",
                                                                description="Maximum probability that a building appears relative to the center",
                                                                min = 0,
                                                                default = 0.2,
                                                                max=1)
                                                          
    bpy.types.Scene.tam_calles = bpy.props.FloatProperty(name= "Width of streets (w)",
                                                         description="Width of streets (w)",
                                                         min = 0,
                                                         default = 4)
                                                          
    bpy.types.Scene.n_coches = bpy.props.IntProperty(name = "Number of vehicles",
                                                     description="Number of vehicles in the scene",
                                                     min = 0, 
                                                     default = 400)
                                                        
    bpy.types.Scene.v_coches = bpy.props.FloatProperty(name= "Vehicle speed",
                                                       description="Vehicle speed (streets per second)",
                                                       min = 0.01,
                                                       default = 1.6)

    bpy.types.Scene.a_desplazamiento = bpy.props.FloatProperty(name= "Travel Width",
                                                               description="displacement amplitude in the vertical axis",
                                                               min = 0,
                                                               default = 2)
    
    bpy.types.Scene.f_desplazamiento = bpy.props.FloatProperty(name= "Displacement frequency",
                                                               description="displacement frequency in the vertical axis",
                                                               min = 0,
                                                               default = 1)
                                                          
    bpy.types.Scene.n_giros = bpy.props.IntProperty(name = "Number of turns",
                                                    description="Total number of turns that cars will make on the streets",
                                                    min = 0, 
                                                    default = 20)

    
    bpy.types.Scene.tau_value = bpy.props.FloatProperty(name= "Tau",
                                                        description="Tau",
                                                        min = 0,
                                                        max = 10,
                                                        default = 0.1)
    
    bpy.types.Scene.interpolation_method = bpy.props.EnumProperty(
                                            name="Interpolation Method",
                                            description="Select the interpolation method to use",
                                            items=[
                                                ("HERMITE", "Hermite", "Hermite Interpolation"),
                                                ("CATMULL", "Catmull", "Catmull Interpolation"),
                                                ("LINEAL", "Lineal", "Lineal Interpolation")
                                            ],
                                            default="LINEAL")
    
    # Propiedad del objeto para activar el alabeo de un determinado objeto (vehiculo)
    bpy.types.Object.utilizar_alabeo = bpy.props.BoolProperty(name = "Use",
                                                       description="Use the bank angle",
                                                    default = False)
    
    # Propirdad de la escena para activar el alabeo de todos los vehiculos
    bpy.types.Scene.activar_alabeo = bpy.props.BoolProperty(name = "Active the bank angle",
                                                       description="Active the bank angle",
                                                       default = False)
    
    bpy.types.Object.utilizar = bpy.props.BoolProperty(name = "Use",
                                                       description="Use reparameterization",
                                                    default = False)
    
    bpy.types.Object.dist_deseada = bpy.props.FloatProperty(name = "Desired distance",
                                                    description="Desired distance for reparameterization", 
                                                    default = 0)
                                                    
    bpy.types.Object.dist_recorrida = bpy.props.FloatProperty(name = "Distance traveled",
                                                    description="Distance traveled with interpolation")

    # Se registra el driver                                                    
    bpy.app.driver_namespace['get_pos'] = vehicles.get_posicion
    bpy.app.driver_namespace['get_quat'] = vehicles.get_quaternion

    # Se registran los operadores                
                                                                                   
    bpy.utils.register_class(ProceduralCityPanel)

    bpy.utils.register_class(ReparametrizacionPanel)
    bpy.utils.register_class(AlabeoPanel)
    
    bpy.utils.register_class(GenerateCityOperator)

    bpy.utils.register_class(Recalc_Dist_RecOperator)
    bpy.utils.register_class(Recalc_Dist_DesOperator)

    bpy.utils.register_class(DirectorXOperator)
    bpy.utils.register_class(DirectorYOperator)
    bpy.utils.register_class(DirectorZOperator)  


def unregister():
    """
    Función de Blender que se utiliza para realizar la limpieza y desregistro de las clases
    y propiedades personalizadas que se registraron previamente en el complemento mediante 
    la función register(). 
    Esta función es llamada cuando se desactiva o se elimina el complemento desde Blender.
    """
    # Se desregistran clases y operadores cuando el complemento se desactive o elimine
    
    bpy.utils.unregister_class(ProceduralCityPanel)
    bpy.utils.unregister_class(GenerateCityOperator)
    bpy.utils.unregister_class(DirectorXOperator)
    bpy.utils.unregister_class(DirectorYOperator)
    bpy.utils.unregister_class(DirectorZOperator)
    
    bpy.utils.unregister_class(ReparametrizacionPanel)
    bpy.utils.unregister_class(AlabeoPanel)

    bpy.utils.unregister_class(Recalc_Dist_RecOperator)
    bpy.utils.unregister_class(Recalc_Dist_DesOperator)

    # Se eliminan las propiedades personalizadas relacionadas con la ciudad procedural
    del bpy.types.Scene.calles_x
    del bpy.types.Scene.calles_y
    del bpy.types.Scene.tam_manzana
    del bpy.types.Scene.alt_edificios_min
    del bpy.types.Scene.alt_edificios_max
    del bpy.types.Scene.var_edificios_min
    del bpy.types.Scene.var_edificios_max
    del bpy.types.Scene.tam_calles
    del bpy.types.Scene.n_coches
    del bpy.types.Scene.v_coches
    del bpy.types.Scene.a_desplazamiento
    del bpy.types.Scene.f_desplazamiento
    del bpy.types.Scene.n_giros
    del bpy.types.Scene.v_director
    del bpy.types.Scene.tau_value
    del bpy.types.Scene.interpolation_method
    del bpy.types.Scene.activar_alabeo
    del bpy.types.Object.utilizar_alabeo
    del bpy.types.Object.utilizar
    del bpy.types.Object.dist_deseada
    del bpy.types.Object.dist_recorrida

# Este bucle if impide que se ejecute la orden register() si se esta ejecutando el fichero mediante un import desde otro programa.
if __name__ == "__main__":
    register()