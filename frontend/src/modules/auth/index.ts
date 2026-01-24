// src/modules/auth/index.ts
export { login, logout, fetchCurrentUser } from './api/authClient';

// UI / model を export するなら client-safe なものだけ
// export { LoginForm } from "./ui/LoginForm";
// export { useLoginModel } from "./model/useLoginModel";
