'use client';

import { useMeals, useDeleteMeal } from '../hooks/useMeals';
import { AddMealDialog } from '@/modules/meals/ui/AddMealDialog';
import { MoreHorizontal, Trash2 } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu';

export const MealList = () => {
  const today = new Date().toISOString().split('T')[0];
  const { data: meals, isLoading, error } = useMeals(today);
  const { mutate: deleteMeal } = useDeleteMeal();

  if (isLoading) return <div className="p-4 text-center">読み込み中...</div>;
  if (error)
    return <div className="p-4 text-red-500">エラーが発生しました</div>;

  return (
    <div className="space-y-6">
      {/* 登録ボタンを配置 */}
      <AddMealDialog />

      <div>
        <h2 className="text-lg font-bold mb-4">今日の食事 ({today})</h2>

        {meals?.length === 0 ? (
          <div className="text-center py-8 text-gray-500 bg-white rounded-lg border border-dashed">
            まだ記録がありません。
            <br />
            上のボタンから追加してください。
          </div>
        ) : (
          <ul className="space-y-3">
            {meals?.map((meal) => (
              <li
                key={meal.id}
                className="p-4 border rounded-lg bg-white shadow-sm flex justify-between items-start"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        meal.meal_type === 'main'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-orange-100 text-orange-700'
                      }`}
                    >
                      {meal.meal_type === 'main' ? '食事' : '間食'}
                    </span>
                    <span className="font-bold text-gray-800">{meal.name}</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {meal.amount_value
                      ? `${meal.amount_value}${meal.amount_unit}`
                      : '量指定なし'}
                  </div>
                </div>

                {/* 操作メニュー */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <span className="sr-only">メニューを開く</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      className="text-red-600 focus:text-red-600"
                      onClick={() => {
                        if (confirm('本当に削除しますか？')) {
                          deleteMeal(meal.id);
                        }
                      }}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      削除
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
