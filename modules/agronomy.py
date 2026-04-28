"""
modules/agronomy.py
────────────────────
Agronomic helpers:
  • Relative field calendar generation (phase-by-phase)
  • Fertiliser dose calculator
  • Soil health scoring
  • Irrigation scheduling
"""

from modules.config import CROP_NPK, SOIL_ZONES

# ── Relative Crop Calendars ───────────────────────────────────────────────────
RELATIVE_CROP_CALENDARS = {
    "apple": {
        "Month 1": {
            "phase": "Dormancy & Pruning",
            "weeks": {
                "Week 1-2": "Conduct dormant pruning. Remove dead, diseased, and crossing branches.",
                "Week 3-4": "Apply dormant oil spray to suffocate overwintering pests and eggs."
            }
        },
        "Month 2": {
            "phase": "Bud Break & Bloom",
            "weeks": {
                "Week 1-2": "Monitor bud break. Apply preventive fungicide for apple scab.",
                "Week 3-4": "Bloom phase. Introduce beehives to the orchard. DO NOT apply insecticides."
            }
        },
        "Month 3": {
            "phase": "Fruit Set & Thinning",
            "weeks": {
                "Week 1-2": "Monitor fruit set. Begin chemical or manual thinning to ensure fruit size.",
                "Week 3-4": "Apply first cover sprays for codling moth and apple maggots."
            }
        },
        "Month 4": {
            "phase": "Fruit Growth",
            "weeks": {
                "Week 1-2": "Provide steady irrigation. Summer pruning to expose fruit to sunlight.",
                "Week 3-4": "Monitor for powdery mildew and aphids. Maintain weed control."
            }
        },
        "Month 5": {
            "phase": "Pre-Harvest Prep",
            "weeks": {
                "Week 1-2": "Apply pre-harvest drop control sprays if necessary.",
                "Week 3-4": "Prepare harvest bins and cold storage. Stop irrigation to improve sugar content."
            }
        },
        "Month 6": {
            "phase": "Harvesting",
            "weeks": {
                "Week 1-2": "Conduct starch-iodine tests to determine maturity. Begin early harvest.",
                "Week 3-4": "Main harvest. Grade and store apples immediately to preserve crispness."
            }
        }
    },
    "banana": {
        "Month 1": {
            "phase": "Planting & Establishment",
            "weeks": {
                "Week 1-2": "Dig pits, expose to sun. Plant disease-free tissue culture suckers.",
                "Week 3-4": "Apply basal FYM and light irrigation. First manual weeding."
            }
        },
        "Month 2": {
            "phase": "Early Vegetative Growth",
            "weeks": {
                "Week 1-2": "Apply 1st split dose of Nitrogen and Potassium. Maintain soil moisture.",
                "Week 3-4": "Desuckering (remove unwanted side shoots). Monitor for nematodes."
            }
        },
        "Month 3": {
            "phase": "Active Vegetative Growth",
            "weeks": {
                "Week 1-2": "Earthing up to support the pseudo-stem. Apply 2nd split dose of NPK.",
                "Week 3-4": "Apply neem cake for rhizome weevil prevention. Second weeding."
            }
        },
        "Month 4": {
            "phase": "Pre-Shooting Stage",
            "weeks": {
                "Week 1-2": "Apply 3rd split dose of fertilizers. Ensure strict irrigation.",
                "Week 3-4": "Remove dried leaves. Spray micro-nutrients (Zinc/Boron) if deficient."
            }
        },
        "Month 5": {
            "phase": "Bunch Emergence",
            "weeks": {
                "Week 1-2": "Shooting begins. Apply bunch covers to protect from sun and pests.",
                "Week 3-4": "Propping: support stems with bamboo poles to prevent wind damage."
            }
        },
        "Month 6": {
            "phase": "Bunch Development & Harvest",
            "weeks": {
                "Week 1-2": "Denavelling: remove the male bud to direct energy to the fruit.",
                "Week 3-4": "Harvesting: cut bunches when fruit angles become rounded and plump."
            }
        }
    },
    "barley": {
        "Month 1": {
            "phase": "Sowing & Tillering",
            "weeks": {
                "Week 1-2": "Seed treatment with fungicide. Sowing at 3-5 cm depth.",
                "Week 3-4": "Crown Root Initiation (CRI). First critical irrigation. Apply nitrogen top-dressing."
            }
        },
        "Month 2": {
            "phase": "Active Tillering & Booting",
            "weeks": {
                "Week 1-2": "Maximum tillering stage. Monitor for broadleaf weeds and apply herbicides.",
                "Week 3-4": "Booting stage begins. Second critical irrigation required if dry."
            }
        },
        "Month 3": {
            "phase": "Heading & Grain Filling",
            "weeks": {
                "Week 1-2": "Heading and flowering. Do not stress the crop for water.",
                "Week 3-4": "Grain filling (milk to dough stage). Monitor for aphids and rust diseases."
            }
        },
        "Month 4": {
            "phase": "Maturity & Harvest",
            "weeks": {
                "Week 1-2": "Physiological maturity. Leaves turn yellow and spikes dry.",
                "Week 3-4": "Harvesting. Cut when grain moisture drops below 14%."
            }
        }
    },
    "blackgram": {
        "Month 1": {
            "phase": "Sowing & Germination",
            "weeks": {
                "Week 1": "Land prep. Treat seeds with Rhizobium. Sow seeds.",
                "Week 2": "Monitor germination. Apply light life-saving irrigation if needed.",
                "Week 3": "First weeding. Check for early sap-sucking pests (whiteflies).",
                "Week 4": "Apply first foliar nutrient spray if growth is stunted."
            }
        },
        "Month 2": {
            "phase": "Vegetative & Pre-Flowering",
            "weeks": {
                "Week 1": "Second weeding. Earthing up rows to prevent water-logging.",
                "Week 2": "Pre-flowering irrigation to maximize bud count.",
                "Week 3": "Monitor for yellow mosaic virus. Uproot infected plants.",
                "Week 4": "Flowering begins. Avoid harsh chemical sprays to protect pollinators."
            }
        },
        "Month 3": {
            "phase": "Pod Development & Harvest",
            "weeks": {
                "Week 1": "Pod formation. Prevent water stress to avoid pod drop.",
                "Week 2": "Monitor for pod borers. Apply neem-based controls if necessary.",
                "Week 3": "Leaves begin yellowing. Stop all irrigation.",
                "Week 4": "Harvesting. Pluck when 80% of pods turn black and brittle."
            }
        }
    },
    "chickpea": {
        "Month 1": {
            "phase": "Sowing & Early Vegetative",
            "weeks": {
                "Week 1-2": "Deep summer ploughing. Sow seeds treated with Trichoderma.",
                "Week 3-4": "Pre-emergence weed control. Ensure adequate soil moisture."
            }
        },
        "Month 2": {
            "phase": "Branching & Nipping",
            "weeks": {
                "Week 1-2": "First irrigation (if rainfall is deficient) at branching stage.",
                "Week 3-4": "Nipping (plucking apical buds) at 30-35 days to encourage lateral branching."
            }
        },
        "Month 3": {
            "phase": "Flowering",
            "weeks": {
                "Week 1-2": "Flowering stage begins. Crucial time for 2nd irrigation.",
                "Week 3-4": "Monitor intensely for Gram Pod Borer (Helicoverpa). Install pheromone traps."
            }
        },
        "Month 4": {
            "phase": "Pod Development",
            "weeks": {
                "Week 1-2": "Pod formation and grain filling. Avoid heavy irrigation.",
                "Week 3-4": "Apply bio-pesticides (NPV) if pod borer crosses economic threshold."
            }
        },
        "Month 5": {
            "phase": "Harvesting",
            "weeks": {
                "Week 1-2": "Crop matures. Leaves shed and pods turn light brown/yellow.",
                "Week 3-4": "Harvesting and threshing. Dry seeds to 10% moisture for storage."
            }
        }
    },
    "coconut": {
        "Month 1": {
            "phase": "Basin Prep & Fertilization",
            "weeks": {
                "Week 1-2": "Open basins around palms (1.8m radius).",
                "Week 3-4": "Apply organic manure and 1st split of NPK before monsoons."
            }
        },
        "Month 2": {
            "phase": "Green Manuring",
            "weeks": {
                "Week 1-2": "Sow green manure crops (like sunn hemp) in the palm basin.",
                "Week 3-4": "Check crowns for Rhinoceros beetle damage. Clean crowns."
            }
        },
        "Month 3": {
            "phase": "Nutrient Recovery",
            "weeks": {
                "Week 1-2": "Incorporate grown green manure into the soil.",
                "Week 3-4": "Apply 2nd split dose of NPK post-monsoon."
            }
        },
        "Month 4": {
            "phase": "Moisture Conservation",
            "weeks": {
                "Week 1-2": "Mulch basins with dried coconut leaves or coir pith.",
                "Week 3-4": "Begin summer irrigation schedule (drip irrigation preferred)."
            }
        }
    },
    "coffee": {
        "Month 1": {
            "phase": "Blossom & Backing Showers",
            "weeks": {
                "Week 1-2": "Crucial period. Provide sprinkler irrigation if natural blossom showers fail.",
                "Week 3-4": "Backing showers needed 21 days after blossom for fruit set."
            }
        },
        "Month 2": {
            "phase": "Vegetative Growth & Borer Control",
            "weeks": {
                "Week 1-2": "Handling/centering bushes to allow air circulation.",
                "Week 3-4": "Track and trace White Stem Borer. Remove affected stems."
            }
        },
        "Month 3": {
            "phase": "Berry Expansion & Shade Management",
            "weeks": {
                "Week 1-2": "Shade lopping to regulate sunlight during the heavy monsoon.",
                "Week 3-4": "Apply post-monsoon fertilizers. Weed control in the estate."
            }
        },
        "Month 4": {
            "phase": "Harvesting Prep",
            "weeks": {
                "Week 1-2": "Clean drying yards. Prepare pulping machinery.",
                "Week 3-4": "Arabica harvest begins. Selective hand-picking of ripe red cherries only."
            }
        }
    },
    "cotton": {
        "Month 1": {
            "phase": "Sowing & Seedling",
            "weeks": {
                "Week 1-2": "Sow acid-delinted seeds. Apply basal NPK.",
                "Week 3-4": "Gap filling and thinning. Maintain ideal plant population. First weeding."
            }
        },
        "Month 2": {
            "phase": "Vegetative Growth",
            "weeks": {
                "Week 1-2": "Apply 1st top dressing of Nitrogen. Inter-cultivation for weed control.",
                "Week 3-4": "Square (flower bud) formation begins. Monitor for jassids and aphids."
            }
        },
        "Month 3": {
            "phase": "Flowering & Boll Formation",
            "weeks": {
                "Week 1-2": "Peak flowering. High water requirement; irrigate if dry.",
                "Week 3-4": "Apply 2nd top dressing of Nitrogen. Install traps for Pink Bollworm."
            }
        },
        "Month 4": {
            "phase": "Boll Development",
            "weeks": {
                "Week 1-2": "Boll maturation. Apply foliar spray (KNO3) to improve boll weight.",
                "Week 3-4": "Monitor intensely for bollworm complex. Late irrigation."
            }
        },
        "Month 5": {
            "phase": "Boll Opening & Picking",
            "weeks": {
                "Week 1-2": "Stop irrigation. Bolls begin to burst open.",
                "Week 3-4": "First picking after morning dew dries. Second picking follows 15 days later."
            }
        }
    },
    "grapes": {
        "Month 1": {
            "phase": "Foundation Pruning",
            "weeks": {
                "Week 1-2": "Severe pruning (back to 1-2 buds) to build vegetative framework.",
                "Week 3-4": "Apply heavy basal organic manures and first dose of NPK. Heavy irrigation."
            }
        },
        "Month 2": {
            "phase": "Shoot Growth",
            "weeks": {
                "Week 1-2": "Active shoot growth. Perform sub-cane formation (pinching).",
                "Week 3-4": "Spray preventive fungicides for Downy Mildew. Maintain weed-free vineyard."
            }
        },
        "Month 3": {
            "phase": "Cane Maturity",
            "weeks": {
                "Week 1-2": "Reduce irrigation and nitrogen to stop vegetative growth.",
                "Week 3-4": "Apply Potassium and Phosphorus to encourage cane maturity (turning brown)."
            }
        },
        "Month 4": {
            "phase": "Forward (Fruit) Pruning",
            "weeks": {
                "Week 1-2": "Prune for fruiting. Apply Hydrogen Cyanamide paste to ensure uniform bud break.",
                "Week 3-4": "Bud sprouting. Apply preventive sprays for Thrips and Flea beetles."
            }
        },
        "Month 5": {
            "phase": "Flowering & Fruit Set",
            "weeks": {
                "Week 1-2": "Flowering begins. Withhold irrigation slightly to aid fruit set.",
                "Week 3-4": "Berry setting stage. Apply Gibberellic Acid (GA3) dips for berry elongation."
            }
        },
        "Month 6": {
            "phase": "Berry Development & Harvest",
            "weeks": {
                "Week 1-2": "Veraison (color change and sugar accumulation). Apply high Potassium.",
                "Week 3-4": "Harvest when berries reach optimal TSS (Total Soluble Solids). Pack immediately."
            }
        }
    },
    "lentil": {
        "Month 1": {
            "phase": "Sowing & Early Vegetative",
            "weeks": {
                "Week 1": "Deep ploughing and seedbed preparation. Seed treatment with Rhizobium.",
                "Week 2": "Sow seeds at 3-4 cm depth. Apply basal dose of phosphorus.",
                "Week 3": "Monitor for uniform germination. Light irrigation if soil is completely dry.",
                "Week 4": "First manual weeding (crucial before canopy closes). Monitor for early aphids."
            }
        },
        "Month 2": {
            "phase": "Branching & Pre-Flowering",
            "weeks": {
                "Week 1-2": "Active vegetative branching. Maintain weed-free environment.",
                "Week 3-4": "Pre-flowering stage. Apply irrigation if soil moisture is critically low. Watch for pod borers."
            }
        },
        "Month 3": {
            "phase": "Flowering & Pod Formation",
            "weeks": {
                "Week 1-2": "Flowering phase. Avoid water stress but do not over-irrigate.",
                "Week 3-4": "Pod formation begins. Install pheromone traps for pest monitoring."
            }
        },
        "Month 4": {
            "phase": "Maturity & Harvest",
            "weeks": {
                "Week 1-2": "Maturity phase. Lower leaves turn yellow and drop.",
                "Week 3-4": "Harvest when 80% of pods turn brown and hard. Thresh after sun-drying."
            }
        }
    },
    "rice": {
        "Month 1": {
            "phase": "Nursery & Transplanting",
            "weeks": {
                "Week 1-2": "Prepare wet nursery bed. Sow pre-germinated seeds.",
                "Week 3-4": "Puddling of main field. Transplant 21-25 day old seedlings. Apply basal NPK."
            }
        },
        "Month 2": {
            "phase": "Tillering Stage",
            "weeks": {
                "Week 1-2": "Maintain 2-3 cm water level. Apply first top dressing of Urea (Nitrogen).",
                "Week 3-4": "Active tillering. Monitor for stem borer and leaf folder pests. Manual weeding."
            }
        },
        "Month 3": {
            "phase": "Panicle Initiation & Heading",
            "weeks": {
                "Week 1-2": "Panicle initiation. Apply second top dressing of Urea and Potassium.",
                "Week 3-4": "Heading and flowering. Maintain 5 cm standing water. Do not spray chemicals during bloom."
            }
        },
        "Month 4": {
            "phase": "Maturity & Harvest",
            "weeks": {
                "Week 1-2": "Dough stage. Drain water from the field 10 days before harvest.",
                "Week 3-4": "Harvest when 80% of panicles turn golden yellow. Dry grains to 14% moisture."
            }
        }
    },
    "maize": {
        "Month 1": {
            "phase": "Sowing & Establishment",
            "weeks": {
                "Week 1": "Deep ploughing. Sow seeds on ridges. Apply basal NPK and Zinc.",
                "Week 2": "Emergence. Gap filling to maintain ideal plant population.",
                "Week 3": "Thinning. Remove weak seedlings.",
                "Week 4": "First inter-cultivation/weeding. Apply early irrigation if dry."
            }
        },
        "Month 2": {
            "phase": "Vegetative Growth (Knee High)",
            "weeks": {
                "Week 1-2": "Knee-high stage (V8). Crucial time for 1st top dressing of Nitrogen. Earthing up.",
                "Week 3-4": "Rapid growth. Monitor for Fall Armyworm (Spodoptera frugiperda) strictly."
            }
        },
        "Month 3": {
            "phase": "Tasseling & Silking",
            "weeks": {
                "Week 1-2": "Tasseling stage. Most critical stage for irrigation—prevent any water stress.",
                "Week 3-4": "Silking and pollination. Apply final top dressing of Nitrogen."
            }
        },
        "Month 4": {
            "phase": "Grain Filling to Harvest",
            "weeks": {
                "Week 1-2": "Dough to dent stage. Protect from birds and rodents.",
                "Week 3-4": "Physiological maturity. Harvest when husk turns dry and brown (grain moisture < 20%)."
            }
        }
    }
}


