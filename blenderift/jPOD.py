#*!*********************************************************************************************************************
#\File         jPOD.py
#\Title        JSON POD
#\Author       PowerVR by Imagination, Developer Technology Team.
#\Copyright    Copyright (c) Imagination Technologies Limited.
#\Description  This script will generate a JSON file with a readable representation of a POD file.
#              Binary data will be expressed as an offset in bites in the original POD file. 
#***********************************************************************************************************************/
#!/usr/bin/python
import re
import os
import re
import sys
import shutil
import optparse
import struct
from SETTINGS import *
from functools import partial

blockID = {
# BlockID:["BlockName","dataType","NumElements],
    1000:["Version","s",1],
    1001:["Scene","",0],
    1002:["ExpOpt","o",1],
    1003:["History","s",1],
    1004:["EndiannessMisMatch","",0],

    2000:["ColourBackground","f",3],
    2001:["ColourAmbient","f",3],
    2002:["NumCamera","i",1],
    2003:["NumLight","i",1],
    2004:["NumMesh","i",1],
    2005:["NumNode","i",1],
    2006:["NumMeshNode","i",1],
    2007:["NumTexture","i",1],
    2008:["NumMaterial","i",1],
    2009:["NumFrame","i",1],
    2010:["Camera","",0],
    2011:["Light","",0],
    2012:["Mesh","",0],
    2013:["Node","",0],
    2014:["Texture","",0],
    2015:["Material","",0],
    2016:["Flags","x",1],
    2017:["FPS","i",1],
    2018:["UserData","s",1],
    2019:["Units","f",1],

    3000:["MatName","s",1],
    3001:["MatIdxTexDiffuse","i",1],
    3002:["MatOpacity","f",1],
    3003:["MatAmbient","f",3],
    3004:["MatDiffuse","f",3],
    3005:["MatSpecular","f",3],
    3006:["MatShininess","f",1],
    3007:["MatEffect","s",1],
    3008:["MatEffectName","s",1],
    3009:["MatIdxTexAmbient","i",1],
    3010:["MatIdxTexSpecularColour","i",1],
    3011:["MatIdxTexSpecularLevel","i",1],
    3012:["MatIdxTexBump","i",1],
    3013:["MatIdxTexEmissive","i",1],
    3014:["MatIdxTexGlossiness","i",1],
    3015:["MatIdxTexOpacity","i",1],
    3016:["MatIdxTexReflection","i",1],
    3017:["MatIdxTexRefraction","i",1],
    3018:["MatBlendSrcRGB","x",1],
    3019:["MatBlendSrcA","x",1],
    3020:["MatBlendDstRGB","x",1],
    3021:["MatBlendDstA","x",1],
    3022:["MatBlendOpRGB","x",1],
    3023:["MatBlendOpA","x",1],
    3024:["MatBlendColour","x",1],
    3025:["MatBlendFactor","x",1],
    3026:["MatFlags","x",1],
    3027:["MatUserData","s",1],
    # PBR Extension
    3028:["MatMetallicity","f",1],
    3029:["MatRoughness","f",1],
    3030:["MatIOR","f",1],
    3031:["MatFresnel","f",1],
    3032:["MatReflectivity","f",1],
    3033:["MatSSScattering","f",1],
    3034:["MatSSScateringDepth","f",1],
    3035:["MatSSScateringColor","f",3],
    3036:["MatEmission","f",1],
    3037:["MatEmissionLuminance","f",1],
    3038:["MatEmissionKelvin","f",1],
    3039:["MatAnisotropy","f",1],
    3040:["MatIdxTexMetallicity","i",1],
    3041:["MatIdxTexRoughness","i",1],

    4000:["TexName","s",1],

    5000:["NodeIdx","i",1],
    5001:["NodeName","s",1],
    5002:["NodeIdxMat","i",1],
    5003:["NodeIdxParent","i",1],
    5004:["NodePos","f",3],
    5005:["NodeRot","f",3],
    5006:["NodeScale","f",3],
    5007:["NodeAnimPos","fl",3],
    5008:["NodeAnimRot","fl",4],
    5009:["NodeAnimScale","fl",7],
    5010:["NodeMatrix","f",16],
    5011:["NodeAnimMatrix","fl",16],
    5012:["NodeAnimFlags","xl",1],
    5013:["NodeAnimPosIdx","il",1],
    5014:["NodeAnimRotIdx","il",1],
    5015:["NodeAnimScaleIdx","il",1],
    5016:["NodeAnimMatrixIdx","il",1],
    5017:["NodeUserData","s",1],

    6000:["MeshNumVtx","i",1],
    6001:["MeshNumFaces","i",1],
    6002:["MeshNumUVW","i",1],
    6003:["MeshFaces","",0],
    6004:["MeshStripLength","il",1],
    6005:["MeshNumStrips","i",1],
    6006:["MeshVtx","",0],
    6007:["MeshNor","",0],
    6008:["MeshTan","",0],
    6009:["MeshBin","",0],
    6010:["MeshUVW","",0],
    6011:["MeshVtxCol","",0],
    6012:["MeshBoneIdx","",0],
    6013:["MeshBoneWeight","",0],
    6014:["MeshInterleaved","Bl",1],
    6015:["MeshBoneBatches","il",1],
    6016:["MeshBoneBatchBoneCnts","il",1],
    6017:["MeshBoneBatchOffsets","il",1],
    6018:["MeshBoneBatchBoneMax","i",1],
    6019:["MeshBoneBatchCnt","i",1],
    6020:["MeshUnpackMatrix","f",16],
    6021:["MeshType","i",1],
    6022:["MeshAdjacencyIdx","il",6],

    7000:["LightIdxTgt","i",1],
    7001:["LightColour","f",3],
    7002:["LightType","i",1],
    7003:["LightConstantAttenuation","f",1],
    7004:["LightLinearAttenuation","f",1],
    7005:["LightQuadraticAttenuation","f",1],
    7006:["LightFalloffAngle","f",1],
    7007:["LightFalloffExponent","i",1],

    8000:["CamIdxTgt","i",1],
    8001:["CamFOV","f",1],
    8002:["CamFar","f",1],
    8003:["CamNear","f",1],
    8004:["CamAnimFOV","fl",1],

    9000:["DataType","i",1],
    9001:["N","i",1],
    9002:["Stride","i",1],
    9003:["Data","?l",1]
}

