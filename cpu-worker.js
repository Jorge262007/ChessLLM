// SPDX-License-Identifier: MIT
import {chooseCPU} from './cpu.js';
self.onmessage=e=>{try{self.postMessage({move:chooseCPU(e.data.fen,e.data.level)})}catch(error){self.postMessage({error:error.message})}};
