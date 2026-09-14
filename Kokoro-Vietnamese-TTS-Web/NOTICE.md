# Third-party notices

## Kokoro Vietnamese

This product uses model artifacts from:

- Project: `contextboxai/Kokoro-Vietnamese`
- Source: https://huggingface.co/contextboxai/Kokoro-Vietnamese
- License identified by the publisher: Apache License 2.0

The model, configuration, and voicepacks are downloaded separately from
Hugging Face when the application is first used. They are not included in
this repository or its release ZIP.

The ONNX inference flow in `server.py` was adapted from concepts and code in:

- Project: `iamdinhthuan/Kokoro-Vietnamese`
- Source: https://github.com/iamdinhthuan/Kokoro-Vietnamese
- License: Apache License 2.0

Modifications made for this application include the local HTTP API, direct
ONNX Runtime integration, multi-voice loading, WAV generation, in-memory
response caching, browser UI integration, and macOS/Windows launchers.

## Other dependencies

Runtime dependencies such as ONNX Runtime, PyTorch, Hugging Face Hub,
SoundFile, NumPy, `vig2p`, and `sea-g2p` remain subject to their own licenses.
Their inclusion as dependencies does not change those licenses.

This NOTICE file is informational and does not modify the terms of the
Apache License 2.0 contained in `LICENSE`.
