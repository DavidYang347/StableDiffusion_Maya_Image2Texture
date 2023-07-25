
from cgm.lib import files
import maya.cmds as mc
import maya.mel as mel

import cgm.core.tools.Project as PROJECT
from cgm.tools.stableDiffusion import stableDiffusionTools as sd
from cgm.tools.stableDiffusion import renderTools as rt
from cgm.tools.stableDiffusion import generateImage as gi
from cgm.tools.stableDiffusion import stableDiffusionUI as sdui
from cgm.tools import imageViewer as iv
from cgm.tools import imageTools as it

import os
import base64
import traceback
from PIL import Image, ImageFilter
from io import BytesIO
import logging

output_path = os.path.normpath(os.path.join(PROJECT.getImagePath(), "four_view"))
#output_path = "C:\\Users\\19814\\Desktop\\Image2Texture\\babyYodaRig_v008\\scenes\\images\\sd_output\\lantent_space_image_1.png"
output_filename = "four_view_1.png"
camera_name = "cgmProjectionCamera1" 
fourview_image_path = None


#------------------
# generate latent space image. Main function in button 
#------------------

def getLetentDepthMap(self):
    rotation_angle = [0,0,0,0]
    rotation_angle[0] = self.uiFourView_angle1(query=True, value=True)
    rotation_angle[1] = self.uiFourView_angle2(query=True, value=True)
    rotation_angle[2] = self.uiFourView_angle3(query=True, value=True)
    rotation_angle[3] = self.uiFourView_angle4(query=True, value=True)
    
    index = 0
    for i in range(4):
        rotate_camera_around_origin(camera_name,rotation_angle[i])
        renderAndSaveImage(self, index)
        index = index + 1
    
    composeImage(self)
    print("output materialpass image")

def generateFourViewImage(self):
    generateImage(self)
    
def BakeAndMerge(self):
    
    bgColor = self.bakeAndProjectionBt(q=True, bgc=True)
    origText = self.bakeAndProjectionBt(q=True, label=True)
    setButtonProperties(self.bakeAndProjectionBt, False, "Generating...", (1, 0.5, 0.5))
    
    paths = LoadImage(self)
    if paths:
        projectionAndBake(self,paths)
        setButtonProperties(self.bakeAndProjectionBt, True, origText, bgColor)
    else:
        setButtonProperties(self.bakeAndProjectionBt, True, origText, bgColor)
    

#------------------
# useful little function
#------------------
def rotate_camera_around_origin(camera_name, rotation_angle):
    mc.select(camera_name)
    mc.rotate(0, rotation_angle, 0, relative=True, pivot=(0, 0, 0))

def renderAndSaveImage(self, index,display=True, ):
    _str_func = "uiFunc_renderImage"
    
    outputImage = renderMaterialPass(
        camera=self.uiTextField_projectionCamera(q=True, text=True),
        resolution=self.resolution,     
    )
    
    if display:
       iv.ui([outputImage], {"outputImage": outputImage})
       
    # save image
    output_path_fourview = os.path.normpath(os.path.join(PROJECT.getImagePath(), "fourview_output"))
    output_name_fourview = output_path_fourview + "_materialpass_" +str(index) + ".png"
    #output_name_fourview = files.create_unique_filename(output_name_fourview)
    image = Image.open(outputImage)
    image.save(output_name_fourview, "PNG")

    return outputImage

def composeImage(self, display=True):
    output_path_fourview = os.path.normpath(os.path.join(PROJECT.getImagePath(), "fourview_output"))
    output_name_fourview_compose = output_path_fourview + "_materialpass_compose" + ".png"
    image = []
    
    for i in range(4):
        image_path = output_path_fourview + "_materialpass_" +str(i) + ".png"
        image_file = Image.open(image_path)
        image.append(image_file)
        
    width, height = image[0].size
    
    #result_width = width * 2
    #result_height = height * 2
    result_width = width * 4

    result_image = Image.new("RGBA", (result_width, height))
    
    '''result_image.paste(image[0], (0, 0))
    result_image.paste(image[1], (width, 0))
    result_image.paste(image[2], (0, height))
    result_image.paste(image[3], (width, height))'''
    
    result_image.paste(image[0], (0, 0))
    result_image.paste(image[1], (width, 0))
    result_image.paste(image[2], (width * 2, 0))
    result_image.paste(image[3], (width * 3, 0))
    
    result_image.save(output_name_fourview_compose)
    
    if display:
        iv.ui([output_name_fourview_compose], {"outputImage": output_name_fourview_compose})

