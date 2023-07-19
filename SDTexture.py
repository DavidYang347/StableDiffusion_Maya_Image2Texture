<<<<<<< HEAD

from maya import cmds
import random


def showWindow():
    # The name of a window needs to be one word
    name = "SDTextureWindow"

    # We first check if the window is open, and if it is, we delete it
    # This makes sure we only ever have one window open
    if cmds.window(name, query=True, exists=True):
        cmds.deleteUI(name)

    # Then we create the window and then show it
    cmds.window(name)
    cmds.showWindow()
    
    
    
    # The column layout puts all our UI elements in a vertical layout
    column = cmds.columnLayout()
    # The frame layout gives us a nice section
    cmds.frameLayout(label="Screen capture")
    
    cmds.frameLayout(label="Choose an image")

    # Inside this we define a column layout for our radio buttons
    cmds.columnLayout()
    # the radio collection lets us have a group of radio buttons where only one can be selected
    cmds.radioCollection("objectCreationType")
    cmds.radioButton(label="Sphere")
    cmds.radioButton(label="Cube", select=True)
    cmds.radioButton(label="Cone")

    # The intfield is a text field that only allows integer numbers
    cmds.intField("numObjects", value=3)

    # Then we set our parent back to the first column
    cmds.setParent(column)
    frame = cmds.frameLayout("Choose your max ranges")


    # The grid layout puts our elements in a grid.
    # The grid here is 2 columns wide, so it'll put two elements side by side
    # before putting the next ones on the next row
    cmds.gridLayout(numberOfColumns=2, cellWidth=100)

    # We loop through the axes so we dont have to repeat code
    for axis in 'xyz':
        cmds.text(label='%s axis' % axis)
        cmds.floatField('%sAxisField' % axis, value=random.uniform(0, 10))

    cmds.setParent(frame)
    cmds.rowLayout(numberOfColumns=2)

    cmds.radioCollection("randomMode")
    cmds.radioButton(label='Absolute', select=True)
    cmds.radioButton(label='Relative')

    cmds.setParent(column)
    cmds.rowLayout(numberOfColumns=2)

    # Buttons can call commands and we tell it what to call
    cmds.button(label="Create", command=onCreateClick)
    cmds.button(label="Randomize", command=onRandomClick)
    
    
    
    


# The *args captures any arguments received by this function
# The buttons send an extra argument that we don't care about
# so *args stores it and we can just ignore it
def onCreateClick(*args):
    # First we check the radio collection to see which radio button is selected
    radio = cmds.radioCollection("objectCreationType", query=True, select=True)
    # Then we use the radio button to see what its text says to get its value
    mode = cmds.radioButton(radio, query=True, label=True)

    # We also get the value of the integer field
    numObjects = cmds.intField("numObjects", query=True, value=True)

    # We then create our objects using the values we just got
    createObjects(mode, numObjects)
    # Finally we call the onRandomClick function to randomize the items
    onRandomClick()

def onRandomClick(*args):
    radio = cmds.radioCollection("randomMode", query=True, select=True)
    mode = cmds.radioButton(radio, query=True, label=True)

    # For each axis we get its range values and then call the randomize function with that data
    for axis in 'xyz':
        val = cmds.floatField("%sAxisField" % axis, query=True, value=True)
        randomize(minValue=val*-1, maxValue=val, mode=mode, axes=axis)

def createObjects(mode, numObjects=5):
    """This creates objects. Supports Cubes, Spheres, Cylinder and Cones"""
    # Create an empty list to keep track of the objects we create
    objList = []
    for n in range(numObjects):
        # Here we check if the mode is equal to a value
        if mode == 'Cube':
            # If it's equal to Cube, then create a cube and store it in the obj variable
            obj = cmds.polyCube()
        elif mode == 'Sphere':
            # We can have multiple conditions
            obj = cmds.polySphere()
        elif mode == "Cylinder":
            obj = cmds.polyCylinder()
        elif mode == 'Cone':
            obj = cmds.polyCone()
        else:
            # And if no conditions are met we can error
            cmds.error("I don't know what to create")
        
        # Finally we just want to store the first item in the obj variable inside our objList
        # We add to the objList by using the append method on it.
        objList.append(obj[0])
    
    # Finally we select the objects we created
    cmds.select(objList)

    # Functions can also return values, that is give something back
    # This is how we get values from the polyCube() function
    # Our function will return a list of the objects we created
    return objList


def randomize(objList=None, minValue=0, maxValue=10, axes='xyz', mode='Absolute'):
    # First we check if no object list is given
    if objList is None:
        # If it's not given, we'll default to using the current selection
        objList = cmds.ls(selection=True)
    
    # Then we'll loop through all the objects
    for obj in objList:
        # And for each object we'll loop through the given axes
        for axis in axes:
            # We store the current value so we can add on to it if using relative mode
            current = 0
            if mode == 'Relative':
                # '%s.t%s' % (obj,axis) is using string substitution
                # It is the same as saying
                # obj + '.t' + axis
                # e.g '%s.t%s' % ('polyCube1','x') gives us 'polyCube1.tx'
                # It is an efficient way to make strings from other values
                current = cmds.getAttr('%s.t%s' % (obj,axis))
            
            # random.uniform gives us back a random float value between our given range
            val = current + random.uniform(minValue, maxValue)
            cmds.setAttr('%s.t%s' % (obj,axis), val)
