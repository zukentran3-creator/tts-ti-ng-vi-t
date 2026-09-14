#!/usr/bin/env python3
"""Local web server for the Vietnamese Kokoro TTS demo."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import threading
import traceback
from collections import OrderedDict
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MAX_TEXT_LENGTH = 10_000
MODEL_REPO = "contextboxai/Kokoro-Vietnamese"
SAMPLE_RATE = 24_000
VOICE_FILES = {
    voice: f"voicepacks/{voice}.pt" for voice in (
        "diem_trinh", "hung_thinh", "mai_linh", "mai_loan", "manh_dung",
        "my_yen", "ngoc_huyen", "phat_tai", "thanh_dat", "thuc_trinh",
        "tuan_ngoc", "storyvert", "duc_an", "duc_duy",
    )
}

VOICES = {
    "diem_trinh": "Diễm Trinh", "hung_thinh": "Hưng Thịnh",
    "mai_linh": "Mai Linh", "mai_loan": "Mai Loan", "manh_dung": "Mạnh Dũng",
    "my_yen": "Mỹ Yến", "ngoc_huyen": "Ngọc Huyền", "phat_tai": "Phát Tài",
    "thanh_dat": "Thành Đạt", "thuc_trinh": "Thục Trinh", "tuan_ngoc": "Tuấn Ngọc",
    "storyvert": "Storyvert", "duc_an": "Đức An", "duc_duy": "Đức Duy",
}


class KokoroEngine:
    """Load the 326 MB ONNX model once and cache the small voicepacks."""

    def __init__(self, device: str = "cpu", cache_size: int = 8) -> None:
        self.device = device
        self.cache_size = cache_size
        self._model: Any | None = None
        self._voicepacks: dict[str, Any] = {}
        self._audio_cache: OrderedDict[str, bytes] = OrderedDict()
        self._lock = threading.Lock()

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def _ensure_model(self) -> Any:
        if self._model is None:
            import onnxruntime as ort
            from huggingface_hub import hf_hub_download

            model_path = hf_hub_download(MODEL_REPO, "kokoro_vi.onnx")
            config_path = hf_hub_download(MODEL_REPO, "config.json")
            with open(config_path, encoding="utf-8") as config_file:
                config = json.load(config_file)

            options = ort.SessionOptions()
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            available = ort.get_available_providers()
            if self.device == "cuda" and "CUDAExecutionProvider" in available:
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            else:
                providers = ["CPUExecutionProvider"]
                self.device = "cpu"

            self._model = {
                "session": ort.InferenceSession(
                    str(model_path), sess_options=options, providers=providers
                ),
                "vocab": config["vocab"],
                "context_length": config["plbert"]["max_position_embeddings"],
            }
            self._load_voice("diem_trinh")
        return self._model

    def preload(self) -> None:
        with self._lock:
            self._ensure_model()

    def _load_voice(self, voice: str) -> Any:
        if voice in self._voicepacks:
            return self._voicepacks[voice]
        import torch
        from huggingface_hub import hf_hub_download

        path = hf_hub_download(MODEL_REPO, VOICE_FILES[voice])
        voicepack = torch.load(path, map_location="cpu", weights_only=True)
        self._voicepacks[voice] = voicepack
        return voicepack

    @staticmethod
    def _split_text(text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text.strip())
        if not normalized:
            return []
        chunks: list[str] = []
        start = 0
        for match in re.finditer(r'[.!?…]+(?:["”’)]*)', normalized):
            end = match.end()
            if end < len(normalized) and not normalized[end].isspace():
                continue
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
        remainder = normalized[start:].strip()
        if remainder:
            chunks.append(remainder)
        return chunks

    @staticmethod
    def _merge_audio(chunks: list[Any], crossfade_samples: int) -> Any:
        import numpy as np

        valid = [np.asarray(chunk, dtype=np.float32) for chunk in chunks if len(chunk)]
        if not valid:
            return np.array([], dtype=np.float32)
        merged = valid[0]
        for chunk in valid[1:]:
            overlap = min(crossfade_samples, len(merged), len(chunk))
            if overlap <= 0:
                merged = np.concatenate([merged, chunk])
                continue
            fade_out = np.linspace(1.0, 0.0, overlap + 2, dtype=np.float32)[1:-1]
            crossfaded = merged[-overlap:] * fade_out + chunk[:overlap] * (1.0 - fade_out)
            merged = np.concatenate([merged[:-overlap], crossfaded, chunk[overlap:]])
        return merged.astype(np.float32, copy=False)

    def _run_model(self, text: str, voice: str, speed: float) -> Any:
        import numpy as np
        from vig2p import phonemize_text

        model = self._ensure_model()
        voicepack = self._load_voice(voice)
        audio_chunks = []
        for text_chunk in self._split_text(text):
            phonemes = phonemize_text(text_chunk)
            if not phonemes:
                continue
            token_ids = [model["vocab"][symbol] for symbol in phonemes if symbol in model["vocab"]]
            if len(token_ids) + 2 > model["context_length"]:
                raise ValueError(
                    "Một câu quá dài. Hãy thêm dấu chấm để chia nội dung thành nhiều câu ngắn hơn."
                )
            input_ids = np.asarray([[0, *token_ids, 0]], dtype=np.int64)
            voice_array = voicepack.detach().cpu().numpy() if hasattr(voicepack, "detach") else voicepack
            voice_array = np.asarray(voice_array, dtype=np.float32)
            style_index = min(len(phonemes), voice_array.shape[0]) - 1
            ref_s = np.asarray(voice_array[style_index], dtype=np.float32)
            waveform, _duration = model["session"].run(None, {
                "input_ids": input_ids,
                "ref_s": ref_s,
                "speed": np.asarray(float(speed), dtype=np.float32),
            })
            audio_chunks.append(np.asarray(waveform, dtype=np.float32).reshape(-1))
        return self._merge_audio(audio_chunks, round(SAMPLE_RATE * 0.05))

    def synthesize(self, text: str, voice: str, speed: float) -> bytes:
        cache_key = hashlib.sha256(
            f"v1\0{voice}\0{speed:.2f}\0{text}".encode("utf-8")
        ).hexdigest()
        # Upstream stores the active voicepack on the model, so keep this atomic.
        with self._lock:
            cached = self._audio_cache.get(cache_key)
            if cached is not None:
                self._audio_cache.move_to_end(cache_key)
                return cached
            audio = self._run_model(text, voice, speed)
        if len(audio) == 0:
            raise RuntimeError("Model không tạo được âm thanh từ nội dung này.")
        import soundfile as sf
        output = io.BytesIO()
        sf.write(output, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        wav = output.getvalue()
        # Avoid keeping very long recordings in RAM. Smaller repeated requests
        # are cached for an immediate response.
        if len(wav) <= 10_000_000:
            with self._lock:
                self._audio_cache[cache_key] = wav
                self._audio_cache.move_to_end(cache_key)
                while len(self._audio_cache) > self.cache_size:
                    self._audio_cache.popitem(last=False)
        return wav


ENGINE = KokoroEngine()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _json(self, data: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            self.path = "/Doc-Tieng-Viet.html"
        if self.path == "/api/voices":
            self._json({"engine": "contextboxai/Kokoro-Vietnamese", "voices": [
                {"id": voice_id, "name": name} for voice_id, name in VOICES.items()
            ]})
            return
        if self.path == "/api/health":
            try:
                import huggingface_hub  # noqa: F401
                import numpy  # noqa: F401
                import onnxruntime  # noqa: F401
                import soundfile  # noqa: F401
                import torch  # noqa: F401
                import vig2p  # noqa: F401
            except Exception as exc:
                self._json({"ready": False, "loaded": False, "error": str(exc)})
            else:
                self._json({
                    "ready": True,
                    "loaded": ENGINE.loaded,
                    "device": ENGINE.device,
                })
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/tts":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                raise ValueError("Dữ liệu gửi lên không hợp lệ.")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Dữ liệu JSON phải là một object.")
            text = str(payload.get("text", "")).strip()
            voice = str(payload.get("voice", "diem_trinh"))
            speed = float(payload.get("speed", 1.0))
            if not text:
                raise ValueError("Bạn chưa nhập nội dung cần đọc.")
            if len(text) > MAX_TEXT_LENGTH:
                raise ValueError(f"Nội dung tối đa {MAX_TEXT_LENGTH:,} ký tự.")
            if voice not in VOICES:
                raise ValueError("Giọng đọc không hợp lệ.")
            if not 0.6 <= speed <= 1.4:
                raise ValueError("Tốc độ phải từ 0,6 đến 1,4.")
            audio = ENGINE.synthesize(text, voice, speed)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            traceback.print_exc()
            self._json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(audio)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Disposition", 'inline; filename="kokoro-vietnamese.wav"')
        self.end_headers()
        self.wfile.write(audio)


def main() -> None:
    parser = argparse.ArgumentParser(description="Kokoro Vietnamese TTS web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument(
        "--preload", action="store_true",
        help="Download and load the model before accepting requests",
    )
    args = parser.parse_args()
    ENGINE.device = args.device
    if args.preload:
        print("Đang tải Kokoro Vietnamese vào bộ nhớ...")
        ENGINE.preload()
        print("Model đã sẵn sàng.")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    display_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    print(f"Kokoro Vietnamese TTS: http://{display_host}:{args.port}")
    if not args.preload:
        print("Lần đọc đầu tiên sẽ tải model ONNX khoảng 326 MB.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
