"""
AETHERIS — Classical Yoga Detector
Every yoga with exact classical citations,
cancellation conditions, and contradictions between authors.
Source: BPHS Yoga Adhyaya (Parashara)
        Phaldipika Ch.6 (Mantreswara)
        Brihat Jataka Ch.12 (Varahamihira)
        Jataka Parijata (Vaidyanatha Dikshita)
        Saravali (Kalyanavarma)
"""
from typing import Dict, List, Tuple
from app.classical_knowledge import YOGA_RULES, PLANET_DIGNITY
from app.shadbala import get_dignity_state, check_combustion


SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
         "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]

HOUSE_LORDS = {
    "aries": "mars",   "taurus": "venus",  "gemini": "mercury",
    "cancer": "moon",  "leo": "sun",       "virgo": "mercury",
    "libra": "venus",  "scorpio": "mars",  "sagittarius": "jupiter",
    "capricorn": "saturn", "aquarius": "saturn", "pisces": "jupiter"
}

KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]
DUSTHANA_HOUSES = [6, 8, 12]
UPACHAYA_HOUSES = [3, 6, 10, 11]


class ClassicalYogaDetector:
    """
    Detects Yogas and Doshas with full classical citations.
    Every result includes: Book | Author | Chapter | Shloka
    """

    def __init__(self, planets: Dict, houses: Dict, lagna_sign: str):
        self.planets = planets
        self.houses = houses
        self.lagna_sign = lagna_sign
        self.yogas = []
        self.doshas = []
        self.sun_lon = planets.get("sun", {}).get("longitude", 0)

    def detect_all(self) -> Tuple[List[Dict], List[Dict]]:
        self._pancha_mahapurusha()
        self._raja_yogas()
        self._gajakesari()
        self._budha_aditya()
        self._chandra_mangala()
        self._kemdrum()
        self._viparita_raj_yogas()
        self._neecha_bhanga()
        self._dhana_yogas()
        self._mangal_dosha()
        self._kaal_sarp()
        self._pitra_dosha()
        return self.yogas, self.doshas

    # ────────────────────────────────
    # PANCHA MAHAPURUSHA YOGAS
    # ────────────────────────────────
    def _pancha_mahapurusha(self):
        """
        Five Great Human Yogas.
        Source: BPHS Yoga Adhyaya | Parashara | Shloka 36-40
                Phaldipika | Mantreswara | Chapter 6 | Shloka 8-12
        """
        yoga_map = {
            "mars":    ("Ruchaka",  ["aries", "scorpio", "capricorn"]),
            "mercury": ("Bhadra",   ["gemini", "virgo"]),
            "jupiter": ("Hamsa",    ["sagittarius", "pisces", "cancer"]),
            "venus":   ("Malavya",  ["taurus", "libra", "pisces"]),
            "saturn":  ("Shasha",   ["capricorn", "aquarius", "libra"]),
        }

        for planet, (yoga_name, required_signs) in yoga_map.items():
            pdata = self.planets.get(planet)
            if not pdata:
                continue

            sign = pdata.get("sign", "")
            house = self._get_house_of_planet(planet)

            if sign in required_signs and house in KENDRA_HOUSES:
                # Check cancellations
                combust = check_combustion(planet, pdata.get("longitude", 0),
                                           self.sun_lon, pdata.get("is_retrograde", False))
                dignity = get_dignity_state(planet, sign, pdata.get("degree", 0))

                cancellations = []
                yoga_cancelled = False

                if combust["is_combust"]:
                    cancellations.append(f"{planet.capitalize()} is combust — Yoga cancelled")
                    yoga_cancelled = True
                if dignity["state"] in ["neecha", "paramaneecha"]:
                    cancellations.append(f"{planet.capitalize()} is debilitated — Yoga cancelled")
                    yoga_cancelled = True

                rule = YOGA_RULES.get(yoga_name.lower(), {})

                if not yoga_cancelled:
                    self.yogas.append({
                        "name": f"{yoga_name} Yoga",
                        "type": "Pancha Mahapurusha",
                        "planet": planet.capitalize(),
                        "sign": sign.capitalize(),
                        "house": house,
                        "strength": "Full" if dignity["state"] in
                                    ["paramoccha","uccha","moolatrikona","swakshetra"] else "Partial",
                        "results": rule.get("results", {}).get("full", ""),
                        "conditions_met": f"{planet.capitalize()} in {sign.capitalize()} (House {house})",
                        "cancellations_checked": "None found — Yoga is active",
                        "citation": {
                            "primary": rule.get("citation", {}).get("primary", ""),
                            "secondary": rule.get("citation", {}).get("secondary", ""),
                        },
                        "dignity_detail": dignity["state_label"],
                        "combustion_status": "Clear" if not combust["is_combust"] else "Combust"
                    })
                else:
                    self.yogas.append({
                        "name": f"{yoga_name} Yoga (Cancelled)",
                        "type": "Pancha Mahapurusha — CANCELLED",
                        "status": "Present in chart but cancelled",
                        "cancellation_reasons": cancellations,
                        "citation": rule.get("citation", {}).get("primary", "")
                    })

    # ────────────────────────────────
    # GAJAKESARI YOGA
    # ────────────────────────────────
    def _gajakesari(self):
        """
        Source: BPHS Yoga Adhyaya | Parashara | Shloka 14
                Phaldipika | Mantreswara | Chapter 6 | Shloka 1
                Jataka Parijata | Vaidyanatha Dikshita | Ch.9 | Sl.4
        """
        moon = self.planets.get("moon", {})
        jup = self.planets.get("jupiter", {})
        if not moon or not jup:
            return

        moon_house = self._get_house_of_planet("moon")
        jup_house = self._get_house_of_planet("jupiter")

        # Jupiter in Kendra FROM Moon
        diff = (jup_house - moon_house) % 12
        if diff not in [0, 3, 6, 9]:
            return

        rule = YOGA_RULES["gajakesari"]
        cancellations = []
        cancelled = False

        # Check cancellations
        jup_combust = check_combustion("jupiter",
                                        jup.get("longitude", 0), self.sun_lon)
        jup_dignity = get_dignity_state("jupiter", jup.get("sign", ""),
                                         jup.get("degree", 0))

        if jup_combust["is_combust"]:
            cancellations.append("Jupiter combust — Gajakesari weakened")
            cancelled = True
        if jup_dignity["state"] in ["neecha", "paramaneecha"]:
            cancellations.append("Jupiter debilitated (Capricorn) — Gajakesari cancelled")
            cancelled = True

        # Phaldipika additional condition: Jupiter free from malefic aspect
        # (simplified — full check needs aspect calculation)

        self.yogas.append({
            "name": "Gaja Kesari Yoga",
            "type": "Raja Yoga",
            "status": "Cancelled" if cancelled else "Active",
            "jupiter_house": jup_house,
            "moon_house": moon_house,
            "houses_apart_from_moon": diff,
            "strength": "Full" if not cancelled and jup_dignity["state"] in
                        ["uccha","moolatrikona","swakshetra"] else "Partial",
            "results": rule["results"]["full"] if not cancelled else "Results reduced due to cancellation",
            "cancellations": cancellations if cancellations else ["None — Yoga fully active"],
            "citation": rule["citation"],
            "contradiction_note": rule.get("contradiction", ""),
            "jupiter_dignity": jup_dignity["state_label"]
        })

    # ────────────────────────────────
    # BUDHA-ADITYA YOGA
    # ────────────────────────────────
    def _budha_aditya(self):
        """
        Source: Phaldipika | Mantreswara | Ch.6 | Sl.2
        IMPORTANT: Mercury must NOT be combust — common mistake to include combust Mercury
        """
        sun = self.planets.get("sun", {})
        merc = self.planets.get("mercury", {})
        if not sun or not merc:
            return

        if sun.get("sign") != merc.get("sign"):
            return

        rule = YOGA_RULES["budha_aditya"]
        dist = abs(sun.get("longitude", 0) - merc.get("longitude", 0)) % 360
        if dist > 180:
            dist = 360 - dist

        combust = check_combustion("mercury", merc.get("longitude", 0),
                                    self.sun_lon, merc.get("is_retrograde", False))

        if combust["is_combust"]:
            self.yogas.append({
                "name": "Budha-Aditya Yoga (CANCELLED — Mercury Combust)",
                "type": "Intelligence Yoga — INVALID",
                "status": "Many charts wrongly claim this Yoga — Mercury is combust here",
                "distance_from_sun": round(dist, 2),
                "cancellation": f"Mercury is {round(dist,1)}° from Sun — within combustion orb of {combust['combust_orb']}°",
                "important_note": rule.get("contradiction", ""),
                "citation": rule["citation"]["primary"],
                "combustion_citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 17"
            })
        else:
            merc_dignity = get_dignity_state("mercury", merc.get("sign",""),
                                              merc.get("degree",0))
            self.yogas.append({
                "name": "Budha-Aditya Yoga",
                "type": "Intelligence Yoga",
                "status": "Active",
                "distance_from_sun": round(dist, 2),
                "strength": "Full" if merc_dignity["state"] in
                            ["uccha","moolatrikona","swakshetra"] else "Partial",
                "results": rule["results"]["full"],
                "mercury_dignity": merc_dignity["state_label"],
                "citation": rule["citation"]
            })

    # ────────────────────────────────
    # KEMDRUM YOGA
    # ────────────────────────────────
    def _kemdrum(self):
        """
        Source: BPHS Yoga Adhyaya | Parashara | Shloka 22
                Phaldipika | Mantreswara | Chapter 6 | Shloka 15
        9 cancellation conditions from classical texts.
        """
        moon_house = self._get_house_of_planet("moon")
        moon = self.planets.get("moon", {})
        if not moon:
            return

        house_2_from_moon = (moon_house % 12) + 1
        house_12_from_moon = ((moon_house - 2) % 12) + 1

        planets_2nd = self.houses.get(house_2_from_moon, {}).get("planets", [])
        planets_12th = self.houses.get(house_12_from_moon, {}).get("planets", [])
        planets_with_moon = [p for p in self.houses.get(moon_house, {}).get("planets", [])
                              if p != "moon"]

        # Remove Sun from consideration (classical rule)
        planets_2nd = [p for p in planets_2nd if p != "sun"]
        planets_12th = [p for p in planets_12th if p != "sun"]
        planets_with_moon = [p for p in planets_with_moon if p != "sun"]

        has_kemdrum = (not planets_2nd and not planets_12th and not planets_with_moon)

        if not has_kemdrum:
            return

        rule = YOGA_RULES["kemdrum"]
        cancellations_found = []

        # Check all 9 classical cancellation conditions
        # 1. Any planet in Kendra from Lagna
        planets_in_kendra = []
        for h in KENDRA_HOUSES:
            planets_in_kendra.extend(self.houses.get(h, {}).get("planets", []))
        if any(p not in ["moon","sun"] for p in planets_in_kendra):
            cancellations_found.append("Condition 1: Planet in Kendra from Lagna — Kemdrum cancelled")

        # 2. Moon in Kendra from Lagna
        if moon_house in KENDRA_HOUSES:
            cancellations_found.append("Condition 2: Moon itself in Kendra — Kemdrum cancelled")

        # 3-9 require more data — noted for completeness
        moon_dignity = get_dignity_state("moon", moon.get("sign",""),
                                          moon.get("degree",0))
        if moon_dignity["state"] in ["uccha","paramoccha","moolatrikona","swakshetra"]:
            cancellations_found.append(
                f"Condition 7/8: Moon is {moon_dignity['state']} — Kemdrum cancelled"
            )

        is_cancelled = len(cancellations_found) > 0

        self.doshas.append({
            "name": "Kemdrum Yoga",
            "type": "Moon Isolation Dosha",
            "status": "Cancelled — results nullified" if is_cancelled else "ACTIVE — needs attention",
            "severity": "Low" if is_cancelled else "High",
            "condition": "No planets in 2nd or 12th from Moon, and no planets with Moon (Sun excluded)",
            "cancellations_found": cancellations_found if is_cancelled else [],
            "cancellations_not_found": "Yoga is active" if not is_cancelled else "",
            "all_9_cancellations": rule["cancellations"],
            "results_if_active": rule["results"]["full"],
            "citation": rule["citation"],
            "contradiction": rule.get("contradiction", "")
        })

    # ────────────────────────────────
    # VIPARITA RAJ YOGAS
    # ────────────────────────────────
    def _viparita_raj_yogas(self):
        """
        Three types of Viparita Raj Yoga.
        Source: BPHS Yoga Adhyaya | Parashara | Shloka 76-78
                Phaldipika | Mantreswara | Chapter 6 | Shloka 18-20
        """
        lagna_sign = self.lagna_sign
        lagna_idx = SIGNS.index(lagna_sign)

        house_signs = {}
        for h in range(1, 13):
            house_signs[h] = SIGNS[(lagna_idx + h - 1) % 12]

        house_lords = {h: HOUSE_LORDS[s] for h, s in house_signs.items()}

        for dusthana, yoga_name, results_key in [(6, "Harsha", "viparita_raj_harsha"),
                                                   (8, "Sarala", "viparita_raj_sarala"),
                                                   (12, "Vimala", "viparita_raj_vimala")]:
            lord = house_lords[dusthana]
            lord_house = self._get_house_of_planet(lord)

            if lord_house in DUSTHANA_HOUSES:
                rule = YOGA_RULES[results_key]
                self.yogas.append({
                    "name": f"Viparita Raja Yoga — {yoga_name}",
                    "type": "Viparita Raja Yoga",
                    "condition": f"Lord of {dusthana}th house ({lord.capitalize()}) in house {lord_house} (a Dusthana)",
                    "results": rule["results"]["full"],
                    "citation": rule["citation"]
                })

    # ────────────────────────────────
    # RAJA YOGAS
    # ────────────────────────────────
    def _raja_yogas(self):
        """
        Kendra-Trikona Raja Yogas.
        Source: BPHS Yoga Adhyaya | Parashara | Shloka 50-75
        """
        lagna_sign = self.lagna_sign
        lagna_idx = SIGNS.index(lagna_sign)
        house_signs = {h: SIGNS[(lagna_idx + h - 1) % 12] for h in range(1, 13)}
        house_lords = {h: HOUSE_LORDS[s] for h, s in house_signs.items()}

        kendra_lords = [house_lords[h] for h in KENDRA_HOUSES]
        trikona_lords = [house_lords[h] for h in TRIKONA_HOUSES]

        # Check for Kendra lord + Trikona lord conjunction or mutual aspect
        for k_house in KENDRA_HOUSES:
            for t_house in TRIKONA_HOUSES:
                if k_house == t_house:
                    continue
                k_lord = house_lords[k_house]
                t_lord = house_lords[t_house]

                if k_lord == t_lord:
                    # Same planet rules both — automatic Raj Yoga
                    self.yogas.append({
                        "name": f"Raja Yoga — {k_lord.capitalize()} rules Kendra({k_house}) and Trikona({t_house})",
                        "type": "Kendra-Trikona Raja Yoga",
                        "planet": k_lord.capitalize(),
                        "houses_ruled": [k_house, t_house],
                        "strength": "Strong if planet is well-placed",
                        "results": f"Success and authority — {k_lord.capitalize()} governs both a Kendra and Trikona house",
                        "citation": "BPHS Yoga Adhyaya | Parashara | Shloka 55 — A planet owning both Kendra and Trikona is a Yogakaraka"
                    })
                    break  # One per planet is enough

                # Check if they are conjunct
                k_lord_house = self._get_house_of_planet(k_lord)
                t_lord_house = self._get_house_of_planet(t_lord)

                if k_lord_house == t_lord_house and k_lord_house not in DUSTHANA_HOUSES:
                    self.yogas.append({
                        "name": f"Raja Yoga — Lords of {k_house} and {t_house} conjunct",
                        "type": "Kendra-Trikona Raja Yoga",
                        "planets_involved": [k_lord.capitalize(), t_lord.capitalize()],
                        "conjunction_house": k_lord_house,
                        "results": "Power, authority, success in career and life — strength depends on house and dignity",
                        "citation": "BPHS Yoga Adhyaya | Parashara | Shloka 52"
                    })

    # ────────────────────────────────
    # DHANA YOGAS
    # ────────────────────────────────
    def _dhana_yogas(self):
        """
        Wealth combinations.
        Source: BPHS Dhana Yoga Adhyaya | Parashara | Shloka 1-20
        """
        lagna_sign = self.lagna_sign
        lagna_idx = SIGNS.index(lagna_sign)
        house_signs = {h: SIGNS[(lagna_idx + h - 1) % 12] for h in range(1, 13)}
        house_lords = {h: HOUSE_LORDS[s] for h, s in house_signs.items()}

        # Classic Dhana Yoga: Lord of 2 and 11 related
        lord_2 = house_lords[2]
        lord_11 = house_lords[11]
        lord_2_house = self._get_house_of_planet(lord_2)
        lord_11_house = self._get_house_of_planet(lord_11)

        if lord_2_house in [1, 2, 5, 9, 11] or lord_11_house in [1, 2, 5, 9, 11]:
            self.yogas.append({
                "name": "Dhana Yoga",
                "type": "Wealth Yoga",
                "condition": f"Lord of 2nd ({lord_2.capitalize()}) in house {lord_2_house}, Lord of 11th ({lord_11.capitalize()}) in house {lord_11_house}",
                "results": "Wealth accumulation, financial prosperity",
                "citation": "BPHS Dhana Yoga Adhyaya | Parashara | Shloka 5"
            })

        # 5th and 9th lord relationship (Lakshmi Yoga basis)
        lord_5 = house_lords[5]
        lord_9 = house_lords[9]
        lord_5_house = self._get_house_of_planet(lord_5)
        lord_9_house = self._get_house_of_planet(lord_9)

        if lord_9_house in KENDRA_HOUSES or lord_9_house in TRIKONA_HOUSES:
            lord_9_dignity = get_dignity_state(
                lord_9, SIGNS[(lagna_idx + lord_9_house - 1) % 12], 0
            )
            if lord_9_dignity["state"] in ["uccha","moolatrikona","swakshetra"]:
                self.yogas.append({
                    "name": "Lakshmi Yoga",
                    "type": "Wealth and Fortune Yoga",
                    "condition": f"Lord of 9th ({lord_9.capitalize()}) in Kendra/Trikona in own/exalted sign",
                    "results": "Great wealth, fortune, happiness, fame",
                    "citation": "BPHS Yoga Adhyaya | Parashara | Shloka 80"
                })

    # ────────────────────────────────
    # MANGAL DOSHA
    # ────────────────────────────────
    def _mangal_dosha(self):
        """
        Source: Phaldipika | Mantreswara | Ch.7 | Sl.1-5
        CONTRADICTION: Parashara includes 2nd house (6 houses total)
                       Mantreswara counts 5 houses only
        """
        mars_house = self._get_house_of_planet("mars")
        if not mars_house:
            return

        rule = YOGA_RULES["mangal_dosha"]
        # Mantreswara's 5 houses
        mangal_houses_mantreswara = [1, 4, 7, 8, 12]
        # Parashara adds 2nd house
        mangal_houses_parashara = [1, 2, 4, 7, 8, 12]

        if mars_house not in mangal_houses_mantreswara:
            return

        cancellations_found = []
        mars = self.planets.get("mars", {})

        # Check cancellations
        mars_sign = mars.get("sign", "")
        mars_dignity = get_dignity_state("mars", mars_sign, mars.get("degree", 0))

        if mars_dignity["state"] in ["uccha","moolatrikona","swakshetra"]:
            cancellations_found.append(
                f"Mars in {mars_dignity['state']} — Dosha cancelled (Phaldipika Ch.7 Sl.3)"
            )

        # Check Jupiter aspect (simplified)
        jup_house = self._get_house_of_planet("jupiter")
        if jup_house:
            jup_7th_from = (jup_house + 6) % 12 + 1
            if jup_7th_from == mars_house:
                cancellations_found.append("Jupiter aspects Mars — Dosha cancelled (classical rule)")

        severity = rule["severity"].get(f"house_{mars_house}", "Moderate")
        is_cancelled = len(cancellations_found) > 0

        self.doshas.append({
            "name": "Kuja Dosha (Mangal Dosha)",
            "type": "Marriage Affliction",
            "status": "Cancelled" if is_cancelled else "Active",
            "severity": "Cancelled" if is_cancelled else severity,
            "mars_house": mars_house,
            "cancellations": cancellations_found,
            "effect": rule["severity"].get(f"house_{mars_house}", ""),
            "cancellation_conditions": rule["cancellations"],
            "citation": rule["citation"],
            "contradiction": rule.get("contradiction", ""),
            "important_note": "Parashara counts 2nd house also (6 houses), Mantreswara counts 5 houses — both views have classical support"
        })

    # ────────────────────────────────
    # KAAL SARP DOSHA
    # ────────────────────────────────
    def _kaal_sarp(self):
        """
        NOTE: Not in BPHS, Brihat Jataka, Phaldipika, or Saravali.
        Appears in later medieval texts only.
        Source: Muhurta Chintamani (later text)
        """
        rahu = self.planets.get("mean_node", {})
        ketu_lon = (rahu.get("longitude", 0) + 180) % 360
        rahu_lon = rahu.get("longitude", 0)

        all_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        all_between = True

        for p in all_planets:
            lon = self.planets.get(p, {}).get("longitude")
            if lon is None:
                continue
            # Check if planet is between Rahu and Ketu
            if rahu_lon < ketu_lon:
                if not (rahu_lon <= lon <= ketu_lon):
                    all_between = False
                    break
            else:
                if not (lon >= rahu_lon or lon <= ketu_lon):
                    all_between = False
                    break

        if all_between:
            rule = YOGA_RULES["kaal_sarp"]
            self.doshas.append({
                "name": "Kaal Sarp Yoga",
                "type": "Planetary Hemming Dosha",
                "status": "Present",
                "severity": "Moderate — depends on Rahu/Ketu houses",
                "results": rule["results"]["full"],
                "important_classical_note": rule["important_note"],
                "citation": rule["citation"]["primary"],
                "scholarly_warning": "This Yoga does NOT appear in BPHS, Brihat Jataka, Phaldipika, or Saravali — the four primary classical texts. Always disclose this to clients."
            })

    # ────────────────────────────────
    # NEECHA BHANGA RAJ YOGA
    # ────────────────────────────────
    def _neecha_bhanga(self):
        """
        Source: BPHS Neecha Bhanga Adhyaya | Parashara | Shloka 1-7
                Phaldipika | Mantreswara | Chapter 7 | Shloka 22-25
        """
        lagna_sign = self.lagna_sign
        lagna_idx = SIGNS.index(lagna_sign)
        house_signs = {h: SIGNS[(lagna_idx + h - 1) % 12] for h in range(1, 13)}
        house_lords = {h: HOUSE_LORDS[s] for h, s in house_signs.items()}

        for planet, dignity_data in PLANET_DIGNITY.items():
            if planet not in self.planets:
                continue
            pdata = self.planets[planet]
            sign = pdata.get("sign", "")

            if sign != dignity_data.get("debilitation_sign"):
                continue

            # Planet IS debilitated — check Neecha Bhanga conditions
            conditions_met = []
            rule = YOGA_RULES["neecha_bhanga_raj"]

            # Condition 1: Lord of debilitation sign in Kendra from Lagna or Moon
            debil_sign_lord = HOUSE_LORDS.get(sign, "")
            debil_lord_house = self._get_house_of_planet(debil_sign_lord)
            if debil_lord_house in KENDRA_HOUSES:
                conditions_met.append(
                    f"Condition 1 met: Lord of debilitation sign ({debil_sign_lord.capitalize()}) "
                    f"is in Kendra house {debil_lord_house} from Lagna"
                )

            # Condition 3: Debilitated planet itself in Kendra
            planet_house = self._get_house_of_planet(planet)
            if planet_house in KENDRA_HOUSES:
                conditions_met.append(
                    f"Condition 3 met: Debilitated {planet.capitalize()} "
                    f"itself is in Kendra house {planet_house}"
                )

            # Condition 6: Planet in exalted Navamsha (simplified check)
            # Full check needs Navamsha calculation

            if conditions_met:
                strength = "Full Raja Yoga" if len(conditions_met) >= 2 else "Partial Neecha Bhanga"
                self.yogas.append({
                    "name": f"Neecha Bhanga Raja Yoga — {planet.capitalize()}",
                    "type": "Debilitation Cancellation Yoga",
                    "debilitated_planet": planet.capitalize(),
                    "debilitation_sign": sign.capitalize(),
                    "conditions_met": conditions_met,
                    "strength": strength,
                    "results": rule["results"][
                        "full_raj_yoga" if len(conditions_met) >= 2 else "partial"
                    ],
                    "all_7_conditions": rule["conditions"],
                    "citation": rule["citation"]
                })

    # ────────────────────────────────
    # CHANDRA-MANGALA YOGA
    # ────────────────────────────────
    def _chandra_mangala(self):
        """
        Source: BPHS Yoga Adhyaya | Parashara | Shloka 20
        """
        moon = self.planets.get("moon", {})
        mars = self.planets.get("mars", {})
        if not moon or not mars:
            return

        moon_house = self._get_house_of_planet("moon")
        mars_house = self._get_house_of_planet("mars")

        # Conjunction or mutual 7th aspect
        conjunct = moon_house == mars_house
        mutual_aspect = abs(moon_house - mars_house) == 6

        if conjunct or mutual_aspect:
            rule = YOGA_RULES["chandra_mangala"]
            self.yogas.append({
                "name": "Chandra-Mangala Yoga",
                "type": "Wealth Yoga",
                "condition": "Conjunction" if conjunct else "Mutual 7th Aspect",
                "moon_house": moon_house,
                "mars_house": mars_house,
                "results": rule["results"]["full"],
                "citation": rule["citation"]
            })

    # ────────────────────────────────
    # PITRA DOSHA
    # ────────────────────────────────
    def _pitra_dosha(self):
        """
        Source: BPHS | Parashara | Pitra Dosha Adhyaya
        """
        sun = self.planets.get("sun", {})
        sat = self.planets.get("saturn", {})
        rahu = self.planets.get("mean_node", {})

        sun_lon = sun.get("longitude", 0)
        sat_lon = sat.get("longitude", 0)
        rahu_lon = rahu.get("longitude", 0)

        rule = YOGA_RULES["pitra_dosha"]
        dist_sun_sat = abs(sun_lon - sat_lon) % 360
        if dist_sun_sat > 180:
            dist_sun_sat = 360 - dist_sun_sat

        dist_sun_rahu = abs(sun_lon - rahu_lon) % 360
        if dist_sun_rahu > 180:
            dist_sun_rahu = 360 - dist_sun_rahu

        if dist_sun_sat < 10:
            self.doshas.append({
                "name": "Pitra Dosha",
                "type": "Ancestral Affliction",
                "cause": f"Sun-Saturn conjunction — {round(dist_sun_sat,1)}° apart",
                "severity": "Moderate",
                "results": rule["results"]["full"],
                "citation": rule["citation"]["primary"]
            })
        elif dist_sun_rahu < 10:
            self.doshas.append({
                "name": "Pitra Dosha",
                "type": "Ancestral Affliction",
                "cause": f"Sun-Rahu conjunction — {round(dist_sun_rahu,1)}° apart",
                "severity": "High",
                "results": rule["results"]["full"],
                "citation": rule["citation"]["primary"]
            })

    # ────────────────────────────────
    # HELPER METHODS
    # ────────────────────────────────
    def _get_house_of_planet(self, planet: str) -> int:
        for hnum, hdata in self.houses.items():
            if planet in hdata.get("planets", []):
                return hnum
        return 0