def get_relative_calendar(crop: str) -> dict:
    """
    Return timeline phases → activity mapping for a crop.
    """
    normalized_crop = crop.lower().replace(" ", "")
    
    # Default fallback dynamically uses the crop name if it isn't in the dictionary
    default_calendar = {
        "Month 1": {
            "phase": f"Initial Planning ({crop.title()})",
            "weeks": {
                "Week 1-4": f"Awaiting detailed operational schedule for {crop.title()}."
            }
        }
    }
    
    return RELATIVE_CROP_CALENDARS.get(normalized_crop, default_calendar)


# ── Agronomic Calculators ─────────────────────────────────────────────────────

def fertiliser_recommendation(crop: str, N: float, P: float, K: float,
                               land_acres: float = 1.0) -> dict:
    """
    Calculate fertiliser doses to bridge the gap between
    current soil NPK and optimal NPK for the crop.

    Returns: dict with doses in kg/ha and product names.
    """
    crop_l  = crop.lower()
    opt_N, opt_P, opt_K = CROP_NPK.get(crop_l, (80, 40, 40))
    ha = land_acres * 0.405  # 1 acre = 0.405 ha

    deficit_N = max(0, opt_N - N)
    deficit_P = max(0, opt_P - P)
    deficit_K = max(0, opt_K - K)

    # Convert to product doses (approximate content):
    # Urea = 46% N, DAP = 18%N + 46%P₂O₅ (=20%P), MOP = 60%K₂O (=50%K)
    urea_kg  = round((deficit_N / 0.46) * ha, 1)
    dap_kg   = round((deficit_P / 0.20) * ha, 1)
    mop_kg   = round((deficit_K / 0.50) * ha, 1)

    schedule = []
    if urea_kg > 0:
        schedule.append({
            "product": "Urea (46% N)",
            "dose_kg": urea_kg,
            "timing": "Split: 50% at sowing, 50% at 30 days",
        })
    if dap_kg > 0:
        schedule.append({
            "product": "DAP (18N + 46P₂O₅)",
            "dose_kg": dap_kg,
            "timing": "Basal application at sowing",
        })
    if mop_kg > 0:
        schedule.append({
            "product": "MOP / Muriate of Potash (60% K₂O)",
            "dose_kg": mop_kg,
            "timing": "Basal application at sowing",
        })

    return {
        "optimal_N": opt_N, "optimal_P": opt_P, "optimal_K": opt_K,
        "deficit_N": round(deficit_N, 1),
        "deficit_P": round(deficit_P, 1),
        "deficit_K": round(deficit_K, 1),
        "schedule":  schedule,
        "land_ha":   round(ha, 2),
    }


