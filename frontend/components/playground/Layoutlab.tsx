'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';

type ViewState =
  | { kind: 'htmlbox' }
  | { kind: 'modalexample' }
  | { kind: 'flexgridlab' }
  | { kind: 'dropdownexample' };

export default function LayoutLab({ viewState }: { viewState: ViewState }) {
  switch (viewState.kind) {
    case 'htmlbox':
      return <HtmlBox />;
    case 'modalexample':
      return <ModalExample />;
    case 'flexgridlab':
      return <FlexGridLab />;
    case 'dropdownexample':
      return <DropdownExample />;
  }
}

function HtmlBox() {
  return (
    <div className="min-h-screen bg-black p-6 text-white">
      {/* ここが「外枠」: max幅 + 中央寄せ */}
      <div className="mx-auto max-w-5xl space-y-6">
        <h1 className="text-xl font-semibold">
          Layout Lab（配置・サイズ・親子関係の実験）
        </h1>

        {/* A: Box Model（margin/padding/border） */}
        <section className="rounded-xl border border-slate-700 bg-black p-4">
          <h2 className="font-semibold">A. Box Model（箱の構造）</h2>

          <div className="mt-4 border border-slate-700 p-4">
            親（border + padding）
            <div className="mt-4 border border-slate-700 p-4">
              子（border + padding）
              <div className="mt-4 border border-slate-700 p-4">
                孫（border + padding）
              </div>
            </div>
          </div>

          <p className="mt-3 text-sm text-slate-300">
            <span className="font-mono">p-4</span> は内側余白、
            <span className="font-mono">mt-4</span>{' '}
            は外側余白（兄弟/親子の距離）。
            入れ子（DOMツリー）がそのまま「箱が入る」関係になります。
          </p>
        </section>

        {/* B: Flex（ヘッダー） */}
        <section className="rounded-xl border border-slate-700 bg-black">
          <div className="flex items-center justify-between border-b border-slate-700 p-4">
            <div className="space-y-1">
              <div className="font-semibold">
                B. Flex（横並び・中央寄せ・余り幅）
              </div>
              <div className="text-sm text-slate-300">
                ヘッダーは{' '}
                <span className="font-mono">flex + justify-between</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button className="rounded-lg border border-slate-600 bg-black px-3 py-1 text-sm hover:bg-slate-900">
                Cancel
              </button>
              <button className="rounded-lg border border-slate-600 bg-black px-3 py-1 text-sm hover:bg-slate-900">
                Save
              </button>
            </div>
          </div>

          {/* C: “アプリっぽい”レイアウト（サイドバー固定 + メイン可変） */}
          <div className="flex min-h-[360px]">
            {/* サイドバー：固定幅 + shrink-0 */}
            <aside className="w-56 shrink-0 border-r border-slate-700 p-4">
              <div className="font-semibold">Sidebar</div>
              <ul className="mt-3 space-y-2 text-sm">
                <li className="rounded border border-slate-700 bg-black px-2 py-1">
                  Menu A
                </li>
                <li className="rounded border border-slate-700 bg-black px-2 py-1">
                  Menu B
                </li>
                <li className="rounded border border-slate-700 bg-black px-2 py-1">
                  Menu C
                </li>
              </ul>

              <p className="mt-4 text-xs text-slate-300">
                <span className="font-mono">w-56</span> で固定、
                <span className="font-mono">shrink-0</span> で潰れにくく。
              </p>
            </aside>

            {/* メイン：flex-1 で “残り全部” */}
            <main className="flex-1 p-4">
              <div className="flex items-end justify-between">
                <div>
                  <div className="font-semibold">C. 親が flex のときの子</div>
                  <div className="text-sm text-slate-300">
                    メインは <span className="font-mono">flex-1</span>{' '}
                    で残り幅を全部取る
                  </div>
                </div>

                <div className="text-xs text-slate-400">
                  ここは “兄弟（Sidebar）” の幅の影響を受けます
                </div>
              </div>

              {/* D: Grid（カード一覧） */}
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <Card key={n} index={n} />
                ))}
              </div>
            </main>
          </div>
        </section>

        {/* E: position と h-full 罠 */}
        <section className="rounded-xl border border-slate-700 bg-black p-4">
          <h2 className="font-semibold">E. position / h-full の罠</h2>

          <div className="mt-3 grid gap-4 md:grid-cols-2">
            {/* position の基準 */}
            <div className="rounded-lg border border-slate-700 bg-black p-3">
              <div className="text-sm font-semibold">
                E-1. absolute の基準は “直近の relative”
              </div>

              <div className="mt-3 relative rounded border border-slate-700 bg-black p-4">
                親（relative）
                <div className="absolute right-2 top-2 rounded border border-slate-600 bg-black px-2 py-1 text-xs">
                  absolute バッジ
                </div>
                <div className="mt-3 text-sm text-slate-300">
                  <span className="font-mono">relative</span>{' '}
                  を外すと、バッジの基準がズレます。
                </div>
              </div>
            </div>

            {/* h-full 罠 */}
            <div className="rounded-lg border border-slate-700 bg-black p-3">
              <div className="text-sm font-semibold">
                E-2. h-full は “親に高さがある時だけ”
              </div>

              <div className="mt-3 rounded border border-slate-700 bg-black p-3">
                <div className="text-xs text-slate-300">
                  親：高さ未指定（auto）
                </div>
                <div className="h-full rounded border border-slate-700 bg-black p-2 text-sm">
                  子：h-full（でも親に高さがないので効きづらい）
                </div>
              </div>

              <div className="mt-3 rounded border border-slate-700 bg-black p-3">
                <div className="text-xs text-slate-300">
                  親：h-24（高さ指定あり）
                </div>
                <div className="h-24 rounded border border-slate-700 bg-black p-2">
                  <div className="h-full rounded border border-slate-700 bg-black p-2 text-sm">
                    子：h-full（親の高さ100%になる）
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function Card({ index }: { index: number }) {
  return (
    <div className="relative rounded-xl border border-slate-700 bg-black p-4">
      <div className="absolute right-3 top-3 rounded-full border border-slate-600 bg-black px-2 py-1 text-xs">
        badge
      </div>

      <div className="text-sm font-semibold">Card {index}</div>
      <div className="mt-2 text-sm text-slate-300">
        Grid の “セル” に配置される箱。
        <br />
        padding/border/margin がサイズ感を作る。
      </div>

      <div className="mt-3 flex items-center gap-2 rounded border border-slate-700 bg-black p-2">
        <div className="w-20 rounded border border-slate-700 bg-black px-2 py-1 text-xs">
          w-20
        </div>
        <div className="flex-1 rounded border border-slate-700 bg-black px-2 py-1 text-xs">
          flex-1（残り全部）
        </div>
      </div>
    </div>
  );
}