def divideImage(filepath):
    output_path_fourview = os.path.normpath(os.path.join(PROJECT.getImagePath(), "fourview_output"))
    #output_name_fourview_compose = output_path_fourview + "_materialpass_compose" + ".png"
    output_name_fourview_divide = output_path_fourview + "_controlNet__divide_"
    original_image = Image.open(filepath)
    
    width, height = original_image.size
    #split_width = width // 2
    #split_height = height // 2

    '''image1 = original_image.crop((0, 0, split_width, split_height))
    image2 = original_image.crop((split_width, 0, width, split_height))
    image3 = original_image.crop((0, split_height, split_width, height))
    image4 = original_image.crop((split_width, split_height, width, height))'''
    
    split_width = width // 4
    image1 = original_image.crop((0, 0, split_width, height))
    image2 = original_image.crop((split_width, 0, split_width * 2, height))
    image3 = original_image.crop((split_width*  2, 0, split_width * 3, height))
    image4 = original_image.crop((split_width * 3, 0, width, height))
    
    images = [image1, image2,image3,image4]
    images_paths = []
    for i in range(4):
        images[i].save(output_name_fourview_divide + str(i) + ".png")
        images_paths.append(output_name_fourview_divide + str(i) + ".png")
    
    return images_paths

def saveImageToFile(imagePaths):
    
    # save image to file
    output_path_fourview = os.path.normpath(os.path.join(PROJECT.getImagePath(), "fourview_output"))
    output_name_fourview = output_path_fourview + "_controlNet_compose" + ".png"
    for i in range(len(imagePaths)-1):
        image = Image.open(imagePaths[i])
        output_name_fourview = files.create_unique_filename(output_name_fourview)
        image.save(output_name_fourview, "PNG")
        
        
def LoadImage(self):
    _str_func = "uiFunc_loadProjectionImage"
    # use fileDialog2 to choose image in window
    _path = mc.fileDialog2(
        fileFilter="Image Files (*.jpg *.jpeg *.png *.exr *.tif *.tiff)",
        dialogStyle=2,
        fileMode=1,
        caption="Select Image File",
        dir=PROJECT.getImagePath(),
    )
    if not _path:
        return

    _path = _path[0]
    paths = divideImage(_path)
    
    return paths

    
def projectionAndBake(self, paths):
    rotation_angle = [0,0,0,0]
    rotation_angle[0] = self.uiFourView_angle1(query=True, value=True)
    rotation_angle[1] = self.uiFourView_angle2(query=True, value=True)
    rotation_angle[2] = self.uiFourView_angle3(query=True, value=True)
    rotation_angle[3] = self.uiFourView_angle4(query=True, value=True)
    
    for i in range(len(paths)):
        rotate_camera_around_origin(camera_name,rotation_angle[i])
        self.assignImageToProjection(paths[i], {})
        self.uiFunc_bakeProjection()
    

    
#------------------
# generate image Function
#------------------

