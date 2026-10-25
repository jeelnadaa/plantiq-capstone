import { useEffect, type ReactNode } from "react";
import { HashRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { I18nProvider, useI18n } from "./lib/i18n";
import { ThemeProvider } from "./lib/theme";
import { AuthProvider, useAuth } from "./lib/auth";
import { LocationProvider } from "./lib/location";
import { ToastProvider, useToast } from "./lib/toast";
import { ServerStatusProvider } from "./lib/server-status";
import { needsServerSetup, onSessionExpired } from "./lib/api";
import { initNativeBack } from "./lib/native";
import { Spinner } from "./components/common";
import { ServerSetup } from "./screens/ServerSetup";
import { AuthScreen } from "./screens/Auth";
import { Scanner } from "./screens/Scanner";
import { Chat } from "./screens/Chat";
import { Market } from "./screens/Market";
import { History } from "./screens/History";
import { Profile } from "./screens/Profile";

function Splash() {
  return <div className="screen" style={{ alignItems: "center", justifyContent: "center" }}><Spinner size={36} /></div>;
}

/** Auth guard: server configured → signed in → screen. */
function Private({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  const loc = useLocation();
  if (needsServerSetup()) return <Navigate to="/setup" replace />;
  if (!ready && !user) return <Splash />;
  if (!user) return <Navigate to="/signin" replace state={{ from: loc.pathname }} />;
  return <LocationProvider>{children}</LocationProvider>;
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  if (needsServerSetup()) return <Navigate to="/setup" replace />;
  if (ready && user) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function Effects() {
  const nav = useNavigate();
  const loc = useLocation();
  const toast = useToast();
  const { t } = useI18n();
  useEffect(() => onSessionExpired(() => { toast.show(t("sessionExpired"), "error"); nav("/signin", { replace: true }); }), [nav, toast, t]);
  useEffect(() => { initNativeBack(() => nav("/"), () => window.location.hash === "#/" || window.location.hash === ""); }, [nav]);
  useEffect(() => { window.scrollTo(0, 0); }, [loc.pathname]);
  return null;
}

export function AppRoutes() {
  return (
    <>
      <Effects />
      <Routes>
        <Route path="/setup" element={<ServerSetup />} />
        <Route path="/signin" element={<PublicOnly><AuthScreen mode="signin" /></PublicOnly>} />
        <Route path="/signup" element={<PublicOnly><AuthScreen mode="signup" /></PublicOnly>} />
        <Route path="/" element={<Private><Scanner /></Private>} />
        <Route path="/chat" element={<Private><Chat /></Private>} />
        <Route path="/market" element={<Private><Market /></Private>} />
        <Route path="/history" element={<Private><History /></Private>} />
        <Route path="/profile" element={<Private><Profile /></Private>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <I18nProvider>
      <ThemeProvider>
        <ToastProvider>
          <ServerStatusProvider>
            <AuthProvider>{children}</AuthProvider>
          </ServerStatusProvider>
        </ToastProvider>
      </ThemeProvider>
    </I18nProvider>
  );
}

export default function App() {
  return (
    <Providers>
      <HashRouter>
        <AppRoutes />
      </HashRouter>
    </Providers>
  );
}
