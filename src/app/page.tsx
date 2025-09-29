'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import Button from '@/components/Button';
import { Sparkles, ShieldCheck, Code } from 'lucide-react';

export default function HomePage() {
  return (
    <section className="container py-16">
      <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            สร้างโปรเจคตามลิงก์นี้
            <span className="block text-primary">สวยงาม ใช้งานง่าย พร้อมดีพลอย</span>
          </h1>
          <p className="text-gray-600">
            เว็บไซต์ตัวอย่างที่ออกแบบให้ใช้งานได้จริง รองรับภาษาไทย
            ใช้ Next.js + Tailwind และมีแอนิเมชันลื่นไหลด้วย Framer Motion
            พร้อมฟอร์มติดต่อที่ทำงานกับ Netlify Forms โดยไม่ต้องเขียนแบ็คเอนด์
          </p>

          <div className="flex flex-wrap gap-3">
            <Link href="/features">
              <Button className="px-5 py-3">ดูฟีเจอร์</Button>
            </Link>
            <Link href="/contact">
              <Button variant="secondary" className="px-5 py-3">ติดต่อเรา</Button>
            </Link>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <Feature icon={<Sparkles className="h-5 w-5 text-primary" />} title="ดีไซน์ทันสมัย" />
            <Feature icon={<ShieldCheck className="h-5 w-5 text-primary" />} title="พร้อมดีพลอย Netlify" />
            <Feature icon={<Code className="h-5 w-5 text-primary" />} title="TypeScript + Tailwind" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="relative rounded-xl border bg-white p-6 shadow-sm"
        >
          <div className="absolute inset-0 rounded-xl bg-gradient-to-tr from-blue-50 to-transparent" />
          <div className="relative space-y-3">
            <div className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold">โครงสร้างโปรเจคพร้อมใช้งาน</h2>
            </div>
            <ul className="list-disc list-inside text-gray-700">
              <li>หน้า Home, ฟีเจอร์ และ ติดต่อเรา</li>
              <li>คอมโพเนนต์ Navbar + Footer</li>
              <li>ฟอร์มติดต่อส่งเข้า Netlify Forms</li>
            </ul>
            <p className="text-sm text-gray-500">สามารถปรับแต่งให้เหมือนโปรเจคต้นฉบับได้เมื่อได้รับรายละเอียดเพิ่ม</p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Feature({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-2 rounded-md border bg-white p-3 shadow-sm">
      {icon}
      <span className="text-sm font-medium">{title}</span>
    </div>
  );
}