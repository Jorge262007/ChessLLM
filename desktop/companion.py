# SPDX-License-Identifier: MIT
"""ChessLLM: same web UI, loopback-only native inference companion."""
import atexit, ctypes, json, os, secrets, socket, subprocess, sys, threading, time, urllib.request, urllib.error, webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
ROOT=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent.parent
WEB=ROOT/'web' if (ROOT/'web').is_dir() else ROOT
TOKEN=secrets.token_urlsafe(32)
RUNTIME_TOKEN=secrets.token_urlsafe(32)
LOCK=threading.Lock()
PROC=None
LOADED=None
PORT=None
LOG=None
JOB=None
# Kill runtime descendants even when the companion is closed from Task Manager.
if os.name=='nt':
    import ctypes.wintypes as wt
    class Basic(ctypes.Structure):
        _fields_=[('a',ctypes.c_int64),('b',ctypes.c_int64),('flags',wt.DWORD),('c',ctypes.c_size_t),('d',ctypes.c_size_t),('e',wt.DWORD),('f',ctypes.c_size_t),('g',wt.DWORD),('h',wt.DWORD)]
    class IO(ctypes.Structure):
        _fields_=[(n,ctypes.c_uint64) for n in ['a','b','c','d','e','f']]
    class Extended(ctypes.Structure):
        _fields_=[('basic',Basic),('io',IO),('a',ctypes.c_size_t),('b',ctypes.c_size_t),('c',ctypes.c_size_t),('d',ctypes.c_size_t)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.restype=wt.HANDLE
    kernel.SetInformationJobObject.argtypes=[wt.HANDLE,ctypes.c_int,ctypes.c_void_p,wt.DWORD]
    kernel.AssignProcessToJobObject.argtypes=[wt.HANDLE,wt.HANDLE]
    JOB=kernel.CreateJobObjectW(None,None)
    limits=Extended(); limits.basic.flags=0x2000
    kernel.SetInformationJobObject(JOB,9,ctypes.byref(limits),ctypes.sizeof(limits))
def freeport():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0)); return s.getsockname()[1]
def stop():
    global PROC,LOADED,LOG
    if PROC and PROC.poll() is None:
        PROC.terminate()
        try: PROC.wait(10)
        except subprocess.TimeoutExpired: PROC.kill(); PROC.wait()
    PROC=None; LOADED=None
    if LOG: LOG.close(); LOG=None
atexit.register(stop)
def models():
    return sorted(p.name for p in (ROOT/'models').glob('*.gguf') if p.is_file())
def load(model,backend):
    global PROC,PORT,LOADED,LOG
    if model not in models(): raise ValueError('Choose a GGUF file from the models folder.')
    if backend not in ['Auto','CUDA','Vulkan','CPU']: raise ValueError('Invalid compute backend.')
    if PROC and PROC.poll() is None and LOADED and LOADED[:2]==(model,backend): return LOADED[2]
    stop(); failures=[]
    order=['CUDA','Vulkan','CPU'] if backend=='Auto' else ([backend,'CPU'] if backend!='CPU' else ['CPU'])
    for name in order:
        folder=ROOT/'runtime'/name.lower(); exe=folder/'llama-server.exe'
        if not exe.is_file(): failures.append(name+': runtime not installed'); continue
        env=os.environ.copy(); env['PATH']=str(folder)+os.pathsep+env.get('PATH','')
        device='none'
        if name!='CPU':
            try:
                probe=subprocess.run([str(exe),'--list-devices'],cwd=str(folder),env=env,capture_output=True,text=True,errors='replace',timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
                import re
                found=re.search(r'^\s*('+('CUDA' if name=='CUDA' else 'Vulkan')+r'\d+)\s*:',probe.stdout+probe.stderr,re.M)
                if not found: failures.append(name+': no supported device'); continue
                device=found.group(1)
            except Exception as e: failures.append(name+': '+str(e)); continue
        PORT=freeport(); (ROOT/'logs').mkdir(exist_ok=True)
        LOG=open(ROOT/'logs'/'runtime.log','wb')
        args=[str(exe),'-m',str(ROOT/'models'/model),'--host','127.0.0.1','--port',str(PORT),'-c','16384','-np','1','-ngl','0' if name=='CPU' else 'auto','--device',device,'--api-key',RUNTIME_TOKEN,'--jinja','--reasoning','auto','--reasoning-format','deepseek']
        PROC=subprocess.Popen(args,cwd=str(folder),env=env,stdout=LOG,stderr=LOG,creationflags=subprocess.CREATE_NO_WINDOW)
        if JOB: kernel.AssignProcessToJobObject(JOB,wt.HANDLE(PROC._handle))
        deadline=time.monotonic()+240
        while time.monotonic()<deadline and PROC.poll() is None:
            try:
                with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(PORT)+'/health',headers={'Authorization':'Bearer '+RUNTIME_TOKEN}),timeout=2) as response:
                    if response.status==200:
                        LOADED=(model,backend,name+' | '+device); return LOADED[2]
            except (OSError,urllib.error.URLError): time.sleep(.25)
        failures.append(name+': model load failed; see logs/runtime.log'); stop()
    raise ValueError('; '.join(failures))
