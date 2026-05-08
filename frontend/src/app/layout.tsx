import { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AvatarLM',
  description: 'An emotionally intelligent, avatar-based learning platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 font-sans min-h-screen">
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <header className="mb-8 border-b pb-4">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">AvatarLM</h1>
            <p className="mt-2 text-sm text-gray-600">Emotionally expressive learning avatars</p>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
