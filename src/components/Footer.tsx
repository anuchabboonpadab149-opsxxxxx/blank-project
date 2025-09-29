import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="border-t bg-white">
      <div className="container flex h-16 items-center justify-between">
        <p className="text-sm text-gray-500">© {new Date().getFullYear()} โปรเจคตัวอย่าง. สงวนสิทธิ์ทุกประการ.</p>
        <div className="flex items-center gap-4 text-sm">
          <Link href="/features" className="text-gray-600 hover:text-primary">ฟีเจอร์</Link>
          <Link href="/contact" className="text-gray-600 hover:text-primary">ติดต่อเรา</Link>
        </div>
      </div>
    </footer>
  );
}