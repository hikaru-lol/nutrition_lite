export type MealStatus = 'draft' | 'logged' | 'flagged';

export type Meal = {
  id: string;
  date: string; // YYYY-MM-DD
  title: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  status: MealStatus;
};

export type Toast = { id: string; title: string; message?: string };

export type CommandGroup = 'Actions' | 'Filters' | 'Sort';

export type Command = {
  id: string;
  name: string;
  group: CommandGroup;
  icon?: string;
  keywords?: string[];
  shortcut?: string;
  run: () => void;
};

export type SortState = {
  key: 'date' | 'calories' | 'protein';
  dir: 'asc' | 'desc';
};

export type Totals = {
  day: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
};
