import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  API, api, cacheUser, cachedUser, clearSession, getAccessToken, hasRefreshToken, onSessionExpired, saveSession,
  type TokenResponse, type User,
} from "./api";

type AuthState = {
  user: User | null;
  ready: boolean;
  signIn: (identifier: string, password: string, remember: boolean) => Promise<User>;
  signUp: (body: Record<string, unknown>) => Promise<User>;
  signOut: (everywhere?: boolean) => Promise<void>;
  setUser: (u: User) => void;
  refreshUser: () => Promise<void>;
  acceptSession: (t: TokenResponse) => void;
};

const AuthCtx = createContext<AuthState | null>(null);

function deviceName() {
  const ua = navigator.userAgent;
  if (/Android/i.test(ua)) return "Android phone";
  if (/iPhone|iPad/i.test(ua)) return "iPhone / iPad";
  if (/Windows/i.test(ua)) return "Windows browser";
  if (/Mac OS/i.test(ua)) return "Mac browser";
  return "Browser";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(() => (getAccessToken() || hasRefreshToken() ? cachedUser() : null));
  const [ready, setReady] = useState(false);

  const setUser = useCallback((u: User) => {
    cacheUser(u);
    setUserState(u);
  }, []);

  const acceptSession = useCallback((t: TokenResponse) => {
    saveSession(t);
    setUserState(t.user);
  }, []);

  const refreshUser = useCallback(async () => {
    const me = await api<User>(`${API}/auth/me`);
    setUser(me);
  }, [setUser]);

  useEffect(() => {
    const off = onSessionExpired(() => setUserState(null));
    (async () => {
      if (getAccessToken() || hasRefreshToken()) {
        try {
          await refreshUser();
        } catch (e: any) {
          if (e?.status === 401) {
            clearSession();
            setUserState(null);
          }
          // network errors: keep the cached user so the farmer can still open the app offline
        }
      }
      setReady(true);
    })();
    return () => {
      off();
    };
  }, [refreshUser]);

  const value = useMemo<AuthState>(() => ({
    user, ready, setUser, refreshUser, acceptSession,
    async signIn(identifier, password, remember) {
      const t = await api<TokenResponse>(`${API}/auth/login`, { body: { identifier, password, remember, device: deviceName() }, auth: false });
      acceptSession(t);
      return t.user;
    },
    async signUp(body) {
      const t = await api<TokenResponse>(`${API}/auth/register`, { body: { ...body, device: deviceName() }, auth: false });
      acceptSession(t);
      return t.user;
    },
    async signOut(everywhere = false) {
      try {
        await api(`${API}/auth/${everywhere ? "logout-all" : "logout"}`, { method: "POST", timeoutMs: 5000 });
      } catch {
        /* sign out locally even if the server is unreachable */
      }
      clearSession();
      setUserState(null);
    },
  }), [user, ready, setUser, refreshUser, acceptSession]);

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}
