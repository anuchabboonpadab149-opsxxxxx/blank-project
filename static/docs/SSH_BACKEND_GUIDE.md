# SSH และ Backend Guide (End-to-End)

คู่มือนี้สรุปวิธีใช้งาน SSH อย่างปลอดภัย พร้อมแนวทางตั้งค่า “แบ็กเอนด์” ของระบบแบบครบวงจร ตั้งแต่เริ่มต้นจนใช้งานจริงได้ 24/7

---

## 1) SSH คืออะไร

SSH (Secure Shell) คือโปรโตคอลสำหรับเชื่อมต่อเครื่อง/เซิร์ฟเวอร์จากระยะไกลผ่านช่องทางที่เข้ารหัส ปลอดภัยกว่าการใช้ Telnet/FTP

องค์ประกอบ
- IP/Hostname: ที่อยู่เครื่องปลายทางที่จะเชื่อมต่อ
- Port: พอร์ตของ SSH (ดีฟอลต์ 22). ถ้าไม่ใช่ 22 ต้องระบุ `-p`
- Auth: ใช้รหัสผ่าน หรือ key-based authentication (แนะนำ)

คำสั่งพื้นฐาน
```bash
# พอร์ต 22
ssh username@host_or_ip

# ระบุพอร์ตเอง เช่น 2222
ssh username@host_or_ip -p 2222

# ใช้กุญแจส่วนตัว
ssh -i ~/.ssh/id_ed25519 username@host_or_ip -p 2222
```

ตัวอย่าง
```bash
ssh admin@192.168.1.100
ssh ubuntu@example.com -p 2222
```

ไฟล์คอนฟิก (ทางเลือก) `~/.ssh/config`
```bash
Host myserver
  HostName 192.168.1.100
  User admin
  Port 2222
  IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 60
  ServerAliveCountMax 3
```
ใช้งาน: `ssh myserver`

การโอนไฟล์ (SCP/SFTP)
```bash
# ส่งไฟล์ไปเซิร์ฟเวอร์
scp ./file.txt user@host:/remote/path/

# ดึงไฟล์จากเซิร์ฟเวอร์
scp user@host:/remote/path/file.txt .

# SFTP แบบโต้ตอบ
sftp user@host
```

---

## 2) ตั้งค่า Permission ของกุญแจ

กรณีขึ้น `Permission denied (publickey)` ให้ตรวจสิทธิ์ไฟล์:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## 3) แนวทางความปลอดภัย SSH (สรุป)

- ปิด root login (`PermitRootLogin no`)
- ใช้ key-based auth และเมื่อพร้อมให้ปิด PasswordAuth (`PasswordAuthentication no`)
- ใช้คีย์รุ่นใหม่ `ed25519`
  ```bash
  ssh-keygen -t ed25519 -C "your-note"
  ```
- เปิดพอร์ตไฟร์วอลล์เท่าที่จำเป็น (22/TCP)
  ```bash
  sudo ufw allow 22/tcp
  sudo ufw enable
  ```
- พิจารณา `fail2ban` ป้องกัน brute force

---

## 4) ติดตั้ง “แบ็กเอนด์” 24/7 แบบครบวงจร

> แนะนำ Ubuntu/Debian + Docker/Compose

### ขั้นตอนย่อ
1) ติดตั้ง Docker + Compose
2) ตั้งค่า `.env` (พอร์ต/interval/คีย์จริง/ผู้ให้บริการ)
3) เปิดไฟร์วอลล์อย่างน้อยพอร์ต 8000/TCP (และ 22/TCP สำหรับ SSH)
4) รัน: `docker compose up -d --build`
5) ตรวจสุขภาพที่ `/healthz`, สตรีมสด SSE ที่ `/events`
6) ใส่คีย์จริงใน `/credentials` — จากนั้นระบบจะยิง API จริงอัตโนมัติ

