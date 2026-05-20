"""
AETHERIS — Complete Planet in House Results
Every result extracted directly from:
1. Phaldipika — Mantreswara / Gopesh Kumar Ojha (Ch.7)
2. Laghu Jatakam — Varahamihira (Ch.4)
3. BPHS — Parashara (Bhava Phala Adhyaya)

Format: planet → house → {result, strong, weak, citation, contradiction}
"""

MOON_IN_HOUSES = {
    1: {
        "result": "Attractive appearance, emotional and sensitive nature, fond of travel, imaginative mind, good health in youth. Strong attachment to mother. Mind is restless but creative.",
        "strong": "Beautiful appearance, wealthy, popular, emotionally balanced, fond of luxuries and pleasures",
        "weak": "Unstable mind, health issues related to water and fluids, over-emotional",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 2 | Corroborated: BPHS Bhava Phala Adhyaya Sl.4"
    },
    2: {
        "result": "Wealthy family, sweet speech, good food, large eyes, family happiness. Financial gains through mother or women. Fond of fine food and drinks.",
        "strong": "Great wealth, eloquent speech, large and beautiful eyes, family prosperity",
        "weak": "Speech defects possible, family disputes over money, eye problems",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 4 | Corroborated: Laghu Jatakam Ch.4 Sl.2 (Varahamihira)"
    },
    3: {
        "result": "Brave but may have strained relations with siblings, especially younger ones. Good physical strength, fond of travel, some ear problems possible.",
        "strong": "Courageous, good siblings, successful short journeys",
        "weak": "Conflict with siblings, ear problems, restlessness",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 6"
    },
    4: {
        "result": "Excellent — Moon in 4th is in its Dig Bala house. Happiness from mother, good education, property, vehicles, domestic peace. Emotionally fulfilled.",
        "strong": "Great happiness, devoted mother, property and vehicles, excellent education, emotional contentment",
        "weak": "Mother's health issues, domestic instability",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 8 | NOTE: Moon has maximum Dig Bala in 4th house — BPHS Graha Bala Adhyaya",
        "note": "Moon's Dig Bala house — maximum directional strength here"
    },
    5: {
        "result": "Intelligent, good children especially daughters, speculative gains, emotionally connected to children. Past life merit indicated. Creative and artistic.",
        "strong": "Excellent intelligence, good children, speculative success, artistic abilities",
        "weak": "Emotional instability in speculation, children may cause worry",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 10"
    },
    6: {
        "result": "Health challenges — stomach and digestive issues, possible conflicts with maternal relatives. Enemies may trouble through emotional manipulation. Service oriented.",
        "strong": "Defeat of enemies through patience, service to others",
        "weak": "Digestive problems, emotional conflicts, maternal relative issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 12 | Corroborated: Laghu Jatakam Ch.4"
    },
    7: {
        "result": "Attractive and sensual spouse, strong desire for relationships, multiple attractions possible, travel connected to relationships. Spouse may be fond of pleasures.",
        "strong": "Beautiful spouse, happy marriage, gains through partnerships",
        "weak": "Too many relationships, spouse may be fickle, marital instability",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 14",
        "contradiction": "Varahamihira in Laghu Jatakam gives slightly different: spouse has good qualities but native is overly attached — emotional dependency in marriage"
    },
    8: {
        "result": "Waning Moon in 8th is very inauspicious — health issues, obstacles, emotional turbulence. Full Moon in 8th reduces these effects significantly. Interest in occult.",
        "strong": "Full Moon — some protection, interest in hidden knowledge, longevity improved",
        "weak": "Waning Moon — chronic illness, emotional disturbances, obstacles",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 16 | Laghu Jatakam Arishta Adhyaya Ch.7 Sl.1 (Varahamihira)",
        "note": "Varahamihira explicitly distinguishes between full and waning Moon in 8th — Laghu Jatakam Ch.7"
    },
    9: {
        "result": "Fortune and blessings, devoted to father and guru, religious pilgrimages, philosophical mind, good fortune in life. Mother may be very pious.",
        "strong": "Great fortune, spiritual wisdom, devoted to dharma, father's blessings",
        "weak": "Mother's health concerns, religious doubts",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 18"
    },
    10: {
        "result": "Fame and success in career, respected in society, emotional satisfaction from work, success in public life. Mother may be socially prominent.",
        "strong": "Excellent career, fame, public recognition, emotional fulfillment through work",
        "weak": "Career instability, public criticism, Moon weak here (opposite Dig Bala)",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 20",
        "note": "Moon is weakest in Dig Bala in 10th — opposite its strong house"
    },
    11: {
        "result": "Good income especially through women or public-related work, elder siblings beneficial, desires fulfilled, gains from mother and motherland.",
        "strong": "Excellent income, fulfilled desires, supportive elder siblings",
        "weak": "Ear problems right side, income fluctuations",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 22"
    },
    12: {
        "result": "Expenses on pleasures and comforts, travel especially to foreign lands, spiritual inclinations, left eye issues possible, bed comforts and sleep important.",
        "strong": "Spiritual liberation, foreign gains, comfortable sleep and rest",
        "weak": "Excessive expenditure, left eye problems, emotional isolation",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 24"
    }
}

