import type { Command } from '../../types';

export type CommandSection = { title: string; items: Command[] };

export function buildSections(args: {
  query: string;
  filtered: Command[];
  recentCommands: Command[];
}): CommandSection[] {
  const { query, filtered, recentCommands } = args;

  const q = query.trim();
  const showRecent = q.length === 0 && recentCommands.length > 0;

  const recentSet = new Set(recentCommands.map((c) => c.id));
  const baseList =
    q.length === 0 ? filtered.filter((c) => !recentSet.has(c.id)) : filtered;

  const byGroup = new Map<Command['group'], Command[]>();
  for (const c of baseList)
    byGroup.set(c.group, [...(byGroup.get(c.group) ?? []), c]);

  const ordered: CommandSection[] = [];
  if (showRecent) ordered.push({ title: 'Recent', items: recentCommands });

  (['Actions', 'Filters', 'Sort'] as const).forEach((g) => {
    const items = byGroup.get(g) ?? [];
    if (items.length) ordered.push({ title: g, items });
  });

  return ordered;
}
