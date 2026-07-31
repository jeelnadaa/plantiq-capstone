from typing import Dict, Any

TRANSLATIONS = {
    "en": {
        "app_title": "PlantIQ - Coffee Agronomy",
        "scanner_title": "Leaf Disease Diagnosis",
        "chatbot_title": "Agri AI Assistant",
        "marketplace_title": "Coffee Marketplace",
        "no_image_selected": "No image selected for current query.",
        "image_attached": "Attached leaf image for review.",
        "location_allowed": "Location enabled for environment analysis.",
        "location_disallowed": "Location access disabled. Using general context.",
        "low_confidence_badge": "Blended Advisory (Low Confidence Caution)"
    },
    "kn": {
        "app_title": "ಪ್ಲಾಂಟ್-ಐಕ್ಯೂ - ಕಾಫಿ ಕೃಷಿ",
        "scanner_title": "ಎಲೆ ರೋಗ ನಿರ್ಣಯ",
        "chatbot_title": "ಕೃಷಿ ಎಐ ಸಹಾಯಕ",
        "marketplace_title": "ಕಾಫಿ ಮಾರುಕಟ್ಟೆ",
        "no_image_selected": "ಪ್ರಸ್ತುತ ಪ್ರಶ್ನೆಗೆ ಯಾವುದೇ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆ ಮಾಡಲಾಗಿಲ್ಲ.",
        "image_attached": "ಪರಿಶೀಲನೆಗಾಗಿ ಎಲೆ ಚಿತ್ರವನ್ನು ಲಗತ್ತಿಸಲಾಗಿದೆ.",
        "location_allowed": "ಪರಿಸರ ವಿಶ್ಲೇಷಣೆಗಾಗಿ ಸ್ಥಳವನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.",
        "location_disallowed": "ಸ್ಥಳ ಪ್ರವೇಶವನ್ನು ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ. ಸಾಮಾನ್ಯ ವಿಷಯ ಬಳಸಲಾಗುತ್ತಿದೆ.",
        "low_confidence_badge": "ಸಂಯೋಜಿತ ಸಲಹೆ (ಕಡಿಮೆ ನಂಬಿಕೆಯ ಎಚ್ಚರಿಕೆ)"
    }
}

def get_translations(lang: str = "en") -> Dict[str, str]:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
