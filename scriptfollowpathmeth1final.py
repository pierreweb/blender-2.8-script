#setting see line 314

import bpy
from mathutils import geometry, Vector
import random
from math import asin, pi

#################################functions######################################
def get_length_and_ctrl_points(obj):
    print("function get_length")
    print(obj)
    bpy.context.view_layer.objects.active = obj
#    bpy.ops.object.duplicate_move()#not useful i do keep original
    # the duplicate is active, apply all transforms to get global coordinates
    # warning curve has to be 3d not 2d if location &rotation
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    #calcul nbr control bezier points
    nbr_ctrl_points=0
    for points in obj.data.splines[0].points:
        nbr_ctrl_points+=1 
    # convert to mesh
    obj_name = obj.name# print(obj_name)
    obj_mesh = convert_to_mesh(obj_name)#print("obj_mesh", obj_mesh)

    _data = obj_mesh.data
    edge_length = 0
    for edge in _data.edges:
        vert0 = _data.vertices[edge.vertices[0]].co
        vert1 = _data.vertices[edge.vertices[1]].co
        edge_length += (vert0-vert1).length  
    print("edge_length:",obj_name,"=",edge_length)
    bpy.ops.object.delete()# delete obj_mesh
    return (edge_length,nbr_ctrl_points)

###########
def get_length_temp(obj):##use for test only##
    print("function get_length_temp")
    # print(obj)
    edge_length = 0     
    for i in range(0,len(obj)-1):
        vert0 = obj[i]
        vert1 = obj[i+1]
        edge_length = (vert0-vert1).length
#        print("edge_length:",edge_length)
#    print("edge_length:",obj_name,"=",edge_length)
#    bpy.ops.object.delete()  # delete obj_mesh(it s the active object)
    print("trackcoord_length:",len(obj))
    return edge_length

############
def convert_to_mesh(obj_name):
    print("function convert_to_mesh")
    scn = bpy.context.scene
    ob = bpy.context.scene.objects[obj_name]# Get the object bye name
    bpy.ops.object.select_all(action='DESELECT')# Deselect all objects
    bpy.context.view_layer.objects.active = ob# Make it the active object
    ob.select_set(True)
    # it s bad to use bpy.ops but.....
    bpy.ops.object.convert(target='MESH', keep_original=True)
    obj_mesh = bpy.context.view_layer.objects.active
    return obj_mesh

############
def select_chemins(col_name):
    print("function select_chemins")
    col = bpy.data.collections.get(col_name)
#    if col:
#        for obj in col.objects:
#            obj.select_set(True)
#            print(obj.name)
#            print(bpy.context.active_object.name)
#            obj.select_set(False)
#    return col.objects
    # il faut trier par nom ( sort bye name)
    return sorted(col.objects, key=lambda obj: obj.name)

############
def calculate_coords(objs, step):
    print("function calculate_coords")
#    print(objs)
    pas = step  #meter/frame(voir walking cycle)

    points_on_curves = []
    for obj in objs:    
        curve_name = obj.name;print(obj.name)
        curve_length,nbr_ctrl_points = get_length_and_ctrl_points(obj)
        print("curve_length=",curve_length,"nbr_ctrl_points=",nbr_ctrl_points)
        resolution_U= int(round(curve_length/(pas*nbr_ctrl_points)))
        points_on_curves.append(get_coord(resolution_U, obj))
        print("obj.name:",obj.name,"U=",resolution_U)
#    print("points_on_curves=", points_on_curves)

#    # Create cubes pour test
#    newCol = bpy.data.collections.new('effacable')
#    bpy.context.scene.collection.children.link(newCol)
#    cube_rad = 0.1
#    for point in points_on_curves[3]:
#        bpy.ops.mesh.primitive_uv_sphere_add(radius=cube_rad,location=point)
#        cube = bpy.context.active_object
#        bpy.ops.collection.objects_remove_all()
#        # link the object to collection
#        newCol.objects.link(cube)
    return points_on_curves

###########
def get_coord(resolution_U, obj):
    print("function get_coord1")
    #print("obj=", obj.name, "resolution_U=", resolution_U)
    bpy.context.view_layer.objects.active = obj
    bpy.data.objects[obj.name].select_set(True)
#    print(obj)
#    bpy.ops.object.duplicate_move()#not useful i keep the original
#    the duplicate is active, apply all transforms to get global coordinates
#    warning curve has to be 3d not 2d if location &rotation
    bpy.context.object.data.dimensions = '3D'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

