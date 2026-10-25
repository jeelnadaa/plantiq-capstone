"""Built-in bilingual disease cards used when no LLM provider is reachable (offline advisory).

Doses are limited to widely published CCRI extension practice (e.g. 0.5% Bordeaux mixture). Anything beyond
that tells the farmer to follow the product label / extension officer.
"""
from __future__ import annotations

CARDS: dict[str, dict[str, dict[str, list[str] | str]]] = {
    "Rust": {
        "en": {
            "summary": "Coffee leaf rust (Hemileia vastatrix): orange powdery spots under the leaf, leaves drop early.",
            "today": ["Pick and destroy badly infected leaves.", "Thin shade so the canopy dries faster after rain."],
            "spray": ["Bordeaux mixture 0.5% (1 kg copper sulphate + 1 kg lime in 200 L water), covering the underside of leaves.",
                      "Systemic fungicides only as per the product label or your Coffee Board extension officer."],
            "timing": ["Pre-monsoon (May) and post-monsoon (September–October) sprays.", "Spray on a dry morning; avoid rain within 24 hours."],
            "prevent": ["Grow rust-tolerant selections where possible.", "Balanced fertiliser keeps bushes vigorous."],
        },
        "kn": {
            "summary": "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ: ಎಲೆಯ ಕೆಳಭಾಗದಲ್ಲಿ ಕಿತ್ತಳೆ ಬಣ್ಣದ ಪುಡಿ ಚುಕ್ಕೆಗಳು, ಎಲೆಗಳು ಬೇಗ ಉದುರುತ್ತವೆ.",
            "today": ["ಹೆಚ್ಚು ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದು ನಾಶಮಾಡಿ.", "ಮಳೆಯ ನಂತರ ಗಿಡ ಬೇಗ ಒಣಗಲು ನೆರಳು ಕಡಿಮೆ ಮಾಡಿ."],
            "spray": ["0.5% ಬೋರ್ಡೋ ಮಿಶ್ರಣ (200 ಲೀ ನೀರಿಗೆ 1 kg ಮೈಲುತುತ್ತ + 1 kg ಸುಣ್ಣ), ಎಲೆಯ ಕೆಳಭಾಗಕ್ಕೂ ಸಿಂಪಡಿಸಿ.",
                      "ಇತರ ಶಿಲೀಂಧ್ರನಾಶಕಗಳನ್ನು ಲೇಬಲ್ ಅಥವಾ ಕಾಫಿ ಮಂಡಳಿ ಅಧಿಕಾರಿಯ ಸಲಹೆಯಂತೆ ಮಾತ್ರ ಬಳಸಿ."],
            "timing": ["ಮುಂಗಾರು ಪೂರ್ವ (ಮೇ) ಮತ್ತು ಮುಂಗಾರು ನಂತರ (ಸೆಪ್ಟೆಂಬರ್–ಅಕ್ಟೋಬರ್).", "ಒಣ ಬೆಳಿಗ್ಗೆ ಸಿಂಪಡಿಸಿ; 24 ಗಂಟೆ ಮಳೆ ಇರಬಾರದು."],
            "prevent": ["ಸಾಧ್ಯವಾದರೆ ತುಕ್ಕು ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ.", "ಸಮತೋಲಿತ ಗೊಬ್ಬರ ಗಿಡವನ್ನು ಬಲವಾಗಿಡುತ್ತದೆ."],
        },
    },
    "Cerscospora": {
        "en": {
            "summary": "Cercospora leaf spot (brown eye spot): round brown spots with a grey centre and yellow halo; worse on stressed, sun-exposed bushes.",
            "today": ["Restore shade on exposed patches.", "Remove fallen infected leaves and berries."],
            "spray": ["Bordeaux mixture 0.5% on affected blocks.", "Other fungicides only as per label / extension advice."],
            "timing": ["Spray at the start of the monsoon and repeat after heavy rain spells as advised."],
            "prevent": ["Correct nutrition (especially nitrogen and potash) — stressed plants get more spots.", "Mulch to keep soil moisture even."],
        },
        "kn": {
            "summary": "ಸೆರ್ಕೋಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ: ಬೂದು ಮಧ್ಯಭಾಗ ಮತ್ತು ಹಳದಿ ಅಂಚಿನ ಕಂದು ದುಂಡು ಚುಕ್ಕೆಗಳು; ಬಿಸಿಲು ಹೆಚ್ಚಿರುವ ಗಿಡಗಳಲ್ಲಿ ಹೆಚ್ಚು.",
            "today": ["ಬಿಸಿಲು ಬೀಳುವ ಭಾಗಗಳಲ್ಲಿ ನೆರಳು ಒದಗಿಸಿ.", "ಬಿದ್ದ ಸೋಂಕಿತ ಎಲೆ ಮತ್ತು ಹಣ್ಣುಗಳನ್ನು ತೆಗೆಯಿರಿ."],
            "spray": ["ಬಾಧಿತ ಭಾಗಗಳಿಗೆ 0.5% ಬೋರ್ಡೋ ಮಿಶ್ರಣ.", "ಇತರ ಔಷಧಗಳನ್ನು ಲೇಬಲ್ / ಅಧಿಕಾರಿಯ ಸಲಹೆಯಂತೆ ಮಾತ್ರ."],
            "timing": ["ಮುಂಗಾರು ಆರಂಭದಲ್ಲಿ ಸಿಂಪಡಿಸಿ, ಭಾರೀ ಮಳೆಯ ನಂತರ ಸಲಹೆಯಂತೆ ಪುನರಾವರ್ತಿಸಿ."],
            "prevent": ["ಸರಿಯಾದ ಪೋಷಕಾಂಶ (ಸಾರಜನಕ ಮತ್ತು ಪೊಟ್ಯಾಷ್) ನೀಡಿ.", "ಮಣ್ಣಿನ ತೇವಾಂಶಕ್ಕಾಗಿ ಹೊದಿಕೆ ಮಾಡಿ."],
        },
    },
    "Phoma": {
        "en": {
            "summary": "Phoma leaf spot / tip blight: dark, irregular spots and blackened young shoots, mostly in cool, wet, windy weather at high elevation.",
            "today": ["Prune and burn blackened shoot tips.", "Plant wind-breaks on exposed slopes."],
            "spray": ["Copper fungicide (e.g. Bordeaux mixture 0.5%) on young flush during cool wet spells.", "Follow label doses for any other fungicide."],
            "timing": ["Protect new growth during the cold, wet months."],
            "prevent": ["Avoid wounds on young shoots; keep bushes well fed."],
        },
        "kn": {
            "summary": "ಫೋಮಾ ಎಲೆ ಚುಕ್ಕೆ / ತುದಿ ಒಣಗು: ಕಪ್ಪು ಅನಿಯಮಿತ ಚುಕ್ಕೆಗಳು, ಎಳೆಯ ಚಿಗುರು ಕಪ್ಪಾಗುತ್ತದೆ; ತಂಪು, ತೇವ, ಗಾಳಿಯ ವಾತಾವರಣದಲ್ಲಿ ಹೆಚ್ಚು.",
            "today": ["ಕಪ್ಪಾದ ಚಿಗುರು ತುದಿಗಳನ್ನು ಕತ್ತರಿಸಿ ಸುಡಿ.", "ಗಾಳಿ ಬೀಸುವ ಇಳಿಜಾರುಗಳಲ್ಲಿ ಗಾಳಿ ತಡೆ ಮರ ನೆಡಿ."],
            "spray": ["ತಂಪು ಮಳೆಗಾಲದಲ್ಲಿ ಎಳೆಯ ಚಿಗುರಿಗೆ ತಾಮ್ರ ಶಿಲೀಂಧ್ರನಾಶಕ (ಉದಾ. 0.5% ಬೋರ್ಡೋ).", "ಇತರ ಔಷಧಗಳಿಗೆ ಲೇಬಲ್ ಪ್ರಮಾಣ ಪಾಲಿಸಿ."],
            "timing": ["ತಂಪು ಮಳೆಗಾಲದಲ್ಲಿ ಹೊಸ ಚಿಗುರನ್ನು ರಕ್ಷಿಸಿ."],
            "prevent": ["ಎಳೆಯ ಚಿಗುರಿಗೆ ಗಾಯವಾಗದಂತೆ ನೋಡಿ; ಉತ್ತಮ ಪೋಷಣೆ ನೀಡಿ."],
        },
    },
    "Miner": {
        "en": {
            "summary": "Coffee leaf miner (Leucoptera): pale brown blotch mines inside the leaf caused by small caterpillars; worse in dry spells.",
            "today": ["Collect and destroy heavily mined leaves.", "Keep moderate shade — open, dry blocks suffer most."],
            "spray": ["Usually not needed for light damage. For severe outbreaks use only insecticides recommended by the Coffee Board, at label dose."],
            "timing": ["Watch closely in the dry season (after the monsoon)."],
            "prevent": ["Encourage natural enemies (parasitic wasps) by avoiding unnecessary sprays."],
        },
        "kn": {
            "summary": "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಕೀಟ: ಸಣ್ಣ ಹುಳುಗಳು ಎಲೆಯೊಳಗೆ ತಿಳಿ ಕಂದು ಸುರಂಗ ಮಾಡುತ್ತವೆ; ಒಣ ಹವೆಯಲ್ಲಿ ಹೆಚ್ಚು.",
            "today": ["ಹೆಚ್ಚು ಬಾಧಿತ ಎಲೆಗಳನ್ನು ಸಂಗ್ರಹಿಸಿ ನಾಶಮಾಡಿ.", "ಮಧ್ಯಮ ನೆರಳು ಇರಲಿ."],
            "spray": ["ಕಡಿಮೆ ಹಾನಿಗೆ ಸಿಂಪಡಣೆ ಬೇಡ. ತೀವ್ರ ಬಾಧೆಯಲ್ಲಿ ಕಾಫಿ ಮಂಡಳಿ ಶಿಫಾರಸು ಮಾಡಿದ ಕೀಟನಾಶಕವನ್ನು ಲೇಬಲ್ ಪ್ರಮಾಣದಲ್ಲಿ ಮಾತ್ರ ಬಳಸಿ."],
            "timing": ["ಮುಂಗಾರು ನಂತರದ ಒಣ ಕಾಲದಲ್ಲಿ ಗಮನವಿಡಿ."],
            "prevent": ["ಅನಗತ್ಯ ಸಿಂಪಡಣೆ ತಪ್ಪಿಸಿ ನೈಸರ್ಗಿಕ ಶತ್ರು ಕೀಟಗಳನ್ನು ಉಳಿಸಿ."],
        },
    },
    "Healthy": {
        "en": {
            "summary": "The leaf looks healthy. Keep up good estate hygiene.",
            "today": ["Check 10 bushes across the block every week, especially under dense shade."],
            "spray": ["No spray needed now."],
            "timing": ["Keep to the routine pre- and post-monsoon prophylactic schedule advised for your area."],
            "prevent": ["Balanced fertiliser, shade regulation and good drainage keep bushes resistant."],
        },
        "kn": {
            "summary": "ಎಲೆ ಆರೋಗ್ಯಕರವಾಗಿದೆ. ತೋಟದ ಸ್ವಚ್ಛತೆಯನ್ನು ಮುಂದುವರಿಸಿ.",
            "today": ["ಪ್ರತಿ ವಾರ ವಿವಿಧ ಭಾಗಗಳ 10 ಗಿಡಗಳನ್ನು ಪರಿಶೀಲಿಸಿ."],
            "spray": ["ಈಗ ಸಿಂಪಡಣೆ ಅಗತ್ಯವಿಲ್ಲ."],
            "timing": ["ನಿಮ್ಮ ಪ್ರದೇಶಕ್ಕೆ ಸಲಹೆಯಾದ ಮುಂಗಾರು ಪೂರ್ವ/ನಂತರದ ನಿಯಮಿತ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಪಾಲಿಸಿ."],
            "prevent": ["ಸಮತೋಲಿತ ಗೊಬ್ಬರ, ನೆರಳು ನಿಯಂತ್ರಣ ಮತ್ತು ಉತ್ತಮ ಬಸಿಗಾಲುವೆ ಗಿಡವನ್ನು ಬಲವಾಗಿಡುತ್ತವೆ."],
        },
    },
}

