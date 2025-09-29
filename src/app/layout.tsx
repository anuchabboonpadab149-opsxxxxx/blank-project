import type { Metadata } from 'next';
import './globals.css';
import { Noto_Sans_Thai } from 'next/font/google';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const notoThai = Noto_Sans_Thai({
  subsets: ['thai'],
  weight: ['400', '500', '700'],
  variable: '--font-sans',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'โปรเจคตัวอย่าง | สร้างโปรเจคตามลิ้งค์',
  description: 'เว็บไซต์ตัวอย่างสำหรับโปรเจคภาษาไทย พร้อมดีพลอยบน Netlify',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th" className={notoThai.variable}>
      <body>
        <Navbar />
        <main className="min-h-[calc(100vh-64px-64px)] bg-gradient-to-b from-white to-blue-50">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}