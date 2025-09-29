'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Menu, X, Rocket } from 'lucide-react';
import Button from './Button';

const navItems = [
  { href: '/', label: 'หน้าหลัก' },
  { href: '/features', label: 'ฟีเจอร์' },
  { href: '/contact', label: 'ติดต่อเรา' },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Rocket className="h-6 w-6 text-primary" />
          <span className="text-lg font-semibold">โปรเจคตัวอย่าง</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="text-sm text-gray-700 hover:text-primary">
              {item.label}
            </Link>
          ))}
          <Link href="/contact">
            <Button className="ml-2 px-4 py-2 shadow-glow">เริ่มใช้งาน</Button>
          </Link>
        </nav>

        <button
          aria-label="Toggle menu"
          className="md:hidden inline-flex items-center justify-center rounded-md p-2 text-gray-700 hover:bg-blue-50"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t bg-white">
          <div className="container py-3 flex flex-col gap-3">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-sm text-gray-700 hover:text-primary"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <Link href="/contact" onClick={() => setOpen(false)}>
              <Button className="mt-2 w-full px-4 py-2">เริ่มใช้งาน</Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}