=======

from maya import cmds
import random


def showWindow():
    # The name of a window needs to be one word
    name = "SDTextureWindow"

    # We first check if the window is open, and if it is, we delete it
    # This makes sure we only ever have one window open
    if cmds.window(name, query=True, exists=True):
        cmds.deleteUI(name)

    # Then we create the window and then show it
    cmds.window(name)
    cmds.showWindow()
    
    
    
    # The column layout puts all our UI elements in a vertical layout
    column = cmds.columnLayout()
    # The frame layout gives us a nice section
    cmds.frameLayout(label="Screen capture")
    
    cmds.frameLayout(label="Choose an image")

    # Inside this we define a column layout for our radio buttons
    cmds.columnLayout()
    # the radio collection lets us have a group of radio buttons where only one can be selected
    cmds.radioCollection("objectCreationType")
    cmds.radioButton(label="Sphere")
    cmds.radioButton(label="Cube", select=True)
    cmds.radioButton(label="Cone")

    # The intfield is a text field that only allows integer numbers
    cmds.intField("numObjects", value=3)

    # Then we set our parent back to the first column
    cmds.setParent(column)
    frame = cmds.frameLayout("Choose your max ranges")


    # The grid layout puts our elements in a grid.
    # The grid here is 2 columns wide, so it'll put two elements side by side
    # before putting the next ones on the next row
    cmds.gridLayout(numberOfColumns=2, cellWidth=100)

    # We loop through the axes so we dont have to repeat code
    for axis in 'xyz':
        cmds.text(label='%s axis' % axis)
        cmds.floatField('%sAxisField' % axis, value=random.uniform(0, 10))

    cmds.setParent(frame)
    cmds.rowLayout(numberOfColumns=2)

    cmds.radioCollection("randomMode")
    cmds.radioButton(label='Absolute', select=True)
    cmds.radioButton(label='Relative')

    cmds.setParent(column)
    cmds.rowLayout(numberOfColumns=2)

    # Buttons can call commands and we tell it what to call
    cmds.button(label="Create", command=onCreateClick)
    cmds.button(label="Randomize", command=onRandomClick)
    
    
    
    


# The *args captures any arguments received by this function
# The buttons send an extra argument that we don't care about
# so *args stores it and we can just ignore it
def onCreateClick(*args):
    # First we check the radio collection to see which radio button is selected
    radio = cmds.radioCollection("objectCreationType", query=True, select=True)
    # Then we use the radio button to see what its text says to get its value
    mode = cmds.radioButton(radio, query=True, label=True)

    # We also get the value of the integer field
    numObjects = cmds.intField("numObjects", query=True, value=True)

    # We then create our objects using the values we just got
    createObjects(mode, numObjects)
    # Finally we call the onRandomClick function to randomize the items
    onRandomClick()

def onRandomClick(*args):
    radio = cmds.radioCollection("randomMode", query=True, select=True)
    mode = cmds.radioButton(radio, query=True, label=True)

    # For each axis we get its range values and then call the randomize function with that data
    for axis in 'xyz':
        val = cmds.floatField("%sAxisField" % axis, query=True, value=True)
        randomize(minValue=val*-1, maxValue=val, mode=mode, axes=axis)

def createObjects(mode, numObjects=5):
    """This creates objects. Supports Cubes, Spheres, Cylinder and Cones"""
    # Create an empty list to keep track of the objects we create
    objList = []
    for n in range(numObjects):
        # Here we check if the mode is equal to a value
        if mode == 'Cube':
            # If it's equal to Cube, then create a cube and store it in the obj variable
            obj = cmds.polyCube()
        elif mode == 'Sphere':
            # We can have multiple conditions
            obj = cmds.polySphere()
        elif mode == "Cylinder":
            obj = cmds.polyCylinder()
        elif mode == 'Cone':
            obj = cmds.polyCone()
        else:
            # And if no conditions are met we can error
            cmds.error("I don't know what to create")
        
        # Finally we just want to store the first item in the obj variable inside our objList
        # We add to the objList by using the append method on it.
        objList.append(obj[0])
    
    # Finally we select the objects we created
    cmds.select(objList)

    # Functions can also return values, that is give something back
    # This is how we get values from the polyCube() function
    # Our function will return a list of the objects we created
    return objList


def randomize(objList=None, minValue=0, maxValue=10, axes='xyz', mode='Absolute'):
    # First we check if no object list is given
    if objList is None:
        # If it's not given, we'll default to using the current selection
        objList = cmds.ls(selection=True)
    
    # Then we'll loop through all the objects
    for obj in objList:
        # And for each object we'll loop through the given axes
        for axis in axes:
            # We store the current value so we can add on to it if using relative mode
            current = 0
            if mode == 'Relative':
                # '%s.t%s' % (obj,axis) is using string substitution
                # It is the same as saying
                # obj + '.t' + axis
                # e.g '%s.t%s' % ('polyCube1','x') gives us 'polyCube1.tx'
                # It is an efficient way to make strings from other values
                current = cmds.getAttr('%s.t%s' % (obj,axis))
            
            # random.uniform gives us back a random float value between our given range
            val = current + random.uniform(minValue, maxValue)
            cmds.setAttr('%s.t%s' % (obj,axis), val)
>>>>>>> ab16a6bb4ce2903ffc7b5dd3d52fa7dffddc975d
