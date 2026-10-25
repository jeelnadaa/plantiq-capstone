import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import type { ReactNode } from "react";
import { Markdown } from "../../src/lib/markdown";
import { I18nProvider } from "../../src/lib/i18n";
import { ThemeProvider } from "../../src/lib/theme";
import { ToastProvider, useToast } from "../../src/lib/toast";
import { PasswordStrength, PasswordInput } from "../../src/components/common";
import { ListingCard } from "../../src/components/ListingCard";
import { Probabilities } from "../../src/components/DiagnosisCard";
import { RiskBanner } from "../../src/components/WeatherCard";
import { PalettePicker } from "../../src/components/modals/PalettePicker";
import { api, ApiError, saveSession, clearSession, setServerUrl, apiBase } from "../../src/lib/api";
import type { Listing } from "../../src/lib/types";

function wrap(ui: ReactNode) {
  return render(
    <I18nProvider><ThemeProvider><ToastProvider><MemoryRouter>{ui}</MemoryRouter></ToastProvider></ThemeProvider></I18nProvider>,
  );
}

beforeEach(() => localStorage.clear());

describe("Markdown (XSS safety)", () => {
  it("renders script/HTML as inert text", () => {
    const { container } = render(<Markdown text={'## Spray\n- <img src=x onerror="alert(1)"> **bold** <script>alert(2)</script>'} />);
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("img")).toBeNull();
    expect(container.textContent).toContain("<script>alert(2)</script>");
    expect(container.querySelector("strong")?.textContent).toBe("bold");
    expect(container.querySelector("h4")?.textContent).toBe("Spray");
  });
  it("supports italics, code and ordered lists", () => {
    const { container } = render(<Markdown text={"1. Use *copper* `0.5%`\n2. Repeat"} />);
    expect(container.querySelectorAll("ol li")).toHaveLength(2);
    expect(container.querySelector("em")?.textContent).toBe("copper");
    expect(container.querySelector("code")?.textContent).toBe("0.5%");
  });
});

describe("Password widgets", () => {
  it("shows rules and strength", () => {
    wrap(<PasswordStrength password="Estate-Coffee-2026" username="ravi" />);
    expect(screen.getByText("Strong")).toBeInTheDocument();
    expect(screen.getByText("At least 8 characters").closest("li")).toHaveClass("ok");
  });
  it("toggles visibility", async () => {
    wrap(<PasswordInput aria-label="pw" defaultValue="secret12" />);
    const input = screen.getByLabelText("pw");
    expect(input).toHaveAttribute("type", "password");
    await userEvent.click(screen.getByRole("button", { name: "Show password" }));
    expect(input).toHaveAttribute("type", "text");
  });
});

const listing: Listing = {
  id: 1, user_id: 2, title: "Robusta Cherry", variety: "Robusta", quantity: 40, quantity_unit: "bag (50kg)", quantity_kg: 2000,
  price: 9500, price_unit: "per 50kg bag", price_per_kg: 190, farmer_name: "Ravi", phone_number: "9876543210", address: "Hassan",
  latitude: 12.9, longitude: 75.8, distance_km: 8.4, photos: [], created_at: new Date().toISOString(),
  google_maps_url: "https://maps.example", whatsapp_url: "https://wa.me/919876543210", is_owner: false, reported_by_me: false,
};

describe("ListingCard", () => {
  it("shows price per unit, ≈₹/kg, distance and buyer actions", () => {
    const onReport = vi.fn();
    wrap(<ListingCard item={listing} onReport={onReport} />);
    expect(screen.getByText("₹9,500")).toBeInTheDocument();
    expect(screen.getByText("≈ ₹190/kg")).toBeInTheDocument();
    expect(screen.getByText("8.4 km")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Call/ })).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("report-btn"));
    expect(onReport).toHaveBeenCalled();
  });
  it("shows owner actions for own lot and hides contact buttons", () => {
    const onEdit = vi.fn();
    wrap(<ListingCard item={{ ...listing, is_owner: true }} onEdit={onEdit} onDelete={() => {}} />);
    expect(screen.queryByRole("button", { name: /Call/ })).toBeNull();
    fireEvent.click(screen.getByTestId("edit-listing"));
    expect(onEdit).toHaveBeenCalled();
  });
  it("escapes listing text", () => {
    wrap(<ListingCard item={{ ...listing, title: "<b>x</b>" }} />);
    expect(screen.getByTestId("listing-title").innerHTML).toBe("&lt;b&gt;x&lt;/b&gt;");
  });
});

