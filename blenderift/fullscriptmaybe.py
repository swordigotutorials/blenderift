import bpy
import bmesh
import mathutils
import os
from ast import literal_eval
def making_matrix(pos, rot, scale):
    m = mathutils.Quaternion((rot[0], rot[1], rot[2], rot[3])).to_matrix().to_4x4()
    mm = [0 for i in range(16)]
    mm[0] = m[2][2]
    mm[1] = -m[1][2]
    mm[2] = m[0][2]
    mm[3] = m[0][3]
    mm[4] = m[2][1]
    mm[5] = -m[1][1]
    mm[6] = m[0][1]
    mm[7] = m[1][3]
    mm[8] = -m[2][0]
    mm[9] = m[1][0]
    mm[10] = -m[0][0]
    mm[11] = m[2][3]
    mm[12] = pos[0]
    mm[13] = pos[1]
    mm[14] = pos[2]
    mm[15] = m[3][3]
    matrix = mathutils.Matrix()
    for g in range(4):
        for h in range(4):
            matrix[h][g] = mm[g*4+h]
    return matrix
def normalize_coords(pos, YZInversion=True):
    (x, y, z) = pos[:3]
#    try:
#        x = pos[0]
#    except IndexError:
#        x = 0
#    try:
#        y = pos[1]
#    except IndexError:
#        y = 0
#    try:
#        z = pos[2]
#    except IndexError:
#        z = 0
    if YZInversion:
        return (y, x, z)
    else:
        return (x, y, z)
def create_mesh(data, position, rotation, scale, mesh_name="Mesh"):
    vertices = data["vtxdata"]
    vertices2 = data["vtxdataalt"] #Some models have "Interleave vertex data" disabled. This is for those cases
#    normals = data["Normals"]
    indices = data["facdata"]
#    position = data["Position"]
#    rotation = data["Rotation"]
#    scale = data["Scale"]
#    uvs = data["UVs"]

#    material_idx = data["Material"]
#    material = create_material(materials[material_idx], base_path)

    mesh = bpy.data.meshes.new(mesh_name)
    obj = bpy.data.objects.new(mesh_name, mesh)

    obj.location = normalize_coords(position)
    obj.rotation_quaternion = rotation

    scale = normalize_coords(scale)
    obj.scale = (scale[0], scale[1], scale[2])
#    obj.scale = (1, 1, 1)

    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Create UV layer
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Create vertices
    bm_verts = [bm.verts.new(normalize_coords(v[0:3])) for v in vertices]
    bm.verts.ensure_lookup_table()

    # Create faces and assign UVs
    for i in range(0, len(indices)):
        try:
            face_indices = indices[i]
            try:  # There's a better way of doing this but whatever
                bm_faces = [bm_verts[j] for j in face_indices]
            except IndexError:
                #bm_verts = [bm.verts.new(normalize_coords(v[0:3])) for v in vertices2]
                data["vtxdata"] = vertices2
                vertices = data["vtxdata"]
                bm_verts = [bm.verts.new(normalize_coords(v[0:3])) for v in vertices]
                bm_faces = [bm_verts[j] for j in face_indices]
            face = bm.faces.new(bm_faces)

            try:
                for loop, uv in zip(face.loops, [vertices[j][6:8] for j in face_indices]):
                    loop[uv_layer].uv = (uv[0], uv[1])  # Keep same pos
            except IndexError:
                pass # TODO: add uv stuff for the uninterlvd models
        except ValueError:
            pass
    normals = []
    for j in range(len(vertices)):
        normals.append(vertices[j][3:6])
        #TODO: add support for uninterlvd models
    if normals:
        for vert, norm in zip(bm.verts, normals):
            vert.normal = norm

    bm.to_mesh(mesh)
    bm.free()

#    obj.data.materials.append(material)

    return obj
def assign_weights(obj, bones, meshdata):
    for i in range(len(meshdata['vtxdata'])):
        try:
            index = meshdata['vtxdata'][i][8]
            realindex = meshdata["boneind"][index]
            groupname = bones[realindex]["name"]
            obj.vertex_groups[str(groupname)[2:-1]].add([i], meshdata['vtxdata'][i][9], 'REPLACE')
        except IndexError:
            continue

    #TODO: add support for uninterlvd models
def matrix_world(armature_ob, bone_name):
    local = armature_ob.data.bones[bone_name].matrix_local
    basis = armature_ob.pose.bones[bone_name].matrix_basis
    parent = armature_ob.pose.bones[bone_name].parent
    if parent == None:
        return local * basis
    else:
        parent_local = armature_ob.data.bones[parent.name].matrix_local
        return matrix_world(armature_ob, parent.name) * (parent_local.inverted() * local) * basis



dir = os.path.join(bpy.context.space_data.text.filepath, os.pardir)