#   change resolution to have correct number of vertice then converting to mesh
    resolution_U_init=bpy.context.object.data.resolution_u
    bpy.context.object.data.resolution_u = resolution_U

#   convert to mesh
#    obj_name = obj.name;print(obj_name)
    obj_mesh = convert_to_mesh(obj.name)#print("obj_mesh", obj_mesh)
    obj.data.resolution_u=resolution_U_init#back to correct resolution for curve render
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    # you have to install looptools addons and it s bad to use bpy.ops but..........
    bpy.ops.mesh.looptools_space(influence=100, input='selected',
                                 interpolation='cubic', lock_x=False, lock_y=False, lock_z=False)
    bpy.ops.object.editmode_toggle()
#   put in a list the vertices coord
    points_on_curve = []
    vertices = [v.co for v in obj_mesh.data.vertices]#print("vertices=",vertices)
    points_on_curve += vertices#print("points_on_curve=",points_on_curve)

    bpy.ops.object.delete()#delete the curve mesh
    return points_on_curve

#############
def calculate_angles(objs):
    print("function calculate_angles")
    angles = []
    v2 = Vector((1, 0))#vector 2d x axe
    v3 = Vector((0, 1))#z axe
    # j=-1 for test only
    for v in objs:
        i = Vector((0, 0, 0))  #j+=1
        angle = []
        for vertice in v:
            # print("vertice=",vertice)
            vertice_temp = vertice-i
            # print("vertice=",vertice)
            # vector 2d vertice_temp.resize_2d();#
            v1 = Vector(vertice_temp[0:2])
            # Vector(vertice_temp[-2:]);print(v1z)#vector 2d
            v1z = vertice_temp.normalized()
#            if j==n:
#                print("v1=",v1)
            i = vertice
            a1 = v1.angle_signed(v2)#a1 angle beetween curve and axe x
            b1 = -asin(v1z[2]) #print("b1=",b1) b1=angle beetween curve and z b1=0 if you want z up
            angle.append(Vector((0, b1, a1)))
# permutation circulaire algorithme python decalage circulaire
        angle = angle+[angle[-1]]#angle calculate at vertice 1
        del angle[0]
        angles.append(angle)
        # print(len(angles),len(objs[0]))
        # print("angles=",angles)
        # raw_input()
    return angles


#############
def choix_chemin(chemin_temp, noeud_next):
    # https://docs.python.org/fr/3/tutorial/datastructures.html
    print("function choix_chemin")
    #change color only for test 
    mat = bpy.data.materials['Material']
    i,j,k=random.randint(0,10)/10,random.randint(0,10)/10,random.randint(0,10)/10
    #mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (i, j, k,1)#color
    mat.node_tree.nodes["Principled BSDF"].inputs[17].default_value = (i, j, k, 1)#emission

    noeud_depart = noeud_next[:]#print(noeud_depart)
    noeud_temp = [j for i in noeud_depart for j in i]#print(noeud_temp)
    noeud_len = len(noeud_temp)#print(noeud_len)

    i = random.randint(0, noeud_len-1)
    chemin_temp = noeud_temp[i]
    #[test.index(tupl) for tupl in test if 5 in tupl]
    temp = [noeud_depart.index(tupl)
            for tupl in noeud_depart if chemin_temp in tupl]
    #print(temp)
    noeud_arrive = noeuds[temp[0]]#print(noeud_arrive)
    if chemin_temp < 0:
        chemin_sens = -1
        chemin_temp = abs(chemin_temp)
        compteur=0
    else:
        chemin_sens = 1
        compteur=0
#    print(chemin_temp,noeud_temp)
    return [chemin_temp, noeud_arrive, chemin_sens,compteur]

#############
def my_handler(scene):
    print("function my_handler")   
    # i know it is very bad to use global variable but......
    global chemin_temp
    global noeud_next
    global chemin_sens
    global compteur
#print("chemin_temp=", chemin_temp, "noeud_next=",noeud_next, "chemin_sens=", chemin_sens)
    # chemin_temp-1 car la liste commence à 0 et pas à 1
    if chemin_sens == -1:
        compteur+=-1
        bpy.data.objects[moving_object_name].location = chemins_coords[chemin_temp-1][compteur]#-1 a -5
        angle_sens = Vector((0, 0, pi))
        u = Vector((1, 0, 0))
        bpy.data.objects[moving_object_name].rotation_euler = (
            chemins_angles[chemin_temp-1][compteur]).cross(u).xzy+angle_sens
    else:
        compteur+=1
        bpy.data.objects[moving_object_name].location = chemins_coords[chemin_temp-1][compteur-1]#de 0 à 4
        bpy.data.objects[moving_object_name].rotation_euler = (
            chemins_angles[chemin_temp-1][compteur-1])
