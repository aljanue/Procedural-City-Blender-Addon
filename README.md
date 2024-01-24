# PROCEDURAL CREATION OF A FUTURISTIC CITY

The Procedural City addon is a script for Blender that allows for the procedural creation of cities. It was developed by Alberto Jativa and Jordi Beltran.

This addon allows Blender users to generate cities procedurally, providing a quick and efficient way to create detailed urban environments without the need to model each building individually.

In addition to city creation, this addon also provides functionalities for the creation and configuration of vehicles, allowing users to customize the traffic and movement of vehicles in the generated city.

## Installation

1. Click on `<> Code` and Download the folder as `.zip`.
2. Compress the `Procedural-City` folder into a `.zip` file.
3. Open Blender and go to `Edit > Preferences`.
4. In the preferences window, select the `Add-ons` tab.
5. Click on `Install...` and locate the `.zip` file you compressed.
6. Once installed, make sure the addon is enabled by checking the box next to its name.

## Usage

1. Modify the values on the creation of the terrain such as the width or the number of streets.
2. Modify the values on the buildings such as height or size.
3. Modify the values of the vehicles such as speed, number of turns...
4. Select an interpolation method for vehicle movement. If you select Catmull-Rom, you will need to set a value for "tau".
5. When you press the button to generate the city, select the object "car.obj" or another.

**NOTE:** You can add materials named buildings and vehicles to your scene. The addon will be responsible for assigning them randomly to the objects.

In the vehicle object interface, you can enable or disable roll for each vehicle, as well as use reparameterization along the animation curve.

To use curve reparametrization:
1. Activate the checkbox.
2. Access the animation graph and modify the desired distance curve.

### What is reparametrization along the animation curve?

Reparametrization along the curve allows changing the speed with which the vehicle travels the curve without needing to change its trajectory. This is very useful when using the Catmull-Rom method, as it allows us to traverse the curve obtained for a specific tau at a custom speed.

## How it works

### Buildings:

The city.py script is responsible for generating the buildings in the procedural city. It contains several functions:

1. CreateBuilding(pos_x, pos_y, pos_z, l, h, material, city): This function creates a single building. It takes in the x, y, and z coordinates of the building, the width (l) and height (h) of the building, the material to be used for the building, and the collection (city) where the building will be stored. A cube is created using the bpy.ops.mesh.primitive_cube_add function with the provided location and scale. The scale is divided by 2 to adjust for Blender's default cube size. This cube represents the building.

2. Materials(tipo): This function returns a list of materials whose names start with the string provided in the tipo parameter. These materials are used for the buildings.

3. probabilidad_edificio(x, y): This function calculates the probability of a building appearing based on its proximity to the center of the city. The closer to the center, the higher the probability.

4. CreateCity(): This function creates the procedural city. It gets the values of the variables from the user interface, calculates the center of the city, and uses for loops to place the buildings. It calls the CreateBuilding function with the necessary parameters. The buildings are placed in a grid, and their probability of appearance is checked. If a building is created, its height is calculated based on its distance from the center.

### Vehicles:

The vehicles.py script is responsible for generating the vehicles in the procedural city and their animations. It contains several functions:

1. CreateVehicle(pos_x, pos_y, pos_z, tipo, city): This function creates a single vehicle at the specified location (pos_x, pos_y, pos_z) of the specified type (tipo), and adds it to the specified city collection. The type of the vehicle determines the model and materials used for the vehicle. The vehicle is represented by a mesh object in Blender.

2. getPosicion(frame, velocidad, direccion): This function calculates the position of a vehicle at a given frame based on its speed (velocidad) and direction (direccion). The direction is a vector that points in the direction the vehicle is moving, and the speed is a scalar that determines how fast the vehicle is moving.

The function multiplies the direction vector by the speed and the frame number to calculate how far the vehicle has moved from its starting position. This gives a new vector that represents the vehicle's displacement from its starting position. This displacement vector is then added to the vehicle's initial position to get its current position.

The function returns this current position as a vector, which is used as a driver for the vehicle's location property. This means that at each frame, the vehicle's location is updated to the value returned by this function, creating the animation of the vehicle moving.

3. getQuaternion(frame, velocidad, direccion): This function calculates the orientation of a vehicle at a given frame based on its speed (velocidad) and direction (direccion). It returns a quaternion, which is a way to represent rotation in 3D space.

The function calculates the angle of rotation based on the vehicle's speed and the frame number. It then creates a quaternion that represents a rotation of this angle around the direction vector. This quaternion is used as a driver for the vehicle's rotation property.

This means that at each frame, the vehicle's rotation is updated to the value returned by this function, creating the animation of the vehicle rotating as it moves. The vehicle's rotation is always aligned with its direction of motion, so it appears to turn as it changes direction.