types = [ 
"",		#	0  none
"f",	#	1  signed 32bit float
"I",	#	2  unsigned 32bit integer
"H",	#	3  unsigned short
"x",	#	4  four, single byte integer values representing colour channels in the order RGBA
"x",	#	5  four, single byte integer values representing colour channels in the order ARGB
"x",	#	6  a 4 byte value representing a D3DCOLOR (see msdn.microsoft.com)
"x",	#	7  a 4 byte value representing UBYTE4
"x",	#	8  a 4 byte value representing a DEC3N
"p",	#	9  a 4 byte value representing a fixed point value in the format 16.16
"B",	#	10  unsigned byte
"h",	#	11  short
"h",	#	12  normalised short
"b",	#	13  byte
"b",	#	14  normalised byte
"B",	#	15  unsigned normalised byte
"H",	#	16  unsigned normalised short
"I", 	#	17  unsigned integer
"I", 	#	18  four, single byte integer values representing colour channels in the order ABGR
"t" 	#	19  half-float
]

storedType = 0
numN = 0

###################################################################
# Function: printData
# Description: 
###################################################################
def CloseBrackets(level, outputFile):
        outputFile.seek(outputFile.tell()-3) # go backwards two spaces to remove the last comma
        if level<1: outputFile.write("\n}\n")
        else: outputFile.write("\n"+"  "*(level-1)*2+"},\n")
###################################################################
# Function: printData
# Description: 
###################################################################
def processOptions(opt):

    eExpFormat = [ "ePOD", "eH", "eCPP" ]
    cS = [ "eMax", "eD3D", "eOGL" ]
    eTriSort = [ "eNone", "e590Blocks", "eD3DX", "ePVRTTriStrip", "ePVRTTriStripSlow"]
    ePrimType = [ "eList", "eStrip" ]
    dataType = ["None","Float","Int","UnsignedShort","RGBA","ARGB","D3DCOLOR","UBYTE4","DEC3N","Fixed16_16","UnsignedByte","Short","ShortNorm","Byte","ByteNorm","UnsignedByteNorm","UnsignedShortNorm","UnsignedInt","ABGR","HalfFloat"]
    channelVal = {0:"0",1:"x",2:"y",4:"z",8:"w"}
    channelSing = ["","-"]
    textureFormat = [ "ePVRTC_2bpp", "ePVRTC_4bpp", "ePVRTC2_2bpp", "ePVRTC2_4bpp", "eETC1", "eETC2", "eRGB565", "eRGBA4", "eRGBA8", "eRGBA16", "eRGBA32" ]

    name, value = opt.split("=")

    if "nEnable" in name:
        val = int(value)
        value = "["
        for i in range(0,4):
            sign = val>>(24+i) & 1
            enabled = val>>(0+i) & 1
            channel = val>>(20-i*4) & 15
            value = value + "\""+ channelSing[sign]+channelVal[channel]+"\""
            if i<3: value = value +","
        value = value +"]"

    if name[0] == 'b' or "bExport" in name: # boolean
        if value == "0": value = "false"
        else: value = "true"

    elif "eType" in name: value = "\""+dataType[int(value)]+"\""

    if name[0] == 's' and  name[1] != 'V': value = "\""+value+"\"" # String
    elif name == "eExpFormat": value = "\""+eExpFormat[int(value)]+"\""
    elif name == "cS": value = "\""+cS[int(value)]+"\""
    elif name == "eTriSort": value = "\""+eTriSort[int(value)]+"\""
    elif name == "ePrimType": value = "\""+ePrimType[int(value)]+"\""
    elif name == "eTextureFormat": value = "\""+textureFormat[int(value)]+"\""

    optOuput = "\""+name+"\": "+value
    return optOuput
