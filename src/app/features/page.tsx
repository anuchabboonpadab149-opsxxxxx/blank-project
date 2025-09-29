import { Rocket, Zap, Layers, ShieldCheck, Wrench, Globe } from 'lucide-react';

const features = [
  {
    icon: Rocket,
    title: 'Next.js + TypeScript',
    desc: 'ใช้โครงสร้างสมัยใหม่ รองรับการพัฒนาอย่างเป็นระบบ',
  },
  {
    icon: Zap,
    title: 'Tailwind CSS',
    desc: 'ออกแบบ UI ได้รวดเร็วและสวยงามด้วยยูทิลิตี้คลาส',
  },
  {
    icon: Layers,
    title: 'โครงสร้างคอมโพเนนต์',
    desc: 'แยกส่วน Navbar, Footer, ปุ่ม และหน้าต่างๆ ชัดเจน',
  },
  {
    icon: ShieldCheck,
    title: 'พร้อมดีพลอย',
    desc: 'ตั้งค่า Netlify และ static export ให้เรียบร้อย',
  },
  {
    icon: Wrench,
    title: 'ปรับแต่งง่าย',
    desc: 'สามารถเพิ่มเติมหน้าและบล็อกเนื้อหาได้สะดวก',
  },
  {
    icon: Globe,
    title: 'ภาษาไทยเต็มรูปแบบ',
    desc: 'เนื้อหาและฟอนต์รองรับภาษาไทยสวยงามอ่านง่าย',
  },
];

export default function FeaturesPage() {
  return (
    <section className="container py-16">
      <h1 className="text-3xl font-bold">ฟีเจอร์ของโปรเจค</h1>
      <p className="mt-2 text-gray-600">ภาพรวมความสามารถและเทคโนโลยีที่ใช้ในโปรเจคนี้</p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <div key={f.title} className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md">
            <div className="flex items-center gap-3">
              <f.icon className="h-6 w-6 text-primary" />
              <h3 className="text-lg font-semibold">{f.title}</h3>
            </div>
            <p className="mt-2 text-gray-700">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}