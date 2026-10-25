# 🛒 Module 5: Direct-to-Buyer Marketplace & Spatial Discovery Engine

## 1. Executive Summary & Problem Statement
Smallholder coffee growers are traditionally subject to multi-tiered middleman brokerage fees, opaque parchment pricing, and geographic isolation from premium roasters and direct green bean buyers.

The **Marketplace & Spatial Discovery Module** provides a decentralized, peer-to-peer agricultural marketplace enabling planters to publish lot-level crop listings with:
1. **Multi-Image Galleries with Descriptive Lot Captions**
2. **Inline Estate GPS Coordinates & Google Maps Spatial Navigation**
3. **1-Tap Direct Telephony & WhatsApp Business Protocol Handshake**
4. **Ownership Filtering & Client-Side Search Indexing**

---

## 2. Technical Architecture & Data Schema

### 2.1 Database Schema (`MarketplaceListing`)
```sql
CREATE TABLE marketplace_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    variety VARCHAR(80) NOT NULL,          -- 'Arabica Selection 795', 'Robusta CXR', etc.
    quantity_kg FLOAT NOT NULL,
    price_per_kg FLOAT NOT NULL,
    farmer_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    photos_json TEXT,                     -- JSON Array of { url, caption }
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 3. Spatial Estate Routing & External App Handshake

### 3.1 Haversine Distance Calculation
When buyers search for nearby estates or compute transit logistics from curing works:
$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
Where $R = 6371 \text{ km}$, $\phi$ represents latitude, and $\lambda$ represents longitude.

### 3.2 Native Intent Bridge Protocol
To prevent WebView navigation errors inside mobile apps (e.g. `ERR_UNKNOWN_URL_SCHEME`):
* **WhatsApp Communication**:
  $$\text{URI} = \text{https://wa.me/} + \text{PhoneNumber} + \text{?text=} + \text{EncodedMessage}$$
* **Google Maps Navigation**:
  $$\text{URI} = \text{https://www.google.com/maps/search/?api=1\&query=} + \text{Lat} + \text{,} + \text{Lng}$$
* **Native Telephony**:
  $$\text{URI} = \text{tel:} + \text{PhoneNumber}$$

All external URIs are launched via `@capacitor/browser` and Android OS system intent handlers, allowing buyers to message planters or navigate to farm gates directly in Google Maps.