export function FlexGridLab() {
  return (
    <div className="min-h-screen bg-black p-6 text-white">
      <div className="mx-auto max-w-5xl space-y-10">
        <h1 className="text-xl font-semibold">Flex & Grid Lab</h1>

        {/* ===================== FLEX ===================== */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">Flex（1次元レイアウト）</h2>

          {/* Flex例1：ヘッダー（左右に分ける） */}
          <div className="rounded-xl border border-slate-700 p-4">
            <div className="text-sm text-slate-300">
              例1：ヘッダー（左情報 / 右ボタン）
            </div>

            <div className="mt-3 flex items-center justify-between rounded-lg border border-slate-700 p-3">
              <div>
                <div className="font-semibold">Title</div>
                <div className="text-sm text-slate-300">subtitle</div>
              </div>

              <div className="flex items-center gap-2">
                <button className="rounded border border-slate-600 px-3 py-1 text-sm hover:bg-slate-900">
                  Cancel
                </button>
                <button className="rounded border border-slate-600 px-3 py-1 text-sm hover:bg-slate-900">
                  Save
                </button>
              </div>
            </div>

            <ul className="mt-3 list-disc pl-5 text-sm text-slate-300">
              <li>
                親に <span className="font-mono">flex justify-between</span> →
                左ブロックと右ブロックが両端へ
              </li>
              <li>
                ボタン側は <span className="font-mono">flex gap-2</span> →
                ボタン同士を横並び
              </li>
            </ul>
          </div>

          {/* Flex例2：固定 + 可変（サイドバー + メイン） */}
          <div className="rounded-xl border border-slate-700 p-4">
            <div className="text-sm text-slate-300">
              例2：サイドバー固定 + メイン可変（鉄板）
            </div>

            <div className="mt-3 flex min-h-[160px] rounded-lg border border-slate-700">
              <aside className="w-56 shrink-0 border-r border-slate-700 p-3">
                <div className="font-semibold">Sidebar</div>
                <div className="mt-2 text-sm text-slate-300">
                  w-56 / shrink-0
                </div>
              </aside>

              <main className="flex-1 p-3">
                <div className="font-semibold">Main</div>
                <div className="mt-2 text-sm text-slate-300">
                  flex-1（残り全部）
                </div>
              </main>
            </div>

            <ul className="mt-3 list-disc pl-5 text-sm text-slate-300">
              <li>
                兄弟の <span className="font-mono">w-56</span> が決まる → 残りを{' '}
                <span className="font-mono">flex-1</span> が取る
              </li>
              <li>
                固定側に <span className="font-mono">shrink-0</span>{' '}
                を付けると「潰れにくい」
              </li>
            </ul>
          </div>

          {/* Flex例3：折り返し（タグ・チップ） */}
          <div className="rounded-xl border border-slate-700 p-4">
            <div className="text-sm text-slate-300">
              例3：タグの折り返し（wrap）
            </div>

            <div className="mt-3 flex flex-wrap gap-2 rounded-lg border border-slate-700 p-3">
              {[
                'React',
                'Tailwind',
                'Flex',
                'Grid',
                'Layout',
                'UI',
                'Design',
                'Chip',
                'Wrap',
                'LayoutLab',
              ].map((t) => (
                <span
                  key={t}
                  className="rounded-full border border-slate-600 px-3 py-1 text-sm"
                >
                  {t}
                </span>
              ))}
            </div>

            <ul className="mt-3 list-disc pl-5 text-sm text-slate-300">
              <li>
                <span className="font-mono">flex-wrap</span>{' '}
                で「横幅が足りない分は次の行へ」
              </li>
              <li>一覧だけど「行/列を厳密に揃えない」なら flex の方が楽</li>
            </ul>
          </div>
        </section>

        {/* ===================== GRID ===================== */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">Grid（2次元レイアウト）</h2>

          {/* Grid例1：カード一覧（レスポンシブ列数） */}
          <div className="rounded-xl border border-slate-700 p-4">
            <div className="text-sm text-slate-300">
              例1：カード一覧（列数をレスポンシブで変える）
            </div>

            <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="rounded-lg border border-slate-700 p-4">
                  <div className="font-semibold">Card {i + 1}</div>
                  <div className="mt-2 text-sm text-slate-300">
                    grid-cols-1 / sm:2 / lg:3
                  </div>
                </div>
              ))}
            </div>

            <ul className="mt-3 list-disc pl-5 text-sm text-slate-300">
              <li>
                親に “列の設計図” <span className="font-mono">grid-cols-*</span>{' '}
                を書くだけで一気に揃う
              </li>
              <li>一覧は grid が最強（gap も直感的）</li>
            </ul>
          </div>

          {/* Grid例2：ダッシュボード（spanで面積を変える） */}
          <div className="rounded-xl border border-slate-700 p-4">
            <div className="text-sm text-slate-300">
              例2：パネル配置（col-span で大きさを変える）
            </div>

            <div className="mt-3 grid grid-cols-12 gap-4">
              <div className="col-span-12 lg:col-span-8 rounded-lg border border-slate-700 p-4">
                <div className="font-semibold">Main Panel</div>
                <div className="mt-2 text-sm text-slate-300">
                  col-span-12 / lg:col-span-8
                </div>
              </div>

              <div className="col-span-12 lg:col-span-4 rounded-lg border border-slate-700 p-4">
                <div className="font-semibold">Side Panel</div>
                <div className="mt-2 text-sm text-slate-300">
                  col-span-12 / lg:col-span-4
                </div>
              </div>

              <div className="col-span-12 sm:col-span-6 lg:col-span-3 rounded-lg border border-slate-700 p-4">
                <div className="font-semibold">Stat A</div>
              </div>
              <div className="col-span-12 sm:col-span-6 lg:col-span-3 rounded-lg border border-slate-700 p-4">
                <div className="font-semibold">Stat B</div>
              </div>
              <div className="col-span-12 sm:col-span-6 lg:col-span-3 rounded-lg border border-slate-700 p-4">
                <div className="font-semibold">Stat C</div>
              </div>
              <div className="col-span-12 sm:col-span-6 lg:col-span-3 rounded-lg border border-slate-700 p-4">
                <div className="font-semibold">Stat D</div>
              </div>
            </div>

            <ul className="mt-3 list-disc pl-5 text-sm text-slate-300">
              <li>
                grid は「マス目（12列など）」を作って{' '}
                <span className="font-mono">col-span</span>{' '}
                で面積を割り当てるのが強い
              </li>
              <li>ダッシュボード系はこれでほぼ作れる</li>
            </ul>
          </div>

          {/* Grid例3：フォーム（ラベルと入力を綺麗に整列） */}
          <div className="rounded-xl border border-slate-700 p-4">
            <div className="text-sm text-slate-300">
              例3：フォーム（2列で整列）
            </div>

            <div className="mt-3 grid grid-cols-12 gap-3 rounded-lg border border-slate-700 p-3">
              <label className="col-span-12 sm:col-span-3 text-sm text-slate-300">
                Name
              </label>
              <input
                className="col-span-12 sm:col-span-9 rounded border border-slate-600 bg-black px-3 py-2 text-sm"
                placeholder="your name"
              />

              <label className="col-span-12 sm:col-span-3 text-sm text-slate-300">
                Email
              </label>
              <input
                className="col-span-12 sm:col-span-9 rounded border border-slate-600 bg-black px-3 py-2 text-sm"
                placeholder="you@example.com"
              />
            </div>

            <ul className="mt-3 list-disc pl-5 text-sm text-slate-300">
              <li>「ラベル列」と「入力列」を grid で固定すると崩れにくい</li>
              <li>
                小さい画面では <span className="font-mono">col-span-12</span>{' '}
                で縦積みにして、sm以上で2列にするのが定番
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}