#    print(compteur,":",len(chemins_coords[chemin_temp-1]))

    if abs(compteur) == len(chemins_coords[chemin_temp-1]):
        print("change curve")
        chemin_temp, noeud_next, chemin_sens,compteur = choix_chemin(chemin_temp, noeud_next)



####################################initialisation###################################
print("#############################debut#################################")
moving_object_name='Cube'
#ligne 178 material name  to change if change color use!!!!!
tracks_col_name = "Tracks"  # name of the collection with your track
step = 0.5  # meter/frame(see the walking cycle of your character)
# set node track matrix
noeud1 = [(3,), (1, 2), ()]  # ()=no links,1=chemin1,2=chemin2......
# , obligatoire print("type",type(noeud2[1]))
noeud2 = [(-1, -2), (), (4,)]#[(-1, -2), (), (4,4,4)] for  more 4 in random
noeud3 = [(), (-4,), ()]#teleportation [(3,), (-4,), ()]
noeuds = [noeud1, noeud2, noeud3]
nbr_noeuds = 3
# raw_input()#use as break point for test
chemin_sens = 1  # 1 ou -1
chemin_temp = 1# 1 à 4 (got 4 tracks) si sens inverse alors chemin_sens=-1
noeud_temp = noeuds[0]  # noeud1 à noeud3
# print("noeud_temp=",noeud_temp)
# remove all handlers
for i in range(len(bpy.app.handlers.frame_change_pre)):
    bpy.app.handlers.frame_change_pre.pop()
# remove actions
for action in bpy.data.actions:
    bpy.data.actions.remove(action)
# deselect all
bpy.ops.object.select_all(action='DESELECT')
# set cont
# bpy.ops.object.mode_set(mode='OBJECT')->error context it s why don't use ops!!!!
# append handler
bpy.app.handlers.frame_change_pre.append(my_handler)
# raw_input()

# select cube
#MonObjet=bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
# bpy.data.objects['Empty'].select_set(False)
bpy.data.objects[moving_object_name].select_set(True)
bpy.data.objects[moving_object_name].location = (0, 0, 0)
bpy.data.objects[moving_object_name].rotation_euler = (0, 0, 0)
bpy.data.objects[moving_object_name].select_set(False)

#####delete collection "effacable" for test purpose only#####
col = bpy.data.collections.get("effacable")
if col:
    print("col=", col)
    while col.objects:
        col.objects.unlink(col.objects[0])
    bpy.data.collections.remove(col)


####curves####
chemins = select_chemins(tracks_col_name)# print(chemins[4])
#unbevel curves if bevel. compulsary
for chemin in chemins:
    #print("chemin=",chemin.data.bevel_depth)
    chemin.data.bevel_depth = 0
    
chemins_coords = calculate_coords(chemins, step)
#get_length_temp(chemins_coords[1])#test purpose only
#raw_input()
chemins_angles = calculate_angles(chemins_coords)# print("chemins_angles=",chemins_angles)

#for test only
# n=4
# print("len=",len(chemins_coords[n]),len(chemins_angles[n]))
# for i in range(0,len(chemins_coords[n])):
#    print(chemins_coords[n][i],chemins_angles[n][i])
# Create sphere pour test
#newCol = bpy.data.collections.new('effacable')
# bpy.context.scene.collection.children.link(newCol)
#radius = 0.1
# for i in range(0,len(chemins_coords[n])):
# bpy.ops.mesh.primitive_uv_sphere_add(radius=radius,location=chemins_coords[n][i])
#sphere = bpy.context.active_object
#sphere.rotation_euler = chemins_angles[n][i]
#bpy.context.object.show_axis = True

# bpy.ops.collection.objects_remove_all()
#    # link the object to collection
# newCol.objects.link(sphere)
# raw_input()
#print("chemins_coords=", chemins_coords)


#bevel curves
for chemin in chemins:
    #print("chemin=",chemin.data.bevel_depth)
    chemin.data.bevel_depth = 0.02
# raw_input()

