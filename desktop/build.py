# SPDX-License-Identifier: MIT
"""Run: py -3.10 -m pip install pyinstaller==6.22.3; py -3.10 desktop/build.py"""
import hashlib,json,shutil,subprocess,sys,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT.parent/'ChessLLM-Releases'
TARGET=OUT/'ChessLLM-Windows'
WEB_FILES=['index.html','styles.css','app.js','local.js','gemini.js','cpu.js','cpu-worker.js','README.md','LICENSE']
def main():
    OUT.mkdir(exist_ok=True);TARGET.mkdir(exist_ok=True)
    for name in WEB_FILES:
        (TARGET/'web').mkdir(exist_ok=True);shutil.copy2(ROOT/name,TARGET/'web'/name)
    for name in ['assets','vendor','Licenses']:
        shutil.copytree(ROOT/name,TARGET/'web'/name,dirs_exist_ok=True)
    shutil.copytree(ROOT/'Licenses',TARGET/'Licenses',dirs_exist_ok=True)
    shutil.copy2(ROOT/'LICENSE',TARGET/'LICENSE')
    manifest=json.loads((ROOT/'desktop'/'runtime-manifest.json').read_text())
    cache=OUT/'download-cache';cache.mkdir(exist_ok=True)
    for key,item in manifest['backends'].items():
        if key!='cpu':continue
        archive=cache/item['name']
        if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest()!=item['sha256']:
            print('Downloading',item['name'],flush=True);urllib.request.urlretrieve(item['url'],archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('Runtime checksum mismatch')
        destination=TARGET/'runtime'/('cuda' if key=='cuda-libraries' else key);destination.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            if any(not (destination/n).resolve().is_relative_to(destination.resolve()) for n in z.namelist()):raise RuntimeError('Unsafe archive path')
            z.extractall(destination)
    (TARGET/'models').mkdir(exist_ok=True)
    (TARGET/'models'/'PUT-GGUF-MODELS-HERE.txt').write_text('Place GGUF files here. Models are not included.')
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--windowed','--name','ChessLLM','--distpath',str(TARGET),'--workpath',str(OUT/'build'),'--specpath',str(OUT),str(ROOT/'desktop'/'companion.py')],check=True)
    # Explicit allowlist: never include user models, runtime logs or credentials.
    with zipfile.ZipFile(OUT/'ChessLLM-Windows-x64.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in TARGET.rglob('*'):
            if path.is_file() and not (path.relative_to(TARGET).parts[0]=='runtime' and path.relative_to(TARGET).parts[1]!='cpu') and (path.relative_to(TARGET).parts[0] in ['web','runtime','Licenses'] or path.name in ['ChessLLM.exe','LICENSE','PUT-GGUF-MODELS-HERE.txt']):z.write(path,Path('ChessLLM-Windows')/path.relative_to(TARGET))
    print('Ready:',OUT/'ChessLLM-Windows-x64.zip')
if __name__=='__main__':main()