// Modal
// モーダルのフォーカス管理をするための関数

export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selectors = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(',');

  return Array.from(container.querySelectorAll<HTMLElement>(selectors)).filter(
    (el) => !el.hasAttribute('disabled') && !el.getAttribute('aria-hidden')
  );
}

type ModalProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  initialFocusRef?: React.RefObject<HTMLElement>;
};

function Modal({
  open,
  onClose,
  title,
  children,
  initialFocusRef,
}: ModalProps) {
  const panelRef = useRef<HTMLDivElement | null>(null);
  const titleId = `modal-title-${crypto.randomUUID().slice(2)}`;

  useEffect(() => {
    if (!open) return;

    // スクロールロック
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    // フォーカス復元用
    const prevActive = document.activeElement as HTMLElement | null;

    // 初期フォーカス（描画後に）
    const t = window.setTimeout(() => {
      const panel = panelRef.current;
      if (!panel) return;

      const target = initialFocusRef?.current;
      if (target) {
        target.focus();
        return;
      }

      const focusables = getFocusableElements(panel);
      (focusables[0] ?? panel).focus();
    }, 0);

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

        // フォーカスできる要素が無ければパネルに固定
        if (focusables.length === 0) {
          e.preventDefault();
          panel.focus();
          return;
        }

        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        const active = document.activeElement as HTMLElement | null;

        // 前方向（Shift+Tab）
        if (e.shiftKey) {
          if (!active || active === first) {
            e.preventDefault();
            last.focus();
          }
          return;
        }

        // 後方向（Tab）
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

      // スクロール復元
      document.body.style.overflow = prevOverflow;

      // フォーカス復元
      prevActive?.focus?.();
    };
  }, [open, onClose, initialFocusRef]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/70 flex min-h-full items-center justify-center p-4"
      onMouseDown={(e) => {
        // 背景（オーバーレイ）クリックで閉じる
        if (e.target === e.currentTarget) onClose();
      }}
      aria-hidden={false}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className="relative w-[min(560px,92vw)] rounded-2xl border border-slate-700 bg-black p-5 text-white shadow-lg outline-none"
        onMouseDown={(e) => {
          // パネル内のクリックで背景閉じが発火しないように
          e.stopPropagation();
        }}
      >
        {/* ここが position の学びどころ：親 relative + 子 absolute */}
        <button
          type="button"
          onClick={onClose}
          className="absolute right-3 top-3 rounded-lg border border-slate-600 px-2 py-1 text-sm hover:bg-slate-900"
          aria-label="Close modal"
        >
          ✕
        </button>

        <h2 id={titleId} className="text-lg font-semibold">
          {title}
        </h2>

        <div className="mt-3 text-sm text-slate-300">{children}</div>

        <div className="mt-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-600 px-3 py-1 text-sm hover:bg-slate-900"
          >
            Cancel
          </button>
          <button
            type="button"
            className="rounded-lg border border-slate-600 px-3 py-1 text-sm hover:bg-slate-900"
          >
            OK
          </button>
        </div>
      </div>
    </div>
  );
}

