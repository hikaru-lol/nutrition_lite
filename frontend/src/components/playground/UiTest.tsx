'use client';

import React, { useEffect, useMemo, useState } from 'react';

type ClassValue = string | false | null | undefined;
const cx = (...values: ClassValue[]) => values.filter(Boolean).join(' ');

// -----------------------------
// 1) Button（variant / size / 状態）
// -----------------------------
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  ...props
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition ' +
    'focus:outline-none focus:ring-2 focus:ring-offset-2 ' +
    'disabled:opacity-50 disabled:cursor-not-allowed';

  const variants: Record<ButtonVariant, string> = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary:
      'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-400 ' +
      'dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700 dark:focus:ring-gray-600',
    ghost:
      'bg-transparent text-gray-900 hover:bg-gray-100 focus:ring-gray-400 ' +
      'dark:text-gray-100 dark:hover:bg-gray-800 dark:focus:ring-gray-600',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };

  const sizes: Record<ButtonSize, string> = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-5 text-base',
  };

  return (
    <button
      className={cx(base, variants[variant], sizes[size], className)}
      {...props}
    />
  );
}

// -----------------------------
// 2) Badge（小さなラベル）
// -----------------------------
type BadgeVariant = 'default' | 'info' | 'success' | 'warning';

function Badge({
  children,
  variant = 'default',
}: {
  children: React.ReactNode;
  variant?: BadgeVariant;
}) {
  const variants: Record<BadgeVariant, string> = {
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200',
    success:
      'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200',
    warning:
      'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200',
  };

  return (
    <span
      className={cx(
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        variants[variant]
      )}
    >
      {children}
    </span>
  );
}

// -----------------------------
// 3) Card（group-hover / 影 / 枠線）
// -----------------------------
function ProductCard() {
  return (
    <div className="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-gray-800 dark:bg-gray-950">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="truncate text-base font-semibold text-gray-900 dark:text-gray-100">
              Tailwind Starter Pack
            </h3>
            <Badge variant="info">NEW</Badge>
          </div>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            group-hover / border / shadow の基本練習用カード
          </p>
        </div>

        {/* group-hover の例：カードにホバーするとボタンも反応 */}
        <Button
          variant="ghost"
          size="sm"
          className="shrink-0 group-hover:bg-gray-100 dark:group-hover:bg-gray-800"
        >
          詳細
        </Button>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-gray-50 p-3 text-sm dark:bg-gray-900">
          <div className="text-xs text-gray-500 dark:text-gray-400">Price</div>
          <div className="mt-1 font-semibold text-gray-900 dark:text-gray-100">
            ¥2,980
          </div>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-sm dark:bg-gray-900">
          <div className="text-xs text-gray-500 dark:text-gray-400">Stock</div>
          <div className="mt-1 font-semibold text-gray-900 dark:text-gray-100">
            12
          </div>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-sm dark:bg-gray-900">
          <div className="text-xs text-gray-500 dark:text-gray-400">Rating</div>
          <div className="mt-1 font-semibold text-gray-900 dark:text-gray-100">
            4.7
          </div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------
// 4) レスポンシブ Grid（sm/md で列数が変わる）
// -----------------------------
function ResponsiveGrid() {
  const items = useMemo(
    () =>
      Array.from({ length: 6 }, (_, i) => ({
        title: `Item ${i + 1}`,
        desc: 'grid-cols / gap / breakpoint の練習',
      })),
    []
  );

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((it) => (
        <div
          key={it.title}
          className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-950"
        >
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {it.title}
            </h4>
            <Badge variant="default">BETA</Badge>
          </div>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {it.desc}
          </p>
          <div className="mt-4 flex items-center justify-end gap-2">
            <Button variant="secondary" size="sm">
              Edit
            </Button>
            <Button size="sm">Open</Button>
          </div>
        </div>
      ))}
    </div>
  );
}

// -----------------------------
// 5) Navbar（モバイルメニューの開閉 / md:hidden 等）
// -----------------------------
function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-20 border-b border-gray-200 bg-white/80 backdrop-blur dark:border-gray-800 dark:bg-gray-950/80">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900">
            T
          </div>
          <div className="font-semibold text-gray-900 dark:text-gray-100">
            Tailwind Lab
          </div>
        </div>

        <nav className="hidden items-center gap-3 md:flex">
          <a
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
            href="#"
          >
            Docs
          </a>
          <a
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
            href="#"
          >
            Pricing
          </a>
          <Button size="sm">Login</Button>
        </nav>

        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 md:hidden dark:border-gray-800"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle Menu"
        >
          <span className="text-sm text-gray-700 dark:text-gray-200">
            {open ? '✕' : '☰'}
          </span>
        </button>
      </div>

      {/* モバイルメニュー */}
      {open && (
        <div className="border-t border-gray-200 px-4 py-3 md:hidden dark:border-gray-800">
          <div className="flex flex-col gap-2">
            <a
              className="rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
              href="#"
            >
              Docs
            </a>
            <a
              className="rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
              href="#"
            >
              Pricing
            </a>
            <Button className="w-full">Login</Button>
          </div>
        </div>
      )}
    </header>
  );
}