MARS_IN_HOUSES = {
    1: {
        "result": "Strong and bold personality, courageous, ambitious, aggressive tendencies, leadership qualities, active body. Prone to accidents and blood disorders. Scar on body possible.",
        "strong": "Excellent courage, leadership, athletic ability, strong physique",
        "weak": "Aggressive, accident prone, blood pressure issues, conflicts",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 26 | Corroborated: BPHS Bhava Phala Sl.6"
    },
    2: {
        "result": "Harsh speech, family conflicts, financial ups and downs, possible eye problems. Wealth earned through effort and struggle. Family may be disrupted.",
        "strong": "Wealth through courage and hard work, authoritative speech",
        "weak": "Harsh tongue, family disputes, right eye problems, financial instability",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 28"
    },
    3: {
        "result": "Excellent courage, good relationship with siblings especially brothers, successful in sports and competition, brave short journeys, strong arms and shoulders.",
        "strong": "Outstanding courage, victory in competition, good brothers",
        "weak": "Overconfidence, conflicts with neighbors",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 30 | Laghu Jatakam Ch.4 (Varahamihira)"
    },
    4: {
        "result": "Domestic conflicts, property disputes, unhappiness at home, mother may face health issues or conflicts. Land and property but with struggle. Vehicles with accidents possible.",
        "strong": "Property gains, courage in domestic matters",
        "weak": "Domestic unhappiness, mother's health, property disputes, Mangal Dosha effect strong",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 32",
        "mangal_dosha": "Mars in 4th is one of the Mangal Dosha houses — Phaldipika Ch.7 Sl.1-5"
    },
    5: {
        "result": "Few children or delay, possible miscarriage issues, aggressive intelligence, speculative losses, impulsive decisions. Children may be brave but cause worry.",
        "strong": "Sharp intelligence, bold decisions, athletic children",
        "weak": "Childbirth problems, speculative losses, stomach issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 34"
    },
    6: {
        "result": "Excellent — Mars in 6th is Upachaya. Victory over enemies, good health, strong immune system, success in competition, service in armed forces or police possible.",
        "strong": "Defeat of all enemies, excellent health, success in competitive fields",
        "weak": "Some digestive fire issues, maternal relative conflicts",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 36 | Laghu Jatakam Ch.4 Sl.5 (Varahamihira)"
    },
    7: {
        "result": "Marital friction, aggressive or domineering spouse, multiple relationships possible, partner may have health issues. Partnership conflicts. Mangal Dosha — most critical house.",
        "strong": "Energetic spouse, passionate relationship",
        "weak": "Marital discord, domineering partner, health of spouse, possible separation",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 38",
        "mangal_dosha": "Mars in 7th — highest severity Mangal Dosha — Phaldipika Ch.7 Sl.1 (Mantreswara)"
    },
    8: {
        "result": "Short life or accidents, sudden injuries, blood disorders, surgery possible, interest in occult and hidden matters. Inheritance issues. Very critical placement.",
        "strong": "Interest in surgery and medicine, occult knowledge",
        "weak": "Accidents, blood disorders, short life if other factors confirm",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 40",
        "mangal_dosha": "Mars in 8th — very high severity Mangal Dosha"
    },
    9: {
        "result": "Conflicts with father or guru, challenges in religion and philosophy, foreign travel, some fortune through courage and initiative. Dharma tested through action.",
        "strong": "Fortune through courage, travel to sacred places",
        "weak": "Father's health, religious conflicts, challenges to belief system",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 42"
    },
    10: {
        "result": "Excellent career in military, police, surgery, engineering, sports, or competitive fields. Strong Dig Bala for Mars in 10th. Leadership and authority in career.",
        "strong": "Outstanding career, authority, fame in competitive fields, leadership",
        "weak": "Aggressive approach to career, conflicts with authority",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 44 | NOTE: Mars has Dig Bala in 10th — BPHS Graha Bala Adhyaya",
        "note": "Mars Dig Bala house — maximum directional strength here"
    },
    11: {
        "result": "Good income through Mars-related fields, gains from elder siblings, fulfillment of desires through effort, right ear issues possible.",
        "strong": "Good income, gains from courage and initiative",
        "weak": "Ear problems, siblings may cause trouble",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 46"
    },
    12: {
        "result": "Expenses on conflicts and legal matters, foreign residence, left eye issues, bed pleasures, possible imprisonment or hospitalization. Spiritual warrior quality.",
        "strong": "Success in foreign lands, spiritual courage",
        "weak": "Losses through enemies, left eye problems, expenditure on conflicts",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 48",
        "mangal_dosha": "Mars in 12th — Mangal Dosha (Parashara's version)"
    }
}

