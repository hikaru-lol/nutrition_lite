export function isTypingTarget(el: Element | null) {
  if (!el) return false;
  const tag = el.tagName.toLowerCase();
  const isInput = tag === 'input' || tag === 'textarea' || tag === 'select';
  const isEditable = (el as HTMLElement).isContentEditable;
  return isInput || isEditable;
}
