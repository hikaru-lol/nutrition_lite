'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

export function RichUi() {
  const [open, setOpen] = useState(false);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  return (
    <div className="p-6">
      <button className="border px-3 py-2" onClick={() => setOpen(true)}>
        Open modal
      </button>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="食事を追加"
        initialFocusRef={closeBtnRef as React.RefObject<HTMLElement>}
        footer={
          <div
            className="flex items-center justify-end gap-2"
            ref={closeBtnRef as unknown as React.RefObject<HTMLDivElement>}
          >
            <button
              className="border px-3 py-2"
              onClick={() => setOpen(false)}
              // ref={closeBtnRef}
            >
              キャンセル
            </button>
            <button className="border px-3 py-2">保存</button>
          </div>
        }
      >
        <p className="text-sm text-zinc-600 dark:text-zinc-300">
          ここにフォームや内容を入れてください。
        </p>
      </Modal>
    </div>
  );
}

type ModalProps = {
  open: boolean;
  onClose: () => void;

  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;

  /** 背景クリックで閉じる */
  closeOnBackdrop?: boolean;

  /** 開いた直後にフォーカスしたい要素（例：閉じるボタン） */
  initialFocusRef?: React.RefObject<HTMLElement>;

  /** aria-describedby 用に本文側のidを渡すなら */
  descriptionId?: string;

  /** パネル幅 */
  maxWidthClassName?: string;
};

type ClassValue = string | false | null | undefined;
const cx = (...v: ClassValue[]) => v.filter(Boolean).join(' ');

function getFocusableElements(root: HTMLElement) {
  const selector = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(',');

  return Array.from(root.querySelectorAll<HTMLElement>(selector)).filter(
    (el) => !el.hasAttribute('disabled') && !el.getAttribute('aria-hidden')
  );
}

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  closeOnBackdrop = true,
  initialFocusRef,
  descriptionId,
  maxWidthClassName = 'max-w-lg',
}: ModalProps) {
  const panelRef = useRef<HTMLDivElement | null>(null);
  const titleId = useMemo(
    () => `modal-title-${crypto.randomUUID().slice(2)}`,
    []
  );

  // open中：bodyスクロールロック + フォーカス管理 + ESC/Tab処理
  useEffect(() => {
    if (!open) return;

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const prevActive = document.activeElement as HTMLElement | null;

    const focusToInitial = () => {
      const panel = panelRef.current;
      if (!panel) return;

      const target = initialFocusRef?.current;
      if (target) {
        target.focus();
        return;
      }

      // initialFocusRefが無ければ、パネル内の最初のフォーカス可能要素へ
      const focusables = getFocusableElements(panel);
      (focusables[0] ?? panel).focus();
    };

    // commit後にフォーカス（微小遅延）
    const t = window.setTimeout(focusToInitial, 0);

    const onKeyDown = (e: KeyboardEvent) => {
      if (!panelRef.current) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }

      if (e.key === 'Tab') {
        const panel = panelRef.current;
        const focusables = getFocusableElements(panel);

        // フォーカス可能要素が無いならパネルに閉じ込める
        if (focusables.length === 0) {
          e.preventDefault();
          panel.focus();
          return;
        }

        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        const active = document.activeElement as HTMLElement | null;

        // Shift+Tab で先頭から戻ろうとしたら末尾へ
        if (e.shiftKey) {
          if (active === first || active === panel) {
            e.preventDefault();
            last.focus();
          }
          return;
        }

        // Tab で末尾から進もうとしたら先頭へ
        if (active === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener('keydown', onKeyDown);

    return () => {
      window.clearTimeout(t);
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = prevOverflow;

      // フォーカス復元
      prevActive?.focus?.();
    };
  }, [open, onClose, initialFocusRef]);

  if (!open) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50"
      onMouseDown={(e) => {
        // 背景クリック判定：パネル外を押したら閉じる（押下開始時点で判定）
        if (!closeOnBackdrop) return;
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {/* overlay */}
      <div className="absolute inset-0 bg-black/50" />

      {/* container */}
      <div className="relative flex min-h-full items-center justify-center p-4">
        <div
          ref={panelRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? titleId : undefined}
          aria-describedby={descriptionId}
          tabIndex={-1}
          className={cx(
            'w-full rounded-2xl bg-white shadow-xl outline-none',
            'dark:bg-zinc-900',
            maxWidthClassName
          )}
        >
          {/* header */}
          <div className="flex items-center justify-between border-b border-zinc-200 px-5 py-4 dark:border-zinc-800">
            <div className="min-w-0">
              {title ? (
                <h2 id={titleId} className="truncate text-lg font-semibold">
                  {title}
                </h2>
              ) : (
                <span className="sr-only">Dialog</span>
              )}
            </div>

            <button
              type="button"
              className="rounded-lg px-3 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800"
              onClick={onClose}
              aria-label="Close"
            >
              ✕
            </button>
          </div>

          {/* body */}
          <div className="px-5 py-4">{children}</div>

          {/* footer */}
          {footer ? (
            <div className="flex items-center justify-end gap-2 border-t border-zinc-200 px-5 py-4 dark:border-zinc-800">
              {footer}
            </div>
          ) : null}
        </div>
      </div>
    </div>,
    document.body
  );
}
