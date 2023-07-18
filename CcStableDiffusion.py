'''
SCRIPT NAME: CcStableDiffusion
AUTHOR: Cody Childress
VERSION: 0.1                                                                 
DESCRIPTION: Stable Diffusion in Maya using Dream Studio's API
INSTALLING: 
USING: insert youtube link here
    
LICENSE:    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.


SETUP INSTRUCTIONS

    open command prompt and run this:

    WINDOWS USERS:
    "C:\Program Files\Autodesk\Maya2022\bin\mayapy.exe" -m pip install stability-sdk

    MAC USERS:
    /Applications/Autodesk/maya2023/Maya.app/Contents/bin/mayapy -m pip install stability-sdk

    To get your API key, visit https://beta.dreamstudio.ai/membership

    for step by step detailed instructions check out this video by Evan Atherton: https://www.youtube.com/watch?v=zKBCbUq52j0&list=LL&index=1


'''

from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

import getpass
import os
import io
import warnings

#import pymel.core as pm
from maya import cmds
import random

class CcStableDiffusion():

    def __init__(self):
        # settings
        floating = 0 # 0=docked 1=floating
        defaultDockArea = 'left' # // "top", "left", "bottom", "right";
        blankLine = 15
        blankLineStyle = 'in'

        #define our GUI window
        title = 'StableDiffusionMaya'
        win = 'StableDiffusionMaya'
        dock = win +'dock'

        #check if the window exists and delete it if it does
        if (cmds.window(win, exists=True)):
            cmds.deleteUI(win);
        if ( cmds.dockControl(dock, exists=True)):
            cmds.deleteUI(dock);

        #define the GUI window
        self.win = cmds.window(win, width=212, height=256, menuBar=True, sizeable=True, title=title)
        cmds.menu(label='Help', tearOff=True)
        cmds.menuItem(label='Instructions', c=self.ccScriptInstructions)
        cmds.menuItem(divider=True)
        cmds.menuItem(label='About', c=self.ccAbout)
        cmds.setParent("..")

        # column layout
        cmds.columnLayout(cal='center')

        cmds.button( label='Dream Studio website', height=25, width=400, command='cmds.launch(web= "https://beta.dreamstudio.ai/membership")')
        cmds.button( label='Set API key', height=25, width=400, command=self.CcSetAPIKey)

        self.promptField = cmds.textFieldGrp( label='prompt', text='south park character by greg rutkowski' )
        self.widthField = cmds.intFieldGrp( numberOfFields=1, label='width', extraLabel='pixels', value1=512 )
        self.heightField = cmds.intFieldGrp( numberOfFields=1, label='height', extraLabel='pixels', value1=512 )
        self.cfgScaleField = cmds.intFieldGrp( numberOfFields=1, label='cfg scale', extraLabel='pixels', value1=8 )

        self.samplerField = cmds.optionMenuGrp(label='sampler')
        cmds.menuItem( label='k_lms' )       
        cmds.menuItem( label='dim' )
        cmds.menuItem( label='plms' )
        cmds.menuItem( label='k_euler' )
        cmds.menuItem( label='k_euler_ancestral' )
        cmds.menuItem( label='k_heun' )
        cmds.menuItem( label='k_dpm_2' )
        cmds.menuItem( label='k_dpm_2_ancestral' )
     
        self.stepsField = cmds.intFieldGrp( numberOfFields=1, label='steps', value1=50 )
        self.randomizeSeedCheckBox = cmds.checkBox( label='randomize seed' )
        self.seedField = cmds.intFieldGrp( numberOfFields=1, label='seed', value1=12345 )
        self.numSamplesField = cmds.intFieldGrp( numberOfFields=1, label='num_samples', value1=40 )
        self.nameField = cmds.textFieldGrp( label='image name', text='image_name' )
        self.appendPromptToNameCheckBox = cmds.checkBox( label='append prompt to image name' )
        self.appendSeedToNameCheckBox = cmds.checkBox( label='append seed to image name' )

        cmds.button( label='Generate', height=50, width=400, command=self.CcGenerateImage )
        cmds.button( label='Buy me a coffee <3', height=30, width=200, command='cmds.launch(web= "https://www.buymeacoffee.com/codychildress")' )

        # end contents 
        # show & dock window
        cmds.showWindow (win)
        cmds.dockControl(dock, area=defaultDockArea, floating=floating, content=win, allowedArea= 'left', label=title) # allowedArea='right'

    def CcGenerateImage(self, *args):
        selection = []
        selection = cmds.ls(selection=True, dag=True, type="mesh", noIntermediate=True)

        _input_prompt = cmds.textFieldGrp(self.promptField, query=True, text=True)
        _height = cmds.intFieldGrp(self.heightField, query=True, value1=True)
        _width = cmds.intFieldGrp(self.widthField, query=True, value1=True)
        _cfgScale = cmds.intFieldGrp(self.cfgScaleField, query=True, value1=True)
        #_sampler = cmds.intFieldGrp(self.samplerField, query=True, value=True)
        _steps = cmds.intFieldGrp(self.stepsField, query=True, value1=True)
        _randomizeSeed = cmds.checkBox(self.randomizeSeedCheckBox, query=True, value=True)
        _seed = cmds.intFieldGrp(self.seedField, query=True, value1=True)

        if _randomizeSeed:
            _seed = random.randrange(1,99999999) 

        _numSamples = cmds.intFieldGrp(self.numSamplesField, query=True, value1=True)

        image_dir = pm.workspace(fileRuleEntry='sourceImages')
        image_dir = pm.workspace(expandName=image_dir)

        _appendPromptToName = cmds.checkBox(self.appendPromptToNameCheckBox, query=True, value=True)
        _appendSeedToName = cmds.checkBox(self.appendSeedToNameCheckBox, query=True, value=True)

        image_name = cmds.textFieldGrp(self.nameField, query=True, text=True)
        image_name = image_name.replace(" ", "_")

        if _appendPromptToName:
            cleanedPromptString = _input_prompt.replace(" ", "_")
            image_name = image_name + cleanedPromptString
        if _appendSeedToName:
            image_name = image_name + str(_seed)
        image_name = image_name + ".png"

        if len(selection) < 1:
            selection = cmds.polyPlane(width=_width, height=_height, subdivisionsX=1, subdivisionsY=1, axis=(0, 1, 0), createUVs=2, constructionHistory=True)
            cmds.setAttr(selection[0]+'.rotate', 90, 0, 0, type='double3')
            self.CcApplyTexture(self.nameField)
            selection = cmds.ls(selection=True, dag=True, type="mesh", noIntermediate=True)

        _fileNode = self.CcGetFileNode()
        _fileNode = _fileNode + ".fileTextureName"

        stability_api = client.StabilityInference(key=os.environ['STABILITY_KEY'], verbose=True)

        # the object returned is a python generator
        answers = stability_api.generate(
            prompt=_input_prompt,
            height=_height,
            width=_width,
            cfg_scale=_cfgScale,
            # sampler=_sampler,
            steps=_steps, # defaults to 50 if not specified
            seed=_seed, # if provided, specifying a random seed makes results deterministic
            # num_samples=_numSamples,            

        )

        # iterating over the generator produces the api response
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save(fp=os.path.join(image_dir, image_name))
                   
        pm.setAttr(_fileNode, image_name)


    def CcGetFileNode(self, *args):
        shapesInSel = cmds.ls(dag=1,o=1,s=1,sl=1)
        shadingGrps = cmds.listConnections(shapesInSel,type='shadingEngine')
        shaders = cmds.ls(cmds.listConnections(shadingGrps),materials=1)
        fileNode = cmds.listConnections((shaders[0]), type='file') #use .baseColor for Arnold shaders!
        return fileNode[0]


    def CcApplyTexture(self, *args):
        # object = [] 
        object = cmds.ls(sl=True)
        
        #create surface shader and shading group
        imgMaterialGrp = cmds.sets(name='imageMaterialGroup', renderable=True, empty=True)
        shaderNode = cmds.shadingNode('surfaceShader', name='SD_shaderNode', asShader=True)
        
        #construct name for file node
        image_name = cmds.textFieldGrp(self.nameField, query=True, text=True)
        image_name = image_name.replace(" ", "_")
        image_name = image_name + 'fileTexture'

        #create file node
        fileNode = cmds.shadingNode('file', name=image_name, asTexture=True)

        #create shading group, connect surface shader to shading group
        shadingGroup = cmds.sets(name='textureMaterialGroup', renderable=True, empty=True)
        cmds.connectAttr(shaderNode+'.outColor',shadingGroup+'.surfaceShader', force=True) 

        #connect file node to surface shader
        cmds.connectAttr(fileNode+'.outColor',shaderNode+'.outColor', force=True)
        cmds.surfaceShaderList(shaderNode, add=imgMaterialGrp) 
        cmds.sets(object, e=True, forceElement=imgMaterialGrp) 
        cmds.select(object, replace=True)


    def ccScriptInstructions(self, *args):

        title1 = 'Instructions'
        win1 = 'instructionsWin'

        if(cmds.window(win1, exists=True)):
            cmds.deleteUI(win1)
            
        cmds.window(win1, width=150, title=title1)
        cmds.columnLayout (adjustableColumn=True)
        cmds.text(label='Script instructions')
        cmds.showWindow(win1)

    def ccAbout(self, *args):

        title1 = 'About'
        win1 = 'aboutWin'
        
        if (cmds.window(win1, exists=True)):
            cmds.deleteUI(win1)

        cmds.window(win1, width=150, title=title1) 
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Created by Cody Childress 2022 \n \n Contact \n email: codyrchildress@gmail.com \n \nMore info at \n')
        cmds.button(label='www.codychildress.com', command= 'cmds.launch(web= "www.codychildress.com")')
        cmds.showWindow(win1);    

    def CcSetAPIKey(self, *args):
        # To get your API key, visit https://beta.dreamstudio.ai/membership
        os.environ['STABILITY_KEY'] = getpass.getpass('Enter your API Key')


CcStableDiffusion()

