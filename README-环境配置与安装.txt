环境配置与安装

一、安装sd webUI.(可以跟随b站教程安装：https://www.bilibili.com/video/BV1P84y1g7jS/?spm_id_from=333.337.search-card.all.click&vd_source=9d93ad1dedeec0e819f7f2ea1379fcc7)
1. 为sd webUI安装controlNet
2. 对sd webUI的bat 文件进行编辑，添加--api，使得其他软件可以调用sd webUI画图： set COMMANDLINE_ARGS= --xformers --no-half  --api 


二、安装maya的python开发者工具(maya的cmd库)：
1. 按照官方文档的说明安装maya.cmd：https://help.autodesk.com/view/MAYAUL/2022/CHS/?guid=Maya_SDK_Setting_up_your_build_Windows_environment_64_bit_html
2. （非必须）下载VScode或者pycharm编辑python代码
3. （非必须）设置mayapy作为python代码的解释器（https://www.bilibili.com/video/BV1Cz4y1R7MC/?spm_id_from=333.337.search-card.all.click&vd_source=9d93ad1dedeec0e819f7f2ea1379fcc7）
4. （非必须）在VScode的extension 中安装MEL - Maya Embedded Language库


三、安装2022 mayapy对应版本的numpy:
1. 控制台进入 C:\Program Files\Autodesk\Maya2022\bin
2. 输入mayapy.exe -m pip install numpy ; 运行以后，自动联网安装1.21.6版本的numpy
3. 在maya的bin文件（D:\Program Files\Autodesk\Maya2024\bin）中安装pillow，输入mayapy -m pip install pillow


四、将插件的压缩包解压以后，复制粘贴到以下maya的脚本文件夹中：
C:\Users\“此处替换为自己的用户名”\Documents\maya\2022\scripts

五、进入C:\Users\“此处替换为自己的用户名”\Documents\maya\2022\scripts\cgm\tools\stableDiffusion
      将OneClickGenerateTexture和stableDiffusionUI两个文件替换掉，就可以使用up主自己写的一键生成材质贴图的功能了


六、在maya的scripts editor中输入以下python代码，打开Image2Textrure的ui界面：

import sys
import imp

# 添加库的文件夹路径, 此文件夹为stableDiffusionUI.py所在文件夹
#注意在 Python 中，反斜杠（\）被用作转义字符，使用双反斜杠（\\）进行文件夹中的路径分隔：
library_folder = 'C:\\Users\\19814\\Documents\\maya\\2022\\scripts\\cgm\\tools\\stableDiffusion'

# 将文件夹路径添加到 sys.path
sys.path.append(library_folder)

# 导入插件，打开ui界面
import stableDiffusionUI
imp.reload(stableDiffusionUI)

ui_instance = stableDiffusionUI.ui()
ui_instance.show()


七、将上面的脚本文件保存为Custom中的自定义插件：
在scripts editor脚本编辑器中点击 Save scripts to Shelf...按钮，给插件命名为Image2Texture
这样以后每次打开maya，都可以直接点击Custome中的Image2Texture，快捷打开插件
，
