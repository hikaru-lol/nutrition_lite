import { useQuery } from '@tanstack/react-query';
import { fetchTodaySummary } from '../infra/api';

export const useToday = () => {
  return useQuery({
    queryKey: ['today'], // 'meals' が更新されたらここも更新したい場合、キー管理が必要ですが、一旦シンプルに
    queryFn: fetchTodaySummary,
  });
};
