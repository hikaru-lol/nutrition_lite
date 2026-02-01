'use client';

import { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export interface FoodSearchResult {
  id: string;
  name: string;
  description?: string;
  calories_per_100g?: number;
  protein_per_100g?: number;
  category?: string;
}

interface FoodSearchInputProps {
  value: string;
  onValueChange: (value: string) => void;
  onSelectFood?: (food: FoodSearchResult) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

// モック食品データベース（実際の実装では API から取得）
const MOCK_FOODS: FoodSearchResult[] = [
  { id: '1', name: '白米', description: 'ご飯', calories_per_100g: 168, protein_per_100g: 2.5, category: '主食' },
  { id: '2', name: '玄米', description: 'ご飯', calories_per_100g: 165, protein_per_100g: 2.8, category: '主食' },
  { id: '3', name: '鶏胸肉', description: '皮なし', calories_per_100g: 108, protein_per_100g: 22.3, category: '肉類' },
  { id: '4', name: '鮭', description: '焼き鮭', calories_per_100g: 139, protein_per_100g: 22.3, category: '魚類' },
  { id: '5', name: 'ブロッコリー', description: '茹で', calories_per_100g: 27, protein_per_100g: 3.5, category: '野菜' },
  { id: '6', name: '卵', description: '鶏卵', calories_per_100g: 151, protein_per_100g: 12.3, category: 'その他' },
  { id: '7', name: 'バナナ', description: '', calories_per_100g: 86, protein_per_100g: 1.1, category: '果物' },
  { id: '8', name: 'パン', description: '食パン', calories_per_100g: 264, protein_per_100g: 9.3, category: '主食' },
  { id: '9', name: '牛乳', description: '普通牛乳', calories_per_100g: 67, protein_per_100g: 3.3, category: '乳製品' },
  { id: '10', name: 'ヨーグルト', description: 'プレーン', calories_per_100g: 62, protein_per_100g: 3.6, category: '乳製品' },
];

export function FoodSearchInput({
  value,
  onValueChange,
  onSelectFood,
  placeholder = "食品名を入力...",
  disabled = false,
  className,
}: FoodSearchInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<FoodSearchResult[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 検索ロジック
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!value.trim()) {
        setSearchResults([]);
        setIsOpen(false);
        return;
      }

      // 実際の実装では API 呼び出し
      const filtered = MOCK_FOODS.filter((food) =>
        food.name.toLowerCase().includes(value.toLowerCase()) ||
        (food.description && food.description.toLowerCase().includes(value.toLowerCase())) ||
        (food.category && food.category.toLowerCase().includes(value.toLowerCase()))
      ).slice(0, 8); // 最大8件

      setSearchResults(filtered);
      setIsOpen(filtered.length > 0);
      setHighlightedIndex(-1);
    }, 200); // デバウンス

    return () => clearTimeout(timeoutId);
  }, [value]);

  // 外部クリックで閉じる
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // キーボードナビゲーション
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < searchResults.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev > 0 ? prev - 1 : searchResults.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < searchResults.length) {
          handleSelectFood(searchResults[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  const handleSelectFood = (food: FoodSearchResult) => {
    onValueChange(food.name);
    onSelectFood?.(food);
    setIsOpen(false);
    setHighlightedIndex(-1);
    inputRef.current?.blur();
  };

  const handleClear = () => {
    onValueChange('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onValueChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => value.trim() && setIsOpen(searchResults.length > 0)}
          placeholder={placeholder}
          disabled={disabled}
          className="pl-10 pr-10"
        />
        {value && !disabled && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="absolute right-1 top-1/2 transform -translate-y-1/2 w-8 h-8 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* 検索結果ドロップダウン */}
      {isOpen && (
        <Card className="absolute top-full left-0 right-0 z-50 mt-1 max-h-64 overflow-y-auto">
          <CardContent className="p-0">
            {searchResults.map((food, index) => (
              <div
                key={food.id}
                className={`px-4 py-3 cursor-pointer border-b border-border last:border-b-0 hover:bg-muted ${
                  index === highlightedIndex ? 'bg-muted' : ''
                }`}
                onClick={() => handleSelectFood(food)}
                onMouseEnter={() => setHighlightedIndex(index)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium truncate">{food.name}</span>
                      {food.description && (
                        <span className="text-sm text-muted-foreground">
                          ({food.description})
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                      {food.category && (
                        <span className="bg-muted px-2 py-0.5 rounded">
                          {food.category}
                        </span>
                      )}
                      {food.calories_per_100g && (
                        <span>{food.calories_per_100g} kcal/100g</span>
                      )}
                      {food.protein_per_100g && (
                        <span>P: {food.protein_per_100g}g</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}