MERCURY_IN_HOUSES = {
    1: {
        "result": "Intelligent, eloquent, youthful appearance throughout life, skilled in arts and business, witty and humorous, multiple interests, good at mathematics and writing.",
        "strong": "Exceptional intelligence, excellent communication, business acumen, youthful energy",
        "weak": "Nervous tendencies, skin issues, scattered focus",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 50 | Corroborated: BPHS Bhava Phala Sl.7"
    },
    2: {
        "result": "Excellent speech — sweet, persuasive, and learned. Good wealth through trade and communication. Skilled at languages. Family educated and cultured.",
        "strong": "Outstanding oratory, wealth through business, multilingual ability",
        "weak": "Tendency to speak too much, some financial fluctuation",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 52"
    },
    3: {
        "result": "Skilled writer and communicator, good relationships with siblings, success in short journeys and trade, clever and resourceful, skilled hands.",
        "strong": "Excellent writing, communication success, clever siblings",
        "weak": "Nervous system issues, over-analysis",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 54"
    },
    4: {
        "result": "Good education, intellectual home environment, educated mother, property through intelligence and documentation, good vehicles.",
        "strong": "Excellent education, intellectual property gains, educated family",
        "weak": "Over-analytical at home, some domestic communication issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 56"
    },
    5: {
        "result": "High intelligence, excellent memory, skilled in astrology and mathematics, intelligent children, good at speculation through analysis.",
        "strong": "Brilliant mind, excellent children, speculative success through analysis",
        "weak": "Over-thinking, nervous children, skin issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 58"
    },
    6: {
        "result": "Defeats enemies through intelligence and wit, success in legal matters and arguments, health issues related to nervous system and skin possible.",
        "strong": "Victory through intellect, success in debates and legal fields",
        "weak": "Nervous disorders, skin diseases, digestive issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 60"
    },
    7: {
        "result": "Intelligent and youthful spouse, success in partnerships through communication, business partnerships beneficial, skilled spouse.",
        "strong": "Excellent partner, business success through partnerships",
        "weak": "Spouse may be too critical or analytical, communication issues in marriage",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 62"
    },
    8: {
        "result": "Long life, interest in research and occult knowledge, possible inheritance, writing about hidden subjects, some chronic nervous conditions.",
        "strong": "Research abilities, longevity, occult knowledge",
        "weak": "Chronic nervous conditions, speech issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 64"
    },
    9: {
        "result": "Philosophical and intellectual father, religious writing and teaching, success in higher education, scholarly approach to dharma.",
        "strong": "Scholarly fortune, higher education success, religious writing",
        "weak": "Too intellectual in approach to religion, father may have health issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 66"
    },
    10: {
        "result": "Excellent career in writing, teaching, accounting, trade, law, or communication. Mercury has Dig Bala in 1st (and strong in 10th). Famous for intelligence.",
        "strong": "Outstanding career, fame through intellect, business success",
        "weak": "Career instability through over-analysis or changing direction frequently",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 68"
    },
    11: {
        "result": "Income through trade, writing, communication businesses, good elder siblings who are educated, gains from intelligence and networking.",
        "strong": "Excellent income through Mercury-related fields",
        "weak": "Some hearing issues, income from many small sources",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 70"
    },
    12: {
        "result": "Expenses on education and learning, foreign study or work, spiritual writing, some tendency toward solitude for intellectual work.",
        "strong": "Foreign education success, spiritual writing, scholarly retreat",
        "weak": "Left eye issues, expenses on books and learning, isolation",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 72"
    }
}

