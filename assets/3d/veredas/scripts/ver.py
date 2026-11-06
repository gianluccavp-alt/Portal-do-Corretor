# ver.py -- render rapido (Workbench) para conferir, sem salvar nada
import bpy
def ver(path, loc, alvo=None, escala=None, w=1400, h=800, lente=30):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('tmp_ver')
    ob = bpy.data.objects.new('tmp_ver', cam)
    sc.collection.objects.link(ob)
    ob.location = loc
    if escala:
        cam.type = 'ORTHO'; cam.ortho_scale = escala
    else:
        cam.lens = lente; cam.clip_end = 20000
        from mathutils import Vector
        ob.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.clip_end = 20000
    sc.camera = ob
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'; sc.display.shading.show_shadows = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(ob); bpy.data.cameras.remove(cam)