###################################################################
# Function: printData
# Description: 
###################################################################
def printData(outputFile, level, id, data):
    global storedType
    global numN

    type = ""
    mod = ""
    numGroups = 1
    numElements = blockID[id][2]

    if len(blockID[id][1])>0: type = blockID[id][1][0]
    if len(blockID[id][1])>1: mod = blockID[id][1][1]

    if (type == '?'):
        type = types[storedType]
        numElements = numN

    structType = type
    if (type == "x"): structType = "i"
    if (type == "p"): structType = "i"
    if (type == "t"): structType = "H"

    if (type == "s"):
        l = len(data)-1 # remove last character
        outputFile.write("\""+str(data[:l])+"\",\n" )
        return

    if (type == "o"): # Options are split to be readable
        outputFile.write("{\n")
        options = re.findall('[a-zA-Z]+[*[0-9]*]*\.*[a-zA-Z]*=[0-9]*', str(data))
        for opt in options:
            opt = processOptions(opt)
            outputFile.write("  "+opt+",\n")
        CloseBrackets(1, outputFile)
        return

    if (mod == "l" and struct.calcsize(structType)>0 and numElements>0):
        numGroups = len(data)/(struct.calcsize(structType)*numElements) # list

    stride  = 0

    for j in range (0,numGroups):
        if (len(data) < struct.calcsize(structType)): continue # Avoid error when trying to read data blocks without data
        if (numElements>1): outputFile.write ("[")
        for i in range (0,numElements):
            strVal = ""
            val = struct.unpack_from(structType, data, stride)[0]
            stride = stride + struct.calcsize(structType)
            if (id == 9000): storedType = val
            if (type == "p"):
                valf = float(val)/65536.0
                strVal ='%f'%valf + ","
            elif (type == "f"):
                strVal = '%f'%val + ","
            else:
                strVal = str(val) + ","
            if (numElements>1 and i==numElements-1): strVal = strVal.replace(",","],") # remove the last comma
            outputFile.write(strVal)

        if (j<numGroups-1 and numElements>1):
            outputFile.write ("/n")

    outputFile.write ("\n")
