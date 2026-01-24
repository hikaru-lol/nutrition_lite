// src/app/layout.tsx
import './globals.css';
import { Providers } from './providers';

export default function RootLayout(props: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <Providers>{props.children}</Providers>
      </body>
    </html>
  );
}