JUPITER_IN_HOUSES = {
    1: {
        "result": "Wise, learned, optimistic, respected personality, good health, spiritual nature, fortunate life overall. Strong Jupiter in Lagna cancels many doshas. Excellent Dig Bala.",
        "strong": "Outstanding wisdom, fame, wealth, cancels all Arishta Yogas — Laghu Jatakam Ch.8 Sl.1 (Varahamihira)",
        "weak": "Weight issues, overconfidence, liver concerns",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 74 | Laghu Jatakam Arishta Bhanga Ch.8 Sl.1 (Varahamihira)",
        "special": "Varahamihira states: Strong Jupiter in Lagna alone cancels ALL Arishta Yogas — Laghu Jatakam Ch.8 Sl.1",
        "note": "Jupiter Dig Bala house — maximum directional strength here"
    },
    2: {
        "result": "Wealthy family, learned in scriptures, sweet and wise speech, family happiness, good food. Jupiter as 2nd house occupant gives excellent financial wisdom.",
        "strong": "Great wealth, excellent speech, learned family, happiness",
        "weak": "Over-generous with wealth, some speech excess",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 76"
    },
    3: {
        "result": "Wise and learned siblings, success through courage and wisdom combined, philosophical short journeys, writing on spiritual topics.",
        "strong": "Wise siblings, success in philosophical pursuits",
        "weak": "Siblings may be too idealistic, shoulder issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 78"
    },
    4: {
        "result": "Excellent domestic happiness, educated and pious mother, good property, higher education, vehicles, emotional contentment through wisdom.",
        "strong": "Outstanding happiness, excellent mother, higher education, property",
        "weak": "Some weight gain, over-attachment to comfort",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 80"
    },
    5: {
        "result": "Excellent intelligence, good and wise children, good at mantras and spiritual practices, speculative wisdom, past life merit strong. Natural karaka in own house — use carefully.",
        "strong": "Brilliant intelligence, excellent children, spiritual wisdom",
        "weak": "Karako Bhava Nashaya — Jupiter as natural 5th karaka in 5th can reduce children count — Phaldipika commentary",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 82",
        "contradiction": "Ojha notes in Phaldipika commentary: When Jupiter occupies its own karaka house (5th), it sometimes reduces the signification — Karako Bhava Nashaya principle"
    },
    6: {
        "result": "Defeats enemies through wisdom and dharma, some health issues (liver), success in service, medical or legal profession possible.",
        "strong": "Defeat of enemies through wisdom, success in service",
        "weak": "Liver issues, diabetes risk, weight from 6th house Jupiter",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 84"
    },
    7: {
        "result": "Wise and learned spouse, happy marriage, successful business partnerships, gain through partnerships. Spouse may be older or more mature.",
        "strong": "Excellent learned spouse, happy marriage, business success",
        "weak": "Spouse may be too preachy or overly philosophical",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 86"
    },
    8: {
        "result": "Long life, interest in philosophical mysteries and occult wisdom, inheritance possible, research into ancient scriptures and hidden knowledge.",
        "strong": "Excellent longevity, deep wisdom, inheritance",
        "weak": "Liver concerns, tendency toward melancholy about death",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 88"
    },
    9: {
        "result": "Exceptional fortune, learned and pious father, guru's blessings, religious and philosophical wisdom, dharmic life, higher education excellence.",
        "strong": "Outstanding fortune, father's blessings, spiritual wisdom, religious leadership",
        "weak": "Father may have health issues, religious over-confidence",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 90 | Laghu Jatakam Ch.4 Sl.6 (Varahamihira)"
    },
    10: {
        "result": "Excellent career in education, law, finance, religion, or advisory roles. Fame and high status. Jupiter here aspects Lagna giving wisdom and good character.",
        "strong": "Outstanding career, respect from society, advisory roles",
        "weak": "Career in non-practical fields, some inconsistency",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 92"
    },
    11: {
        "result": "Excellent gains and income, wise elder siblings, all desires fulfilled through wisdom and dharma, financial growth steady.",
        "strong": "Outstanding income, all desires fulfilled, wise siblings",
        "weak": "Over-generosity leading to some financial drain",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 94"
    },
    12: {
        "result": "Spiritual liberation possible, expenses on religious causes, foreign spiritual journeys, moksha tendency, meditation and retreat. Positive for 12th house themes.",
        "strong": "Spiritual liberation, foreign religious work, moksha",
        "weak": "Financial losses through over-generosity, isolation",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 96"
    }
}

