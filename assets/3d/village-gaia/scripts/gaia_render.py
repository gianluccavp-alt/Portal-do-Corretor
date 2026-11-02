# gaia_render.py -- luz, ceu, cameras e renders de comparacao com as fotos do book.
# Uso: python3 -I bl.py gaia_render.py. VIEWS / RODADA / OUT podem ser definidos antes (exec).
# Cameras de 'fachada' e 'torre' vem de cams_fit.json (ajuste aos cantos das torres nas fotos).
import bpy, math, mathutils, json, os
_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_DIR, '..', '..', '..', '..'))
sc = bpy.context.scene
try:
    VIEWS
except NameError:
    VIEWS = ['fachada', 'torre', 'aerea']
try:
    RODADA
except NameError:
    RODADA = 'r3'
try:
    OUT
except NameError:
    OUT = _REPO + '/.superpowers/sdd/2026-11-02-maquete-3d'

_f = json.load(open(os.path.join(_DIR, 'cams_fit.json')))
def _cam(k):
    c = _f[k]; y = math.radians(c['yaw_deg'])
    return ((c['x'], c['y'], c['z']), (c['x'] + 100 * math.cos(y), c['y'] + 100 * math.sin(y), c['z']),
            c['lens'], (0.0, c['shift_y']))
# aerea: elevacao ~22 graus, vista do -Y, pitch -15
_cx, _cy, _hd, _hh = -26.0, 15.0, 332.0, 134.0
_az = math.radians(-8)
_camA = (_cx + _hd * math.sin(_az), _cy - _hd * math.cos(_az), _hh)
_dt = _hh / math.tan(math.radians(15))
_tgtA = (_camA[0] + (_cx - _camA[0]) / _hd * _dt, _camA[1] + (_cy - _camA[1]) / _hd * _dt, 0)
CAMS = {'fachada': _cam('fachada'), 'torre': _cam('torre'), 'aerea': (_camA, _tgtA, 20.0, (0, 0))}

def world(sun_elev, sun_rot, strength=1.0, dusk=False):
    w = bpy.data.worlds.get('ceu') or bpy.data.worlds.new('ceu')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    sk = nt.nodes.new('ShaderNodeTexSky')
    sk.sky_type = 'MULTIPLE_SCATTERING'
    sk.sun_disc = False
    sk.sun_elevation = math.radians(sun_elev)
    sk.sun_rotation = math.radians(sun_rot)
    sk.altitude = 300
    sk.air_density = 1.0
    sk.aerosol_density = 1.0
    if dusk:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        cr = nt.nodes.new('ShaderNodeValToRGB')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        nt.links.new(sep.outputs['Z'], cr.inputs['Fac'])
        e = cr.color_ramp.elements
        e[0].position, e[0].color = 0.0, (0.55, 0.42, 0.33, 1)
        e[1].position, e[1].color = 0.35, (0.10, 0.17, 0.42, 1)
        e3 = e.new(0.06); e3.color = (0.42, 0.40, 0.48, 1)
        nt.links.new(cr.outputs['Color'], bg.inputs['Color'])
    else:
        nt.links.new(sk.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs['Background'], o.inputs['Surface'])
    # sol
    for ob in [o_ for o_ in bpy.data.objects if o_.type == 'LIGHT']:
        bpy.data.objects.remove(ob, do_unlink=True)
    ld = bpy.data.lights.new('sol', 'SUN')
    ld.energy = 0.5 if dusk else 5.5
    ld.color = (1.0, 0.75, 0.55) if dusk else (1.0, 0.96, 0.9)
    ld.angle = math.radians(1.0)
    ob = bpy.data.objects.new('sol', ld)
    sc.collection.objects.link(ob)
    # direcao: elevacao/rotacao como no ceu (rotacao 0 = sol vindo de +Y)
    e, r = math.radians(max(sun_elev, 3)), math.radians(sun_rot)
    d = mathutils.Vector((math.sin(r) * math.cos(e), math.cos(r) * math.cos(e), math.sin(e)))
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

def emissao(on):
    for nm, st in (('unidade', 1.6), ('varanda_forro', 0.0)):
        m = bpy.data.materials[nm]
        p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        p.inputs['Emission Strength'].default_value = st if on else 0.0

