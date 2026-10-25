import type { EnvData } from "./location";

export type Citation = { source: string; title?: string; page?: number; section?: string; score?: number };
export type SafetyAudit = { verified: boolean; detected_dosages: string[]; unverified_dosages: string[]; safety_note: string };

export type Diagnosis = {
  scan_id: number | null;
  cache_hit: boolean;
  sha256_hash: string;
  filename?: string;
  image_url?: string | null;
  disease: string;
  disease_display: string;
  disease_display_kn: string;
  latin_name?: string | null;
  kind: "disease" | "pest" | "healthy";
  confidence: number;
  is_healthy: boolean;
  distribution: Record<string, number>;
  env_data?: EnvData | null;
  advisory: string;
  sources: string[];
  citations: Citation[];
  is_blended: boolean;
  reasons: string[];
  safety_audit?: SafetyAudit | null;
  provider?: string | null;
  language: string;
  created_at?: string;
};

export type Scan = {
  id: number;
  disease: string;
  disease_display: string;
  disease_display_kn: string;
  confidence: number;
  is_healthy: boolean;
  is_blended: boolean;
  image_url: string | null;
  distribution: Record<string, number>;
  env_data: EnvData | null;
  advisory: string;
  sources: string[] | null;
  citations: Citation[] | null;
  safety_audit: SafetyAudit | null;
  reasons: string[] | null;
  question: string | null;
  language: string;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
};

export type Photo = { media_id: string; url: string; caption: string };

export type Listing = {
  id: number;
  user_id: number;
  title: string;
  variety: string;
  quantity: number;
  quantity_unit: string;
  quantity_kg: number;
  price: number;
  price_unit: string;
  price_per_kg: number;
  farmer_name: string;
  phone_number: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
  distance_km: number | null;
  photos: Photo[];
  created_at: string;
  updated_at?: string | null;
  google_maps_url: string | null;
  whatsapp_url: string | null;
  is_owner: boolean;
  reported_by_me: boolean;
};

export type Thread = { id: string; title: string; created_at: string; updated_at?: string; message_count: number };
export type Message = {
  id: number | string;
  role: "user" | "assistant";
  content: string;
  image_url?: string | null;
  attached_image_name?: string | null;
  disease?: string | null;
  created_at?: string;
  pending?: boolean;
};

export type ChatResponse = {
  session_id: string;
  reply: string;
  history: { role: string; content: string }[];
  disease?: string | null;
  language: string;
  provider?: string;
  sources: { source: string; page?: number; score?: number }[];
  env_used: boolean;
  image_url?: string | null;
};

export type Session = { id: number; device: string; ip: string | null; created_at: string; last_used_at: string; current: boolean };
export type Stats = { scans: number; listings: number; chats: number };

/** Hand-off from Scanner/History to Chat (same fields as the original sessionStorage hand-off). */
export type Handoff = { disease: string; confidence: number; advisory: string; imageUrl?: string | null; mediaId?: string | null; env?: EnvData | null };