def soil_health_score(N: float, P: float, K: float, ph: float,
                      humidity: float) -> dict:
    """
    Compute a 0-100 soil health score and individual ratings.
    """
    def rate(val, low, ideal_lo, ideal_hi, high):
        if val < low or val > high:
            return 0
        elif ideal_lo <= val <= ideal_hi:
            return 100
        elif val < ideal_lo:
            return int((val - low) / (ideal_lo - low) * 100)
        else:
            return int((high - val) / (high - ideal_hi) * 100)

    n_score  = rate(N,   0,  60,  120, 180)
    p_score  = rate(P,   0,  30,   80, 145)
    k_score  = rate(K,   0,  30,   80, 205)
    ph_score = rate(ph,  4,  6.0,  7.5, 9)
    hum_score= rate(humidity, 0, 40, 80, 100)

    composite = round((n_score*0.25 + p_score*0.20 + k_score*0.20 +
                       ph_score*0.25 + hum_score*0.10), 1)

    def label(s):
        return "Excellent" if s>=80 else "Good" if s>=60 else "Fair" if s>=40 else "Poor"

    return {
        "overall":   composite,
        "label":     label(composite),
        "N_score":   n_score,  "P_score": p_score,  "K_score": k_score,
        "ph_score":  ph_score, "hum_score": hum_score,
        "N_label":   label(n_score), "P_label": label(p_score),
        "K_label":   label(k_score), "ph_label": label(ph_score),
    }


