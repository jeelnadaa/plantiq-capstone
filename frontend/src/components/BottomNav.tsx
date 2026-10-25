import { NavLink } from "react-router-dom";
import { History, MessagesSquare, ScanLine, Store, UserRound } from "lucide-react";
import { useI18n } from "../lib/i18n";

const ITEMS = [
  { to: "/", key: "navScan", icon: ScanLine, scan: true },
  { to: "/chat", key: "navAsk", icon: MessagesSquare },
  { to: "/market", key: "navMarket", icon: Store },
  { to: "/history", key: "navHistory", icon: History },
  { to: "/profile", key: "navProfile", icon: UserRound },
] as const;

export function BottomNav() {
  const { t } = useI18n();
  return (
    <nav className="bottom-nav" aria-label="Main">
      {ITEMS.map(({ to, key, icon: Icon, ...rest }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) => `nav-item${"scan" in rest ? " scan" : ""}${isActive ? " active" : ""}`}
          data-testid={`nav-${key}`}
        >
          <span className="nav-ico"><Icon /></span>
          {t(key)}
        </NavLink>
      ))}
    </nav>
  );
}
