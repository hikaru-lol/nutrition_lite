'use client';

import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { GripVertical, Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';

export interface MealItem {
  id: string;
  name: string;
  meal_type: 'main' | 'snack';
  meal_index?: number | null;
  serving_count?: number | null;
  note?: string | null;
}

interface DraggableMealListProps {
  items: MealItem[];
  onReorder?: (newOrder: MealItem[]) => void;
  onDelete?: (itemId: string) => void;
  disabled?: boolean;
  mealTypeLabels: Record<string, string>;
  className?: string;
}

export function DraggableMealList({
  items,
  onReorder,
  onDelete,
  disabled = false,
  mealTypeLabels,
  className,
}: DraggableMealListProps) {
  const handleDragEnd = (result: DropResult) => {
    if (!result.destination || disabled) return;

    const startIndex = result.source.index;
    const endIndex = result.destination.index;

    if (startIndex === endIndex) return;

    const reorderedItems = Array.from(items);
    const [removed] = reorderedItems.splice(startIndex, 1);
    reorderedItems.splice(endIndex, 0, removed);

    onReorder?.(reorderedItems);
  };

  if (items.length === 0) {
    return (
      <div className={`text-sm text-muted-foreground ${className}`}>
        今日の食事ログはまだありません。
      </div>
    );
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="meal-list" isDropDisabled={disabled}>
        {(provided, snapshot) => (
          <div
            {...provided.droppableProps}
            ref={provided.innerRef}
            className={`space-y-2 ${className} ${
              snapshot.isDraggingOver ? 'bg-muted/50 rounded-lg p-2' : ''
            }`}
          >
            {items.map((item, index) => (
              <Draggable
                key={item.id}
                draggableId={item.id}
                index={index}
                isDragDisabled={disabled}
              >
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    className={`flex items-start justify-between rounded-md border p-3 bg-background transition-shadow ${
                      snapshot.isDragging
                        ? 'shadow-lg ring-2 ring-primary/20'
                        : 'hover:shadow-sm'
                    } ${disabled ? 'opacity-50' : ''}`}
                  >
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {/* ドラッグハンドル */}
                      <div
                        {...provided.dragHandleProps}
                        className={`mt-1 text-muted-foreground hover:text-foreground transition-colors ${
                          disabled ? 'cursor-not-allowed' : 'cursor-grab active:cursor-grabbing'
                        }`}
                      >
                        <GripVertical className="w-4 h-4" />
                      </div>

                      {/* アイテム情報 */}
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">{item.name}</div>
                        <div className="text-xs text-muted-foreground mt-1 space-y-0.5">
                          <div>
                            {mealTypeLabels[item.meal_type]}
                            {item.meal_type === 'main' && item.meal_index
                              ? ` #${item.meal_index}`
                              : ''}
                          </div>
                          {item.serving_count && (
                            <div>数量: {item.serving_count}</div>
                          )}
                          {item.note && (
                            <div className="text-xs text-muted-foreground truncate">
                              メモ: {item.note}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* 削除ボタン */}
                    {onDelete && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onDelete(item.id)}
                        disabled={disabled}
                        className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 shrink-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
}