def renderMaterialPass(
    material=None,
    meshes=None,
    fileName="temp_materialpass",
    format="png",
    camera=None,
    resolution=None,
):
    # print("renderMaterialPass(%s, %s, %s, %s, %s)" % (material, meshObj, fileName, asJpg, camera))

    output_path = os.path.normpath(os.path.join(PROJECT.getImagePath(), "Temp_Image"))
    #tmpdir = tempfile.TemporaryDirectory().name
    log.debug(f"Created temporary directory: {output_path}")

    currentResolution = [
        mc.getAttr("defaultResolution.width"),
        mc.getAttr("defaultResolution.height"),
    ]

    pAx = mc.getAttr("defaultResolution.pixelAspect")
    pAr = mc.getAttr("defaultResolution.deviceAspectRatio")
    al = mc.getAttr("defaultResolution.aspectLock")

    if resolution != None:
        mc.setAttr("defaultResolution.aspectLock", 0)
        mc.setAttr("defaultResolution.width", resolution[0])
        mc.setAttr("defaultResolution.height", resolution[1])
        mc.setAttr("defaultResolution.pixelAspect", pAx)
        mc.setAttr("defaultResolution.deviceAspectRatio", pAr)
        mc.refresh()
    else:
        resolution = currentResolution

    wantedName = os.path.join(output_path, "RenderPass")

    if material:
        # assign depth shader
        sg = mc.listConnections(material, type="shadingEngine")
        if sg:
            sg = sg[0]

        if sg and meshes:
            for meshObj in meshes:
                rt.assignMaterial(meshObj, sg)
        else:
            log.warning("No shading group or meshes found for material %s" % material)

        wantedName = os.path.join(output_path, material)

    if fileName:
        wantedName = os.path.join(output_path, fileName)

    # setAttr "defaultRenderGlobals.imageFormat" 8;
    currentImageFormat = mc.getAttr("defaultRenderGlobals.imageFormat")
    currentFilenamePrefix = mc.getAttr("defaultRenderGlobals.imageFilePrefix")

    if format.lower() == "jpg" or format.lower() == "jpeg":
        mc.setAttr("defaultRenderGlobals.imageFormat", 8)
    elif format.lower() == "png":
        mc.setAttr("defaultRenderGlobals.imageFormat", 32)

    # mc.setAttr("defaultRenderGlobals.imageFilePrefix", wantedName, type="string")
    # outputFileName = mc.renderSettings(fullPathTemp=True, firstImageName=True)

    uniqueFileName = files.create_unique_filename(wantedName)

    log.debug("uniqueFileName: %s" % uniqueFileName)

    mc.setAttr("defaultRenderGlobals.imageFilePrefix", uniqueFileName, type="string")

    if camera:
        cameras = mc.ls(type="camera")

        # iterate through the cameras and set them to not be renderable
        for renderCam in cameras:
            if renderCam == camera:
                mc.setAttr(renderCam + ".renderable", 1)
            else:
                mc.setAttr(renderCam + ".renderable", 0)

    imagePath = mc.render(batch=False, rep=True, x=resolution[0], y=resolution[1])

    log.debug("currentFilenamePrefix: %s" % currentFilenamePrefix)
    mc.setAttr("defaultRenderGlobals.imageFormat", currentImageFormat)
    mc.setAttr(
        "defaultRenderGlobals.imageFilePrefix",
        currentFilenamePrefix or "",
        type="string",
    )
    mc.setAttr("defaultResolution.aspectLock", al)
    mc.setAttr("defaultResolution.width", currentResolution[0])
    mc.setAttr("defaultResolution.height", currentResolution[1])
    mc.setAttr("defaultResolution.pixelAspect", pAx)
    mc.setAttr("defaultResolution.deviceAspectRatio", pAr)

    log.debug("Rendered material pass, %s, %s" % (material, imagePath))
    return imagePath



logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def generateImage(self, display=True):
    _str_func = "generateImage.generateImageFromUI"

    meshes, camera = getMeshesAndCamera(self)

    bgColor = self.fourViewGenerateBt(q=True, bgc=True)
    origText = self.fourViewGenerateBt(q=True, label=True)
    setButtonProperties(self.fourViewGenerateBt, False, "Generating...", (1, 0.5, 0.5))

    mc.refresh()

    _options = self.getOptions()  

    # standardize the output path
    output_path = os.path.normpath(os.path.join(PROJECT.getImagePath(), "sd_output"))
    _options["output_path"] = output_path
    
    # give values of width and height
    width = self.uiFourView_Width(query=True, value=True)
    height = self.uiFourView_Height(query=True, value=True)
    _options["width"] = width
    _options["height"] = height
    self.saveOption("width", width)
    self.saveOption("height", height)
    
    
    ocgt_processImg2Img(self, meshes, camera, _options)
    ocgt_processControlNets(self, meshes, camera, _options)
    ocgt_processAlphaMatte(self, meshes, camera, _options)

    cameraInfo = getCameraInfo(camera)

    return getImageAndUpdateUI(self, _options, cameraInfo, origText, bgColor, display)


def displayImage(imagePaths, data={}, callbackData=[]):
    log.debug(f"Displaying images: {imagePaths}")
    iv.ui(imagePaths, data, callbackData)
    
def getMeshesAndCamera(self):
    _str_func = "generateImage.getMeshesAndCamera"

    meshes = self.uiList_projectionMeshes(q=True, allItems=True)
    camera = self.uiTextField_projectionCamera(q=True, text=True)

    if not camera:
        log.warning("|{0}| >> No camera loaded.".format(_str_func))

    if meshes is None or len(meshes) == 0:
        log.warning("|{0}| >> No meshes loaded.".format(_str_func))
    
    return meshes, camera

def setButtonProperties(button, state, label=None, bgColor=None):
    button(edit=True, enable=state)
    if label is not None:
        button(edit=True, label=label)
    button(edit=True, bgc=bgColor)
    
