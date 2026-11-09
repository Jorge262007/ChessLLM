# ChessLLM

One English-language chess interface for GitHub Pages and Windows desktop: dark theme, real SVG pieces, animated moves, move history, live model output and token telemetry.

## Play

- **AI vs CPU**, **Player vs CPU** and **Player vs AI**.
- Five browser CPU difficulty levels. This chess opponent is separate from the compute backend used to run a language model.
- **Gemini**: enter your own API key and model ID, then use Test key. API access, availability and billing depend on Google. The key stays in memory in this tab and is sent directly to Google.
- **Local GGUF**: run the Windows package, place a compatible GGUF file in its `models` folder, select Local GGUF and Refresh models. No model or API key is distributed.
- **Auto / CUDA / Vulkan / CPU**: Auto tries CUDA, Vulkan, then CPU. An explicitly selected GPU falls back to CPU if it cannot load. The loaded backend is displayed. CUDA needs a compatible NVIDIA GPU and driver; Vulkan needs a compatible driver; CPU runs without a GPU. These Windows x64 builds do not guarantee compatibility with every processor or model.
- **High / Medium / Low / Off** remains editable during play. Local token budgets are 4096 / 2048 / 512 / 0; the model must support thinking. Gemini uses HIGH / MEDIUM / LOW / MINIMAL, so Off means minimal thinking without summaries.
- Separate **Gemini system prompt** and **Local model system prompt** editors remain editable during play. A prompt and thinking setting are captured when each AI move starts. Edits made during generation apply to the next AI move, including retries using the captured prompt.
- Every AI move receives the updated 8 x 8 board, FEN, legal moves, history and attacked pieces. Default instructions ask for tactical threats and one or two moves of lookahead; this is a prompt, not a guarantee of chess strength. Final moves must be legal JSON moves.
- Match mode, side, difficulty, model and compute backend lock during a match. Pause stops applying/displaying the next move; active inference may finish in the background. Stop unlocks match settings.

## Live page

[Play ChessLLM online](https://jorge262007.github.io/chessllm/)

Pages supports Gemini and the browser chess CPU. Browsers cannot directly load native CUDA or Vulkan DLLs. To run a local GGUF, open **ChessLLM.exe** from the desktop package: it serves this exact same HTML, CSS, images and JavaScript on loopback and opens your browser. The interface and features are shared, including both prompt editors. No separate desktop UI is maintained.

## Windows download / GitHub Releases

The prepared release is beside this repository at `E:\ChessLLM-Releases\ChessLLM-Windows-x64.zip`. Upload that ZIP as an asset of a **GitHub Release**, not as a repository file. Extract the entire ZIP, then double-click `ChessLLM.exe`. Keep its `web`, `runtime`, `Licenses` and `models` folders beside it. The EXE alone does not include the native DLLs.

The portable package includes CPU, Vulkan and CUDA runtimes but no weights, keys, game records or runtime logs. Large model files and CUDA DLLs do not belong in the git repository. Do not upload the sibling download-cache/build folders. The executable is unsigned; Windows may show a publisher warning.

## Build and test

Web checks: `node tests.mjs` (Node 22 or newer). Serve this folder over HTTP for local web use; opening a file URL is not supported for module workers.

Windows build: Python 3.10 or newer, `py -3.10 -m pip install pyinstaller==6.22.3`, then `py -3.10 desktop/build.py`. Downloads are pinned by URL and SHA-256 in `desktop/runtime-manifest.json`. Build output goes to the sibling `ChessLLM-Releases` folder. The manual Windows workflow also produces a downloadable ZIP artifact; it does not publish a release automatically.

The companion binds only to 127.0.0.1, validates Host/Origin, requires a random session token for model access, serves an allowlist of web files, and forwards inference only to its own loopback llama-server. It does not expose a LAN API. Closing the browser tab does not exit the companion; use **Exit desktop** in the interface. Logs are written only to the portable package's `logs` directory.

## Licenses

Original ChessLLM web and companion source: **MIT**, see LICENSE. chess.js: BSD-2-Clause; Fantasy chess artwork by Maurizio Monge: MIT. Native llama.cpp: MIT, LLVM OpenMP: its bundled license, Python: PSF license, PyInstaller: GPL with its distribution exception. CUDA libraries retain NVIDIA terms and are not relicensed under MIT. See `Licenses/README.md` and the individual notices. Model licenses depend on the GGUF you download; Google services have their own terms. The new companion does not bundle python-chess or Stockfish.
