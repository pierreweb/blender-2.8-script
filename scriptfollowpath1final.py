#setting see line 289#

import bpy
from mathutils import geometry, Vector
import random
from math import asin, pi

#################################functions######################################


def get_length(obj):
    print("function get_length")
    # print(obj)
    bpy.context.view_layer.objects.active = obj
#    bpy.ops.object.duplicate_move()#not useful i do keep original
    # the duplicate is active, apply all transforms to get global coordinates
    # warning curve has to be 3d not 2d if location &rotation
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # convert to mesh
    obj_name = obj.name
    # print(obj_name)
    obj_mesh = convert_to_mesh(obj_name)
    #print("obj_mesh", obj_mesh)

#    _data = context.active_object.data
    _data = obj_mesh.data
    edge_length = 0
    for edge in _data.edges:
        vert0 = _data.vertices[edge.vertices[0]].co
        vert1 = _data.vertices[edge.vertices[1]].co
        edge_length += (vert0-vert1).length

    # deal with trailing float smear#edge_length = '{:.6f}'.format(edge_length)
    # print(edge_length)
    bpy.ops.object.delete()  # delete obj_mesh(it s the active object)
    return edge_length

##############


def convert_to_mesh(obj_name):
    print("function convert_to_mesh")
    scn = bpy.context.scene
    ob = bpy.context.scene.objects[obj_name]  # Get the object bye name
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    bpy.context.view_layer.objects.active = ob  # Make it the active object
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

###########


def calculate_coords(objs, step):
    print("function calculate_coords")
#    print(objs)
    pas = step  # 0.1 metre/frame(voir walking cycle)
#    m = 6  # x,y,z,teta,phi,true or false
#    n = len(objs)
#    points_on_curves = [[0] * m for i in range(n)]
#    print("points_on_curves", points_on_curves)

    points_on_curves = []

    for obj in objs:
        # print(obj.name)
        curve_name = obj.name
        curve_length = get_length(obj)  # print("curve_length=",curve_length)
        resolution_U = int(curve_length/(pas*4))
        points_on_curves.append(get_coord(resolution_U, obj))

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

#print("fin calculate_coords")
    return points_on_curves

###########


def get_coord(resolution_U, obj):
    print("function get_coord1")
    #print("obj=", obj.name, "resolution_U=", resolution_U)
    bpy.context.view_layer.objects.active = obj
    bpy.data.objects[obj.name].select_set(True)

#    bpy.ops.object.duplicate_move()#not useful i keep the original
#    the duplicate is active, apply all transforms to get global coordinates
#    warning curve has to be 3d not 2d if location &rotation
    bpy.context.object.data.dimensions = '3D'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
#   i change resolution to have correct number of vertice then converting to mesh
    bpy.context.object.data.resolution_u = resolution_U
#   convert to mesh
#    obj_name = obj.name;print(obj_name)
    obj_mesh = convert_to_mesh(obj.name)
    #print("obj_mesh", obj_mesh)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    # you have to install looptools addons and it s bad to use bpy.ops but..........
    bpy.ops.mesh.looptools_space(influence=100, input='selected',
                                 interpolation='cubic', lock_x=False, lock_y=False, lock_z=False)
    bpy.ops.object.editmode_toggle()
#   put in a list the vertices coord
#   Create an empty list.
    points_on_curve = []
    # Read vertices
    vertices = [v.co for v in obj_mesh.data.vertices]
#    print("vertices=",vertices)
    points_on_curve += vertices
#    print("points_on_curve=",points_on_curve)

#   delete the curve mesh
    bpy.ops.object.delete()
    return points_on_curve
#############


def calculate_angles(objs):
    print("function calculate_angles")
    # https://docs.blender.org/api/current/mathutils.html
