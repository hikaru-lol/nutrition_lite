'use client';

import React from 'react';
import { cx } from '../lib/cx';

export function Button({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled,
  className,
  type = 'button',
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md';
}) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition ' +
    'focus:outline-none focus:ring-2 focus:ring-offset-2 ' +
    'disabled:opacity-50 disabled:cursor-not-allowed';
  const sizes = { sm: 'h-9 px-3 text-sm', md: 'h-10 px-4 text-sm' } as const;
  const variants = {
    primary:
      'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 focus:ring-offset-white dark:focus:ring-offset-gray-950',
    secondary:
      'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-400 focus:ring-offset-white ' +
      'dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700 dark:focus:ring-offset-gray-950',
    ghost:
      'bg-transparent text-gray-900 hover:bg-gray-100 focus:ring-gray-400 focus:ring-offset-white ' +
      'dark:text-gray-100 dark:hover:bg-gray-900 dark:focus:ring-offset-gray-950',
    danger:
      'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 focus:ring-offset-white dark:focus:ring-offset-gray-950',
  } as const;

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={cx(base, sizes[size], variants[variant], className)}
    >
      {children}
    </button>
  );
}
