import type { Meal } from '../types';

export function buildDemoMeals(): Meal[] {
  const today = new Date();
  const names = [
    'Chicken Bowl',
    'Salmon Set',
    'Protein Shake',
    'Pasta',
    'Greek Yogurt',
    'Oatmeal',
    'Sushi',
    'Curry',
    'Steak',
    'Salad',
    'Ramen',
  ];
  const statuses: Meal['status'][] = [
    'logged',
    'logged',
    'draft',
    'logged',
    'flagged',
  ];

  const items: Meal[] = [];
  for (let i = 0; i < 14; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(d.getDate()).padStart(2, '0')}`;

    const count = 2 + (i % 3);
    for (let j = 0; j < count; j++) {
      const calories = 280 + ((i * 37 + j * 83) % 520);
      const protein = 12 + ((i * 5 + j * 7) % 40);
      const carbs = 25 + ((i * 9 + j * 11) % 80);
      const fat = 8 + ((i * 3 + j * 5) % 28);

      items.push({
        id: `${date}-${j}`,
        date,
        title: names[(i * 3 + j) % names.length],
        calories,
        protein,
        carbs,
        fat,
        status: statuses[(i + j) % statuses.length],
      });
    }
  }

  items.sort((a, b) =>
    a.date === b.date ? a.id.localeCompare(b.id) : b.date.localeCompare(a.date)
  );
  return items;
}