describe("Diagnosis + weather widgets", () => {
  it("sorts probabilities with top class first", () => {
    const { container } = wrap(<Probabilities distribution={{ Healthy: 2, Rust: 90, Phoma: 8 }} />);
    expect(container.querySelector(".prob.top")?.textContent).toContain("Leaf rust");
  });
  it("risk banner uses words + level, never colour alone", () => {
    wrap(<RiskBanner env={{ available: true, risk_level: "high" }} />);
    expect(screen.getByTestId("risk-banner")).toHaveAttribute("data-level", "high");
    expect(screen.getByText("High disease risk today")).toBeInTheDocument();
  });
  it("unknown risk when no data", () => {
    wrap(<RiskBanner env={{ available: false }} />);
    expect(screen.getByText("Risk unknown")).toBeInTheDocument();
  });
});

describe("Theme palette", () => {
  it("switches palette and mode on <html>", async () => {
    wrap(<PalettePicker open onClose={() => {}} />);
    await userEvent.click(screen.getByTestId("palette-sunlight"));
    expect(document.documentElement.dataset.palette).toBe("sunlight");
    await userEvent.click(screen.getByTestId("mode-dark"));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(localStorage.getItem("plantiq.palette")).toBe("sunlight");
  });
});

describe("Undo toast", () => {
  afterEach(() => vi.useRealTimers());
  function Trigger({ onUndo, onCommit }: { onUndo: () => void; onCommit: () => void }) {
    const t = useToast();
    return <button onClick={() => t.undo("Scan deleted", onUndo, onCommit)}>go</button>;
  }
  it("undo within 3 s calls onUndo, not onCommit", async () => {
    vi.useFakeTimers();
    const onUndo = vi.fn(), onCommit = vi.fn();
    wrap(<Trigger onUndo={onUndo} onCommit={onCommit} />);
    fireEvent.click(screen.getByText("go"));
    act(() => { vi.advanceTimersByTime(1000); });
    fireEvent.click(screen.getByRole("button", { name: /Undo/ }));
    act(() => { vi.advanceTimersByTime(5000); });
    expect(onUndo).toHaveBeenCalledOnce();
    expect(onCommit).not.toHaveBeenCalled();
  });
  it("commits after 3 s", () => {
    vi.useFakeTimers();
    const onUndo = vi.fn(), onCommit = vi.fn();
    wrap(<Trigger onUndo={onUndo} onCommit={onCommit} />);
    fireEvent.click(screen.getByText("go"));
    act(() => { vi.advanceTimersByTime(3100); });
    expect(onCommit).toHaveBeenCalledOnce();
    expect(screen.queryByText("Scan deleted")).toBeNull();
  });
});

describe("API client", () => {
  afterEach(() => { vi.restoreAllMocks(); clearSession(); setServerUrl(""); });

  it("uses the configured server URL and bearer token", async () => {
    setServerUrl("192.168.1.15");
    expect(apiBase()).toBe("http://192.168.1.15:8000");
    saveSession({ access_token: "AAA", refresh_token: "R".repeat(40), token_type: "bearer", expires_in: 900,
      user: { id: 1, username: "u", full_name: "U", email: null, phone: null, preferred_language: "en", created_at: "" } });
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ ok: 1 }), { status: 200 }));
    await api("/api/v1/scans", { query: { kind: "all", x: undefined } });
    const [url, init] = spy.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://192.168.1.15:8000/api/v1/scans?kind=all");
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer AAA");
  });

  it("refreshes once on 401 and retries", async () => {
    saveSession({ access_token: "OLD", refresh_token: "R".repeat(40), token_type: "bearer", expires_in: 900,
      user: { id: 1, username: "u", full_name: "U", email: null, phone: null, preferred_language: "en", created_at: "" } });
    const spy = vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "expired" }), { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ access_token: "NEW", refresh_token: "S".repeat(40), token_type: "bearer",
        expires_in: 900, user: { id: 1, username: "u", full_name: "U", email: null, phone: null, preferred_language: "en", created_at: "" } }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([1]), { status: 200 }));
    await expect(api("/api/v1/scans")).resolves.toEqual([1]);
    expect(spy).toHaveBeenCalledTimes(3);
    expect(((spy.mock.calls[2][1] as RequestInit).headers as Record<string, string>).Authorization).toBe("Bearer NEW");
  });

  it("turns errors into ApiError with field errors and retry-after", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      detail: { message: "Locked", retry_after: 60 }, code: "locked" }), { status: 423, headers: { "retry-after": "60" } }));
    const err: any = await api("/api/v1/auth/login", { body: {}, auth: false }).catch((e: any) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(423);
    expect(err.retryAfter).toBe(60);
    expect(err.message).toBe("Locked");
  });

  it("network failure becomes a friendly network error", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
    const err: any = await api("/health", { auth: false }).catch((e: any) => e);
    await waitFor(() => expect(err.code).toBe("network"));
  });
});
