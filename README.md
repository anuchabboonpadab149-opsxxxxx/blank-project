Production-ready Full-Stack Template (Frontend: Vite + React, Backend: Express, Proxy: Nginx)

ภาษาไทย
โปรเจกต์นี้ถูกเตรียมให้ใช้งานได้จริง ลดปัญหา Failed to fetch โดยออกแบบให้:
- Dev: ใช้ proxy เพื่อตัด CORS (Vite proxy → Backend)
- Prod: เสิร์ฟ Frontend และ proxy /api ผ่าน Nginx ไป Backend (same-origin) จึงไม่มี CORS
- Backend: เปิด CORS แบบระบุที่มา (สำหรับกรณีเรียกข้ามโดเมน), รองรับ preflight, มี Security/Compression/Rate limit/Logging
- Frontend: มี http client กลาง (timeout, จัดการ network error, parse JSON ปลอดภัย), ErrorBoundary และตัวอย่างการเรียก API

โครงสร้าง
- frontend/ React + Vite + TypeScript
- backend/ Express (Node.js)
- nginx/default.conf Nginx สำหรับ production (เสิร์ฟไฟล์ static และ proxy /api ไป backend)
- docker-compose.yml สำหรับรันแบบ production ด้วย Docker
- .env ตัวอย่างอยู่ใน backend/.env.example

ใช้งานในเครื่อง (Development)
Terminal 1: Backend
  cd backend
  npm install
  npm run dev

Terminal 2: Frontend
  cd frontend
  npm install
  npm run dev

- Frontend (Vite) จะรันที่ http://localhost:5173
- Backend (Express) จะรันที่ http://localhost:8080
- Vite ถูกตั้ง proxy /api → http://localhost:8080 ทำให้ไม่ติด CORS ใน dev

Environment
- backend/.env.example
  - PORT=8080
  - ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:4173
  คัดลอกไฟล์เป็น .env แล้วปรับค่าได้ตามต้องการ

คำสั่งตรวจสอบ API
- Health:
  curl -i http://localhost:8080/api/health

- Preflight (ถ้าเรียกข้ามโดเมนและมี JSON/custom headers):
  curl -i -X OPTIONS http://localhost:8080/api/login \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type, authorization"

รันแบบ Production (Docker)
- ต้องติดตั้ง Docker และ Docker Compose
- คำสั่ง:
  docker compose up --build

- จากนั้นเปิด http://localhost:8081
- Nginx เสิร์ฟไฟล์ React build ที่ / และ proxy คำขอ /api ไปยัง service backend (http://backend:8080)
- โปรดตั้งค่า ALLOWED_ORIGINS ให้เหมาะสม หากจะเปิดให้เรียกข้ามโดเมน

แนวทางแก้ “Failed to fetch” ที่โปรเจกต์นี้รองรับ
- Dev ใช้ proxy เพื่อตัด CORS → ไม่เจอ CORS error ใน dev
- Prod ใช้ same origin (Nginx proxy /api) → ไม่เจอ CORS error ใน prod
- Backend เปิด CORS แบบอนุญาตเฉพาะโดเมนจำเพาะและรองรับ preflight OPTIONS สำหรับกรณีต้องเรียกข้ามโดเมนจริงๆ
- http client ฝั่ง Frontend มี timeout/จำแนก network error/แสดงข้อความให้ผู้ใช้เข้าใจง่าย

หมายเหตุ
- โค้ดถูกทำให้ minimal แต่พร้อมใช้งานจริง คุณสามารถต่อยอด เพิ่ม auth จริง, ฐานข้อมูล, และ CI/CD ตามต้องการ
- หากต้องการเปิดใช้คุกกี้ข้ามโดเมนจริง ให้ใช้ https จริง และตั้งค่า SameSite=None; Secure บนคุกกี้, credentials: 'include' ใน fetch และอย่าตั้ง Allow-Origin เป็น '*'.

License
- MIT