/** デモ用 */
export function ModalExample() {
  const [open, setOpen] = useState(false);
  const okRef = useRef<HTMLButtonElement | null>(null);

  return (
    <div className="min-h-screen bg-black p-6 text-white">
      <button
        className="rounded-lg border border-slate-600 px-4 py-2 hover:bg-slate-900"
        onClick={() => setOpen(true)}
      >
        Open Modal
      </button>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Position Modal Example"
        initialFocusRef={okRef as React.RefObject<HTMLElement>}
      >
        <p>
          これは <span className="font-mono">fixed inset-0</span>{' '}
          のオーバーレイ上に、 パネルを中央配置しています。
        </p>

        <div className="mt-4">
          <button
            ref={okRef}
            className="rounded-lg border border-slate-600 px-3 py-1 text-sm hover:bg-slate-900"
          >
            初期フォーカスされるボタン
          </button>
        </div>
      </Modal>
    </div>
  );
}

// Dropdown
// ドロップダウンのフォーカス管理をするための関数

type MenuItem = {
  id: string;
  label: string;
  onSelect: () => void;
  danger?: boolean;
};

function getMenuItems(container: HTMLElement | null): HTMLButtonElement[] {
  if (!container) return [];
  return Array.from(
    container.querySelectorAll<HTMLButtonElement>('button[role="menuitem"]')
  );
}

