'use client';

import React from 'react';
import type { Meal } from '../../types';
import { Modal } from '../../ui/Modal';
import { Button } from '../../ui/Button';
import { StatusPill } from './StatusPill';
import { formatNumber } from '../../lib/format';

export function MealDetailsModal({
  meal,
  onClose,
  onSave,
}: {
  meal: Meal | null;
  onClose: () => void;
  onSave: () => void;
}) {
  const open = Boolean(meal);

  return (
    <Modal open={open} title={meal ? meal.title : 'Details'} onClose={onClose}>
      {meal && (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Date
              </div>
              <div className="mt-1 text-sm font-semibold">{meal.date}</div>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Status
              </div>
              <div className="mt-2">
                <StatusPill status={meal.status} />
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-950">
            <div className="text-sm font-semibold">Macros</div>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                {
                  label: 'Calories',
                  value: `${formatNumber(meal.calories)} kcal`,
                },
                { label: 'Protein', value: `${formatNumber(meal.protein)} g` },
                { label: 'Carbs', value: `${formatNumber(meal.carbs)} g` },
                { label: 'Fat', value: `${formatNumber(meal.fat)} g` },
              ].map((it) => (
                <div
                  key={it.label}
                  className="rounded-2xl bg-gray-50 p-3 dark:bg-gray-900"
                >
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {it.label}
                  </div>
                  <div className="mt-1 text-sm font-semibold">{it.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2">
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
            <Button onClick={onSave}>Save changes</Button>
          </div>
        </div>
      )}
    </Modal>
  );
}