HEADINGS = {
    "en": {"today": "Do today", "spray": "Spray", "timing": "Timing", "prevent": "Prevent", "weather": "Your weather now",
           "sources": "From the CCRI documents", "offline": "Offline guide (AI assistant not reachable right now)."},
    "kn": {"today": "ಇಂದು ಮಾಡಿ", "spray": "ಸಿಂಪಡಣೆ", "timing": "ಸಮಯ", "prevent": "ತಡೆಗಟ್ಟುವಿಕೆ", "weather": "ನಿಮ್ಮ ಈಗಿನ ಹವಾಮಾನ",
           "sources": "CCRI ದಾಖಲೆಗಳಿಂದ", "offline": "ಆಫ್‌ಲೈನ್ ಮಾರ್ಗದರ್ಶಿ (AI ಸಹಾಯಕ ಈಗ ಲಭ್ಯವಿಲ್ಲ)."},
}


def offline_advisory(disease: str, lang: str, env: dict | None, docs: list[dict]) -> str:
    lang = "kn" if lang == "kn" else "en"
    card = CARDS.get(disease, CARDS["Healthy"])[lang]
    h = HEADINGS[lang]
    lines = [f"**{card['summary']}**", ""]
    for key in ("today", "spray", "timing", "prevent"):
        lines.append(f"## {h[key]}")
        lines.extend(f"- {item}" for item in card[key])  # type: ignore[union-attr]
        lines.append("")
    if env and env.get("available"):
        lines.append(f"## {h['weather']}")
        lines.append(f"- {env.get('temperature')}°C, {env.get('humidity')}% RH, {env.get('rainfall')} mm — {env.get('incubation_risk')}")
        lines.append("")
    if docs:
        lines.append(f"## {h['sources']}")
        for d in docs[:2]:
            excerpt = d["text"].split("] ", 1)[-1][:260].rsplit(" ", 1)[0]
            lines.append(f"- {excerpt}… ({d['source']}, p.{d['metadata'].get('page')})")
        lines.append("")
    lines.append(f"_{h['offline']}_")
    return "\n".join(lines).strip()


