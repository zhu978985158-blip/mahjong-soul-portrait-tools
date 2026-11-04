"""Build and validate a replacement bundle without touching the installed game."""
from pathlib import Path
import json,hashlib,struct,warnings,sys
import UnityPy
from PIL import Image
warnings.filterwarnings('ignore')
UnityPy.config.FALLBACK_UNITY_VERSION='2022.3.62f2'
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'inputs/source-records.json').read_text())
record=next(r for r in records if r['asset_path']=='myassets/deco/character/yasina/full/full.png')
source=Path(record['source'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'output'; OUT.mkdir(parents=True,exist_ok=True)
previous=json.loads((ROOT/'inputs/previous-install.json').read_text())
previous_hash=sha(source)
assert previous_hash in (record['source_sha256'],previous['patched_sha256']),'Unexpected installed game version'
oldcopy=ROOT/'backup/previous'/source.name; oldcopy.parent.mkdir(parents=True,exist_ok=True)
if not oldcopy.exists():oldcopy.write_bytes(source.read_bytes())
assert sha(oldcopy)==previous_hash
backup=ROOT/'backup/original'/source.name; backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():backup.write_bytes(source.read_bytes())
assert sha(backup)==record['source_sha256']
image_path=Path(sys.argv[1]);im=Image.open(image_path)
assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255),'Real alpha required'
w,h=im.size
assert (w,h)==(872,1305),'Original dimensions required'
e=UnityPy.load(str(backup))
original_ids=sorted((o.path_id,o.type.name) for o in e.objects)
for obj in e.objects:
 if obj.type.name=='Texture2D':
  tex=obj.read();tex.set_image(im,target_format=4);tex.save()
 if obj.type.name=='Sprite':
  d=obj.read_typetree();ppu=100.0
  d['m_Rect']={'x':0.0,'y':0.0,'width':float(w),'height':float(h)}
  d['m_PixelsToUnits']=ppu;d['m_Pivot']={'x':0.5,'y':0.5}
  rd=d['m_RD'];rd['textureRect']=dict(d['m_Rect']);rd['textureRectOffset']={'x':0.0,'y':0.0};rd['atlasRectOffset']={'x':0.0,'y':0.0}
  rd['uvTransform']={'x':ppu,'y':w/2,'z':ppu,'w':h/2}
  # Standard interleaved position and UV stream, complete rectangular mesh.
  positions=[(-w/(2*ppu),-h/(2*ppu)),(w/(2*ppu),-h/(2*ppu)),(w/(2*ppu),h/(2*ppu)),(-w/(2*ppu),h/(2*ppu))]
  uv=[(0.,0.),(1.,0.),(1.,1.),(0.,1.)]
  vd=rd['m_VertexData'];vd['m_VertexCount']=4
  for ch in vd['m_Channels']:ch.update(stream=0,offset=0,format=0,dimension=0)
  vd['m_Channels'][0].update(dimension=3)
  vd['m_Channels'][4].update(offset=12,dimension=2)
  vd['m_DataSize']=b''.join(struct.pack('<5f',x,y,0.,u,v) for (x,y),(u,v) in zip(positions,uv))
  rd['m_IndexBuffer']=list(struct.pack('<6H',0,1,2,0,2,3))
  sub=rd['m_SubMeshes'][0];sub.update(firstByte=0,indexCount=6,topology=0,baseVertex=0,firstVertex=0,vertexCount=4)
  sub['localAABB']={'m_Center':{'x':0.,'y':0.,'z':0.},'m_Extent':{'x':w/(2*ppu),'y':h/(2*ppu),'z':0.}}
  rd['m_SubMeshes']=[sub];d['m_PhysicsShape']=[]
  obj.save_typetree(d)
output=OUT/'candidate'/source.name; output.parent.mkdir(parents=True,exist_ok=True)
output.write_bytes(next(iter(e.files.values())).save(packer='lz4'))
check=UnityPy.load(str(output));assert original_ids==sorted((o.path_id,o.type.name) for o in check.objects)
for obj in check.objects:
 if obj.type.name=='Texture2D':
  decoded=obj.read().image;assert decoded.size==im.size and decoded.tobytes()==im.tobytes()
 if obj.type.name=='Sprite':
  d=obj.read_typetree();assert d['m_RD']['m_VertexData']['m_VertexCount']==4
  decoded=obj.read().image;assert decoded.size==im.size
  assert decoded.tobytes()==im.tobytes(),'Sprite UV or mesh pixel mismatch'
assert sha(source)==previous_hash
report=dict(source=str(source),backup=str(backup),patched=str(output),original_sha256=sha(backup),patched_sha256=sha(output),texture=str(image_path.resolve()),previous_sha256=previous_hash,texture_size=[w,h],verified_texture_pixel_exact=True,verified_object_ids_unchanged=True,installed=False)
(OUT/'install-record.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
