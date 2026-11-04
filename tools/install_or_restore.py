from pathlib import Path
import json,hashlib,os,sys
root=Path(__file__).resolve().parents[1]
r=json.loads((root/'output/install-record.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mode=sys.argv[1];assert mode in ('install','restore')
target=Path(r['source']);payload=Path(r['patched'] if mode=='install' else r['backup'])
expected=r['patched_sha256'] if mode=='install' else r['original_sha256']
assert sha(payload)==expected
assert sha(target) in (r['original_sha256'],r['patched_sha256'],r['previous_sha256']),'Game changed, refusing overwrite'
if sha(target)!=expected:
 temp=target.with_name(target.name+'.codex-tmp')
 with temp.open('xb') as f:f.write(payload.read_bytes());f.flush();os.fsync(f.fileno())
 os.chmod(temp,target.stat().st_mode & 0o777)
 os.replace(temp,target)
assert sha(target)==expected
r['installed']=mode=='install';(root/'output/install-record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
legacy=root/'inputs/previous-install.json'
legacy.write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(mode,'verified',target)
