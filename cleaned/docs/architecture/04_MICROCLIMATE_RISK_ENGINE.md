# ⛅ Module 4: Microclimate & Epidemiological Risk Engine

## 1. Executive Summary & Agronomic Relevance
Coffee fungal pathogens (*Hemileia vastatrix*, *Cercospora coffeicola*, *Phoma costaricensis*) are strictly dependent on environmental microclimates for spore germination, appressorium formation, and leaf penetration.

In South India's Western Ghats coffee belt:
* **Elevation** determines nocturnal temperature dips and dew-point condensation.
* **Relative Humidity ($> 80\%$)** and continuous leaf wetness hours ($> 4 \text{ hours}$) are mandatory for fungal spore germination.
* **Pre-Monsoon Blossom Showers** and **Southwest Monsoon** drive rapid spore dissemination.

The **Microclimate & Risk Engine** automatically fusions geospatial GPS coordinates with real-time numerical weather prediction APIs to ground disease diagnosis and treatment timing in localized plantation weather dynamics.

---

## 2. Real-Time Geospatial Weather Ingestion

### 2.1 Open-Meteo & ERA5 Reanalysis Integration
The system queries Open-Meteo High-Resolution Weather APIs:
* **Current Temperature ($T$)**: $^\circ\text{C}$
* **Relative Humidity ($RH$)**: $\%$
* **Precipitation ($P$)**: $\text{mm/hr}$
* **Wind Speed & Direction ($W$)**: $\text{km/h}$
* **Digital Elevation Model (DEM)**: Meters above sea level ($\text{m a.s.l.}$)

```
[ Mobile GPS Latitude / Longitude ]
                │
                ▼
  [ Open-Meteo NWP & DEM Engine ]
                │
  ┌─────────────┼─────────────┬─────────────┐
  ▼             ▼             ▼             ▼
Temperature  Humidity   Precipitation   Elevation (m)
 (18-28°C)    (85%)        (12mm)          (1150m)
  │             │             │             │
  └─────────────┴──────┬──────┴─────────────┘
                       │
                       ▼
          [ Microclimate Risk Index ]
                       │
                       ▼
          [ Dynamic Spray Scheduling ]
```

---

## 3. Epidemiological Disease Risk Modeling

### 3.1 Coffee Leaf Rust (*Hemileia vastatrix*) Spore Germination Index
The biological risk score $\mathcal{R}_{\text{rust}} \in [0, 1]$ is computed as:
$$\mathcal{R}_{\text{rust}} = f_T(T) \times f_{RH}(RH) \times f_P(P)$$

Where:
* **Temperature Factor $f_T(T)$**: Fungal growth is optimal between $21^\circ\text{C}$ and $25^\circ\text{C}$:
  $$f_T(T) = \exp\left(-\frac{(T - 23)^2}{2 \times 3.5^2}\right)$$
* **Humidity Factor $f_{RH}(RH)$**:
  $$f_{RH}(RH) = \begin{cases} 
  1.0 & \text{if } RH \ge 85\% \\
  \frac{RH - 60}{25} & \text{if } 60\% \le RH < 85\% \\
  0.0 & \text{if } RH < 60\%
  \end{cases}$$
* **Rainfall / Wetness Factor $f_P(P)$**:
  $$f_P(P) = \min\left(1.0, \frac{P}{5.0}\right)$$

### 3.2 Dynamic Agronomic Intervention Triggering
* **High Risk ($\mathcal{R} \ge 0.75$)**: Trigger immediate systemic fungicide recommendation (*Hexaconazole 5% EC @ 2 ml/L* or *Triadimefon 25 WP @ 0.5 g/L*) to eradicate incubating mycelium.
* **Moderate Risk ($0.45 \le \mathcal{R} < 0.75$)**: Recommend protective contact fungicide (*Bordeaux Mixture 1%*) before monsoon showers begin.
* **Low Risk ($\mathcal{R} < 0.45$)**: Focus on cultural canopy shade management, organic copper oxychloride, and nutrient balance.

---

## 4. Zero Mock Data Governance & Bilingual Interface Integration

### 4.1 Strict Zero Mock Data Policy
To ensure agronomic safety and prevent misleading chemical applications:
* **No Hardcoded Numbers**: The backend service (`env_service.py`) never supplies static fallback numbers (e.g. `23.5°C`, `82%`).
* **Explicit Unavailability**: If GPS coordinates are not provided, or external meteorological APIs are unreachable, the service explicitly returns `available: False` with `None` values and `note: "Microclimate sensor data unavailable"`.
* **Frontend Handling**: When `available: False`, all UI metric tiles display **"Not Available"** (English) or **"ಲಭ್ಯವಿಲ್ಲ"** (Kannada), and the alert badge is styled as neutral inactive state without fabricated units.

### 4.2 Instant Language Reactivity (English <-> Kannada)
* **Single-Click Switcher**: Toggling the language button immediately triggers `updateDOMTranslations()` and `LocationManager.renderEnvironmentUI()`.
* **Universal Digits & Units**: Numerical values and scientific units (`27.1°C`, `56%`, `0.0 mm`, `1135 m`, `12.5 km/h`, `6.2`) remain in standard universal formatting for agronomic precision.
* **Linguistic Localization**: All text, status titles, labels (`ತಾಪಮಾನ`, `ಆರ್ದ್ರತೆ / ತೇವಾಂಶ`, `24 ಗಂಟೆಗಳ ಮಳೆ`, `ಸಮುದ್ರ ಮಟ್ಟದಿಂದ ಎತ್ತರ`), apparent temperature prefixes (`ಅನುಭವ: 27.5°C`), risk badges (`ಹೆಚ್ಚಿನ ಅಪಾಯ`, `ಮಧ್ಯಮ ಅಪಾಯ`, `ಕಡಿಮೆ ಅಪಾಯ`), and actionable warnings switch into authentic native Kannada script (ಕನ್ನಡ ಲಿಪಿ).

### 4.3 Multimodal Chatbot Environmental Querying
When queries pertain to weather, microclimate, or ambient estate conditions (`weather`, `temperature`, `humidity`, `ಹವಾಮಾನ`, `ವಾತಾವರಣ`, `ಮಳೆ`, `ತಾಪಮಾನ`):
* **With Active GPS**: The chatbot ingests live sensor readings and explains real-time fungal incubation risks and CCRI spray timings in the chosen language.
* **Without GPS**: The chatbot strictly refuses to fabricate mock weather data and politely guides the farmer in Kannada or English to enable GPS or enter coordinates.
