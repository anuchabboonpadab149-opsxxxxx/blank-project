import React from 'react';

type Props = { children: React.ReactNode };
type State = { hasError: boolean };

export default class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(err: unknown, info: unknown) {
    // สามารถเชื่อม Sentry/Logging ที่นี่ได้
    console.error('ErrorBoundary caught error:', err, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 16, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
          <h2>เกิดข้อผิดพลาดในแอปพลิเคชัน</h2>
          <p>โปรดลองรีเฟรชหน้านี้ หากยังพบปัญหา โปรดติดต่อผู้ดูแลระบบ</p>
        </div>
      );
    }
    return this.props.children;
  }
}