# v1=Vector((-0.50,-1,0));v12d=Vector((0,0))
# v2=Vector((1,0,0));v22d=Vector((0,0))
#v12d[:] = v1[:2]
#v22d[:] = v2[:2]
# print(v22d,v12d)
# print(v12d.angle_signed(v22d))
    # print("objs=",objs)
    #v1 = verts_sel[1].co - verts_sel[0].co
    angles = []

    v2 = Vector((1, 0))  # vector 2d
    v3 = Vector((0, 1))
    # j=-1 for test only
    for v in objs:
        i = Vector((0, 0, 0))  # j+=1
        angle = []
        for vertice in v:
            # print("vertice=",vertice)
            vertice_temp = vertice-i
            # print("vertice=",vertice)
            # vector 2dvertice_temp.resize_2d();#
            v1 = Vector(vertice_temp[0:2])
            # Vector(vertice_temp[-2:]);print(v1z)#vector 2d
            v1z = vertice_temp.normalized()
#            if j==n:
#                print("v1=",v1)
            i = vertice
            a1 = v1.angle_signed(v2)
            b1 = -asin(v1z[2])  # print("b1=",b1) b1=0 if you want z up
            # v1z.angle_signed(v3);
#            a1 = v2.angle(vertice)
#            if a1 > pi * 0.5:
#                a1 = pi - a1
            # angle.append((0,0,int(degrees(a1))))
            angle.append(Vector((0, b1, a1)))
#            angle.append(Vector((0,0,pi/2)))
        # raw_input()
#        angle[0]=angle[len(angle)-1]
#        angle[0]=angle[-1]
        # permutation circulaire algorithme python decalage circulaire
#        n=-1
#        rotate = lambda angle, n: angle[-n:] + angle[:-n]
 #       angle.extend(angle[-1]);del angle[0]
        angle = angle+[angle[-1]]
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
    # https://blenderartists.org/t/python-to-cancel-stop-animation/542796/6
    # bpy.ops.screen.animation_cancel(restore_frame=True)
    # bpy.ops.screen.animation_cancel(restore_frame=False)
    # test = [(1, 2, 3), (), (5,)]
    # lentest = sum([len(i) for i in test])
    # print(lentest)

    noeud_depart = noeud_next[:]
    print(noeud_depart)
    # noeud_len = sum([len(i) for i in noeud_depart])
    noeud_temp = [j for i in noeud_depart for j in i]
    print(noeud_temp)
    noeud_len = len(noeud_temp)
    print(noeud_len)
    # i = random.randint(0, nbr_noeuds-1)
    i = random.randint(0, noeud_len-1)
    chemin_temp = noeud_temp[i]
    # bip = [test.index(tupl) for tupl in test if 5 in tupl]
    temp = [noeud_depart.index(tupl)
            for tupl in noeud_depart if chemin_temp in tupl]
    print(temp)
    noeud_arrive = noeuds[temp[0]]
    print(noeud_arrive)
    if chemin_temp < 0:
        chemin_sens = -1
        chemin_temp = abs(chemin_temp)
    else:
        chemin_sens = 1
#    print(chemin_temp,noeud_temp)

    return [chemin_temp, noeud_arrive, chemin_sens]


#####


def my_handler(scene):
    print("function my_handler")

    # i know it is very bad to use global variable but......
    global chemin_temp
    global noeud_next
    global chemin_sens
    print("chemin_temp=", chemin_temp, "noeud_next=",
          noeud_next, "chemin_sens=", chemin_sens)
    # chemin_temp-1 car la liste commence à 0 et pas à 1
    if chemin_sens == -1:
        compteur = (-1*(scene.frame_current %
                        len(chemins_coords[chemin_temp-1])))-1
        angle_sens = Vector((0, 0, pi))
        u = Vector((1, 0, 0))
        bpy.data.objects['Cube'].rotation_euler = (
            chemins_angles[chemin_temp-1][compteur]).cross(u).xzy+angle_sens
    else:
        compteur = scene.frame_current % len(chemins_coords[chemin_temp-1])
        # angle_sens=Vector((0,0,0))
        bpy.data.objects['Cube'].rotation_euler = (
            chemins_angles[chemin_temp-1][compteur])

