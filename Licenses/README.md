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
