/** Client-side validation that mirrors the backend rules, with farmer-friendly "what" and "why" messages. */
import type { TKey } from "./i18n/en";

export function normalizePhone(raw: string): string | null {
  let d = (raw || "").replace(/\D/g, "");
  if (d.length === 12 && d.startsWith("91")) d = d.slice(2);
  else if (d.length === 11 && d.startsWith("0")) d = d.slice(1);
  return /^\d{10}$/.test(d) ? d : null;
}

export const isEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());
export const USERNAME_RE = /^[a-z0-9_.]{3,32}$/;
const COMMON = new Set(["password", "password1", "password123", "12345678", "123456789", "1234567890", "qwerty123",
  "qwertyuiop", "11111111", "00000000", "iloveyou", "abc12345", "admin123", "welcome1", "letmein1", "coffee123",
  "plantiq123", "farmer123", "india123", "karnataka1", "passw0rd", "p@ssw0rd", "asdf1234", "zxcvbnm1"]);

export type PasswordRules = { length: boolean; mix: boolean; common: boolean; username: boolean };

export function passwordRules(pw: string, username = ""): PasswordRules {
  return {
    length: pw.length >= 8,
    mix: /[A-Za-z]/.test(pw) && /\d/.test(pw),
    common: pw.length > 0 && !COMMON.has(pw.toLowerCase()),
    username: !username || pw.toLowerCase() !== username.toLowerCase(),
  };
}

/** 0..4, same idea as the backend's score. */
export function passwordScore(pw: string, username = ""): number {
  const r = passwordRules(pw, username);
  let s = 0;
  if (pw.length >= 8) s++;
  if (pw.length >= 12) s++;
  if (r.mix) s++;
  if (/[^A-Za-z0-9]/.test(pw) || (/[a-z]/.test(pw) && /[A-Z]/.test(pw))) s++;
  if (!(r.length && r.mix && r.common && r.username)) s = Math.min(s, 1);
  return s;
}

export function passwordOk(pw: string, username = "") {
  const r = passwordRules(pw, username);
  return r.length && r.mix && r.common && r.username && pw.length <= 128;
}

// ---------------------------------------------------------------- listings
export type ListingDraft = {
  title: string;
  variety: string;
  quantity: string;
  quantityUnit: string;
  customQtyUnit: string;
  price: string;
  priceUnit: string;
  customPriceUnit: string;
  farmerName: string;
  phone: string;
  address: string;
};

export type Issue = { field: keyof ListingDraft; label: TKey; what: TKey; why: TKey };

export function quantityToKg(qty: number, unit: string): number {
  if (!qty || qty <= 0) return 0;
  const u = (unit || "kg").toLowerCase();
  const n = (re: RegExp) => {
    const m = re.exec(u);
    return m ? parseFloat(m[1]) : 1;
  };
  if (u.includes("ton")) return round2(qty * n(/(\d+(?:\.\d+)?)\s*ton/) * 1000);
  if (u.includes("quintal")) return round2(qty * n(/(\d+(?:\.\d+)?)\s*quintal/) * 100);
  if (u.replace(/\s/g, "").includes("50kg")) return round2(qty * 50);
  if (u.replace(/\s/g, "").includes("60kg")) return round2(qty * 60);
  const kg = /(\d+(?:\.\d+)?)\s*(?:kg|kilo)/.exec(u);
  return round2(kg ? qty * parseFloat(kg[1]) : qty);
}

export function priceToPerKg(price: number, unit: string): number {
  if (!price || price <= 0) return 0;
  const u = (unit || "per kg").toLowerCase();
  const n = (re: RegExp) => {
    const m = re.exec(u);
    return m ? parseFloat(m[1]) : 1;
  };
  if (u.includes("ton")) return round2(price / (n(/(\d+(?:\.\d+)?)\s*ton/) * 1000));
  if (u.includes("quintal")) return round2(price / (n(/(\d+(?:\.\d+)?)\s*quintal/) * 100));
  if (u.replace(/\s/g, "").includes("50kg")) return round2(price / 50);
  if (u.replace(/\s/g, "").includes("60kg")) return round2(price / 60);
  const kg = /(\d+(?:\.\d+)?)\s*(?:kg|kilo)/.exec(u);
  return round2(kg && parseFloat(kg[1]) > 0 ? price / parseFloat(kg[1]) : price);
}

const round2 = (v: number) => Math.round(v * 100) / 100;

export function effectiveQtyUnit(d: ListingDraft) {
  return d.quantityUnit === "custom" ? d.customQtyUnit.trim() : d.quantityUnit;
}
export function effectivePriceUnit(d: ListingDraft) {
  return d.priceUnit === "custom" ? d.customPriceUnit.trim() : d.priceUnit;
}

export function validateListing(d: ListingDraft): Issue[] {
  const issues: Issue[] = [];
  if (d.title.trim().length < 3) issues.push({ field: "title", label: "fldTitle", what: "fldTitleWhat", why: "fldTitleWhy" });
  if (d.variety.trim().length < 2) issues.push({ field: "variety", label: "fldVariety", what: "fldVarietyWhat", why: "fldVarietyWhy" });
  const qty = parseFloat(d.quantity);
  if (!(qty > 0)) issues.push({ field: "quantity", label: "fldQty", what: "fldQtyWhat", why: "fldQtyWhy" });
  else if (quantityToKg(qty, effectiveQtyUnit(d)) > 100000) issues.push({ field: "quantity", label: "fldQty", what: "fldQtyMax", why: "fldQtyWhy" });
  if (d.quantityUnit === "custom" && !d.customQtyUnit.trim()) issues.push({ field: "customQtyUnit", label: "fldUnit", what: "fldUnitWhat", why: "fldUnitWhy" });
  const price = parseFloat(d.price);
  if (!(price > 0)) issues.push({ field: "price", label: "fldPrice", what: "fldPriceWhat", why: "fldPriceWhy" });
  else if (price > 1_000_000) issues.push({ field: "price", label: "fldPrice", what: "fldPriceMax", why: "fldPriceWhy" });
  if (d.priceUnit === "custom" && !d.customPriceUnit.trim()) issues.push({ field: "customPriceUnit", label: "fldUnit", what: "fldUnitWhat", why: "fldUnitWhy" });
  if (d.farmerName.trim().length < 2) issues.push({ field: "farmerName", label: "fldFarmer", what: "fldFarmerWhat", why: "fldFarmerWhy" });
  if (!normalizePhone(d.phone)) issues.push({ field: "phone", label: "fldPhone", what: "fldPhoneWhat", why: "fldPhoneWhy" });
  if (d.address.trim().length < 3) issues.push({ field: "address", label: "fldAddress", what: "fldAddressWhat", why: "fldAddressWhy" });
  return issues;
}

export function validCoords(lat: number, lng: number) {
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}