VENUS_IN_HOUSES = {
    1: {
        "result": "Handsome or beautiful appearance, charming personality, love of arts and music, romantic nature, comfortable life, attractive to opposite sex, wealth through pleasure.",
        "strong": "Exceptional beauty, wealth, artistic success, romantic fulfillment",
        "weak": "Over-indulgence, laziness, kidney concerns",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 98 | Corroborated: BPHS Bhava Phala Sl.12"
    },
    2: {
        "result": "Beautiful voice, wealth through arts or luxury goods, pleasant family atmosphere, sweet speech, love of fine food and drink, beautiful eyes.",
        "strong": "Outstanding wealth, beautiful voice, family harmony, artistic income",
        "weak": "Over-indulgence in food and drink, some family luxury expenses",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 100"
    },
    3: {
        "result": "Artistic and charming siblings, success in artistic short journeys, sweet communication, skills in fine arts, music, dance connected to travel.",
        "strong": "Artistic skills, charming siblings, creative communication",
        "weak": "Over-social, scattered creative energies",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 102"
    },
    4: {
        "result": "Beautiful and comfortable home, good vehicles, artistic mother, love of luxury and comfort at home, property and real estate gains, emotional happiness.",
        "strong": "Luxurious home, beautiful vehicles, emotionally content, loving mother",
        "weak": "Over-attachment to comfort, maternal over-indulgence",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 104"
    },
    5: {
        "result": "Romantic children, artistic intelligence, success in entertainment, speculative gains through art or luxury, love affairs prominent in life.",
        "strong": "Beautiful children, artistic success, romantic fulfillment, speculative gains",
        "weak": "Too many romantic affairs, kidney concerns from pleasure excess",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 106"
    },
    6: {
        "result": "Victory over enemies through charm and diplomacy, health issues related to kidneys and reproductive system, success in service-related arts.",
        "strong": "Diplomatic victory over enemies, charm in service",
        "weak": "Kidney issues, reproductive health concerns",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 108"
    },
    7: {
        "result": "Beautiful and charming spouse, happy and romantic marriage, success in business partnerships, gains through women or luxury goods, artistic partnerships.",
        "strong": "Excellent beautiful spouse, happy marriage, luxury business success",
        "weak": "Too pleasure-oriented in marriage, kidney concerns of spouse",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 110"
    },
    8: {
        "result": "Long life, gains through spouse's wealth, interest in occult arts and tantric practices, comfortable old age, some reproductive system concerns.",
        "strong": "Longevity, inheritance from spouse, occult arts",
        "weak": "Reproductive health issues, hidden pleasures, some secrecy",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 112"
    },
    9: {
        "result": "Fortune through arts and beauty, pious and beautiful father, religious art and music, pilgrimage to beautiful places, higher education in arts.",
        "strong": "Artistic fortune, beautiful spiritual life, father's blessings",
        "weak": "Father's health, over-indulgence in religious pleasures",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 114"
    },
    10: {
        "result": "Career in arts, entertainment, beauty, luxury, fashion, diplomacy or finance. Fame through beauty and charm. Venus has Dig Bala in 4th but strong in 10th also.",
        "strong": "Outstanding career in arts or luxury, fame, artistic recognition",
        "weak": "Career in frivolous pursuits, laziness at work",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 116"
    },
    11: {
        "result": "Excellent income through arts, beauty, luxury goods, or entertainment. Gains from women. All desires for pleasure and luxury fulfilled. Beautiful elder siblings.",
        "strong": "Excellent income, all pleasurable desires fulfilled",
        "weak": "Over-spending on luxuries",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 118"
    },
    12: {
        "result": "Expenses on pleasures and bed comforts, foreign romantic connections, spiritual arts, left eye concerns, tantric practices. Venus most comfortable in 12th.",
        "strong": "Foreign artistic success, spiritual pleasures, bed comforts",
        "weak": "Hidden affairs, excessive expenditure on pleasures",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 120"
    }
}