###################################################################
# Function: processPOD
# Description: 
###################################################################
def processPOD(inputFilename):
    counter = [0,0,0,0,0,0,0,0,0,0]
    outputFilename = "temp.jpod"

    input = open(inputFilename, 'rb')
    outputFile = open(outputFilename,'w')

    level = 1

    # Start-file brackets
    outputFile.write("{\n")

    outputFile.write("\"Source\": \""+inputFilename+"\",\n")
    replmesh = False
    replfac = False
    mbdata = {"Meshes": [],
            "Bones": []}
    meshes = mbdata["Meshes"]
    bones = mbdata["Bones"]
    meshn = -1
    bonen = -1
    temp = [[], []]
    while (1):
        # Read block header/footer
        c =  input.read(4)
        if len(c)<4 or c == "": break # end of file
        val = struct.unpack("i", c)[0]
        id = val & 0x0000FFFF
        isEnd = val >> 31 & 0x00000001
        isList = False
        if (len(blockID[id][1]) > 1 and blockID[id][1][1] == "l"): isList = True

        if (isEnd):
            level = level - 1
            if (size==0):
                CloseBrackets(level, outputFile)
        else:
            if isList: outputFile.write("  "*(level-1)*2+"\""+blockID[id][0]+".offset\": ")
            else:
                if (id>2007 and id<2016):
                    counter [id-2008] = counter [id-2008] + 1
                    outputFile.write("  "*(level-1)*2+"\""+blockID[id][0]+"."+str(counter [id-2008])+"\": ")
                    if id == 2012:
                        meshn = counter[4]-1
                        offs = {"vtxdata": [],
                                "facdata": [],
                                "boneind": []}

                                # "boneposoffs": -1,
                                # "bonepossize": -1,
                                # "bonerotoffs": -1,
                                # "bonerotsize": -1,
                                # "bonescloffs": -1,
                                # "bonesclsize": -1
                        meshes.append(offs)
                    else:
                        meshn = -1
                        if id == 2013:
                            bonen = counter[5]-1
                            offs = {"name": "",
                                    "parent": -1,
                                    "pos": [],
                                    "rot": [],
                                    "scale": [],
                                    "matrix" : []}
                            bones.append(offs)
                else:
                    outputFile.write("  "*(level-1)*2+"\""+blockID[id][0]+"\": ")
            level = level + 1

        # Read size
        c =  input.read(4)
        if len(c)<4 or c == "": break # end of file
        val = struct.unpack("i", c)[0]
        size = val

        if (isEnd==False and size==0): outputFile.write("{\n") # Start of new block
        if id == 6003 and meshn != -1:
            replfac = True
        elif id == 6006:
            replfac = False
        # Read data (if any)
        if (size > 0):
            offset = input.tell()
            data = input.read(size)
            if meshn != -1:
                offs = meshes[meshn]
                if id == 6014:
                    input.seek(offset)
                    for i in range(size//40):
                        ver = []

                        for j in range(10):
                            fl = input.read(4)
                            if j != 8:
                                form = "<f"
                            else:
                                form = "<i"
                            flv = struct.unpack(form, fl)[0]
                            ver.append(flv)
                            if j == 8:
                                temp[0].append(flv)
                        offs["vtxdata"].append(ver)


                    input.seek(offset+size)

                elif id == 6015:
                    input.seek(offset)
                    for i in range(100):
                        boind = input.read(4)
                        boindv = struct.unpack("<i", boind)[0]
                        if i > 0 and boindv == 0:
                            break
                        offs["boneind"].append(boindv)
                        temp[1].append(boindv)
                    input.seek(offset + size)
                    #offs["boneindoffs"] = offset
                elif id == 9003 and replfac:
                    input.seek(offset)
                    for i in range(size//6):
                        fac = []
                        for j in range(3):
                            vn = input.read(2)
                            vnv = struct.unpack("<H", vn)[0]
                            fac.append(vnv)
                        offs["facdata"].append(fac)
                    #offs["facdataoffs"] = offset
                    #offs["facdatasize"] = size
                    input.seek(offset + size)
                    replfac = False
            elif bonen != -1:
                offs = bones[bonen]
                if id == 5001:
                    offs["name"] = data[:-1]
                elif id == 5003:
                    offs["parent"] = struct.unpack("<i", data)[0]
                elif id == 5007 or id == 5008 or id == 5009 or id == 5011:
                    input.seek(offset)
                    if id == 5007:
                        porosc = "pos"
                        ssize = 3
                    elif id == 5008:
                        porosc = "rot"
                        ssize = 4
                    elif id == 5009:
                        porosc = "scale"
                        ssize = 7
                    elif id == 5011:
                        porosc = "matrix"
                        ssize = 16
                    framen = 0
                    offs[porosc].append([])
                    for i in range(size//4):
                        if i != 0 and i % ssize == 0:
                            framen += 1
                            offs[porosc].append([])
                        bn = input.read(4)
                        bnv = struct.unpack("<f", bn)[0]
                        offs[porosc][framen].append(bnv)
                    input.seek(offset + size)
            if data == -1: break # end of file
            if isList:
                            outputFile.write(str(offset)+",\n") # Offset to binary data (it is a list type)

            else: printData(outputFile, level-1, id, data) # Any other data

    # Final brackets
    CloseBrackets(0, outputFile)

    print ("\n"+outputFilename + " created successfully.")
    input.close()
    outputFile.close()
    return mbdata
###################################################################
# Function: ParseCommnadLine
# Description: 
###################################################################
def ParseCommnadLine():

    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', action="store", metavar="FILE", dest="input", help="Input POD file", default="")
    options, args = parser.parse_args()

    return options.input
###################################################################
# Function: main
# Description: 
###################################################################

