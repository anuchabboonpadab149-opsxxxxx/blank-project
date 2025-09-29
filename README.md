# โปรเจคตัวอย่าง (Next.js + TypeScript + Tailwind)

เว็บไซต์ภาษาไทยที่พร้อมใช้งานและดีพลอยบน Netlify ได้ทันที
- Stack: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- UI สวยงาม มีแอนิเมชันด้วย Framer Motion
- ฟอร์มติดต่อส่งเข้า Netlify Forms (ไม่ต้องมีแบ็คเอนด์)
- Static export เพื่อให้ดีพลอยง่าย (`out`)

## การใช้งาน

1) ติดตั้งแพ็กเกจ
```bash
npm install
# หรือ pnpm install / yarn install
```

2) รันโหมดพัฒนา
```bash
npm run dev
```
เปิดที่ http://localhost:3000

3) สร้างไฟล์สำหรับดีพลอย (static export)
```bash
npm run build
```
ผลลัพธ์อยู่ในโฟลเดอร์ `out/`

## ดีพลอยบน Netlify

- ไฟล์ `netlify.toml` ถูกตั้งค่าให้ใช้ `publish = "out"` แล้ว
- ขั้นตอน:
  1. สร้าง Git repo แล้ว push โค้ดขึ้น GitHub/GitLab/Bitbucket
  2. เชื่อมต่อกับ Netlify และเลือก repo นี้
  3. ตั้งค่า build command: `npm run build`
  4. Deploy

Netlify จะตรวจจับฟอร์มในหน้า `/contact` อัตโนมัติ (ต้องมีการ build และ deploy ก่อน)

## โครงสร้างไฟล์

```
.
├─ src/
│  ├─ app/
│  │  ├─ globals.css
│  │  ├─ layout.tsx
│  │  ├─ page.tsx            # หน้าแรก
│  │  ├─ features/page.tsx   # หน้าฟีเจอร์
│  │  └─ contact/page.tsx    # หน้าติดต่อเรา (Netlify Forms)
│  ├─ components/
│  │  ├─ Button.tsx
│  │  └─ Navbar.tsx / Footer.tsx
│  └─ lib/utils.ts
├─ package.json
├─ next.config.mjs
├─ netlify.toml
├─ tailwind.config.ts
├─ tsconfig.json
└─ README.md
```

## หมายเหตุ

- โปรเจคนี้ออกแบบเป็น static export เพื่อให้ดีพลอยบน Netlify ง่ายขึ้น
- หากต้องการฟีเจอร์ dynamic/SSR สามารถลบ `output: 'export'` ใน `next.config.mjs` และเปลี่ยนวิธีดีพลอยตามที่ต้องการ
- ต้องการปรับให้เหมือนโปรเจคในลิงก์ต้นฉบับ แจ้งรายละเอียดเพิ่มเติมได้ เช่น หน้าจอ, ฟีเจอร์, ธีม, integration ฯลฯ