// SPDX-License-Identifier: MIT
import {sse,instructions} from './gemini.js';
let token='',engine=null,busy=false,loadedFiles=null;
const $=id=>document.getElementById(id);
export const localBusy=()=>busy;
function setBusy(value){busy=value;window.dispatchEvent(new Event('local-state'))}
async function api(path,body,signal){const r=await fetch('/native/'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json','X-ChessLLM-Token':token},body:body?JSON.stringify(body):undefined,signal});if(!r.ok){let e;try{e=(await r.json()).error}catch{}throw Error(e||'Desktop service HTTP '+r.status)}return r}
export async function initializeNative(){
 const status=$('nativeStatus');
 $('ggufFile').onchange=()=>{const files=[...$('ggufFile').files];$('localModel').replaceChildren(new Option(files.map(f=>f.name).join(' + ')||'Choose a GGUF file',files.length?'browser':''));status.textContent=files.length?'Selected '+files.map(f=>f.name).join(' + ')+'. Click Load selected GGUF. Browser CPU; files stay on your device.':'Choose a GGUF file.'};
 $('loadGGUF').onclick=()=>loadBrowser().catch(e=>status.textContent='Model load failed: '+e.message);
 $('unloadGGUF').onclick=async()=>{setBusy(true);try{if(engine)await engine.exit();engine=null;loadedFiles=null;status.textContent='Model unloaded. You can choose another GGUF.'}catch(e){status.textContent=e.message}finally{setBusy(false)}};
 if(!['127.0.0.1','localhost'].includes(location.hostname))return;
 let info;try{const response=await fetch('/native/info');if(!response.ok)return;info=await response.json();if(!info.token)return}catch{return}
 token=info.token;$('exitDesktop').hidden=false;$('exitDesktop').onclick=async()=>{if(!confirm('Exit ChessLLM desktop?'))return;await api('quit',{});status.textContent='Desktop closed.'};
 $('refreshModels').hidden=false;const refresh=async()=>{const data=await(await api('models')).json();$('localModel').replaceChildren(new Option('Choose a GGUF file',''));for(const name of data.models)$('localModel').add(new Option(name,name));status.textContent='Choose a file for browser CPU, or select a model from the desktop models folder (native CPU).'};$('refreshModels').onclick=()=>refresh().catch(e=>status.textContent=e.message);await refresh();
}
async function loadBrowser(signal){
 const files=[...$('ggufFile').files];if(!files.length)throw Error('Choose a GGUF file first.');
 if(files.reduce((n,f)=>n+f.size,0)>2*1024**3)throw Error('This browser CPU mode supports small GGUF models up to 2 GiB. Use a smaller quantization or the desktop native CPU model list.');
 if(files.some(f=>!f.name.toLowerCase().endsWith('.gguf')))throw Error('Select only GGUF files.');
 if(loadedFiles&&files.length===loadedFiles.length&&files.every((f,i)=>f===loadedFiles[i]))return;
 setBusy(true);try{
 $('nativeStatus').textContent='Initializing browser CPU and reading GGUF...';
 if(engine)await engine.exit();engine=null;loadedFiles=null;
 const {Wllama}=await import('./vendor/wllama/index.js');
 engine=new Wllama({default:new URL('./vendor/wllama/wllama.wasm',import.meta.url).href},{logger:{debug(){},log(){},warn(){},error(...args){console.error(...args)}}});
 engine.setCompat(null);
 await engine.loadModel(files,{n_ctx:8192,n_batch:128,n_threads:1,n_gpu_layers:0,n_parallel:1,jinja:true,reasoning_format:'deepseek'});
 if(!engine.getLoadedContextInfo().n_vocab)throw Error('The model could not load: insufficient browser memory or unsupported GGUF. Try a smaller model.');
 if(signal?.aborted){await engine.exit();engine=null;throw new DOMException('Stopped','AbortError')}
 loadedFiles=files;$('nativeStatus').textContent='Loaded | Browser CPU (WebAssembly) | '+files.map(f=>f.name).join(' + ');
 }catch(e){if(engine)try{await engine.exit()}catch{}engine=null;loadedFiles=null;throw e}finally{setBusy(false)}
}
export function localPayload(state,level,prompt,correction=''){return {messages:[{role:'system',content:(prompt||instructions(level))+' Return only JSON {"move":"e2e4"} using legal_moves_uci.'},{role:'user',content:JSON.stringify(state)+(correction?' Previous answer invalid: '+correction:'')}],stream:true,stream_options:{include_usage:true},temperature:.6,max_tokens:8192,reasoning_budget_tokens:{High:4096,Medium:2048,Low:512,Off:0}[level],chat_template_kwargs:{enable_thinking:level!=='Off'},...(level==='Off'?{reasoning_effort:'none'}:{}),response_format:{type:'json_schema',json_schema:{name:'chess_move',strict:true,schema:{type:'object',properties:{move:{type:'string',enum:state.legal_moves_uci}},required:['move'],additionalProperties:false}}}}}
export async function generateLocal(key,model,state,level,signal,wait,onChunk,correction='',prompt=''){
 let stream;
 const request=localPayload(state,level,prompt,correction);
 if(model==='browser'){
  await loadBrowser(signal);await wait();
  $('nativeStatus').textContent='Browser CPU | processing board and generating; this can take a few minutes.';
  stream=await engine.createChatCompletion({...request,abortSignal:signal});
 }else{
  if(!token)throw Error('Choose a GGUF file from your computer and click Load selected GGUF.');
  if(!model)throw Error('Choose a GGUF file or a desktop model.');
  const ready=await(await api('load',{model,backend:'CPU'},signal)).json();$('nativeStatus').textContent='Loaded | '+ready.backend;
  stream=sse((await api('generate',request,signal)).body);
 }
 let text='',summary='',tokens=0;const start=performance.now();
 for await(const chunk of stream){await wait();if(signal.aborted)throw new DOMException('Stopped','AbortError');if(chunk.error)throw Error(chunk.error.message||chunk.error);const delta=chunk.choices?.[0]?.delta||{};const thought=delta.reasoning_content||'',answer=delta.content||'';text+=answer;summary+=thought;tokens=chunk.usage?.completion_tokens||tokens+(thought||answer?1:0);onChunk(thought,answer,{tokens,rate:tokens?tokens/Math.max(.001,(performance.now()-start)/1000):null})}
 const cleaned=text.replace(/<think>[\s\S]*?<\/think>/g,'').replace(/^```(?:json)?\s*|\s*```$/g,'').trim();
 const move=JSON.parse(cleaned).move;if(!state.legal_moves_uci.includes(move))throw Error('Local model returned an illegal move.');return {move,summary};
}