def offline_chat_reply(lang: str, disease: str | None, env: dict | None, docs: list[dict], weather_query: bool) -> str:
    if disease and disease in CARDS:
        return offline_advisory(disease, lang, env, docs)
    kn = lang == "kn"
    parts = []
    if weather_query:
        if env and env.get("available"):
            parts.append(("ನಿಮ್ಮ ತೋಟದ ಈಗಿನ ಹವಾಮಾನ: " if kn else "Current conditions at your estate: ")
                         + f"{env.get('temperature')}°C, {env.get('humidity')}% RH, {env.get('rainfall')} mm, "
                         + f"{env.get('wind_speed')} km/h. {env.get('incubation_risk')}")
        else:
            parts.append("ಜಿಪಿಎಸ್ ಸ್ಥಳ ಲಭ್ಯವಿಲ್ಲದ ಕಾರಣ ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ." if kn else
                         "Live weather is unavailable because no GPS location was provided.")
    if docs:
        parts.append("CCRI ದಾಖಲೆಗಳಿಂದ:" if kn else "From the CCRI documents:")
        for d in docs[:2]:
            parts.append(f"- {d['text'].split('] ', 1)[-1][:300]}… ({d['source']}, p.{d['metadata'].get('page')})")
    parts.append(f"_{HEADINGS['kn' if kn else 'en']['offline']}_")
    return "\n".join(parts)