// -----------------------------
// 6) Form（focus:ring / エラー表示 / aria-invalid）
// -----------------------------
function ProfileForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const nameError =
    name.trim().length > 0 && name.trim().length < 2
      ? '2文字以上で入力してください'
      : '';
  const emailError =
    email.trim().length > 0 && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
      ? 'メール形式が不正です'
      : '';

  const Input = ({
    label,
    value,
    onChange,
    placeholder,
    error,
    type = 'text',
  }: {
    label: string;
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
    error?: string;
    type?: string;
  }) => (
    <div>
      <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-invalid={Boolean(error)}
        className={cx(
          'mt-2 w-full rounded-lg border px-3 py-2 text-sm outline-none transition',
          'border-gray-300 bg-white text-gray-900',
          'focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white',
          'dark:border-gray-700 dark:bg-gray-950 dark:text-gray-100 dark:focus:ring-offset-gray-950',
          error && 'border-red-500 focus:ring-red-500'
        )}
      />
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );

  return (
    <form className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Profile
          </h3>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            フォームの基本（focus / error / spacing）
          </p>
        </div>
        <Badge variant="success">OK</Badge>
      </div>

      <div className="mt-5 grid gap-4">
        <Input
          label="Name"
          value={name}
          onChange={setName}
          placeholder="Hikaru"
          error={nameError}
        />
        <Input
          label="Email"
          value={email}
          onChange={setEmail}
          placeholder="you@example.com"
          error={emailError}
          type="email"
        />
      </div>

      <div className="mt-6 flex items-center justify-end gap-2">
        <Button variant="secondary" type="button">
          Cancel
        </Button>
        <Button
          type="button"
          disabled={Boolean(nameError || emailError) || !name || !email}
        >
          Save
        </Button>
      </div>
    </form>
  );
}

// -----------------------------
// 7) Modal（overlay / fixed / ESC / クリックで閉じる）
// -----------------------------
function Modal({
  open,
  title,
  children,
  onClose,
}: {
  open: boolean;
  title: string;
  children: React.ReactNode;
  onClose: () => void;
}) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <button
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-label="Close overlay"
      />
      <div className="relative mx-auto mt-24 w-[min(92vw,520px)] rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-800 dark:bg-gray-950">
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ✕
          </Button>
        </div>
        <div className="mt-4 text-sm text-gray-700 dark:text-gray-300">
          {children}
        </div>
      </div>
    </div>
  );
}

function ModalExample() {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Modal
      </h3>
      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
        fixed / overlay / ESC / click-to-close
      </p>

      <div className="mt-4">
        <Button onClick={() => setOpen(true)}>Open Modal</Button>
      </div>

      <Modal open={open} title="Confirm Action" onClose={() => setOpen(false)}>
        <p>ここに説明テキスト。Tailwindの役割は「見た目」と「状態表現」。</p>
        <div className="mt-5 flex items-center justify-end gap-2">
          <Button variant="secondary" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={() => setOpen(false)}>
            Delete
          </Button>
        </div>
      </Modal>
    </div>
  );
}

// -----------------------------
// 8) Dark Mode（コンテナに dark を付けて学習）
// -----------------------------
function DarkModeWrapper({ children }: { children: React.ReactNode }) {
  const [dark, setDark] = useState(false);

  return (
    <section
      className={cx(
        'rounded-2xl border border-gray-200 p-4 dark:border-gray-800',
        dark && 'dark'
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Dark Mode Preview
          </h3>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            コンテナの dark をON/OFFして確認
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setDark((v) => !v)}
        >
          {dark ? 'Light' : 'Dark'}
        </Button>
      </div>

      <div className="mt-4 rounded-2xl bg-gray-50 p-4 dark:bg-gray-950">
        {children}
      </div>
    </section>
  );
}

// -----------------------------
// メイン：学習プレイグラウンド
// -----------------------------
export default function TailwindLearningPlayground() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      <Navbar />

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
          <h1 className="text-xl font-semibold">
            Tailwind Learning Playground
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            ここにある各コンポーネントの className
            をいじって、変化を観察してください。
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <Button size="sm">Primary</Button>
            <Button variant="secondary" size="sm">
              Secondary
            </Button>
            <Button variant="ghost" size="sm">
              Ghost
            </Button>
            <Button variant="danger" size="sm">
              Danger
            </Button>
            <Button size="sm" disabled>
              Disabled
            </Button>
          </div>
        </section>

        <DarkModeWrapper>
          <div className="space-y-4">
            <ProductCard />
            <ProfileForm />
            <ModalExample />
            <ResponsiveGrid />
          </div>
        </DarkModeWrapper>
      </main>
    </div>
  );
}
