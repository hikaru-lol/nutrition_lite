'use client';

import { useEffect, useState } from 'react';
import { loadJson, saveJson } from '../lib/storage';

export function useRecentCommands(key: string, limit = 10) {
  const [recentIds, setRecentIds] = useState<string[]>([]);

  useEffect(() => {
    const ids = loadJson<string[]>(key, []);
    setTimeout(() => {
      setRecentIds(ids.filter((x) => typeof x === 'string').slice(0, limit));
    }, 0);
  }, [key, limit]);

  useEffect(() => {
    saveJson(key, recentIds.slice(0, limit));
  }, [key, recentIds, limit]);

  const markRecent = (id: string) => {
    setRecentIds((prev) =>
      [id, ...prev.filter((x) => x !== id)].slice(0, limit)
    );
  };

  const clearRecent = () => setRecentIds([]);

  return { recentIds, markRecent, clearRecent };
}
