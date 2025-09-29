/** @type {import('next').NextConfig} */
const nextConfig = {
  // ใช้ static export เพื่อให้ดีพลอยบน Netlify ง่ายขึ้น
  output: 'export',
  images: {
    // ปิด image optimization เพื่อรองรับ static export
    unoptimized: true,
  },
  reactStrictMode: true,
};

export default nextConfig;