fil = open(os.path.join(dir, "outputanim.txt"), 'r')
mb = literal_eval(fil.read())
fil.close()

fil2 = open(os.path.join(dir, "output.txt"), 'r')
mb2 = literal_eval(fil2.read())
fil2.close()


bones = mb["Bones"]
bones2 = mb2["Bones"]
meshnum = len(mb["Meshes"])
meshnum2 = len(mb2["Meshes"])
bpy.ops.object.armature_add()
armature = bpy.context.object
#armature.scale = (0.1, 0.1, 0.1)
armature.name = "Armature"
bpy.ops.object.mode_set(mode='EDIT')
realbones = [-1 for i in range(len(bones2))]
for i in range(meshnum, len(bones) - meshnum):
    bonedata = bones[i]
    if len(bones[i]["pos"]) < 2 and len(bones[i]["rot"]) < 2 and len(bones[i]["scale"]) < 2:
        continue
    numframes = len(bonedata["pos"])
for i in range(meshnum, len(bones2) - meshnum):
    bonedata = bones2[i]
    if "Armature" in str(bonedata["name"]):
        continue
#    if len(bones2[i]["pos"]) < 2 and len(bones2[i]["rot"]) < 2 and len(bones2[i]["scale"]) < 2:
#        continue
#    numframes = len(bonedata["pos"])
    bone = armature.data.edit_bones.new(str(bonedata["name"])[2:-1])
    pos = bonedata["pos"][0]
    rot = bonedata["rot"][0]
    scale = bonedata["scale"][0]
    matrix = making_matrix(pos, rot, scale)
    bone.head = (0, 0, 0)
    bone.tail = (0, 1, 0)
    bone.matrix = matrix
    if bone.name == "CenterPoint":
        centerpoint = mathutils.Vector((bone.head[2]/100, bone.head[0]/100, bone.head[1]/100))
    realbones[i] = bone
for i in range(meshnum, len(bones2) - meshnum):
    
    par = bones2[i]["parent"]
    try:
        if par != -1:
            realbones[i-meshnum].parent = realbones[par-meshnum]
    except TypeError:
        pass
for realbone in realbones:
    if realbone == -1:
        continue
    parents = realbone.parent_recursive
    if len(parents) > 0:
        realbone.matrix = parents[0].matrix @ realbone.matrix


#        realbone.matrix = parents[0].matrix.inverted() @ realbone.matrix
#        realbone.translate(parents[0].head)
#        print()
#for i in range(meshnum, len(bones) - meshnum):
#    bonedata = bones[i]
#    if len(bones[i]["pos"]) < 2 and len(bones[i]["rot"]) < 2 and len(bones[i]["scale"]) < 2:
#        continue
#    bone = realbones[i]
##    try:
##        bone = bpy.context.active_object.data.bones[(str(bonedata["name"]))]
##    except KeyError:
##        continue
#    pos = bonedata["pos"][0]
#    rot = bonedata["rot"][0]
#    scale = bonedata["scale"][0]
#    matrix = making_matrix(pos, rot, scale)
#    bone.head = matrix.translation
#    bone.tail = matrix @ mathutils.Vector((0, bone.length, 0))
#    bone.matrix = matrix


slowdown = 1
bpy.context.scene.frame_end = numframes *slowdown
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.armature_apply()
bpy.ops.object.mode_set(mode='POSE')
for i in range(0, numframes):
    #bpy.context.scene.frame_current = i
    bpy.context.scene.frame_set(i * slowdown)
    for j in range(meshnum, len(bones) - meshnum):
        bonedata = bones[j]
        bonedata2 = bones2[j]
        if len(bones[j]["pos"]) < 2 and len(bones[j]["rot"]) < 2 and len(bones[j]["scale"]) < 2:
            continue
        try:
            bone = bpy.context.active_object.pose.bones[(str(bonedata["name"])[2:-1])]
            ebone = bpy.context.active_object.data.bones[(str(bonedata["name"])[2:-1])]
        except KeyError:
            continue
        try:
            pos = bonedata["pos"][i]
        except IndexError:
            pos = bonedata["pos"][-1]
        try:
            rot = bonedata["rot"][i]
        except IndexError:
            rot = bonedata["rot"][-1]
        try:
            scale = bonedata["scale"][i]
        except IndexError:
            scale = bonedata["scale"][-1]
#            scale = bonedata["scale"][0]
#        except IndexError:
#            pos = bonedata["pos"][-1]
#            rot = bonedata["rot"][-1]
#            scale = bonedata["scale"][0]
        pos1 = bonedata2["pos"][0]
        rot1 = bonedata2["rot"][0]
        scale1 = bonedata2["scale"][0]
        #matrix = mathutils.Matrix.LocRotScale(mathutils.Vector((pos[0], pos[2], pos[1])), mathutils.Quaternion((rot[0], rot[1], rot[2], rot[3])), mathutils.Vector((scale[0], scale[1], scale[2])))
        matrix = making_matrix(pos, rot, scale)
        matrix1 = making_matrix(pos1, rot1, scale1)
        
