'use strict';

const textInput = document.querySelector('#text');
const engineSelect = document.querySelector('#engine');
const voiceSelect = document.querySelector('#voice');
const rateInput = document.querySelector('#rate');
const rateValue = document.querySelector('#rateValue');
const playButton = document.querySelector('#play');
const stopButton = document.querySelector('#stop');
const statusLine = document.querySelector('#status');
const clearButton = document.querySelector('#clearText');
const keepAwakeInput = document.querySelector('#keepAwake');
const wakeHint = document.querySelector('#wakeHint');
const audioPlayer = document.querySelector('#audio');
const downloadLink = document.querySelector('#download');
const synth = window.speechSynthesis;

let vietnameseVoices = [];
let kokoroVoices = [];
let generation = 0;
let currentUtterance = null;
let startTimer;
let wakeLock = null;
let audioUrl = '';
let requestController = null;
const isIOS = /iP(?:hone|ad|od)/.test(navigator.userAgent)
  || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

function status(message, error = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle('error', error);
}

function updateCount() {
  document.querySelector('#count').textContent = `${textInput.value.length.toLocaleString('vi-VN')} ký tự`;
  clearButton.disabled = textInput.value.length === 0;
}

function deviceVoiceOptions(selected = '') {
  if (!synth) return;
  vietnameseVoices = synth.getVoices().filter((voice) => /^vi(?:[-_]|$)/i.test(voice.lang));
  voiceSelect.replaceChildren(new Option('Tiếng Việt mặc định của thiết bị', ''));
  vietnameseVoices.forEach((voice) => voiceSelect.add(new Option(voice.name, voice.voiceURI)));
  if (vietnameseVoices.some((voice) => voice.voiceURI === selected)) voiceSelect.value = selected;
}

function kokoroVoiceOptions(selected = 'diem_trinh') {
  voiceSelect.replaceChildren();
  kokoroVoices.forEach((voice) => voiceSelect.add(new Option(voice.name, voice.id)));
  if ([...voiceSelect.options].some((option) => option.value === selected)) voiceSelect.value = selected;
}

function updateVoiceOptions() {
  const selected = voiceSelect.value;
  if (engineSelect.value === 'kokoro') kokoroVoiceOptions(selected);
  else deviceVoiceOptions(selected);
}

function busy(value) {
  stopButton.disabled = !value;
  playButton.disabled = value;
  textInput.readOnly = value;
  engineSelect.disabled = value;
  voiceSelect.disabled = value;
  rateInput.disabled = value;
}

async function requestWakeLock() {
  if (!keepAwakeInput.checked || !('wakeLock' in navigator)
      || document.visibilityState !== 'visible' || wakeLock) return;
  const requestedGeneration = generation;
  try {
    const lock = await navigator.wakeLock.request('screen');
    if (generation !== requestedGeneration || !keepAwakeInput.checked) {
      await lock.release();
      return;
    }
    wakeLock = lock;
    lock.addEventListener('release', () => {
      if (wakeLock === lock) wakeLock = null;
    });
    wakeHint.textContent = 'Màn hình sẽ được giữ sáng cho đến khi đọc xong.';
    wakeHint.classList.remove('warn');
  } catch {
    wakeHint.textContent = 'Safari chưa cho phép giữ màn hình sáng. Đừng khóa màn hình khi đang đọc.';
    wakeHint.classList.add('warn');
  }
}

function releaseWakeLock() {
  const lock = wakeLock;
  wakeLock = null;
  if (lock) lock.release().catch(() => {});
  wakeHint.textContent = 'Bật để Safari không tự khóa màn hình giữa chừng.';
  wakeHint.classList.remove('warn');
}

function clearAudio() {
  audioPlayer.pause();
  audioPlayer.removeAttribute('src');
  audioPlayer.classList.remove('ready');
  downloadLink.classList.remove('ready');
  downloadLink.removeAttribute('href');
  if (audioUrl) URL.revokeObjectURL(audioUrl);
  audioUrl = '';
}

function stop(message = 'Đã dừng đọc') {
  generation += 1;
  clearTimeout(startTimer);
  if (synth) synth.cancel();
  if (requestController) requestController.abort();
  requestController = null;
  currentUtterance = null;
  audioPlayer.pause();
  releaseWakeLock();
  busy(false);
  status(message);
}

function clearText() {
  stop('Đã dừng và xóa nội dung');
  clearAudio();
  textInput.value = '';
  updateCount();
  textInput.focus();
}

function chunksOf(value) {
  if (isIOS) return [value];
  const chunks = [];
  let rest = value;
  while (rest.length > 180) {
    const head = rest.slice(0, 180);
    const sentence = [...head.matchAll(/[.!?;\n](?:\s|$)/g)].pop();
    let end = sentence ? sentence.index + 1 : head.lastIndexOf(' ');
    if (end < 40) end = 180;
    chunks.push(rest.slice(0, end));
    rest = rest.slice(end);
  }
  if (rest) chunks.push(rest);
  return chunks;
}

