"""Builds 03_rag/questions_curated.json: the fixed RAG question set (written by the authors from the knowledge base).

Every question is something a coffee grower in Karnataka (Chikkamagaluru, Kodagu, Hassan) would ask about disease,
pests or cultivation. Each has a short gold answer and one or more gold evidence quotes copied word-for-word from a
page of the knowledge-base PDFs; this script checks every quote against the PDF text and refuses to write the file if
any quote is not found. Main source: the Central Coffee Research Institute's "Coffee Cultivation Guide for South-West
Monsoon Area Growers" (Coffee Kaipidi, Chikmagalur), plus the rust, Cercospora and leaf-miner papers.

Phoma is absent on purpose: the only Phoma material in the knowledge base (Coffee_Diseases.pdf) extracts as garbled
text, so no system can retrieve it (a knowledge-base gap reported in the paper).

Run:  .venv\\Scripts\\python 03_rag\\make_questions.py   (no API key needed)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import config  # noqa: E402
from common import rag_eval as R  # noqa: E402

G = "coffee_cultivation_guide.pdf"
CER = "cercospora.pdf"
LM = "A_Comprehensive_Review_of_the_Coffee_Leaf_Miner_Le.pdf"
RU = "Strategies_for_Coffee_Leaf_Rust_Management_in_Orga.pdf"

# (id, topic, question, gold answer, source, page, [evidence quotes], kannada version or None)
Q = [
    # ------------------------------------------------------------------ leaf rust
    ("r01", "rust", "When should I give the pre-monsoon Bordeaux mixture spray against coffee leaf rust, and at what strength?",
     "Spray 0.5% Bordeaux mixture during April-May, when rust spreads to young leaves; finish the protection by the first week of June.",
     G, 21, ["Therefore during this period, spray of 0.5% Bordeaux mixture is very important which prevents the spread of disease and protects the young leaves."],
     "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಮುಂಗಾರು ಪೂರ್ವ ಬೋರ್ಡೋ ಮಿಶ್ರಣವನ್ನು ಯಾವಾಗ ಮತ್ತು ಎಷ್ಟು ಸಾಂದ್ರತೆಯಲ್ಲಿ ಸಿಂಪಡಿಸಬೇಕು?"),
    ("r02", "rust", "Should Bordeaux mixture be sprayed on the upper or the lower side of coffee leaves to control rust?",
     "On the lower surface of the leaves; spraying only the upper surface does not protect against the spread of rust.",
     G, 22, ["Spraying the Bordeaux on the upper surface of the leaves does not ensure protection from the spread of the disease."],
     "ತುಕ್ಕು ರೋಗ ನಿಯಂತ್ರಣಕ್ಕೆ ಬೋರ್ಡೋ ಮಿಶ್ರಣವನ್ನು ಎಲೆಯ ಮೇಲ್ಭಾಗಕ್ಕೆ ಸಿಂಪಡಿಸಬೇಕೇ ಅಥವಾ ಕೆಳಭಾಗಕ್ಕೆ?"),
    ("r03", "rust", "How many barrels of Bordeaux spray are needed to cover one hectare of coffee?",
     "About 15 barrels of the spray mixture cover one hectare.",
     G, 22, ["About 15 barrels of the spray mixture adequately covers one hectare of the area."], None),
    ("r04", "rust", "Can I mix urea into the Bordeaux mixture when spraying for leaf rust?",
     "No. Adding urea is a bad practice: nitrogen is lost as ammonia and the spray becomes less effective. Only potash (350 g MOP per barrel) is compatible.",
     G, 22, ["There is a common practice of adding urea to the Bordeaux mixture.", "This is a bad practice which should be avoided."], None),
    ("r05", "rust", "What pH should the Bordeaux mixture have?",
     "Between 9 and 10 for the best efficiency.",
     G, 22, ["Please ensure that the pH of the Bordeaux mixture is maintained between 9 and 10 for the best efficiency of the sprayed mixture."], None),
    ("r06", "rust", "The blossom shower came late and there are no new shoots. What should I spray against leaf rust instead of Bordeaux mixture?",
     "Avoid Bordeaux; spray a systemic fungicide (160 g Bayleton 25 WP or 400 ml Contaf 5EC in 200 litres of water, 7-8 barrels per hectare) during the break in the monsoon.",
     G, 22, ["In such an event, spray of 7-8 barrels per hectare systemic fungicides (160 gm of 25 WP 0.02% Bayleton or 400 ml of Contaf-5EC-0.01% in 200 litres of water) during the break in the monsoon which will help in controlling the CLR disease."],
     "ಹೂಮಳೆ ತಡವಾಗಿ ಬಂದು ಹೊಸ ಚಿಗುರು ಇಲ್ಲದಿದ್ದರೆ ಎಲೆ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಬೋರ್ಡೋ ಬದಲು ಏನು ಸಿಂಪಡಿಸಬೇಕು?"),
    ("r07", "rust", "Which weather conditions favour the early appearance of coffee leaf rust?",
     "Humid cool windy weather from May to November with intermittent showers and sunshine, cloudy misty weather with drizzle in February-March, and thin or no overhead shade during the south-west monsoon.",
     G, 14, ["Thin or no overhead shade during the south-west monsoon is also one of the favourable factors for the development of this disease."], None),
    ("r08", "rust", "When does leaf rust intensify after the monsoon and what should I spray then?",
     "Rust intensifies in September; spray 0.5% Bordeaux mixture at 15 barrels per hectare.",
     G, 28, ["The coffee leaf rust disease intensifies during September month."], None),
    ("r09", "rust", "My estate is above 3500 feet. Do I need to worry about leaf rust in February-March?",
     "Generally no: areas above 3500 feet are usually not affected by leaf rust during February-March.",
     G, 14, ["The areas which are located in elevations more than 3500 feet are generally not affected by leaf rust disease during these months."],
     "ನನ್ನ ತೋಟ 3500 ಅಡಿಗಿಂತ ಎತ್ತರದಲ್ಲಿದೆ. ಫೆಬ್ರವರಿ-ಮಾರ್ಚ್‌ನಲ್ಲಿ ಎಲೆ ತುಕ್ಕು ರೋಗದ ಬಗ್ಗೆ ಚಿಂತಿಸಬೇಕೇ?"),
    ("r10", "rust", "How do I prepare 0.5% Bordeaux mixture?",
     "Dissolve 1 kg copper sulphate in 10 litres of water overnight, dissolve 1 kg spray lime in 10 litres of water, add the lime solution to 180 litres of water and then add the copper sulphate solution while stirring.",
     G, 63, ["Dissolve 1 kg of pure chemically tested copper sulphate in 10 litres of water by suspending it in a gunny bag or cloth bag overnight.",
             "Similarly prepare spray lime solution by dissolving 1 kg of spray lime in 10 litres of water."], None),
    ("r11", "rust", "For an organic coffee farm, what should be the main way to manage leaf rust?",
     "Planting rust-resistant cultivars should be the main control measure, supported by cultural management, biological control and copper fungicides.",
     RU, 9, ["The use of rust-resistant cultivars as the main control measure for rust management should be prioritized, with incentive programs to replace crops with susceptible cultivars in the various organic coffee-producing countries."], None),
    # ------------------------------------------------------------------ Cercospora (brown eye spot)
    ("c01", "cercospora", "How do I protect nursery seedlings from Cercospora (brown eye spot)?",
     "Spray Indofil M-45 (5 g per litre of water) or Bavistin (1 g per litre).",
     G, 17, ["To prevent the disease, spray Indofil -M-45 solutions (5 g/1 litre of water) or Bavistin (1g/litre)"],
     "ನರ್ಸರಿ ಸಸಿಗಳನ್ನು ಸೆರ್ಕೋಸ್ಪೊರಾ (ಕಂದು ಕಣ್ಣಿನ ಚುಕ್ಕೆ) ರೋಗದಿಂದ ಹೇಗೆ ರಕ್ಷಿಸುವುದು?"),
    ("c02", "cercospora", "Which coffee plants are more likely to get Cercospora leaf spot?",
     "Newly established plantings, plants deficient in nutrients (especially nitrogen and potassium) and plants over-exposed to sunlight.",
     CER, 2, ["It affects both leaves and fruits, which is seems more problematic in the newly established coffee orchard and is more susceptible to field with plant nutrition deficiency, particularly nitrogen and potassium and over-exposure to sunlight"],
     "ಯಾವ ಕಾಫಿ ಗಿಡಗಳಿಗೆ ಸೆರ್ಕೋಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ ಬರುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು?"),
    ("c03", "cercospora", "What do Cercospora leaf spot symptoms look like on coffee leaves?",
     "Lesions start as yellow (chlorotic) patches on the upper leaf surface and become deep brown and necrotic.",
     CER, 2, ["On the top leaf surface, lesions begin as chlorotic (yellow) patches that develop to become deep brown and necrotic"], None),
    ("c04", "cercospora", "How does Cercospora show on the green coffee berries and when?",
     "About 90 days after flowering, as irregular brown sunken lesions surrounded by a purple halo.",
     CER, 2, ["On green berries, this includes irregularly shaped brown, sunken lesions that are surrounded by a purple halo."], None),
    ("c05", "cercospora", "Which eco-friendly treatment worked best against Cercospora leaf spot?",
     "Bordeaux mixture was the most effective eco-friendly treatment, due to the toxicity of copper to the pathogen.",
     CER, 9, ["The result indicate that Bordeaux mixture is found to be must effective ecofriendly management treatments over other treatments which might be due to the toxicity of the copper to the pathogens"],
     "ಸೆರ್ಕೋಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗಕ್ಕೆ ಯಾವ ಪರಿಸರ ಸ್ನೇಹಿ ಚಿಕಿತ್ಸೆ ಹೆಚ್ಚು ಪರಿಣಾಮಕಾರಿ?"),
    # ------------------------------------------------------------------ leaf miner
    ("m01", "miner", "How does the coffee leaf miner damage the leaves?",
     "Its larvae feed inside the leaf mesophyll, causing necrosis, loss of photosynthetic capacity, defoliation and yield loss.",
     LM, 1, ["During the immature life stages, the insect feeds in the mesophyll triggering necrosis and causing loss of photosynthetic capacity, defoliation and signiﬁcant yield loss to coffee crops."],
     "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಕೀಟ ಎಲೆಗಳಿಗೆ ಹೇಗೆ ಹಾನಿ ಮಾಡುತ್ತದೆ?"),
    ("m02", "miner", "How much crop loss can the coffee leaf miner cause?",
     "Losses of about 30-70% in grain production, with lower quality.",
     LM, 1, ["Responsible for losses ranging from 30–70%, the CLM impairs the grain production and quality, which negatively reﬂects on the coffee production chain."], None),
    ("m03", "miner", "What does the leaf miner larva look like?",
     "Newly hatched larvae are translucent whitish and turn greenish yellow as they develop.",
     LM, 4, ["Newly hatched larvae have a translucent whitish color, but throughout their development they take on a greenish yellow tone."],
     "ಎಲೆ ಸುರಂಗ ಕೀಟದ ಮರಿಹುಳು ಹೇಗೆ ಕಾಣುತ್ತದೆ?"),
    ("m04", "miner", "Can neem extract control the coffee leaf miner?",
     "Yes, in laboratory tests pupae treated with neem (Azadirachta indica) extract showed 100% mortality, the highest of the plant extracts tested.",
     LM, 13, ["Moreover, pupae treated with A. indica extract showed the highest level of mortality (100%) followed by T. pallida 75% and C."], None),
    ("m05", "miner", "What are the problems with controlling leaf miner only with chemical pesticides?",
     "Harm to human health and the environment and the selection of resistant insect populations, which is why integrated pest management is needed.",
     LM, 1, ["Drawback aspects caused by chemical control with pesticides, such as the harmful effects to human health and environment and the selection of resistant-insect populations, prompt scientists to improve integrated pest management (IPM) tools."], None),
    ("m06", "miner", "What sustainable options are there to control the coffee leaf miner?",
     "Resistant cultivars, biological control, nano-biopesticides and other integrated approaches.",
     LM, 1, ["Therefore, the development of new resistant cultivars, biological control, nano-biopesticide products and other approaches are important strategies to a sustainable CLM control design."],
     "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಕೀಟ ನಿಯಂತ್ರಣಕ್ಕೆ ಯಾವ ಸುಸ್ಥಿರ ವಿಧಾನಗಳಿವೆ?"),
    ("m07", "miner", "Should I think about natural enemies before spraying against leaf miner?",
     "Yes, control strategies must consider parasitoids, predators and insect pathogens that naturally kill the leaf miner.",
     LM, 14, ["Biorational pesticides strategies to control L. coffeella must consider the important role of parasitoids, predators, and insect pathogens on enhancing the natural mortality of the CLM in ﬁeld."], None),
    ("m08", "miner", "How much defoliation can a heavy leaf miner attack cause?",
     "Defoliation can reach up to 75%, and productivity losses up to 87% depending on the season.",
     LM, 2, ["Estimated losses in neotropical producing countries can reach up to 87% of the coffee productivity, depending on the season, the defoliation can reach up to 75%"], None),
    # ------------------------------------------------------------------ other pests and diseases
    ("p01", "pests", "When do coffee white stem borer beetles come out?",
     "Adults emerge in large numbers in April-May and October-December.",
     G, 15, ["Coffee White Stem Borer (WSB) beetles attain their adulthood during April – May and October-December period and emerge out in large numbers."],
     "ಕಾಫಿ ಬಿಳಿ ಕಾಂಡ ಕೊರಕ ದುಂಬಿಗಳು ಯಾವಾಗ ಹೊರಬರುತ್ತವೆ?"),
    ("p02", "pests", "What should I do with coffee plants infested by white stem borer?",
     "Trace them, uproot them and destroy them immediately by burning or by keeping them under water for a week.",
     G, 15, ["As a first step, plants infested with borer should be traced, uprooted and immediately destroyed by burning or be immersed under water for a week."],
     "ಬಿಳಿ ಕಾಂಡ ಕೊರಕ ತಗುಲಿದ ಕಾಫಿ ಗಿಡಗಳನ್ನು ಏನು ಮಾಡಬೇಕು?"),
    ("p03", "pests", "How many pheromone traps per hectare are recommended for white stem borer?",
     "25 traps per hectare in highly infested areas.",
     G, 16, ["WSB pheromone traps (25 traps per hectare) have to be installed in highly infested areas."], None),
    ("p04", "pests", "What should I apply on coffee stems after smoothening them against white stem borer?",
     "A 10% lime wash: 10 kg spray lime and 100 ml Fevicol DDL in 100 litres of water.",
     G, 16, ["The smoothened stems are then given 10% lime wash (10 kg spray lime + 100ml Fevicol DDL in 100 litres of water)."], None),
    ("p05", "pests", "Which shade tree makes black rot and white stem borer more common?",
     "Silver oak: black rot and white stem borer are more prevalent in estates shaded by silver oak.",
     G, 56, ["The black rot disease and white stem borer incidence are more prevalent in estates with silver oak as shade tree."],
     "ಯಾವ ನೆರಳಿನ ಮರದಿಂದ ಕಪ್ಪು ಕೊಳೆ ರೋಗ ಮತ್ತು ಬಿಳಿ ಕಾಂಡ ಕೊರಕ ಹೆಚ್ಚಾಗುತ್ತದೆ?"),
    ("p06", "pests", "How do I prevent coffee berry borer at harvest time?",
     "Install Broca traps in the estate and near drying yards, use picking mats, and pick all leftover berries and gleanings.",
     G, 10, ["Broca traps have to be installed in the estate as well as near the drying yards"], None),
    ("p07", "pests", "What should I do with berries partly damaged by coffee berry borer?",
     "Dip them in boiling water for one minute and then dry them; burn highly damaged berries.",
     G, 10, ["If the berries are partially damaged by Coffee Berry Borer, such berries can be immersed in boiling water for 1 minute and then dried."], None),
    ("p08", "pests", "Is there a biological control for coffee berry borer?",
     "Yes, spray Beauveria bassiana with a backpack sprayer.",
     G, 28, ["Coffee Berry Borer has to be controlled using Beauveria bassiana spray using bakpak sprayer."],
     "ಕಾಫಿ ಹಣ್ಣು ಕೊರಕ ಕೀಟಕ್ಕೆ ಜೈವಿಕ ನಿಯಂತ್ರಣ ವಿಧಾನವಿದೆಯೇ?"),
    ("p09", "pests", "How do I control green mealybug on coffee?",
     "Control the ants that spread it by dusting 5% Malathion around the base of affected plants and shade trees, destroy ant nests, and spray infested plants.",
     G, 23, ["Therefore, control ants by dusting 5% Malathion powder around the base of affected coffee plants and shade trees."], None),
    ("p10", "pests", "How should black rot affected patches be sprayed?",
     "Spray 1.0% Bordeaux mixture in the first week of June.",
     G, 22, ["Black rot affected patches should be sprayed with 1.0 % Bordeaux mixture during the first week of June."], None),
    ("p11", "pests", "Why do black rot and stalk rot increase during the monsoon?",
     "Retaining thick shade during the monsoon increases black rot and stalk rot and causes berry drop because the soil becomes chilly.",
     G, 65, ["Retaining higher levels (thick) shade during the monsoon results in the incidence of black rot and stalk rot diseases in coffee plants and berry drop due to chillness in the soil."], None),
    ("p12", "pests", "My nursery seedlings show water-soaked brown stems and leaves are falling (Myrothecium). What should I spray?",
     "Spray 0.8 ml of Tilt (propiconazole) per litre of water, once a month until the end of the monsoon.",
     G, 17, ["To prevent and cure this disease, spray 0.8ml of Tilt (propiconazole) in one litre of water."], None),
    # ------------------------------------------------------------------ cultivation practice
    ("k01", "cultivation", "What soil pH should be maintained in coffee soils?",
     "Around 6.1 for the best fertilizer use efficiency.",
     G, 11, ["In order to have better fertilize use efficiency of the applied fertilizers, the soil pH should be maintained at around 6.1 in coffee soils."],
     "ಕಾಫಿ ಮಣ್ಣಿನ ಪಿಎಚ್ ಎಷ್ಟು ಇರಬೇಕು?"),
    ("k02", "cultivation", "How often should I test the soil in my coffee estate?",
     "Once every 2-3 years.",
     G, 11, ["Therefore, to monitor the soil pH, soils have to be tested compulsorily once in 2-3 years."], None),
    ("k03", "cultivation", "When is the best time to apply lime to coffee soils?",
     "November to February, with enough moisture in the soil; never during the monsoon.",
     G, 12, ["However, keeping in mind the coffee zones, it is known that November to February months are the ideal period for lime application."],
     "ಕಾಫಿ ಮಣ್ಣಿಗೆ ಸುಣ್ಣ ಹಾಕಲು ಉತ್ತಮ ಸಮಯ ಯಾವುದು?"),
    ("k04", "cultivation", "The soil test says I need more than 3.5 tonnes of lime per hectare. Can I apply it all at once?",
     "No, split it into two equal parts applied in two years.",
     G, 12, ["If the recommended dose of liming material is more than 3.5 metric tonnes per hectare, in such case the dose has to be split into two equal parts and applied in 2 years."], None),
    ("k05", "cultivation", "How should I collect a soil sample from my coffee block?",
     "From each 2-hectare block, pick 20 random spots, remove surface litter, dig 9 inches wide and 9 inches deep, scrape soil from top to bottom and mix into a 1 kg composite sample.",
     G, 12, ["Select at random 20 spots in each block, remove surface litter and dig a hole of 9 inches diameter using a suitable tool up to 9 inches depth."], None),
    ("k06", "cultivation", "When should I prune coffee after the harvest?",
     "Only after one or two summer showers (at least 2 inches of rain), unless the soil is still moist or the estate is above 3500 feet.",
     G, 17, ["But pruning operation should not be started until one or two summer showers (minimum of 2 inches of rain) are received."],
     "ಕೊಯ್ಲಿನ ನಂತರ ಕಾಫಿ ಗಿಡಗಳನ್ನು ಯಾವಾಗ ಸವರಬೇಕು?"),
    ("k07", "cultivation", "What is the basic sustenance dose of fertilizer for grown-up coffee plants?",
     "50:50:50 kg of nitrogen, phosphorus and potash per hectare.",
     G, 21, ["In every coffee estate, the grown up plants need 50:50:50 kgs of nitrogen, phosphorus and potash per hectare for their vegetative growth."],
     "ಬೆಳೆದ ಕಾಫಿ ಗಿಡಗಳಿಗೆ ಮೂಲಭೂತ ಗೊಬ್ಬರದ ಪ್ರಮಾಣ ಎಷ್ಟು?"),
    ("k08", "cultivation", "What is the maximum fertilizer I should give in one split dose?",
     "Not more than 100:75:100 kg of N:P:K per hectare in a single split.",
     G, 21, ["One should note that a single split dose of fertilizer should not exceed 100:75:100 kgs of N: P: K per hectare."], None),
    ("k09", "cultivation", "When should I lop and regulate the shade trees?",
     "Usually in May, but only after 4-5 inches of rainfall; not in dry weather.",
     G, 22, ["Therefore, shade regulation shall be done preferably only after receiving 4-5 inches of rainfall."],
     "ನೆರಳಿನ ಮರಗಳ ಕೊಂಬೆ ಕಡಿತ (ಲಾಪಿಂಗ್) ಯಾವಾಗ ಮಾಡಬೇಕು?"),
    ("k10", "cultivation", "What spacing should I use when planting Arabica coffee?",
     "Arabica talls 7x7, 7x6 or 6x6 feet; Arabica dwarf or semi-dwarf 5x5 feet.",
     G, 19, ["(a) Arabica Talls - 7 X 7, 7 X 6 or 6 X 6 feet (b) Arabica Dwarf/Semi Dwarf – 5 X 5 feet"], None),
    ("k11", "cultivation", "What size of pit should I dig for planting coffee and what should I put in it?",
     "1.5 x 1.5 x 1.5 feet pits, weathered for 15-20 days, filled with 1-1.5 kg compost or farmyard manure and 50-100 g rock phosphate mixed with top soil.",
     G, 20, ["The pits measuring 1.5 X 1.5 X 1.5 feet length, breadth and depth are ideal for planting."], None),
    ("k12", "cultivation", "How should I water young coffee plants after the monsoon ends?",
     "Give 5-10 litres of water per plant once a week.",
     G, 11, ["After the cessation of monsoon, it is recommended that young coffee plants should be irrigated with 5 to 10 litres water per plant once in a week."],
     "ಮುಂಗಾರು ಮುಗಿದ ನಂತರ ಎಳೆಯ ಕಾಫಿ ಗಿಡಗಳಿಗೆ ಹೇಗೆ ನೀರು ಹಾಕಬೇಕು?"),
    ("k13", "cultivation", "How much nitrogen should I apply during the break in the monsoon?",
     "58 kg nitrogen per hectare (2.5 bags of urea), which also reduces berry drop.",
     G, 27, ["Therefore, apply 58 kgs of nitrogen (2.5 bags of Urea) per hectare during the break in the monsoon."], None),
    ("k14", "cultivation", "Which slope directions (aspects) are suitable for a new coffee plantation?",
     "North, east and north-east aspects; western aspects need thick shade because of the scorching sun.",
     G, 19, ["North, East and North-East aspects are suitable for growing coffee."], None),
    ("k15", "cultivation", "What soil mixture should I fill in coffee nursery bags?",
     "6 parts sieved jungle soil, 2 parts well-rotted cattle manure or compost and 1 part coarse river sand (never sea sand).",
     G, 17, ["A nursery mixture of 6 parts of sieved jungle soil( free from nematodes and other pests), two parts of well rotted cattle manure or compost and one part of coarse river sand (do not use sea sand as it contains sodium which is harmful to the seedlings) should be prepared and mixed well to fill the nursery bags."],
     "ಕಾಫಿ ನರ್ಸರಿ ಚೀಲಗಳಿಗೆ ಯಾವ ಮಣ್ಣಿನ ಮಿಶ್ರಣವನ್ನು ತುಂಬಬೇಕು?"),
    ("k16", "cultivation", "How many leaves should I send for leaf nutrient analysis?",
     "At least 25 pairs of leaves (the fourth pair from the tip) per hectare, collected before 10 a.m.",
     G, 14, ["A minimum of 25 pairs of leaves from one hectare land is necessary for precise analysis."], None),
    ("k17", "cultivation", "To what moisture level should parchment coffee be dried?",
     "To 11.0% moisture.",
     G, 7, ["The superficial water content should be removed by spreading the parchment over wire mesh trays and then dried on clean cement or clay lined drying yards till the moisture content reaches a value of 11.0%."], None),
    ("k18", "cultivation", "When are Robusta flower buds ready for blossom irrigation?",
     "Generally between 15 February and 15 March.",
     G, 49, ["Generally between February 15th and March 15th flower buds will mature and will be ready for blooming in Robusta coffee."], None),
]

DISEASE = {"rust": "Rust", "cercospora": "Cerscospora", "miner": "Miner", "pests": "Healthy", "cultivation": "Healthy"}


def build() -> list[dict]:
    pages = {(p["source"], p["page"]): p["text"] for p in R.page_texts()}
    rows, bad = [], []
    for qid, topic, q, a, src, page, ev, kn in Q:
        text = pages.get((src, page))
        if text is None:
            bad.append(f"{qid}: page not found {src} p{page}")
            continue
        for e in ev:
            score = R.quote_in_text(e, text)
            if score < 0.95:
                bad.append(f"{qid}: quote only {score:.2f} found on {src} p{page}: {e[:70]}")
        base = {"topic": topic, "disease": DISEASE[topic], "question_en": q, "gold_answer": a, "evidence": ev,
                "source": src, "page": page, "out_of_kb": 0, "origin": "curated"}
        rows.append({"id": qid, "lang": "en", "question": q, **base})
        if kn:
            rows.append({"id": qid + "_kn", "lang": "kn", "question": kn, "pair": qid, **base})
    if bad:
        raise SystemExit("Evidence check failed:\n" + "\n".join(bad))
    return rows


if __name__ == "__main__":
    rows = build()
    out = config.RAG_DIR / "questions_curated.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    en = sum(r["lang"] == "en" for r in rows)
    print(f"wrote {out.name}: {en} English + {len(rows) - en} Kannada questions; every evidence quote verified")
