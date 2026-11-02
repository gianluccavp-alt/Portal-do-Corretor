# exportar.py -- exporta o .glb (Draco, Y-up, atributo _unit) e salva o .blend
import bpy, os
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
OUTG = REPO + '/assets/3d/village-gaia/gaia.glb'
NOMES = ['torre-1', 'torre-2', 'torre-3', 'guarda-corpo', 'unidades', 'terreno', 'entorno', 'arvores']
for o in bpy.context.view_layer.objects:
    o.select_set(o.name in NOMES)
bpy.context.view_layer.objects.active = bpy.data.objects['unidades']
bpy.ops.export_scene.gltf(
    filepath=OUTG, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
    export_attributes=True, export_cameras=False, export_lights=False, export_extras=False,
    export_image_format='AUTO', export_jpeg_quality=85,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
    export_draco_position_quantization=16, export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=14, export_draco_color_quantization=10,
    export_draco_generic_quantization=16, export_vertex_color='NONE')
result['glb_bytes'] = os.path.getsize(OUTG)
bpy.ops.wm.save_as_mainfile(filepath=REPO + '/assets/3d/village-gaia/gaia.blend', compress=True)
result['blend_bytes'] = os.path.getsize(REPO + '/assets/3d/village-gaia/gaia.blend')