function startDevice(value) {
  if (!synth || !window.SpeechSynthesisUtterance) {
    status('Trình duyệt này chưa hỗ trợ giọng của thiết bị.', true);
    return;
  }
  deviceVoiceOptions(voiceSelect.value);
  const voice = vietnameseVoices.find((item) => item.voiceURI === voiceSelect.value) || vietnameseVoices[0];
  const parts = chunksOf(value);
  const token = generation;
  let index = 0;
  busy(true);
  function next() {
    if (token !== generation) return;
    if (index >= parts.length) {
      currentUtterance = null;
      releaseWakeLock();
      busy(false);
      status('Đã đọc xong');
      return;
    }
    const utterance = new SpeechSynthesisUtterance(parts[index]);
    currentUtterance = utterance;
    utterance.lang = 'vi-VN';
    if (voice) utterance.voice = voice;
    utterance.rate = Number(rateInput.value);
    utterance.onstart = () => {
      clearTimeout(startTimer);
      status(parts.length === 1 ? 'Đang đọc' : `Đang đọc · ${index + 1}/${parts.length}`);
    };
    utterance.onend = () => { index += 1; next(); };
    utterance.onerror = (event) => {
      if (token !== generation) return;
      stop();
      const messages = {
        'language-unavailable': 'Thiết bị chưa có giọng tiếng Việt.',
        'voice-unavailable': 'Giọng này chưa dùng được. Chọn giọng mặc định rồi thử lại.',
        'not-allowed': 'Bấm Đọc văn bản để cho phép phát âm thanh.',
      };
      status(messages[event.error] || 'Chưa phát được giọng đọc của thiết bị.', true);
    };
    startTimer = setTimeout(() => {
      if (token === generation) {
        stop();
        status('Giọng đọc chưa khởi động. Kiểm tra giọng tiếng Việt trong Cài đặt.', true);
      }
    }, 12000);
    synth.speak(utterance);
    if (index === 0) requestWakeLock();
  }
  next();
}

async function startKokoro(value) {
  const token = generation;
  clearAudio();
  busy(true);
  requestController = new AbortController();
  status('Đang tạo audio bằng Kokoro… Lần đầu có thể mất vài phút.');
  requestWakeLock();
  try {
    const response = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: value, voice: voiceSelect.value, speed: Number(rateInput.value) }),
      signal: requestController.signal,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || `Máy chủ trả về lỗi ${response.status}.`);
    }
    const blob = await response.blob();
    if (token !== generation) return;
    audioUrl = URL.createObjectURL(blob);
    audioPlayer.src = audioUrl;
    downloadLink.href = audioUrl;
    audioPlayer.classList.add('ready');
    downloadLink.classList.add('ready');
    try {
      await audioPlayer.play();
      status('Đang phát giọng Kokoro');
    } catch {
      // Some browsers expire the original click permission while the server is
      // generating audio. The WAV is valid; the user only needs to press play.
      status('Đã tạo audio. Bấm nút ▶ trên thanh nghe để phát.');
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      status(`Chưa tạo được audio: ${error.message}`, true);
      releaseWakeLock();
    }
  } finally {
    if (token === generation) {
      requestController = null;
      busy(false);
      stopButton.disabled = audioPlayer.paused;
    }
  }
}

function start() {
  const value = textInput.value.trim();
  if (!value) {
    status('Bạn nhập một đoạn tiếng Việt trước nhé.', true);
    textInput.focus();
    return;
  }
  stop('Đang chuẩn bị giọng đọc…');
  if (engineSelect.value === 'kokoro') startKokoro(value);
  else startDevice(value);
}

async function loadKokoro() {
  try {
    const [voiceResponse, healthResponse] = await Promise.all([
      fetch('/api/voices'), fetch('/api/health'),
    ]);
    if (!voiceResponse.ok) throw new Error('Không kết nối được máy chủ Kokoro.');
    kokoroVoices = (await voiceResponse.json()).voices;
    const health = await healthResponse.json();
    kokoroVoiceOptions();
    if (!health.ready) {
      engineSelect.value = 'device';
      updateVoiceOptions();
      status('Kokoro chưa được cài. App đang dùng giọng của thiết bị.', true);
    } else {
      status('Kokoro Vietnamese đã sẵn sàng');
    }
  } catch {
    engineSelect.value = 'device';
    updateVoiceOptions();
    status('Mở app bằng python server.py để dùng Kokoro. Hiện đang dùng giọng của thiết bị.');
  }
}

updateCount();
textInput.addEventListener('input', updateCount);
clearButton.addEventListener('click', clearText);
engineSelect.addEventListener('change', () => { stop(); clearAudio(); updateVoiceOptions(); });
rateInput.addEventListener('input', () => { rateValue.value = `${Number(rateInput.value).toLocaleString('vi-VN')}×`; });
stopButton.addEventListener('click', () => stop());
playButton.addEventListener('click', start);
audioPlayer.addEventListener('play', () => { stopButton.disabled = false; requestWakeLock(); status('Đang phát giọng Kokoro'); });
audioPlayer.addEventListener('pause', () => { if (!requestController) stopButton.disabled = true; releaseWakeLock(); });
audioPlayer.addEventListener('ended', () => { busy(false); releaseWakeLock(); status('Đã phát xong'); });
keepAwakeInput.addEventListener('change', () => {
  if (!keepAwakeInput.checked) releaseWakeLock();
  else if (currentUtterance || !audioPlayer.paused) requestWakeLock();
});
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && (currentUtterance || !audioPlayer.paused)) requestWakeLock();
});

if (!('wakeLock' in navigator)) {
  keepAwakeInput.checked = false;
  keepAwakeInput.disabled = true;
  wakeHint.textContent = location.protocol === 'file:'
    ? 'Giữ màn hình sáng cần bản web HTTPS; phần đọc vẫn dùng được.'
    : 'Trình duyệt này chưa hỗ trợ giữ màn hình sáng.';
  wakeHint.classList.add('warn');
}
if (synth) {
  deviceVoiceOptions();
  synth.addEventListener('voiceschanged', () => {
    if (engineSelect.value === 'device') deviceVoiceOptions(voiceSelect.value);
  });
}
loadKokoro();
