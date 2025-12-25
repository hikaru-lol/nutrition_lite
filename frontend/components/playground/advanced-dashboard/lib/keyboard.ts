/**
 * キーボードショートカットを判定するユーティリティ
 */

export interface KeyboardShortcut {
  key: string;
  meta?: boolean;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
}

/**
 * イベントが指定されたショートカットと一致するか判定
 */
export function matchesShortcut(
  event: KeyboardEvent,
  shortcut: KeyboardShortcut
): boolean {
  if (event.key.toLowerCase() !== shortcut.key.toLowerCase()) {
    return false;
  }

  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const metaKey = isMac ? event.metaKey : event.ctrlKey;

  if (shortcut.meta !== undefined && metaKey !== shortcut.meta) {
    return false;
  }

  if (shortcut.ctrl !== undefined && event.ctrlKey !== shortcut.ctrl) {
    return false;
  }

  if (shortcut.shift !== undefined && event.shiftKey !== shortcut.shift) {
    return false;
  }

  if (shortcut.alt !== undefined && event.altKey !== shortcut.alt) {
    return false;
  }

  return true;
}

/**
 * ショートカット文字列を生成（表示用）
 */
export function formatShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = [];

  if (shortcut.meta) {
    parts.push('⌘');
  }
  if (shortcut.ctrl) {
    parts.push('Ctrl');
  }
  if (shortcut.shift) {
    parts.push('Shift');
  }
  if (shortcut.alt) {
    parts.push('Alt');
  }
  parts.push(shortcut.key.toUpperCase());

  return parts.join(' + ');
}


