import os
import json
import psd_tools
from PIL import Image
def process_mockup_package(zipName,dirName):
    os.system("unzip " + os.path.join(dirName,zipName) + " -d " + dirName)
    spuDesignDir = os.path.join(dirName,zipName.split(".")[0])
    spuName = os.path.join(dirName,zipName.split("_")[0]) # spu_design.zip
    spuName_ori = zipName.split("_")[0]
    spuMockupPrefix = os.path.join(spuName,"people")
    if os.path.exists(spuName) is not True:
        os.makedirs(spuMockupPrefix)

    # parse psd
    psd_config_lst = []
    for filename in os.listdir(spuDesignDir):
        if "psd" in filename:
            psd_config = parse_psd(os.path.join(spuDesignDir,filename),spuMockupPrefix)
            psd_config_lst.append(psd_config)

    # copy ori points img
    os.system("cp " + os.path.join(spuDesignDir,"ori") + " " + spuMockupPrefix + " -r")

    
    # generate config
    config = parse_generate_config(psd_config_lst)
    with open(os.path.join(spuName,'config.json'), 'w') as f:
        json.dump(config, f)
    os.chdir('data')
    os.system("zip " + spuName_ori + ".zip " + spuName_ori + " -r")

def parse_psd(filename,prefix):
    psd = psd_tools.PSDImage.open(filename)
    viewname = filename.split("/")[-1].split(".")[0]
    view_order_dict = {"front":1,"back":2,"left":3,"right":4}
    order_dict = {layer.name:i for i,layer in enumerate(reversed(psd)) if "base" not in layer.name and "1" != layer.name}
    config = {"mockupName":viewname,
              "mask":"1.png",
              "transformation":"2.png",
              "base":"base.png",
              "orderNum":view_order_dict[viewname.lower()],
              "componentList":[]
             }
    
    for layer in psd:
        if layer.name == "1":continue
            
        if layer.is_group():
            if "base" not in layer.name:
                config['componentList'].append({
                    "componentName":layer.name.split("_")[0],
                    "canvasName":"_".join(layer.name.split("_")[1:]),
                    "overlayNum":order_dict[layer.name]
                })
            
            for c_layer in layer:
                new_im = Image.new("RGBA",(1200,1200),(255,255,255,0))
                layer_im = c_layer.compose()
                x1,y1,x2,y2 = c_layer.bbox
                new_im.paste(layer_im,(x1,y1),layer_im)
                if "base" in layer.name:
                    path = os.path.join(prefix,viewname)
                else:
                    path = os.path.join(prefix,viewname,layer.name.split("_")[0])
                if os.path.exists(path) == False:
                    os.makedirs(path)
                new_im.save(path + "/" + c_layer.name + ".png")

    return config

def parse_generate_config(psd_dict):
    config = {
        "version":"1.0.0",
        "mockupGroupList":[
            {
                "groupName":"people",
                "originalPoints":"people/ori",
                "orderNum":1,
                "mockupList":[]
            }
        ]
    }
    for d in psd_dict:
        config["mockupGroupList"][0]["mockupList"].append(d)
    return config
    
if __name__ == '__main__':
    process_mockup_package("F100_deisgn.zip")