### ตัวอย่างค่า `.env` ที่พบบ่อย
```
RUN_MODE=daemon
TIMEZONE=Asia/Bangkok

WEB_DASHBOARD=true
WEB_PORT=8000

POST_INTERVAL_SECONDS=1
COLLECT_INTERVAL_MINUTES=1

PROVIDERS=twitter,facebook,linkedin,line,telegram,discord,instagram,reddit,tiktok,mastodon
DISTRIBUTE_ALL=true
```

> หมายเหตุ: การโพสต์ทุก 1 วินาทีมีโอกาสชน rate limit บางแพลตฟอร์ม ให้พิจารณาปรับเป็น 10–30 วินาทีต่อโพสต์ตามนโยบายของผู้ให้บริการ

### เปิดไฟร์วอลล์
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### หมายเหตุเรื่อง HTTPS/Mixed Content
- ถ้าเปิดหน้าเว็บ “สาธารณะ” ด้วย HTTPS แล้วเรียกแบ็กเอนด์ผ่าน HTTP ภายใน LAN เบราว์เซอร์บางตัวจะบล็อก (Mixed Content)
- ทางแก้:
  - เปิดหน้าแดชบอร์ดตรงจาก LAN: `http://LAN_IP:8000`
  - หรือทำ Reverse Proxy/HTTPS ให้แบ็กเอนด์ใน LAN

---

## 5) การใส่คีย์จริงของแพลตฟอร์ม

- เปิดหน้า `/credentials` เพื่อวางคีย์จริงของ:
  - Twitter/X, Facebook/IG (Graph), LinkedIn, LINE, Telegram, Discord, Reddit, Mastodon, TikTok Ads, Twitter Ads
- เมื่อคีย์ครบ ระบบจะยิง API จริงโดยอัตโนมัติ (มี Circuit Breaker/Retry พื้นฐาน)

---

## 6) API/หน้า Dashboard สำคัญ

- `/` — แดชบอร์ดสด
- `/healthz` — ตรวจสุขภาพ
- `/events` — SSE Event Stream แบบเรียลไทม์
- `/api/latest`, `/api/feed`, `/api/recent`
- `/api/config` (GET/POST), `/api/reload-schedule`, `/api/post-now`
- `/api/nodes`, `/api/nodes/register`, `/api/nodes/heartbeat`, `/api/nodes/summary`
- `/media/...` — ให้บริการไฟล์เสียง/รูป/วิดีโอ
- `/credentials` — ตั้งค่าคีย์จริง

---

## 7) แก้ปัญหาที่พบบ่อย

- Connection refused: `sshd` หรือแบ็กเอนด์ยังไม่รัน / พอร์ต/ไฟร์วอลล์ไม่เปิด
- Permission denied (publickey): คีย์ไม่ตรงหรือสิทธิ์ไฟล์ผิด — ใช้ `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`
- Timeout: เส้นทางเครือข่าย/ไฟร์วอลล์/พอร์ตไม่เปิด หรือ NAT/Port Forwarding ไม่ตั้ง
- Mixed Content: หน้า HTTPS เรียก HTTP ภายใน — เปิดผ่าน LAN ตรง หรือทำ HTTPS ให้แบ็กเอนด์

---

## 8) Windows (ทางเลือก)

- ใช้ OpenSSH ใน PowerShell/Terminal ได้ (Windows 10/11)
- หรือใช้ PuTTY (กำหนด Host/IP, Port, และคีย์ผ่าน PuTTYgen)

---

## 9) สรุป

เมื่อแบ็กเอนด์รันด้วย Docker และตั้งค่า `.env`/คีย์จริงครบ:
- ระบบสร้างคอนเทนต์ทุก 1 วินาที (ปรับได้) และสตรีมเหตุการณ์แบบสด
- กระจายเนื้อหาไปยังแพลตฟอร์มที่เปิดใช้งาน พร้อมความทนทานต่อความล้มเหลว (Circuit/Retry)
- ควบคุม/มอนิเตอร์ได้ผ่านแดชบอร์ดและ API ที่ให้มา