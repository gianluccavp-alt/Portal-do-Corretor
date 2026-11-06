# exportar.py -- exporta o bairro para assets/3d/veredas/veredas.glb (Draco, Y-up) e salva o .blend
import bpy, os
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
OUTG = REPO + '/assets/3d/veredas/veredas.glb'
sel = [o for o in bpy.context.view_layer.objects if o.name.startswith('mundo-')]
for o in bpy.context.view_layer.objects:
    o.select_set(o.name.startswith('mundo-'))
bpy.context.view_layer.objects.active = sel[0]
bpy.ops.export_scene.gltf(
    filepath=OUTG, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
    export_attributes=False, export_cameras=False, export_lights=False, export_extras=False,
    export_image_format='AUTO', export_image_quality=72,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
    export_draco_position_quantization=15, export_draco_normal_quantization=8,
    export_draco_texcoord_quantization=12, export_draco_generic_quantization=12, export_vertex_color='ACTIVE')
result['glb_bytes'] = os.path.getsize(OUTG)
result['n'] = len(sel)
bpy.ops.wm.save_mainfile()