#    print(compteur)

#    bpy.data.objects['Cube'].select_set(True)
    bpy.data.objects['Cube'].location = chemins_coords[chemin_temp-1][compteur]
#    bpy.data.objects['Cube'].rotation_euler = (chemins_angles[chemin_temp-1][compteur]).cross(u)+angle_sens
    if compteur == len(chemins_coords[chemin_temp-1])-1:
        print("bip+")
        bpy.ops.screen.animation_cancel(restore_frame=False)
        chemin_temp, noeud_next, chemin_sens = choix_chemin(
            chemin_temp, noeud_next)
        bpy.context.scene.frame_set(0)
        bpy.ops.screen.animation_play()
    if compteur == (-1*(len(chemins_coords[abs(chemin_temp-1)])-1))-1:
        print("bip-")
        bpy.ops.screen.animation_cancel(restore_frame=False)
        chemin_temp, noeud_next, chemin_sens = choix_chemin(
            chemin_temp, noeud_next)
        bpy.context.scene.frame_set(0)
        bpy.ops.screen.animation_play()


####################################initialisation###################################
print("#############################debut#################################")
tracks_col_name = "Chemins"  # name of the collection with your track
step = 0.5  # 0.1 metre/frame(voir walking cycle)
# set node track matrix
noeud1 = [(), (1, 2, 3), ()]  # ()=no links,1=chemin1,2=chemin2......
# , obligatoire print("type",type(noeud2[1]))
noeud2 = [(-1, -2, -3), (4, -4), (5,)]
noeud3 = [(), (-5,), ()]
noeuds = [noeud1, noeud2, noeud3]
nbr_noeuds = 3
# raw_input()
chemin_sens = 1  # vaut 1 ou -1
# varie de 1 à 5 (j'ai 5 chemins) si sens inverse alors chemin_sens=-1
chemin_temp = 1
noeud_temp = noeuds[0]  # varie de noeud1 à noeud3
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
# bpy.ops.object.mode_set(mode='OBJECT') error context
# append handler
bpy.app.handlers.frame_change_pre.append(my_handler)
# raw_input()# raw input equivalent a break pour deboggage

# select cube
#MonObjet=bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
# bpy.data.objects['Empty'].select_set(False)
# bpy.data.objects['Cube'].select_set(True)
#bpy.data.objects['Cube'].location = (0, 0, 0)
bpy.data.objects['Cube'].rotation_euler = (0, 0, 0)
bpy.data.objects['Cube'].select_set(False)

#####delete collection effacable for test purpose only#####
col = bpy.data.collections.get("effacable")
if col:
    print("col=", col)
    while col.objects:
        col.objects.unlink(col.objects[0])
    # bpy.context.scene.collection.children.keys()[4]
    bpy.data.collections.remove(col)


####curve####
chemins = select_chemins(tracks_col_name)  # print(chemins[4])
step = 0.5  # 0.1 metre/frame(voir walking cycle)
chemins_coords = calculate_coords(chemins, step)

# print("chemins_angles=",chemins_angles)
chemins_angles = calculate_angles(chemins_coords)
# u=Vector((2,5,10));v=Vector((1,0,0))
# print("uv=",(u.cross(v)).xzy)
# raw_input()
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
# chemin1=chemins_coords[0]#mettre chemin1_coords
# chemin2=chemins_coords[1]
# chemin3=chemins_coords[2]
# chemin4=chemins_coords[3]
# chemin5=chemins_coords[4]


# raw_input()

chemin_temp, noeud_next, chemin_sens = choix_chemin(chemin_temp, noeud_temp)
# noeud_temp=choix_chemin(chemin_temp,noeud_temp)[1]


# raw_input()
# animation play
compteur = 0
bpy.ops.screen.animation_play()
