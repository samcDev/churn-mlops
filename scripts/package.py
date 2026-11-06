from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
out=root.parent/'churn-mlops-entrega-actualizada.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if not p.is_file() or any(x in rel.parts for x in ['.venv','__pycache__','.pytest_cache','mlartifacts','mlruns']): continue
        if p.suffix in ['.db','.pyc'] or p.name=='repository.bundle': continue
        z.write(p,Path(root.name)/rel)
print(out)
