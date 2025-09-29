'use client';

import { useSearchParams } from 'next/navigation';
import { CheckCircle } from 'lucide-react';
import Button from '@/components/Button';

export default function ContactPage() {
  const sp = useSearchParams();
  const success = sp.get('success') === '1';

  return (
    <section className="container py-16">
      <h1 className="text-3xl font-bold">ติดต่อเรา</h1>
      <p className="mt-2 text-gray-600">
        ส่งข้อความหาเราเพื่อสอบถาม ปรับแต่ง หรือขอให้ทำให้เหมือนโปรเจคต้นฉบับตามลิงก์ได้เลย
      </p>

      {success ? (
        <div className="mt-6 rounded-lg border bg-green-50 p-4 text-green-700">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            <span>ส่งข้อความเรียบร้อย ขอบคุณที่ติดต่อเรา!</span>
          </div>
        </div>
      ) : (
        <form
          name="contact"
          method="POST"
          data-netlify="true"
          action="/contact?success=1"
          className="mt-8 grid gap-4 rounded-xl border bg-white p-6 shadow-sm"
        >
          <input type="hidden" name="form-name" value="contact" />
          <p className="hidden">
            <label>
              Don’t fill this out if you’re human: <input name="bot-field" />
            </label>
          </p>

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              ชื่อ-นามสกุล
            </label>
            <input
              id="name"
              name="name"
              required
              className="mt-1 w-full rounded-md border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="เช่น สมชาย ใจดี"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              อีเมล
            </label>
            <input
              id="email"
              type="email"
              name="email"
              required
              className="mt-1 w-full rounded-md border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">
              ข้อความ
            </label>
            <textarea
              id="message"
              name="message"
              rows={5}
              required
              className="mt-1 w-full rounded-md border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="รายละเอียดที่ต้องการให้เราดำเนินการ"
            />
          </div>

          <div className="flex justify-end">
            <Button className="px-5 py-2">ส่งข้อความ</Button>
          </div>
        </form>
      )}
    </section>
  );
}