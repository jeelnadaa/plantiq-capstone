/** Capacitor helpers that degrade gracefully on the web. */
import { Capacitor } from "@capacitor/core";

export function isNative(): boolean {
  try {
    return Capacitor.isNativePlatform();
  } catch {
    return false;
  }
}

/** Open tel:, WhatsApp and Google Maps links in the right app. */
export async function openExternal(url: string) {
  if (!/^(https:|tel:|mailto:|geo:|whatsapp:)/.test(url)) return; // never open javascript:/data: URLs
  if (isNative() && url.startsWith("https:")) {
    try {
      const { Browser } = await import("@capacitor/browser");
      await Browser.open({ url });
      return;
    } catch {
      /* fall through */
    }
  }
  const win = window.open(url, "_blank", "noopener,noreferrer");
  if (!win) window.location.href = url;
}

type BackHandler = () => boolean; // return true when handled
const handlers: BackHandler[] = [];

/** Register a back-button handler (e.g. an open sheet). Last registered runs first. */
export function pushBackHandler(fn: BackHandler) {
  handlers.push(fn);
  return () => {
    const i = handlers.lastIndexOf(fn);
    if (i >= 0) handlers.splice(i, 1);
  };
}

export function runBackHandlers(): boolean {
  for (let i = handlers.length - 1; i >= 0; i--) if (handlers[i]()) return true;
  return false;
}

// Escape closes only the top-most sheet (same stack as the Android back button).
if (typeof document !== "undefined") {
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && handlers.length) {
      e.preventDefault();
      runBackHandlers();
    }
  });
}

/** Android back: close the top sheet → go to Scanner → exit the app (same order as the original). */
export async function initNativeBack(goHome: () => void, isHome: () => boolean) {
  if (!isNative()) return;
  const { App } = await import("@capacitor/app");
  App.addListener("backButton", () => {
    if (runBackHandlers()) return;
    if (!isHome()) {
      goHome();
      return;
    }
    App.exitApp();
  });
}