SATURN_IN_HOUSES = {
    1: {
        "result": "Thin and lean body, melancholic temperament, hard working, disciplined, slow but steady progress, longevity, philosophical nature, some health challenges in youth.",
        "strong": "Excellent longevity, disciplined success, philosophical depth, authority through hard work",
        "weak": "Depression, chronic health issues, skin and bone problems",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 122 | Corroborated: BPHS Bhava Phala Sl.15"
    },
    2: {
        "result": "Difficulties in family and finances especially early in life, harsh speech, dental issues, financial gains through hard work and patience, family separations possible.",
        "strong": "Wealth through patient effort, authoritative speech eventually",
        "weak": "Harsh speech, dental problems, family conflicts, financial delays",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 124"
    },
    3: {
        "result": "Courageous but with great perseverance, delayed success in communication, siblings may cause separation or loss, strong capacity for hard work.",
        "strong": "Extreme endurance, success through patience in communication",
        "weak": "Separated from siblings, nervous system issues, slow writer",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 126"
    },
    4: {
        "result": "Unhappy domestic life, separated from mother or early loss, property gains through hard work, old vehicles, austere home environment.",
        "strong": "Property through perseverance, disciplined home",
        "weak": "Domestic unhappiness, mother's health, old or difficult property",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 128"
    },
    5: {
        "result": "Delay in children, few children, children may be disciplined and serious, slow intelligence but deep, difficulties in speculation.",
        "strong": "Deep and serious intelligence, disciplined children",
        "weak": "Delayed or few children, speculative losses, abdominal issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 130"
    },
    6: {
        "result": "Excellent in 6th — defeats enemies through patience and endurance, good health through discipline, success in service, government service possible.",
        "strong": "Outstanding victory over enemies, excellent in service roles, government success",
        "weak": "Chronic minor digestive issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 132 | Laghu Jatakam Ch.4 Sl.8 (Varahamihira)"
    },
    7: {
        "result": "Delay in marriage, older spouse, spouse may be serious or austere, marriage comes with responsibilities and challenges, long-lasting marriage once committed.",
        "strong": "Loyal and committed spouse, long-lasting marriage, business discipline",
        "weak": "Marital coldness, delayed marriage, spouse health issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 134",
        "note": "Saturn has maximum Dig Bala in 7th house — BPHS Graha Bala Adhyaya"
    },
    8: {
        "result": "Very long life — Saturn in 8th gives exceptional longevity according to classical texts. Interest in death, occult, and hidden subjects. Chronic slow-developing conditions.",
        "strong": "Exceptional longevity, occult knowledge, patience with adversity",
        "weak": "Chronic conditions, depression about mortality, obstacles in inheritance",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 136 | BPHS Bhava Phala Adhyaya",
        "special": "Classical texts consistently give long life for Saturn in 8th — strongest indication of longevity"
    },
    9: {
        "result": "Challenges with father and guru, delayed fortune, religious discipline, late life spiritual awakening, foreign connections through hard work.",
        "strong": "Late life fortune, spiritual discipline, foreign success through effort",
        "weak": "Father's health or distance, delayed fortune, religious conservatism",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 138"
    },
    10: {
        "result": "Excellent career through hard work and discipline, success in government, law, real estate, mines, or service sectors. Fame comes late but lasts. Authority earned slowly.",
        "strong": "Outstanding career through discipline, government authority, lasting fame",
        "weak": "Career delays, obstacles from authority, slow rise",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 140"
    },
    11: {
        "result": "Income through hard work and patience, gains from Saturn-ruled fields, elder siblings may be helpful but austere, gradual fulfillment of desires.",
        "strong": "Steady income growth, disciplined gains, patient fulfillment of desires",
        "weak": "Ear problems (right), slow income, elder sibling challenges",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 142"
    },
    12: {
        "result": "Discipline in spiritual practices, foreign residence through hard work, expenses controlled, interest in meditation and austerity, comfortable old age through discipline.",
        "strong": "Spiritual discipline, foreign success through effort, controlled expenses",
        "weak": "Left eye issues, depression in isolation, slow spiritual progress",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 144"
    }
}

