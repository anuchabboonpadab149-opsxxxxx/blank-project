const $ = (sel) => document.querySelector(sel);
const out = $('#output');
const net = $('#net-status');

function log(obj) {
  out.textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
}

function setNetStatus() {
  const online = navigator.onLine;
  net.innerHTML = online
    ? '<span class="badge ok">Online</span> การเชื่อมต่อพร้อมใช้งาน'
    : '<span class="badge danger">Offline</span> ออฟไลน์: ตรวจสอบอินเทอร์เน็ต';
}
window.addEventListener('online', setNetStatus);
window.addEventListener('offline', setNetStatus);
setNetStatus();

function fetchWithTimeout(url, options = {}, ms = 12000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  const merged = { ...options, signal: controller.signal };
  return fetch(url, merged).finally(() => clearTimeout(id));
}

async function callHealth() {
  log('กำลังเรียก /api/health ...');
  try {
    const res = await fetchWithTimeout('/api/health', { method: 'GET' }, 12000);
    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!res.ok) {
      log({ ok: false, status: res.status, body: data });
      return;
    }
    log({ ok: true, data });
  } catch (err) {
    log({ ok: false, networkError: true, error: err?.message || String(err) });
  }
}

async function callSample() {
  log('กำลังเรียก public API (jsonplaceholder) ...');
  try {
    const res = await fetchWithTimeout('https://jsonplaceholder.typicode.com/todos/1', { method: 'GET' }, 12000);
    const data = await res.json();
    log({ ok: res.ok, status: res.status, data });
  } catch (err) {
    log({ ok: false, networkError: true, error: err?.message || String(err) });
  }
}

$('#btn-health').addEventListener('click', callHealth);
$('#btn-sample').addEventListener('click', callSample);

log('// เลือกการทดสอบด้านบนเพื่อเริ่มต้น');