def ocgt_processImg2Img(self, meshes, camera, _options):
    _str_func = "generateImage.processImg2Img"

    option = _options["img2img_pass"].lower()
    log.debug("img2img_pass {0}".format(option))

    if option != "none":
        if option == "composite" or option == "merged":          
            self.uiFunc_assignMaterial(option, meshes)

            scaleMult = float(self.uiOM_img2imgScaleMultiplier.getValue())
            wantedResolution = (
                self.resolution[0] * scaleMult,
                self.resolution[1] * scaleMult,
            )

            log.debug(
                "rendering composite image at resolution {0}".format(
                    wantedResolution
                )
            )
            composite_path = rt.renderMaterialPass(
                camera=camera, resolution=wantedResolution
            )

            log.debug("composite path: {0}".format(composite_path))

            _options["init_images"] = [iv.encodeImageToString(composite_path)]

        elif option == "custom":
            custom_image = self.uiTextField_customImage(query=True, text=True)
            log.debug("custom image: {0}".format(custom_image))
            
            if os.path.exists(custom_image):
                with open(custom_image, "rb") as c:
                    # Read the image data
                    composite_data = c.read()

                    # Encode the image data as base64
                    composite_base64 = base64.b64encode(composite_data)

                    # Convert the base64 bytes to string
                    composite_string = composite_base64.decode("utf-8")

                    c.close()

                _options["init_images"] = [composite_string]
        elif option == "render layer":
            outputImage = self.uiFunc_renderLayer(display=False)
            log.debug("render layer: {0}".format(outputImage))

            if outputImage:
                _options["init_images"] = [iv.encodeImageToString(outputImage)]

def ocgt_processControlNets(self, meshes, camera, _options):
    _str_func = "generateImage.processControlNets"
    output_path_fourview = os.path.normpath(os.path.join(PROJECT.getImagePath(), "fourview_output"))
    output_name_fourview = output_path_fourview + "_materialpass_compose" + ".png"

    # Get Control Nets
    for i in range(3):
        _controlNetOptions = _options['control_nets'][i]

        if True:
            control_net_image_path = output_name_fourview
            if True:
                control_net_image_path = self.controlNets[i]['custom_image_tf'].getValue()
            
            if os.path.exists(control_net_image_path):
                _controlNetOptions["control_net_image"] = it.encodeImageToString(control_net_image_path)


        _options['control_nets'][i] = _controlNetOptions


def getImageAndUpdateUI(self, _options, cameraInfo, origText, bgColor, display=True):
    try:            
        imagePaths, info = sd.getImageFromAutomatic1111(_options)

        log.debug(f"Generated: {imagePaths} {info}")

        if imagePaths:
            callbacks = []
            callbacks.append(
                {"label": "Make Plane", "function": rt.makeImagePlane}
            )
            callbacks.append(
                {
                    "label": "Set As Custom Image",
                    "function": self.setAsCustomImage,
                }
            )
            callbacks.append(
                {
                    "label": "Set As Projection",
                    "function": self.assignImageToProjection,
                }
            )

            if display:
                displayImage(imagePaths, info, callbacks)

        info["camera_info"] = cameraInfo

        self.lastInfo = info
   
        setButtonProperties(self.fourViewGenerateBt, True, origText, bgColor)
        
        # save image to file
        saveImageToFile(imagePaths)
        

        return imagePaths, info
    
    except Exception:
        # display full error in log
        e = traceback.format_exc()
        log.error(e)

        setButtonProperties(self.fourViewGenerateBt, True, origText, bgColor)

        return [], {"error": e}

def ocgt_processAlphaMatte(self, meshes, camera, _options):
    _str_func = "generateImage.processAlphaMatte"
    
    if _options["use_alpha_pass"] and _options["img2img_pass"] != "none" and meshes:
        self.uiFunc_assignMaterial("alphaMatte", meshes)

        alpha_path = rt.renderMaterialPass(
            fileName="AlphaPass", camera=camera, resolution=self.resolution
        )

        log.debug("alpha_path: {0}".format(alpha_path))

        if os.path.exists(alpha_path):
            # Read the image data
            alpha_image = Image.open(alpha_path)

            # Convert the image data to grayscale
            alpha_image_gray = alpha_image.convert("L")

            # Encode the image data as base64
            buffered = BytesIO()
            alpha_image_gray.save(buffered, format="PNG")

            alpha_base64 = base64.b64encode(buffered.getvalue())

            # Convert the base64 bytes to string
            alpha_string = alpha_base64.decode("utf-8")

            _options["mask"] = alpha_string
            _options["mask_blur"] = self.uiIF_maskBlur(query=True, value=True)
            _options["inpainting_mask_invert"] = 1
        else:
            log.warning("|{0}| >> No alpha matte found.".format(_str_func))

def getCameraInfo(camera):
    cameraInfo = {}
    if camera:
        cameraTransform = mc.listRelatives(camera, parent=True)[0]
        cameraInfo = {
            "position": mc.xform(cameraTransform, q=True, ws=True, t=True),
            "rotation": mc.xform(cameraTransform, q=True, ws=True, ro=True),
            "fov": mc.getAttr(camera + ".focalLength"),
        }
    return cameraInfo