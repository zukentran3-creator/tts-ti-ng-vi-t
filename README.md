# Kokoro Vietnamese TTS Web

Website chuyển văn bản tiếng Việt thành giọng nói bằng model ONNX [`contextboxai/Kokoro-Vietnamese`](https://huggingface.co/contextboxai/Kokoro-Vietnamese). App chạy cục bộ trên macOS hoặc Windows, không cần API key và có thể mở cho điện thoại trong cùng mạng Wi-Fi.

## Tính năng

- 14 giọng Kokoro tiếng Việt.
- Điều chỉnh tốc độ từ 0,6× đến 1,4×.
- Nghe trực tiếp và tải file WAV.
- Dùng `vig2p` để chuyển tiếng Việt thành âm vị.
- Tự tải model và voicepack từ Hugging Face ở lần sử dụng đầu tiên.
- Nạp model một lần và dùng lại cho các yêu cầu tiếp theo.
- Cache tối đa 8 kết quả nhỏ gần nhất trong RAM.
- Có giọng hệ thống của trình duyệt làm phương án dự phòng.
- Có launcher một chạm cho macOS và Windows.

## Yêu cầu hệ thống

- macOS hoặc Windows 10/11 64-bit.
- Python 3.10 trở lên; khuyên dùng **Python 3.11 64-bit**.
- RAM tối thiểu 4 GB; khuyên dùng 8 GB trở lên.
- Khoảng 3 GB dung lượng trống cho Python, thư viện, model và cache.
- Internet trong lần cài đặt và lần tải model đầu tiên.

Model ONNX khoảng 326 MB. Các thư viện như PyTorch cũng khá lớn, vì vậy lần cài đầu có thể mất nhiều phút.

## Cài và chạy trên macOS

### Cách nhanh nhất

1. Cài [Python 3.11](https://www.python.org/downloads/) nếu máy chưa có.
2. Giải nén hoặc chép toàn bộ repo vào một thư mục.
3. Nhấp đúp file `Chay-TTS.command`.
4. Terminal sẽ tự tạo `.venv`, cài thư viện và chạy server.
5. Trình duyệt tự mở tại <http://127.0.0.1:8000>.

Nếu macOS không cho mở file:

- Nhấp chuột phải vào `Chay-TTS.command`, chọn **Open/Mở**, rồi xác nhận.
- Hoặc mở Terminal trong thư mục repo và chạy:

```bash
chmod +x Chay-TTS.command Chay-TTS-LAN.command
./Chay-TTS.command
```

### Chạy thủ công trên macOS

```bash
cd "/đường/dẫn/tới/tts-viet-app"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python server.py
```

## Cài và chạy trên Windows

### Cách nhanh nhất

1. Tải và cài [Python 3.11 64-bit](https://www.python.org/downloads/windows/).
2. Trong trình cài Python, nhớ chọn **Add Python to PATH**.
3. Giải nén toàn bộ repo; không chạy file trực tiếp bên trong ZIP.
4. Nhấp đúp `Chay-TTS-Windows.bat`.
5. Command Prompt sẽ tự tạo `.venv`, cài thư viện và chạy server.
6. Trình duyệt tự mở tại <http://127.0.0.1:8000>.

Nếu Windows SmartScreen hiện cảnh báo, chỉ chọn **More info → Run anyway** khi repo đến từ nguồn bạn tin cậy.

Nếu đã thử bản cũ trước đây, hãy dùng ZIP mới và chạy lại launcher. Bản mới tự nhận biết dependency cũ; nếu vẫn lỗi, xóa thư mục ẩn `.venv` trong repo rồi nhấp đúp launcher để cài sạch.

### Chạy thủ công bằng Command Prompt

```bat
cd /d "C:\duong-dan\toi\tts-viet-app"
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python server.py
```

### Chạy thủ công bằng PowerShell

```powershell
cd "C:\duong-dan\toi\tts-viet-app"
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python server.py
```

## Cách sử dụng

1. Mở <http://127.0.0.1:8000>.
2. Chọn **Kokoro Vietnamese (ONNX)** trong mục Bộ đọc.
3. Chọn giọng đọc.
4. Nhập hoặc dán nội dung tiếng Việt.
5. Điều chỉnh tốc độ nếu cần.
6. Bấm **Đọc văn bản**.
7. Sau khi tạo xong, nghe trên trình phát hoặc bấm **Tải file WAV**.

Lần bấm đọc đầu tiên, app tải model và voicepack. Hãy giữ Terminal/Command Prompt mở và chờ tải xong. Những lần sau nhanh hơn vì model đã nằm trong cache và được giữ trong bộ nhớ khi server đang chạy.

Để dừng server, quay lại Terminal/Command Prompt và nhấn `Control+C`.

## Mở trên iPhone hoặc máy khác trong cùng Wi-Fi

Sau khi đã cài app một lần:

- macOS: nhấp đúp `Chay-TTS-LAN.command`.
- Windows: nhấp đúp `Chay-TTS-LAN-Windows.bat`.

Tìm địa chỉ IP của máy chạy server:

- macOS: vào **System Settings → Wi-Fi → Details**, xem **IP Address**.
- Windows: mở Command Prompt, chạy `ipconfig`, xem **IPv4 Address**.

Trên điện thoại hoặc máy khác, mở:

```text
http://IP-CUA-MAY-TINH:8000
```

Ví dụ: `http://192.168.1.25:8000`.

Hai thiết bị phải cùng mạng Wi-Fi. Nếu Windows Firewall hỏi quyền, cho phép trên **Private networks**. Không nên dùng chế độ LAN trên Wi-Fi công cộng.

## Các tùy chọn server

```text
python server.py [--host HOST] [--port PORT] [--device cpu|cuda] [--preload]
```

- `--host 127.0.0.1`: chỉ máy hiện tại truy cập được; đây là mặc định.
- `--host 0.0.0.0`: cho phép thiết bị trong mạng truy cập.
- `--port 8000`: đổi cổng web.
- `--device cpu`: chạy bằng CPU; mặc định trên macOS và Windows.
- `--device cuda`: dùng NVIDIA CUDA và ONNX Runtime GPU.
- `--preload`: tải model trước khi server nhận yêu cầu, phù hợp khi hosting.

Ví dụ:

```bash
python server.py --host 0.0.0.0 --port 8080 --preload
```

### Tùy chọn NVIDIA GPU trên Windows/Linux

GPU không bắt buộc. Nếu máy có NVIDIA CUDA tương thích, kích hoạt `.venv`, thay ONNX Runtime CPU bằng bản GPU rồi chạy:

```bash
python -m pip uninstall -y onnxruntime
python -m pip install -r requirements-gpu.txt
python server.py --device cuda --preload
```

macOS không hỗ trợ CUDA, vì vậy hãy giữ `--device cpu`. Phiên bản CUDA/cuDNN phải tương thích với phiên bản `onnxruntime-gpu`; xem tài liệu ONNX Runtime nếu quá trình import báo lỗi thư viện CUDA.

## Kiểm tra API

- `GET /api/health`: trạng thái thư viện, model và thiết bị xử lý.
- `GET /api/voices`: danh sách giọng.
- `POST /api/tts`: tạo WAV.

Ví dụ:

```bash
curl -X POST http://127.0.0.1:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào Việt Nam","voice":"diem_trinh","speed":1.0}' \
  --output audio.wav
```

## Chạy bằng Docker

Yêu cầu Docker Desktop hoặc Docker Engine:

```bash
docker compose up --build
```

Mở <http://127.0.0.1:8000>. Docker volume `kokoro-model-cache` giữ model để không phải tải lại khi container được tạo lại.

Để dừng:

```bash
docker compose down
```

Dockerfile mặc định chạy CPU. Triển khai GPU cần image CUDA tương thích, `onnxruntime-gpu`, cấp GPU cho container và chạy với `--device cuda`.

## Đưa lên Internet

Repo có thể chạy trên VPS hoặc máy chủ riêng bằng Docker. Khi mở công khai, nên đặt server sau reverse proxy HTTPS như Caddy hoặc Nginx và bổ sung:

- Domain và chứng chỉ HTTPS.
- Giới hạn số ký tự và rate limit.
- Hàng đợi khi có nhiều người dùng.
- Lưu/cache audio trên object storage.
- Ít nhất một worker luôn chạy để tránh cold start.

Server đi kèm phù hợp cho cá nhân, mạng nội bộ và thử nghiệm. Trước khi phục vụ lượng truy cập lớn, nên chuyển API inference sang FastAPI/Uvicorn hoặc một inference service chuyên dụng.

## Lỗi thường gặp

### Không tìm thấy Python

Cài Python 3.11 và mở lại Terminal/Command Prompt. Trên Windows, cài lại và chọn **Add Python to PATH**.

### Port 8000 đang được sử dụng

Đóng server cũ bằng `Control+C`, hoặc dùng cổng khác:

```bash
python server.py --port 8080
```

### Lần đầu đọc rất lâu

App có thể đang tải model 326 MB hoặc khởi tạo ONNX. Kiểm tra kết nối mạng và nội dung trong Terminal. Sau lần đầu, model được cache trên máy.

### Kokoro chưa được cài

Kích hoạt `.venv` rồi chạy:

```bash
python -m pip install -r requirements.txt
```

### Windows báo thiếu DLL

Cài Python 64-bit và [Microsoft Visual C++ Redistributable x64](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist). Sau đó xóa `.venv` và chạy lại launcher.

### Điện thoại không kết nối được

Kiểm tra server chạy với `--host 0.0.0.0`, hai thiết bị cùng Wi-Fi và firewall cho phép Python trên mạng riêng.

## Cấu trúc repo

```text
.
├── Doc-Tieng-Viet.html          Giao diện web
├── app.js                       Logic giao diện và gọi API
├── server.py                    Web server và Kokoro ONNX inference
├── requirements.txt             Thư viện Python
├── requirements-gpu.txt         Thư viện cho NVIDIA GPU
├── Chay-TTS.command             Launcher macOS
├── Chay-TTS-LAN.command         Launcher macOS cho mạng LAN
├── Chay-TTS-Windows.bat         Launcher Windows
├── Chay-TTS-LAN-Windows.bat     Launcher Windows cho mạng LAN
├── Dockerfile                   Image CPU để triển khai
├── docker-compose.yml           Chạy bằng Docker Compose
├── LICENSE                      Apache License 2.0
└── NOTICE.md                    Nguồn, thay đổi và dependency bên thứ ba
```

## License

Mã nguồn ứng dụng trong repo này được phát hành theo [Apache License 2.0](LICENSE).

Ứng dụng sử dụng model `contextboxai/Kokoro-Vietnamese` và luồng ONNX được điều chỉnh từ `iamdinhthuan/Kokoro-Vietnamese`. Hai nguồn upstream đều công bố Apache License 2.0. Model và voicepack không được commit vào repo; chúng được tải riêng vào Hugging Face cache khi sử dụng lần đầu.

Khi sao chép, sửa hoặc phân phối repo, hãy giữ lại `LICENSE` và `NOTICE.md`, đồng thời ghi chú rõ các file đã thay đổi. Các thư viện được cài qua `requirements.txt` vẫn tuân theo giấy phép riêng của từng dự án. Xem thông tin nguồn và phần đã điều chỉnh trong [NOTICE.md](NOTICE.md).
