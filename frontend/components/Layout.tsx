import { ReactNode } from 'react';
import AudioPlayer from './AudioPlayer';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="h-screen flex flex-col bg-dark-bg">
      <main className="flex-1 overflow-hidden">{children}</main>
      <AudioPlayer />
    </div>
  );
}