#        parents = ebone.parent_recursive
#        if len(parents) > 0:
#            matrix2 = (parents[0].matrix.inverted() @ ebone.matrix).to_4x4()
#            parents2 = bone.parent_recursive
#            matrix3 = (parents2[0].matrix.inverted() @ matrix)
#            matrix4 = parents2[0].matrix @ (matrix3.inverted() @ matrix2)
#        else:
#            matrix4 = matrix.inverted() @ matrix1

        bone.matrix = matrix
#        local = ebone.matrix_local
#        basis = bone.matrix_basis
#        parents = bone.parent_recursive
#        if len(parents) > 0:
#            bone.matrix = parents[0].matrix @ bone.matrix
#        else:
#            bone.matrix = local @ basis
        
#        bone.matrix = mathutils.Matrix(((1.0, 0.0, 0.0, 0.0),
#        (0.0, 1.0, 0.0, 0.0),
#        (0.0, 0.0, 1.0, 0.0),
#        (0.0, 0.0, 0.0, 1.0)))


#        bone.matrix_basis = bpy.context.active_object.data.bones["Bone"].matrix_local
        
        
#        bone.matrix = bpy.context.active_object.pose.bones["Bone"].matrix @ bone.matrix
        
        #bone.matrix = ebone.matrix_local.inverted() @ bone.matrix_basis
#        loc2 = [bone.location[0], bone.location[1], bone.location[2]]
#        loc1 = mathutils.Vector((loc2[0], loc2[1], loc2[2]))
#        rote1 = mathutils.Vector((bone.rotation_euler[0], bone.rotation_euler[1], bone.rotation_euler[2]))
#        bone.matrix = matrix
#        bone.location = loc1 - bone.location 
#        bone.rotation_euler = mathutils.Euler((rote1[0] - bone.rotation_euler[0], rote1[1] - bone.rotation_euler[1], rote1[2] - bone.rotation_euler[2]), 'XYZ')
#        bone.keyframe_insert("location", frame=i*slowdown)
#        bone.keyframe_insert("rotation_quaternion", frame=i*slowdown)
        
        
        bpy.ops.pose.select_all(action="DESELECT")
        bpy.context.active_object.data.bones.active = bpy.context.active_object.data.bones[(str(bonedata["name"])[2:-1])]
        bpy.context.active_object.data.bones[(str(bonedata["name"])[2:-1])].select = True
        bpy.ops.anim.keyframe_insert_menu(type="LocRotScale")
    for j in range(meshnum, len(bones) - meshnum):
        bonedata = bones[j]
        bonedata2 = bones2[j]
        if len(bones[j]["pos"]) < 2 and len(bones[j]["rot"]) < 2 and len(bones[j]["scale"]) < 2:
            continue
        try:
            bone = bpy.context.active_object.pose.bones[(str(bonedata["name"])[2:-1])]
            ebone = bpy.context.active_object.data.bones[(str(bonedata["name"])[2:-1])]
        except KeyError:
            continue
        parents = bone.parent_recursive
        if len(parents) > 0:
            bone.matrix = parents[0].matrix @ bone.matrix
#            bpy.ops.pose.select_all(action="DESELECT")
#            bpy.context.active_object.data.bones.active = bpy.context.active_object.data.bones[(str(bonedata["name"]))]
#            bpy.context.active_object.data.bones[(str(bonedata["name"]))].select = True
#            bpy.ops.anim.keyframe_insert_menu(type="LocRotScale")
            bone.keyframe_insert("location", frame=i*slowdown)
            bone.keyframe_insert("rotation_quaternion", frame=i*slowdown)
        
        
        
bpy.ops.object.mode_set(mode='OBJECT')
for i in range(meshnum2):
    bonedata = bones2[i]
    name = str(bonedata["name"])[2:-1]
    pos = bonedata["pos"][0]
    rot = bonedata["rot"][0]
    scale = bonedata["scale"][0]
    mesh_obj = create_mesh(mb2["Meshes"][i], pos, rot, scale, name)
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    #bpy.ops.transform.mirror(orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False))

    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_NAME')
    assign_weights(mesh_obj, bones2, mb2["Meshes"][i])
bpy.ops.object.select_all(action="SELECT")
armature.select_set(False)
bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False))
#bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=False, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
#try:
#    armature.location = centerpoint
#except NameError:
#    print("There's no CenterPoint")
armature.rotation_euler = mathutils.Vector((1.57079633, 0, 0))