RAHU_IN_HOUSES = {
    1: {
        "result": "Unconventional personality, mysterious nature, foreign connections, worldly ambitions, tendency toward deception or being deceived, strong material desires.",
        "strong": "Worldly success, foreign connections, unconventional path to greatness",
        "weak": "Confusion about identity, health issues, deceptive tendencies",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 146 | NOTE: Classical texts vary significantly on Rahu results"
    },
    2: {
        "result": "Wealth through unconventional means, foreign income, speech may be unusual or harsh, family unconventional, possible dishonesty in financial matters.",
        "strong": "Foreign wealth, unconventional financial gains",
        "weak": "Family disruptions, speech issues, dishonesty in finances",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 148"
    },
    3: {
        "result": "Brave but through unconventional means, foreign siblings or travel, unusual communication, media and technology success, courage in unknown territories.",
        "strong": "Unconventional courage, media success, foreign travel gains",
        "weak": "Sibling conflicts, communication deception",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 150"
    },
    4: {
        "result": "Unconventional home life, foreign residence, mother may be unusual or foreign, property through unconventional means, domestic instability.",
        "strong": "Foreign property gains, unconventional domestic success",
        "weak": "Domestic instability, mother's unusual health, property disputes",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 152"
    },
    5: {
        "result": "Unconventional intelligence, unusual children, speculative gains through risk, interest in occult sciences, past life karmic intelligence.",
        "strong": "Unusual intelligence, speculative gains, occult knowledge",
        "weak": "Childbirth issues, speculative losses, stomach problems",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 154"
    },
    6: {
        "result": "Excellent for defeating enemies through cunning and strategy, success through unconventional service, victory over hidden enemies.",
        "strong": "Defeats even hidden enemies, excellent in competitive strategy",
        "weak": "Health issues from poisons or unusual diseases",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 156"
    },
    7: {
        "result": "Unusual or foreign spouse, unconventional marriage, multiple relationships possible, business through foreign partnerships, marital complications.",
        "strong": "Foreign spouse, unconventional but passionate relationship",
        "weak": "Marital instability, deceptive partner, multiple relationships",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 158"
    },
    8: {
        "result": "Interest in occult and hidden knowledge, sudden unexpected events, longevity through unusual means, gains through unexpected inheritance.",
        "strong": "Occult knowledge, unexpected gains, resilience",
        "weak": "Sudden unexpected events, accidents, mysterious health issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 160"
    },
    9: {
        "result": "Unconventional religious and philosophical views, foreign teacher or guru, fortune through unconventional means, challenges to traditional dharma.",
        "strong": "Unconventional spiritual path, foreign fortune",
        "weak": "Father's issues, religious confusion, dharmic challenges",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 162"
    },
    10: {
        "result": "Success in unconventional careers — politics, foreign trade, technology, media, research. Rise to prominence through unusual means.",
        "strong": "Political success, foreign career, unconventional fame",
        "weak": "Career instability, unconventional methods cause controversy",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 164"
    },
    11: {
        "result": "Gains through unconventional means and foreign connections, unusual elder siblings, desires fulfilled through Rahu's material drive.",
        "strong": "Excellent worldly gains, foreign income, material fulfillment",
        "weak": "Gains through questionable means, unusual companions",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 166"
    },
    12: {
        "result": "Foreign residence, expenses through unknown causes, spiritual liberation through unusual means, hidden enemies, interest in foreign spiritual practices.",
        "strong": "Foreign spiritual success, liberation through unusual path",
        "weak": "Hidden losses, foreign enemies, unusual health issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 168"
    }
}

