# Licenses and third-party credits

| Component | License | Copyright and source |
|---|---|---|
| ChessLLM original web code, styles, CPU search, tests and documentation | MIT; ../LICENSE and MIT.txt | Copyright (c) 2026 ChessLLM contributors |
| chess.js 1.4.0 | BSD-2-Clause; chess.js-BSD-2-Clause.txt | Jeff Hlywa and contributors; https://github.com/jhlywa/chess.js/tree/v1.4.0 |
| Fantasy chess artwork | MIT; chess-art-MIT.txt | Maurizio Monge; https://github.com/maurimo/chess-art ; exact asset URLs/hashes in ../vendor/manifest.json |
| Google Gemini API | External service terms; Gemini-Service-Notice.md | No Google model weights or SDK are bundled |

Keep these upstream license notices when redistributing. MIT does not replace the separate BSD terms of chess.js or Google's service terms. The included SVG pieces replace the previously GPL-licensed Cburnett images. The historical desktop app is separate from this new MIT companion. Its GPL chess engine and artwork are not included here.

## Optional Windows distribution

Original companion source is MIT. The Windows release also includes llama.cpp (MIT), LLVM OpenMP, Python (PSF), PyInstaller (GPL with executable distribution exception) and NVIDIA CUDA redistributables under their respective notices in this directory. Those third-party terms remain in force; the project MIT license does not replace them. Runtime upstream URLs and checksums are pinned in desktop/runtime-manifest.json. CUDA redistribution terms are supplied in NVIDIA-CUDA-EULA.html. Models are not included.

## Restored desktop artwork and browser engine

The displayed PNG pieces are the exact original desktop Wikipedia/Cburnett images by Colin M. L. Burnett, from https://github.com/oakmac/chessboardjs/tree/master/website/img/chesspieces/wikipedia. They are GPL-2.0-or-later, redistributed under GPLv3. See GPL-3.0.txt and cburnett-source-credits.md; editable SVG sources are included in assets/pieces/cburnett-source/. The original ChessLLM application source remains MIT; the artwork is separately licensed. Earlier statements about replacement of Cburnett refer to previous releases.

wllama 3.13.0 (Xuan Son NGUYEN and contributors) is MIT as declared in its upstream package metadata, bundled in vendor/wllama/package.json. See wllama-MIT.txt and llama.cpp-MIT.txt. Upstream: https://github.com/ngxson/wllama. The browser engine and WASM are bundled locally and run on CPU.