class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args): pass
    def reply(self,status,obj):
        body=json.dumps(obj).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
    def allowed(self):
        expected='127.0.0.1:'+str(self.server.server_port)
        return self.headers.get('Host')==expected and self.headers.get('Origin','http://'+expected)=='http://'+expected and self.headers.get('Sec-Fetch-Site','same-origin') not in ['cross-site','same-site']
    def do_GET(self):
        if not self.allowed(): return self.reply(403,{'error':'Loopback same-origin access only.'})
        if self.path=='/native/info': return self.reply(200,{'token':TOKEN})
        if self.path=='/native/models':
            if not secrets.compare_digest(self.headers.get('X-ChessLLM-Token',''),TOKEN): return self.reply(403,{'error':'Invalid session token.'})
            return self.reply(200,{'models':models()})
        from urllib.parse import urlsplit,unquote
        relative=unquote(urlsplit(self.path).path).lstrip('/') or 'index.html'
        path=(WEB/relative).resolve()
        permitted=relative in ['index.html','styles.css','app.js','gemini.js','local.js','cpu.js','cpu-worker.js','README.md','LICENSE'] or relative.startswith(('assets/','vendor/','Licenses/'))
        if not permitted or not path.is_relative_to(WEB.resolve()) or not path.is_file(): return self.reply(404,{'error':'Not found'})
        import mimetypes
        data=path.read_bytes(); mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        if path.suffix=='.js': mime='text/javascript'
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if not self.allowed() or not secrets.compare_digest(self.headers.get('X-ChessLLM-Token',''),TOKEN): return self.reply(403,{'error':'Invalid origin or session token.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=1048576: return self.reply(413,{'error':'Request too large.'})
            body=json.loads(self.rfile.read(length))
            if self.path=='/native/quit':
                self.reply(200,{'ok':True}); threading.Thread(target=self.server.shutdown,daemon=True).start(); return
            if self.path=='/native/load':
                with LOCK: backend=load(body['model'],body['backend'])
                return self.reply(200,{'backend':backend})
            if self.path!='/native/generate': return self.reply(404,{'error':'Not found'})
            with LOCK:
                if not PROC or PROC.poll() is not None: return self.reply(409,{'error':'Load a model first.'})
                # Forward generation parameters only; the destination is fixed loopback.
                allowed={'messages','stream','stream_options','temperature','max_tokens','reasoning_budget_tokens','chat_template_kwargs','reasoning_effort','response_format'}
                body={k:v for k,v in body.items() if k in allowed};body['stream']=True
                request=urllib.request.Request('http://127.0.0.1:'+str(PORT)+'/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+RUNTIME_TOKEN})
                with urllib.request.urlopen(request,timeout=600) as upstream:
                    self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Cache-Control','no-store');self.send_header('Connection','close');self.end_headers();self.close_connection=True
                    while True:
                        line=upstream.readline()
                        if not line: break
                        self.wfile.write(line);self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError): pass
        except Exception as e:
            try: self.reply(500,{'error':str(e)})
            except OSError: pass

def main():
    (ROOT/'models').mkdir(exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    url='http://127.0.0.1:'+str(server.server_port)+'/'
    if '--no-browser' not in sys.argv: webbrowser.open(url)
    (ROOT/'logs').mkdir(exist_ok=True);(ROOT/'logs'/'desktop-url.txt').write_text(url)
    try: server.serve_forever()
    finally: server.server_close();stop()
if __name__=='__main__': main()
