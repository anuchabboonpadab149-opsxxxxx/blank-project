import { useEffect, useState } from 'react';
import { request } from './lib/httpClient';

type ApiState =
  | { loading: true; data?: any; error?: string; networkError?: boolean }
  | { loading: false; data?: any; error?: string; networkError?: boolean };

export default function App() {
  const [online, setOnline] = useState<boolean>(navigator.onLine);
  const [health, setHealth] = useState<ApiState>({ loading: true });
  const [loginResp, setLoginResp] = useState<ApiState>({ loading: false });

  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
  }, []);

  useEffect(() => {
    (async () => {
      setHealth({ loading: true });
      const resp = await request('/api/health', { method: 'GET' });
      setHealth({ loading: false, data: resp.data, error: resp.ok ? undefined : 'โหลดไม่สำเร็จ', networkError: resp.networkError });
    })();
  }, []);

  async function doLogin() {
    setLoginResp({ loading: true });
    const resp = await request('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // ถ้าต้องการส่งคุกกี้/เซสชัน ให้เปิดบรรทัดด้านล่าง
      // credentials: 'include',
      body: JSON.stringify({ email: 'demo@example.com', password: 'password' })
    });
    setLoginResp({
      loading: false,
      data: resp.data,
      error: resp.ok ? undefined : (resp.networkError ? 'Network error' : 'HTTP error'),
      networkError: resp.networkError
    });
  }

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif', padding: 16, lineHeight: 1.5 }}>
      <h1>Full-Stack Starter</h1>

      {!online && (
        <div style={{ background: '#fff3cd', border: '1px solid #ffeeba', padding: 12, borderRadius: 6, color: '#856404', marginBottom: 12 }}>
          โหมดออฟไลน์: ตรวจสอบการเชื่อมต่ออินเทอร์เน็ตของคุณ
        </div>
      )}

      <section style={{ marginBottom: 16 }}>
        <h2>เช็คสุขภาพ API</h2>
        {health.loading ? (
          <p>กำลังโหลด...</p>
        ) : health.networkError ? (
          <p style={{ color: '#b00020' }}>เชื่อมต่อไม่ได้ (Network/CORS/Timeout)</p>
        ) : (
          <pre style={{ background: '#f6f8fa', padding: 12, borderRadius: 6 }}>{JSON.stringify(health.data, null, 2)}</pre>
        )}
      </section>

      <section>
        <h2>ทดสอบ Login (ตัวอย่าง)</h2>
        <button onClick={doLogin} disabled={loginResp.loading} style={{ padding: '8px 12px', cursor: 'pointer' }}>
          {loginResp.loading ? 'กำลังส่ง...' : 'ส่งคำขอ /api/login'}
        </button>
        {!loginResp.loading && (loginResp.error || loginResp.data) && (
          <div style={{ marginTop: 12 }}>
            {loginResp.networkError ? (
              <p style={{ color: '#b00020' }}>เชื่อมต่อไม่ได้ (Network/CORS/Timeout)</p>
            ) : loginResp.error ? (
              <p style={{ color: '#b00020' }}>เกิดข้อผิดพลาด: {loginResp.error}</p>
            ) : (
              <pre style={{ background: '#f6f8fa', padding: 12, borderRadius: 6 }}>{JSON.stringify(loginResp.data, null, 2)}</pre>
            )}
          </div>
        )}
        <p style={{ marginTop: 8, color: '#555' }}>
          หมายเหตุ: ถ้าต้องการส่งคุกกี้/เซสชัน ให้เปิด credentials: 'include' ในคำขอ และตั้งค่า CORS/คุกกี้ฝั่งเซิร์ฟเวอร์ให้ถูกต้อง
        </p>
      </section>
    </div>
  );
}