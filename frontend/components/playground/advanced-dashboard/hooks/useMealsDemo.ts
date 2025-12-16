'use client';

import { useEffect, useState } from 'react';
import { buildDemoMeals } from '../data/demoMeals';
import type { Meal } from '../types';

export function useMealsDemo(delayMs = 650) {
  const [loading, setLoading] = useState(true);
  const [meals, setMeals] = useState<Meal[]>([]);

  useEffect(() => {
    const t = window.setTimeout(() => {
      setMeals(buildDemoMeals());
      setLoading(false);
    }, delayMs);

    return () => window.clearTimeout(t);
  }, [delayMs]);

  return { loading, meals };
}