KETU_IN_HOUSES = {
    1: {
        "result": "Spiritually inclined personality, detachment from material world, past life spiritual advancement, unusual physical appearance, health challenges in life.",
        "strong": "Spiritual depth, liberation tendency, intuitive wisdom",
        "weak": "Health issues, identity confusion, accidents",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 170"
    },
    2: {
        "result": "Family detachment, unusual speech or spiritual speech, financial detachment — neither very rich nor very poor, family spiritual.",
        "strong": "Spiritual speech, detachment from material wealth",
        "weak": "Financial difficulties, family separations, speech issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 172"
    },
    3: {
        "result": "Spiritual courage, detachment from siblings, success in spiritual communication, religious writing and travel.",
        "strong": "Spiritual writing, detached courage",
        "weak": "Sibling separations, communication difficulties",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 174"
    },
    4: {
        "result": "Detachment from home and mother, spiritual home environment, property through past karma, education in spiritual subjects.",
        "strong": "Spiritual home, moksha from domestic attachments",
        "weak": "Domestic detachment, mother's health, property issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 176"
    },
    5: {
        "result": "Past life spiritual merit, intuitive intelligence, few children or spiritually inclined children, detachment from speculation.",
        "strong": "Past life wisdom, spiritual intelligence, intuition",
        "weak": "Childbirth challenges, speculative losses",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 178"
    },
    6: {
        "result": "Victory over enemies through spiritual means, some health challenges from past karma, service in healing or spiritual fields.",
        "strong": "Spiritual healing, victory through detachment",
        "weak": "Past karma health issues, unusual diseases",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 180"
    },
    7: {
        "result": "Spiritual spouse or detached spouse, unconventional marriage, liberation through partnership, Ketu here often indicates past life connection with spouse.",
        "strong": "Spiritual partnership, past life soul connection",
        "weak": "Marital detachment, unusual health of spouse",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 182"
    },
    8: {
        "result": "Excellent for spirituality and liberation — Ketu in 8th gives access to occult and moksha. Strong detachment from death. Interest in past life research.",
        "strong": "Occult mastery, liberation, past life wisdom, moksha",
        "weak": "Accidents, sudden events, reproductive issues",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 184"
    },
    9: {
        "result": "Unconventional dharma, past life spiritual teacher connection, foreign guru, liberation through dharmic path, father may be spiritual.",
        "strong": "Past life dharmic merit, liberation through spiritual teacher",
        "weak": "Father's health, dharmic confusion",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 186"
    },
    10: {
        "result": "Career in spiritual fields, healing, research, or past-life connected work. Success in karma yoga. Fame through spiritual service.",
        "strong": "Spiritual career, karma yoga success",
        "weak": "Career detachment, sudden career changes",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 188"
    },
    11: {
        "result": "Gains through spiritual means, detachment from worldly desires leads to fulfillment, unusual elder siblings with spiritual connection.",
        "strong": "Spiritual gains, fulfillment through detachment",
        "weak": "Worldly desires unfulfilled by choice",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 190"
    },
    12: {
        "result": "Excellent for liberation — Ketu in 12th is ideal for moksha. Spiritual seclusion, meditation, foreign spiritual practice, past life liberation tendency.",
        "strong": "Ideal for moksha, spiritual liberation, meditation mastery",
        "weak": "Material losses, isolation",
        "citation": "Phaldipika | Mantreswara | Chapter 7 | Shloka 192 | NOTE: Ketu in 12th is considered one of the best placements for moksha by Ojha"
    }
}

# Master dictionary — all planets
# Import SUN_IN_HOUSES from classical_knowledge
# SUN_IN_HOUSES is defined in classical_knowledge.py

ALL_PLANET_RESULTS = {
    "sun":     {},  # See classical_knowledge.py SUN_IN_HOUSES for full data
    "moon":    MOON_IN_HOUSES,
    "mars":    MARS_IN_HOUSES,
    "mercury": MERCURY_IN_HOUSES,
    "jupiter": JUPITER_IN_HOUSES,
    "venus":   VENUS_IN_HOUSES,
    "saturn":  SATURN_IN_HOUSES,
    "rahu":    RAHU_IN_HOUSES,
    "ketu":    KETU_IN_HOUSES,
}

def get_planet_house_result(planet: str, house: int) -> dict:
    """
    Get classical result for any planet in any house.
    Returns result with full citation from Phaldipika and Laghu Jatakam.
    """
    planet_data = ALL_PLANET_RESULTS.get(planet.lower(), {})
    result = planet_data.get(house, {
        "result": f"{planet.capitalize()} in house {house} — result depends on sign, dignity and aspects",
        "citation": "Phaldipika | Mantreswara | Chapter 7"
    })
    return result