def camera(name, loc, target, lens, shift=(0, 0), level=True):
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, cd)
        sc.collection.objects.link(ob)
    cd.lens = lens
    cd.sensor_width = 36
    cd.shift_x, cd.shift_y = shift
    cd.clip_end = 5000
    ob.location = loc
    d = mathutils.Vector(target) - mathutils.Vector(loc)
    if level:
        d.z = 0
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = ob
    return ob

def terreno_sem_arvores_perto(cam_loc, raio):
    t = bpy.data.objects['arvores']
    c = t.copy(); c.data = t.data.copy(); c.name = 'terreno_render'
    sc.collection.objects.link(c)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(c.data)
    copa = set(range(len(c.data.materials)))
    cl = mathutils.Vector((cam_loc[0], cam_loc[1]))
    dead = [f for f in bm.faces if f.material_index in copa and (f.calc_center_median().xy - cl).length < raio]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(c.data); bm.free()
    t.hide_render = True
    return t, c

def fim_terreno(t, c):
    t.hide_render = False
    bpy.data.meshes.remove(c.data)

def render(path, w, h):
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    sc.render.image_settings.file_format = 'PNG'
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    try:
        sc.eevee.taa_render_samples = 64
        sc.eevee.use_shadows = True
        sc.eevee.use_raytracing = True
    except Exception:
        pass
    bpy.ops.render.render(write_still=True)

T1 = bpy.data.objects['torre-1'].location
for v in VIEWS:
    if v == 'fachada':
        world(2, 300, 0.35, dusk=True); emissao(True)
        sc.view_settings.exposure = 0.6 if False else 0.4
        camera('cam_fachada', CAMS['fachada'][0], CAMS['fachada'][1], CAMS['fachada'][2], CAMS['fachada'][3])
        render(OUT + '/render-fachada-' + RODADA + '.png', 1600, 1066)
    elif v == 'torre':
        world(35, 110, 0.15); emissao(False); sc.view_settings.exposure = -1.2
        camera('cam_torre', CAMS['torre'][0], CAMS['torre'][1], CAMS['torre'][2], CAMS['torre'][3])
        t_, c_ = terreno_sem_arvores_perto(CAMS['torre'][0], 38)
        render(OUT + '/render-torre-' + RODADA + '.png', 1600, 2000)
        fim_terreno(t_, c_)
    elif v == 'aerea':
        world(50, 150, 0.15); emissao(False); sc.view_settings.exposure = -0.4
        camera('cam_aerea', CAMS['aerea'][0], CAMS['aerea'][1], CAMS['aerea'][2], CAMS['aerea'][3], level=False)
        render(OUT + '/render-aerea-' + RODADA + '.png', 1600, 899)
    elif v == 'faces':
        # close-ups das 4 faces da torre-1 (conferencia das janelas): camera ortografica de frente
        # e uma obliqua da ponta (o dormitorio 2 dos aptos de ponta abre para o recorte da ponta)
        world(40, 120, 0.15); emissao(False); sc.view_settings.exposure = -1.0
        cx, cy = T1.x, T1.y
        vistas = {
            'mais-x': ((cx + 80, cy, 14), (cx, cy, 14), 44, 'O'),
            'menos-x': ((cx - 80, cy, 14), (cx, cy, 14), 44, 'O'),
            'mais-y': ((cx, cy + 80, 14), (cx, cy, 14), 20, 'O'),
            'menos-y': ((cx, cy - 80, 14), (cx, cy, 14), 20, 'O'),
            'ponta-obliqua': ((cx + 16, cy + 34, 9), (cx + 1, cy + 18, 7), 30, 'P'),
        }
        for nome, (loc, alvo, esc, tipo) in vistas.items():
            ob = camera('cam_face', loc, alvo, 35)
            ob.data.type = 'ORTHO' if tipo == 'O' else 'PERSP'
            ob.data.ortho_scale = esc
            ob.data.shift_y = 0
            t_, c_ = terreno_sem_arvores_perto(loc, 200)
            render(OUT + '/task8-face-' + nome + '.png', 1600, 1000)
            fim_terreno(t_, c_)
        bpy.data.objects.remove(bpy.data.objects['cam_face'], do_unlink=True)
result['ok'] = VIEWS
