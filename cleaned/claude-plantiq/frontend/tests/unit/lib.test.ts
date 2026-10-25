import { describe, expect, it } from "vitest";
import en from "../../src/lib/i18n/en";
import kn from "../../src/lib/i18n/kn";
import { format, translate } from "../../src/lib/i18n";
import { normalizeServerUrl, isPrivateHost } from "../../src/lib/api";
import {
  isEmail, normalizePhone, passwordOk, passwordRules, passwordScore, priceToPerKg, quantityToKg, validateListing, validCoords,
  type ListingDraft,
} from "../../src/lib/validation";
import { dayBucket, diseaseName, formatCountdown, haversineKm, num, parseDate, timeAgo } from "../../src/lib/format";
import { parseBlocks } from "../../src/lib/markdown";

describe("i18n", () => {
  it("has identical keys in English and Kannada", () => {
    expect(Object.keys(kn).sort()).toEqual(Object.keys(en).sort());
  });
  it("has no empty translations and keeps placeholders", () => {
    for (const k of Object.keys(en) as (keyof typeof en)[]) {
      expect(kn[k].trim().length, k).toBeGreaterThan(0);
      const ph = (s: string) => (s.match(/\{\w+\}/g) ?? []).sort().join();
      expect(ph(kn[k]), k).toBe(ph(en[k]));
    }
  });
  it("interpolates and falls back", () => {
    expect(format("Hi {name}", { name: "Ravi" })).toBe("Hi Ravi");
    expect(format("Hi {name}")).toBe("Hi {name}");
    expect(translate("kn", "navScan")).toBe("ಸ್ಕ್ಯಾನ್");
    expect(translate("en", "greeting", { name: "Ravi" })).toBe("Hello, Ravi");
  });
});

describe("server URL normalisation (dynamic backend)", () => {
  it.each([
    ["192.168.1.15", "http://192.168.1.15:8000"],
    ["192.168.1.15:9000/", "http://192.168.1.15:9000"],
    [" http://10.0.0.5:8000/// ", "http://10.0.0.5:8000"],
    ["https://plantiq.example.com", "https://plantiq.example.com"],
    ["https://abc.trycloudflare.com/", "https://abc.trycloudflare.com"],
    ["localhost", "http://localhost:8000"],
    ["", ""],
    ["http://", ""],
  ])("%s → %s", (input, out) => expect(normalizeServerUrl(input)).toBe(out));
  it("detects private hosts", () => {
    expect(isPrivateHost("192.168.0.2")).toBe(true);
    expect(isPrivateHost("172.20.1.1")).toBe(true);
    expect(isPrivateHost("8.8.8.8")).toBe(false);
  });
});

describe("validation", () => {
  it("normalises Indian phone numbers", () => {
    expect(normalizePhone("+91 98765 43210")).toBe("9876543210");
    expect(normalizePhone("098765-43210")).toBe("9876543210");
    expect(normalizePhone("12345")).toBeNull();
  });
  it("checks emails and coordinates", () => {
    expect(isEmail("a@b.co")).toBe(true);
    expect(isEmail("not-email")).toBe(false);
    expect(validCoords(13.3, 75.7)).toBe(true);
    expect(validCoords(91, 0)).toBe(false);
    expect(validCoords(NaN, 1)).toBe(false);
  });
  it("mirrors the backend password policy", () => {
    expect(passwordOk("Coffee2026!")).toBe(true);
    expect(passwordOk("short1")).toBe(false);
    expect(passwordOk("password123")).toBe(false);
    expect(passwordOk("ravi2026", "ravi2026")).toBe(false);
    expect(passwordRules("abc").length).toBe(false);
    expect(passwordScore("Estate-Coffee-2026")).toBe(4);
    expect(passwordScore("password123")).toBeLessThanOrEqual(1);
  });
  it.each([
    [2, "ton", 2000], [3, "quintal", 300], [10, "bag (50kg)", 500], [4, "bag (60kg)", 240], [8, "25 kg sack", 200], [5, "kg", 5],
  ])("qty %s %s = %s kg", (q, u, kg) => expect(quantityToKg(q, u)).toBe(kg));
  it.each([
    [35000, "per ton", 35], [900, "per 2 kg", 450], [9500, "per 50kg bag", 190], [40000, "per quintal", 400], [420, "per kg", 420],
  ])("price %s %s = %s/kg", (p, u, v) => expect(priceToPerKg(p, u)).toBe(v));

  const ok: ListingDraft = { title: "Arabica AA", variety: "Arabica", quantity: "2", quantityUnit: "ton", customQtyUnit: "", price: "420",
    priceUnit: "per kg", customPriceUnit: "", farmerName: "Ravi", phone: "9876543210", address: "Mudigere" };
  it("accepts a complete listing", () => expect(validateListing(ok)).toEqual([]));
  it("explains every missing field with what and why", () => {
    const issues = validateListing({ ...ok, title: "", phone: "123", price: "0", quantityUnit: "custom" });
    expect(issues.map((i) => i.field)).toEqual(["title", "customQtyUnit", "price", "phone"]);
    issues.forEach((i) => { expect(en[i.what]).toBeTruthy(); expect(en[i.why]).toBeTruthy(); });
  });
  it("enforces bounds", () => {
    expect(validateListing({ ...ok, quantity: "200" }).map((i) => i.what)).toContain("fldQtyMax");
    expect(validateListing({ ...ok, price: "2000000" }).map((i) => i.what)).toContain("fldPriceMax");
  });
});

describe("format", () => {
  it("haversine matches the backend", () => {
    expect(haversineKm(13.3161, 75.772, 12.42, 75.74)).toBeCloseTo(99.7, 0);
    expect(haversineKm(1, 1, 1, 1)).toBe(0);
  });
  it("parses naive server dates as UTC", () => {
    expect(parseDate("2026-10-25T10:00:00").toISOString()).toBe("2026-10-25T10:00:00.000Z");
    expect(parseDate("2026-10-25T10:00:00+05:30").toISOString()).toBe("2026-10-25T04:30:00.000Z");
  });
  it("relative time and buckets", () => {
    const now = new Date("2026-10-25T12:00:00Z").getTime();
    expect(timeAgo("en", "2026-10-25T11:58:00Z", now)).toBe("2 min ago");
    expect(timeAgo("en", "2026-10-23T12:00:00Z", now)).toBe("2 days ago");
    expect(dayBucket(new Date(), new Date())).toBe("today");
    expect(dayBucket(new Date(Date.now() - 3 * 86400000))).toBe("earlier");
  });
  it("disease names in both languages", () => {
    expect(diseaseName("en", "Cerscospora")).toBe("Cercospora Leaf Spot");
    expect(diseaseName("kn", "Rust")).toBe("ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ");
    expect(diseaseName("en", "Unknown")).toBe("Unknown");
  });
  it("numbers and countdown", () => {
    expect(num(24.0)).toBe("24");
    expect(num(null)).toBe("--");
    expect(formatCountdown(872)).toBe("14:32");
  });
});

describe("markdown parser", () => {
  it("splits headings, lists and paragraphs", () => {
    const b = parseBlocks("## Do today\n- one\n- two\n\nPlain text\nline 2\n1. first\n2. second");
    expect(b.map((x) => x.kind)).toEqual(["h", "ul", "p", "ol"]);
    expect(b[1].lines).toEqual(["one", "two"]);
    expect(b[2].lines).toEqual(["Plain text", "line 2"]);
  });
});
