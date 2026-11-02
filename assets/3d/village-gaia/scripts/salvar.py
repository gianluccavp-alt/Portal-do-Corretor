import bpy, os
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
for o in list(bpy.data.objects):
    if o.name.startswith('terreno_render') or (o.type == 'MESH' and o.data is None):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.data.objects['arvores'].hide_render = False
sc = bpy.context.scene
sc.camera = bpy.data.objects['cam_fachada']
res = {}
for o in sc.objects:
    if o.type == 'MESH':
        o.data.calc_loop_triangles(); res[o.name] = len(o.data.loop_triangles)
result['tris'] = res; result['total'] = sum(res.values())
result['objs'] = [o.name for o in sc.objects]
result['imgs'] = [(i.name, list(i.size), bool(i.packed_file)) for i in bpy.data.images]
bpy.ops.wm.save_as_mainfile(filepath=REPO + '/assets/3d/village-gaia/gaia.blend', compress=True)
