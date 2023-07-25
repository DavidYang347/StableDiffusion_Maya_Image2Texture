1.  在 def addImageToCompositeShader(shader, color, alpha): 方法中，更改 "Facing Ratio", "Distance", "Vignette" 的默认参数。
    每次bake材质时，只bake出projection camera 中alpha map通道值不为0的材质。对于当前相机看不到的模型部分，材质为黑色。
    参数设置如下：

    mc.setAttr("%s.red[0].red_Position" % remapColor, 0)
    mc.setAttr("%s.red[1].red_Position" % remapColor, 0.3)
    #mc.setAttr("%s.red[0].red_FloatValue" % remapColor, 1 if firstConnection else 0)
    mc.setAttr("%s.red[0].red_FloatValue" % remapColor, 0)
    mc.setAttr("%s.red[1].red_FloatValue" % remapColor, 1)
    

    mc.setAttr("%s.green[0].green_Position" % remapColor, 0)
    mc.setAttr("%s.green[1].green_Position" % remapColor, 0.5)
    #mc.setAttr("%s.green[0].green_FloatValue" % remapColor, 1 if firstConnection else 0)
    mc.setAttr("%s.green[0].green_FloatValue" % remapColor, 1)
    mc.setAttr("%s.green[1].green_FloatValue" % remapColor, 1)

    mc.setAttr("%s.blue[0].blue_Position" % remapColor, 0)
    mc.setAttr("%s.blue[1].blue_Position" % remapColor, 0.5)
    #mc.setAttr("%s.blue[0].blue_FloatValue" % remapColor, 1 if firstConnection else 0)
    mc.setAttr("%s.blue[0].blue_FloatValue" % remapColor, 1)
    mc.setAttr("%s.blue[1].blue_FloatValue" % remapColor, 1)

2.  一键生成不同完整的贴图材质。在sd中生成四视图，保证不同角度的材质风格细节一致，再将四视图分别project 并merge 到模型中。
 Latent Space Projection
    1.  选择当前显示材质，是depth还是normal
    2. 设置相机位置，生成depth/normal map shader角度1
    3. 更改相机位置，旋转一定的角度（可以是90度），生成depth/normalmap shader角度2
    4. 生成四张角度图，用PIL将4张图拼到一起，生成四视图
    5. 将四视图作为custom image输入controlnet，生成latent space image
    （注意要保证输入的depth/normal 四视图和controlnet 输出的四视图的像素要一致，否则会导致stable diffusion生成不理想的图片）
    6. 将生成的图片分别裁切成四张不同角度的图片
    7. 用四张图片分别进行projection：load projection image -> set as projection -> bake projection on all. 重复以上操作四次
    
    
