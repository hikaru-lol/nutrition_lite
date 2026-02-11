export { TargetGeneratorPage } from './ui/TargetGeneratorPage';
export { useTargetGeneratorPageModel } from './model/useTargetGeneratorPageModel';

export * from './api/targetClient';

// Layer 4: Feature Logic
export { useActiveTargetQuery } from './hooks/useActiveTargetQuery';
export { useTargetManager } from './hooks/useTargetManager';
export { useCreateTargetMutation } from './hooks/useCreateTargetMutation';

export type { ActiveTargetQueryModel } from './hooks/useActiveTargetQuery';
export type { TargetManagerModel } from './hooks/useTargetManager';
export type { CreateTargetMutationModel } from './hooks/useCreateTargetMutation';