def irrigation_advice(crop: str, rainfall: float, humidity: float,
                      temp: float) -> dict:
    """Simple irrigation frequency recommendation."""
    crop_l = crop.lower()
    # Water demand index
    water_demand = {"rice": 5, "sugarcane": 5, "banana": 4, "cotton": 3,
                    "wheat": 3, "maize": 3, "chickpea": 1, "mustard": 1}
    demand = water_demand.get(crop_l, 2)  # 1=low, 5=high

    effective_rain = rainfall * 0.7  # 70% efficiency
    et_daily = max(1, (temp - 10) * 0.15 + (100 - humidity) * 0.05)

    days_between = max(3, int(effective_rain / (et_daily * demand * 7)))
    days_between = min(days_between, 21)

    method = ("Flood / furrow" if crop_l in {"rice","sugarcane","banana"}
              else "Drip / sprinkler" if demand <= 2
              else "Sprinkler / furrow")

    return {
        "frequency_days": days_between,
        "method":         method,
        "demand_level":   ["—","Low","Low-Med","Medium","Med-High","High"][demand],
        "et_daily_mm":    round(et_daily, 1),
    }
# ── UI Adapters & Constants (Added to resolve ImportError) ────────────────────

MONTHS = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]

ACTIVITY_COLORS = {
    "Rest": "#E1E4E8",
    
    # Germination / Sowing (Ambers/Browns)
    "Sowing & Germination": "#9A6700", "Sowing & Seedling": "#9A6700",
    "Sowing & Tillering": "#9A6700", "Sowing & Early Vegetative": "#9A6700",
    "Sowing & Establishment": "#9A6700", "Planting & Establishment": "#9A6700",
    "Basin Prep & Fertilization": "#9A6700", "Foundation Pruning": "#9A6700",
    "Dormancy & Pruning": "#9A6700",

    # Vegetative / Growth (Greens)
    "Early Vegetative Growth": "#2DA44E", "Active Vegetative Growth": "#2DA44E",
    "Vegetative & Pre-Flowering": "#2DA44E", "Vegetative Growth": "#2DA44E",
    "Vegetative Growth (Knee High)": "#2DA44E", "Vegetative Growth & Borer Control": "#2DA44E",
    "Branching & Nipping": "#2DA44E", "Branching & Pre-Flowering": "#2DA44E",
    "Active Tillering & Booting": "#2DA44E", "Tillering Stage": "#2DA44E",
    "Shoot Growth": "#2DA44E", "Green Manuring": "#2DA44E",

    # Flowering (Yellows)
    "Bud Break & Bloom": "#D4A72C", "Flowering": "#D4A72C",
    "Flowering & Pod Formation": "#D4A72C", "Flowering & Boll Formation": "#D4A72C",
    "Flowering & Fruit Set": "#D4A72C", "Tasseling & Silking": "#D4A72C",
    "Blossom & Backing Showers": "#D4A72C", "Panicle Initiation & Heading": "#D4A72C",
    "Heading & Grain Filling": "#D4A72C",

    # Development / Maturation (Blues)
    "Fruit Set & Thinning": "#0969DA", "Fruit Growth": "#0969DA",
    "Pre-Shooting Stage": "#0969DA", "Bunch Emergence": "#0969DA",
    "Pod Development": "#0969DA", "Pod Development & Harvest": "#0969DA",
    "Boll Development": "#0969DA", "Berry Expansion & Shade Management": "#0969DA",
    "Berry Development & Harvest": "#0969DA", "Nutrient Recovery": "#0969DA",
    "Moisture Conservation": "#0969DA", "Cane Maturity": "#0969DA",
    "Forward (Fruit) Pruning": "#0969DA",

    # Harvest (Reds)
    "Pre-Harvest Prep": "#CF222E", "Harvesting": "#CF222E",
    "Harvesting Prep": "#CF222E", "Bunch Development & Harvest": "#CF222E",
    "Maturity & Harvest": "#CF222E", "Boll Opening & Picking": "#CF222E",
    "Grain Filling to Harvest": "#CF222E"


def get_field_calendar(crop: str) -> dict:
    """
    Adapter function to map the relative calendar data into the format
    expected by the Streamlit frontend.
    """
    rel_cal = get_relative_calendar(crop)
    calendar = {}
    milestones = []

    for month in MONTHS:
        if month in rel_cal:
            phase = rel_cal[month]["phase"]
            calendar[month] = phase

            # Combine the weekly tasks into a single milestone description
            weeks = rel_cal[month].get("weeks", {})
            desc = " ".join(weeks.values())
            milestones.append((month, f"{phase}: {desc}"))
        else:
            calendar[month] = "Rest"

    return {
        "season": "Standard 6-Month Cycle",
        "calendar": calendar,
        "milestones": milestones
    }