chemin_temp, noeud_next, chemin_sens,compteur= choix_chemin(chemin_temp, noeud_temp)
#raw_input()
# animation play
#compteur = 0
# bpy.ops.screen.animation_play()
##########print variables##############################
print("moving_object_name=",moving_object_name)
print("tracks_col_name=",tracks_col_name )
print("step=",step)
i=0
for noeud in noeuds:
    i+=1
    print("noeud",i,"=",noeud)
print("compteur=",compteur)

#####if you want script render
#os.path.join('C:/' , 'programs','myfiles','cat.txt') 
#bpy.context.scene.render.filepath = '//red.avi'
#bpy.context.scene.render.filepath = "I:\\3d\\blender\\mesprojets\\poubelle\\test.avi"
#scene = bpy.context.scene
#scene.frame_set(0)
# for i in range(250):
#     scene.frame_set(i)
#       bpy.context.scene.render.filepath = os.path.join('I:\3d\blender\mesprojets\poubelle','image'+i+'.png')
#bpy.ops.render.render(write_still=True)
#bpy.ops.render.render(animation=True)

#####tutorials useful
# https://docs.blender.org/api/current/mathutils.html
# https://docs.python.org/fr/3/tutorial/datastructures.html
# https://blenderartists.org/t/python-to-cancel-stop-animation/542796/6
    
##########################poubelle#################################
#    m = 6  # x,y,z,teta,phi,true or false
#    n = len(objs)
#    points_on_curves = [[0] * m for i in range(n)]
#    print("points_on_curves", points_on_curves)

# deal with trailing float smear#edge_length = '{:.6f}'.format(edge_length)

# v1=Vector((-0.50,-1,0));v12d=Vector((0,0))
# v2=Vector((1,0,0));v22d=Vector((0,0))
#v12d[:] = v1[:2]
#v22d[:] = v2[:2]
# print(v22d,v12d)
# print(v12d.angle_signed(v22d))
    # print("objs=",objs)
    #v1 = verts_sel[1].co - verts_sel[0].co
    
    
            # v1z.angle_signed(v3);
#            a1 = v2.angle(vertice)
#            if a1 > pi * 0.5:
#                a1 = pi - a1
            # angle.append((0,0,int(degrees(a1))))

#            angle.append(Vector((0,0,pi/2)))
        # raw_input()
#        angle[0]=angle[len(angle)-1]
#        angle[0]=angle[-1]
        # permutation circulaire algorithme python decalage circulaire
#        n=-1
#        rotate = lambda angle, n: angle[-n:] + angle[:-n]
 #       angle.extend(angle[-1]);del angle[0]
 
 # bpy.ops.screen.animation_cancel(restore_frame=True)
    # bpy.ops.screen.animation_cancel(restore_frame=False)
    # test = [(1, 2, 3), (), (5,)]
    # lentest = sum([len(i) for i in test])
    # print(lentest)
    
        # noeud_len = sum([len(i) for i in noeud_depart])
        
#        compteur = (-1*(scene.frame_current %
#                        len(chemins_coords[chemin_temp-1])))-1
#        compteur=-(-compteur%len(chemins_coords[chemin_temp-1]))
#        compteur = scene.frame_current % len(chemins_coords[chemin_temp-1])
        # angle_sens=Vector((0,0,0))
        #        compteur=compteur%len(chemins_coords[chemin_temp-1])
        
#    bpy.data.objects['Cube'].select_set(True)
#    bpy.data.objects['Cube'].location = chemins_coords[chemin_temp-1][compteur]
#    bpy.data.objects['Cube'].rotation_euler = (chemins_angles[chemin_temp-1][compteur]).cross(u)+angle_sens
#    if compteur == len(chemins_coords[chemin_temp-1])-1:

#231        bpy.ops.screen.animation_cancel(restore_frame=True)
        # bpy.ops.screen.animation_play()
                # bpy.ops.screen.animation_play()
#233       bpy.context.scene.frame_set(0)
#        bpy.ops.screen.animation_play()
#    if compteur == (-1*(len(chemins_coords[abs(chemin_temp-1)])-1))-1:
#        print("bip-")
#        bpy.ops.screen.animation_cancel(restore_frame=True)
#        bpy.ops.screen.animation_play()
#        chemin_temp, noeud_next, chemin_sens = choix_chemin(
#            chemin_temp, noeud_next)
#        bpy.context.scene.frame_set(0)
#        bpy.ops.screen.animation_play()

#295 raw_input()
# u=Vector((2,5,10));v=Vector((1,0,0))
# print("uv=",(u.cross(v)).xzy)