export function DropdownExample() {
  const [open, setOpen] = useState(false);

  // positionの基準になる「親」
  const rootRef = useRef<HTMLDivElement | null>(null);

  // フォーカス制御用
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  const menuId = `menu-${crypto.randomUUID().slice(2)}`;

  const items: MenuItem[] = [
    {
      id: 'profile',
      label: 'プロフィール',
      onSelect: () => console.log('profile'),
    },
    { id: 'settings', label: '設定', onSelect: () => console.log('settings') },
    { id: 'billing', label: '支払い', onSelect: () => console.log('billing') },
    {
      id: 'logout',
      label: 'ログアウト',
      onSelect: () => console.log('logout'),
      danger: true,
    },
  ];

  const close = () => setOpen(false);

  useEffect(() => {
    if (!open) return;

    // 開いたら最初の項目にフォーカス
    const t = window.setTimeout(() => {
      const first = getMenuItems(menuRef.current)[0];
      first?.focus();
    }, 0);

    const onDocMouseDown = (e: MouseEvent) => {
      const root = rootRef.current;
      if (!root) return;

      // ルート外をクリックしたら閉じる
      if (!root.contains(e.target as Node)) close();
    };

    const onDocKeyDown = (e: KeyboardEvent) => {
      if (!open) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        close();
        return;
      }

      // 矢印キーで項目移動（メニューが開いている時）
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();

        const itemsEls = getMenuItems(menuRef.current);
        if (itemsEls.length === 0) return;

        const active = document.activeElement as HTMLElement | null;
        const idx = itemsEls.findIndex((el) => el === active);

        const next =
          e.key === 'ArrowDown'
            ? itemsEls[(idx + 1 + itemsEls.length) % itemsEls.length]
            : itemsEls[(idx - 1 + itemsEls.length) % itemsEls.length];

        next?.focus();
      }

      // Enter/Space は button が勝手に押されるが、
      // フォーカスがメニュー外にある場合でも操作できるようにしたいならここで補強する
    };

    document.addEventListener('mousedown', onDocMouseDown);
    document.addEventListener('keydown', onDocKeyDown);

    return () => {
      window.clearTimeout(t);
      document.removeEventListener('mousedown', onDocMouseDown);
      document.removeEventListener('keydown', onDocKeyDown);
    };
  }, [open]);

  // 閉じたらトリガーボタンにフォーカスを戻す
  useEffect(() => {
    if (open) return;
    buttonRef.current?.focus();
  }, [open]);

  return (
    <div className="min-h-screen bg-black p-6 text-white">
      <div className="mx-auto max-w-3xl space-y-6">
        <h1 className="text-xl font-semibold">Dropdown（positionの実装例）</h1>

        {/* ここがポイント：relative を付けた親が absolute の基準になる */}
        <div ref={rootRef} className="relative inline-block">
          <button
            ref={buttonRef}
            type="button"
            className="rounded-lg border border-slate-600 px-4 py-2 hover:bg-slate-900"
            aria-haspopup="menu"
            aria-expanded={open}
            aria-controls={menuId}
            onClick={() => setOpen((v) => !v)}
            onKeyDown={(e) => {
              // ボタンで↓押したら開いて最初にフォーカス、などのUX
              if (e.key === 'ArrowDown') {
                e.preventDefault();
                setOpen(true);
              }
            }}
          >
            Hikaru ▾
          </button>

          {open && (
            <div
              ref={menuRef}
              id={menuId}
              role="menu"
              aria-label="プロフィールメニュー"
              // ここが position の肝：親(relative)を基準に、下に出す
              className="absolute left-0 top-full z-50 w-56 rounded-xl border border-slate-700 bg-black p-2 shadow-lg"
            >
              <div className="px-2 py-2 text-xs text-slate-300">
                signed in as <span className="font-mono">you@example.com</span>
              </div>

              <div className="my-2 border-t border-slate-800" />

              {items.map((it) => (
                <button
                  key={it.id}
                  role="menuitem"
                  type="button"
                  className={[
                    'w-full rounded-lg px-3 py-2 text-left text-sm',
                    'hover:bg-slate-900 focus:bg-slate-900 focus:outline-none',
                    it.danger
                      ? 'text-red-300 hover:text-red-200'
                      : 'text-white',
                  ].join(' ')}
                  onClick={() => {
                    it.onSelect();
                    close();
                  }}
                >
                  {it.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="text-sm text-slate-300">
          <ul className="list-disc space-y-1 pl-5">
            <li>
              <span className="font-mono">relative</span>{' '}
              を付けた親が、メニュー（
              <span className="font-mono">absolute</span>）の座標基準になります
            </li>
            <li>
              <span className="font-mono">absolute right-0 top-full mt-2</span>{' '}
              で「ボタンの右下」に出しています
            </li>
            <li>
              クリック外で閉じる / Escで閉じる / ↑↓で項目移動 が入っています
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
