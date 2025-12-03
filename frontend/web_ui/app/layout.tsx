import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Gujarati & Marathi TTS',
  description: 'Real-time Text-to-Speech for Gujarati and Marathi languages',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">{children}</body>
    </html>
  )
}

