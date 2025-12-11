// frontend/components/targets/TargetCard.tsx
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type {
  TargetResponseApi,
  GoalType,
  ActivityLevel,
  TargetNutrientApi,
} from '@/lib/api/targets';
import { cn } from '@/lib/utils';

type TargetCardProps = {
  target: TargetResponseApi;
  onActivate: () => void;
};

const GOAL_TYPE_LABEL: Record<GoalType, string> = {
  weight_loss: '減量',
  maintain: '現状維持',
  weight_gain: '増量',
  health_improve: '健康改善',
};

const ACTIVITY_LEVEL_LABEL: Record<ActivityLevel, string> = {
  low: '低め',
  normal: 'ふつう',
  high: '高め',
};

const NUTRIENT_LABEL: Record<TargetNutrientApi['code'], string> = {
  carbohydrate: '炭水化物',
  fat: '脂質',
  protein: 'たんぱく質',
  water: '水分',
  fiber: '食物繊維',
  sodium: 'ナトリウム',
  iron: '鉄',
  calcium: 'カルシウム',
  vitamin_d: 'ビタミンD',
  potassium: 'カリウム',
};

export function TargetCard({ target, onActivate }: TargetCardProps) {
  const { title, goal_type, activity_level, is_active, nutrients } = target;

  const mainNutrients = pickMainNutrients(nutrients);

  return (
    <Card className="space-y-3 h-full flex flex-col justify-between">
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-sm font-semibold text-slate-50">{title}</p>
            <p className="mt-1 text-xs text-slate-400">
              目標: {GOAL_TYPE_LABEL[goal_type]} / 活動量:{' '}
              {ACTIVITY_LEVEL_LABEL[activity_level]}
            </p>
          </div>
          {is_active && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/40 whitespace-nowrap">
              アクティブ
            </span>
          )}
        </div>

        {mainNutrients.length > 0 && (
          <div className="mt-1">
            <p className="text-[11px] font-semibold text-slate-400 mb-1">
              主な栄養目標
            </p>
            <ul className="space-y-0.5">
              {mainNutrients.map((n) => (
                <li key={n.code} className="text-[11px] text-slate-200">
                  <span className="text-slate-400">
                    {NUTRIENT_LABEL[n.code]}：
                  </span>{' '}
                  {n.amount}
                  {n.unit}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="pt-2">
        <Button
          size="sm"
          variant={is_active ? 'secondary' : 'primary'}
          disabled={is_active}
          className={cn('w-full', is_active && 'cursor-default')}
          onClick={onActivate}
        >
          {is_active ? '現在のターゲット' : 'このターゲットを使う'}
        </Button>
      </div>
    </Card>
  );
}

function pickMainNutrients(
  nutrients: TargetNutrientApi[]
): TargetNutrientApi[] {
  // よく見る3つだけピックアップ（PFC）＋あれば食物繊維
  const preferredOrder: TargetNutrientApi['code'][] = [
    'energy' as any, // energy があればここに追加（スキーマに無ければ無視）
    'protein',
    'fat',
    'carbohydrate',
    'fiber',
  ];

  const byCode = new Map(nutrients.map((n) => [n.code, n]));
  const picked: TargetNutrientApi[] = [];

  for (const code of preferredOrder) {
    const found = byCode.get(code);
    if (found) picked.push(found);
  }

  // もし少なすぎる場合は先頭から数件補う
  if (picked.length < 3) {
    const rest = nutrients.filter((n) => !picked.includes(n));
    picked.push(...rest.slice(0, 3 - picked.length));
  }

  return picked;
}
