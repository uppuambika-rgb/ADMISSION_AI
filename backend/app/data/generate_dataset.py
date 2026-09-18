"""
One-time script: generates sample_colleges.json and ap_eapcet_colleges.json
from the raw data provided.

Run from backend directory:
    python app/data/generate_dataset.py
"""
import json
import math
from pathlib import Path

OUT_DIR = Path(__file__).parent

# ── helpers ──────────────────────────────────────────────────────────────────
BRANCH_LABELS = {
    "CSE":   "Computer Science and Engineering",
    "ECE":   "Electronics and Communication Engineering",
    "EEE":   "Electrical and Electronics Engineering",
    "MECH":  "Mechanical Engineering",
    "CIVIL": "Civil Engineering",
    "IT":    "Information Technology",
    "CSM":   "Computer Science (AI & ML)",
    "CSD":   "Computer Science (Data Science)",
}

BRANCH_KEYWORDS = {
    "CSE":   ["Data Structures and Algorithms","Object Oriented Programming","Database Management","Computer Networks","Artificial Intelligence","Web Technologies","Software Engineering"],
    "ECE":   ["Digital Communication","Microprocessors and Microcontrollers","Analog Electronics","Signal Processing","VLSI Design","Wireless Networks","Embedded Systems"],
    "EEE":   ["Power Systems","Control Systems","Electrical Machines","Renewable Energy","Power Electronics","Instrumentation","Circuit Analysis"],
    "MECH":  ["Thermodynamics","Fluid Mechanics","Manufacturing Processes","CAD/CAM","Robotics and Automation","Automotive Engineering","Machine Design"],
    "CIVIL": ["Structural Analysis","Fluid Mechanics","Geotechnical Engineering","Transportation Engineering","Environmental Engineering","Construction Management","Surveying"],
    "IT":    ["Software Engineering","Information Security","Network Administration","Database Systems","Cloud Computing","Mobile Computing","Data Analytics"],
    "CSM":   ["Machine Learning","Deep Learning","Natural Language Processing","Computer Vision","Data Analytics","Python","Big Data Systems"],
    "CSD":   ["Data Engineering","Statistical Analysis","Machine Learning","Database Systems","Data Visualization","Big Data","Cloud Analytics"],
}

BRANCH_ROLES = {
    "CSE":   ["Software Engineer","Full Stack Developer","Data Analyst","Systems Engineer"],
    "ECE":   ["VLSI Engineer","Embedded Engineer","Telecom Engineer","Software Developer"],
    "EEE":   ["Electrical Engineer","Power Systems Engineer","PSU Engineer","Automation Engineer"],
    "MECH":  ["Mechanical Design Engineer","Robotics Specialist","Plant Operations Engineer","Automotive Engineer"],
    "CIVIL": ["Structural Engineer","Site Engineer","Urban Planner","Construction Manager"],
    "IT":    ["Software Engineer","Network Engineer","IT Consultant","Data Engineer"],
    "CSM":   ["AI Engineer","ML Engineer","Data Scientist","Research Analyst"],
    "CSD":   ["Data Engineer","Analytics Engineer","BI Developer","Data Scientist"],
}

PLACEMENT = {
    "CSE":   (20.0, 95.0, ["Google","Microsoft","Amazon","Adobe","Uber"]),
    "ECE":   (14.0, 88.0, ["Qualcomm","Samsung","Texas Instruments","NVIDIA","Cisco"]),
    "EEE":   (10.0, 80.0, ["NTPC","BHEL","L&T","Siemens","ABB"]),
    "MECH":  (9.0,  78.0, ["Tata Motors","Mahindra","L&T","Bosch","Maruti Suzuki"]),
    "CIVIL": (8.0,  72.0, ["L&T Construction","DLF","Gammon","NHAI","AECOM"]),
    "IT":    (18.0, 92.0, ["TCS","Infosys","Wipro","IBM","Accenture"]),
    "CSM":   (19.0, 93.0, ["Google","Amazon","Microsoft","Zoho","Freshworks"]),
    "CSD":   (18.5, 91.0, ["Amazon","Microsoft","Flipkart","Walmart Labs","LinkedIn"]),
}

def op(closing):
    return max(1, round(closing * 0.6))

def cutoff_block(general, obc, sc, st, ews=None, year="2024", round_label="Round 6 Closing"):
    cats = {
        "General": {"opening_rank": op(general), "closing_rank": general},
        "OBC-NCL": {"opening_rank": op(obc),     "closing_rank": obc},
        "SC":      {"opening_rank": op(sc),       "closing_rank": sc},
        "ST":      {"opening_rank": op(st),       "closing_rank": st},
    }
    if ews:
        cats["EWS"] = {"opening_rank": op(ews), "closing_rank": ews}
    return {
        "category_cutoffs": {k: {"opening_rank": v["opening_rank"], "closing_rank": v["closing_rank"]} for k,v in cats.items()},
        "cutoff_history": {year: {"round": round_label, "categories": cats}}
    }

def make_record(id_, college_name, branch, college_type, exam, location,
                tier, tuition, hostel_fee, scholarships, higher, entre,
                general, obc, sc, st, ews=None, year="2024", round_label="Round 6 Closing",
                notes=""):
    bname = BRANCH_LABELS[branch]
    cb = cutoff_block(general, obc, sc, st, ews, year, round_label)
    lpa, pct, recruiters = PLACEMENT[branch]
    return {
        "id": id_,
        "college_name": college_name,
        "branch_name": bname,
        "college_type": college_type,
        "exam": exam,
        "location": location,
        "tier_rating": tier,
        "annual_tuition_fee_inr": tuition,
        "hostel_available": True,
        "annual_hostel_fee_inr": hostel_fee,
        "scholarships": scholarships,
        "higher_study_opportunities": higher,
        "entrepreneurship_opportunities": entre,
        "cutoff_year_round": f"{year} ({round_label})",
        "typical_roles": BRANCH_ROLES[branch],
        **cb,
        "curriculum_keywords": BRANCH_KEYWORDS[branch],
        "placement_stats": {
            "median_salary_lpa": lpa,
            "placement_percentage": pct,
            "top_recruiters": recruiters,
            "key_career_domains": [BRANCH_LABELS[branch].split()[0], "Engineering", "Technology"],
        },
        "admission_notes": notes,
    }

# ══════════════════════════════════════════════════════════════════════════════
# IIT DATA  (23 IITs × 5 branches = 115 records)
# Source: institutes list + cutoffs JSON provided by user
# ══════════════════════════════════════════════════════════════════════════════
IITS = [
    (1,  "Indian Institute of Technology, Bombay",       "Mumbai, Maharashtra",    "IIT Bombay"),
    (2,  "Indian Institute of Technology, Delhi",        "New Delhi",              "IIT Delhi"),
    (3,  "Indian Institute of Technology, Madras",       "Chennai, Tamil Nadu",    "IIT Madras"),
    (4,  "Indian Institute of Technology, Kanpur",       "Kanpur, Uttar Pradesh",  "IIT Kanpur"),
    (5,  "Indian Institute of Technology, Kharagpur",   "Kharagpur, West Bengal", "IIT Kharagpur"),
    (6,  "Indian Institute of Technology, Roorkee",     "Roorkee, Uttarakhand",   "IIT Roorkee"),
    (7,  "Indian Institute of Technology, Guwahati",    "Guwahati, Assam",        "IIT Guwahati"),
    (8,  "Indian Institute of Technology, Hyderabad",   "Hyderabad, Telangana",   "IIT Hyderabad"),
    (9,  "Indian Institute of Technology, Indore",      "Indore, Madhya Pradesh", "IIT Indore"),
    (10, "Indian Institute of Technology (BHU), Varanasi","Varanasi, Uttar Pradesh","IIT BHU"),
    (11, "Indian Institute of Technology (ISM), Dhanbad","Dhanbad, Jharkhand",    "IIT ISM Dhanbad"),
    (12, "Indian Institute of Technology, Ropar",       "Ropar, Punjab",          "IIT Ropar"),
    (13, "Indian Institute of Technology, Patna",       "Patna, Bihar",           "IIT Patna"),
    (14, "Indian Institute of Technology, Gandhinagar", "Gandhinagar, Gujarat",   "IIT Gandhinagar"),
    (15, "Indian Institute of Technology, Bhubaneswar", "Bhubaneswar, Odisha",    "IIT Bhubaneswar"),
    (16, "Indian Institute of Technology, Jodhpur",     "Jodhpur, Rajasthan",     "IIT Jodhpur"),
    (17, "Indian Institute of Technology, Mandi",       "Mandi, Himachal Pradesh","IIT Mandi"),
    (18, "Indian Institute of Technology, Tirupati",    "Tirupati, Andhra Pradesh","IIT Tirupati"),
    (19, "Indian Institute of Technology, Palakkad",    "Palakkad, Kerala",       "IIT Palakkad"),
    (20, "Indian Institute of Technology, Goa",         "Goa",                    "IIT Goa"),
    (21, "Indian Institute of Technology, Dharwad",     "Dharwad, Karnataka",     "IIT Dharwad"),
    (22, "Indian Institute of Technology, Bhilai",      "Bhilai, Chhattisgarh",   "IIT Bhilai"),
    (23, "Indian Institute of Technology, Jammu",       "Jammu, J&K",             "IIT Jammu"),
]

# cutoffs from the JSON you provided: oc, obc, sc, st (per institute_id per branch)
IIT_CUTOFFS = {
    # id: {branch: (oc, obc, sc, st)}
    1:  {"CSE":(80,32,17,9),  "ECE":(144,57,31,17), "EEE":(208,83,45,24),  "MECH":(272,108,59,32),  "CIVIL":(336,134,73,40)},
    2:  {"CSE":(160,64,35,19),"ECE":(288,115,63,34),"EEE":(416,166,91,49), "MECH":(544,217,119,65), "CIVIL":(672,268,147,80)},
    3:  {"CSE":(240,96,52,28),"ECE":(432,172,95,51),"EEE":(624,249,137,74),"MECH":(816,326,179,97), "CIVIL":(1008,403,221,120)},
    4:  {"CSE":(320,128,70,38),"ECE":(576,230,126,69),"EEE":(832,332,183,99),"MECH":(1088,435,239,130),"CIVIL":(1344,537,295,161)},
    5:  {"CSE":(400,160,88,48),"ECE":(720,288,158,86),"EEE":(1040,416,228,124),"MECH":(1360,544,299,163),"CIVIL":(1680,672,369,201)},
    6:  {"CSE":(480,192,105,57),"ECE":(864,345,190,103),"EEE":(1248,499,274,149),"MECH":(1632,652,359,195),"CIVIL":(2016,806,443,241)},
    7:  {"CSE":(560,224,123,67),"ECE":(1008,403,221,120),"EEE":(1456,582,320,174),"MECH":(1904,761,418,228),"CIVIL":(2352,940,517,282)},
    8:  {"CSE":(2400,960,528,288),"ECE":(4320,1728,950,518),"EEE":(6240,2496,1372,748),"MECH":(8160,3264,1795,979),"CIVIL":(10080,4032,2217,1209)},
    9:  {"CSE":(2700,1080,594,324),"ECE":(4860,1944,1069,583),"EEE":(7020,2808,1544,842),"MECH":(9180,3672,2019,1101),"CIVIL":(11340,4536,2494,1360)},
    10: {"CSE":(3000,1200,660,360),"ECE":(5400,2160,1188,648),"EEE":(7800,3120,1716,936),"MECH":(10200,4080,2244,1224),"CIVIL":(12600,5040,2772,1512)},
    11: {"CSE":(3300,1320,726,396),"ECE":(5940,2376,1306,712),"EEE":(8580,3432,1887,1029),"MECH":(11220,4488,2468,1346),"CIVIL":(13860,5544,3049,1663)},
    12: {"CSE":(3600,1440,792,432),"ECE":(6480,2592,1425,777),"EEE":(9360,3744,2059,1123),"MECH":(12240,4896,2692,1468),"CIVIL":(15120,6048,3326,1814)},
    13: {"CSE":(3900,1560,858,468),"ECE":(7020,2808,1544,842),"EEE":(10140,4056,2230,1216),"MECH":(13260,5304,2917,1591),"CIVIL":(16380,6552,3603,1965)},
    14: {"CSE":(4200,1680,924,504),"ECE":(7560,3024,1663,907),"EEE":(10920,4368,2402,1310),"MECH":(14280,5712,3141,1713),"CIVIL":(17640,7056,3880,2116)},
    15: {"CSE":(4500,1800,990,540),"ECE":(8100,3240,1782,972),"EEE":(11700,4680,2574,1404),"MECH":(15300,6120,3366,1836),"CIVIL":(18900,7560,4158,2268)},
    16: {"CSE":(4000,1600,880,480),"ECE":(7200,2880,1584,864),"EEE":(10400,4160,2288,1248),"MECH":(13600,5440,2992,1632),"CIVIL":(16800,6720,3696,2016)},
    17: {"CSE":(4250,1700,935,510),"ECE":(7650,3060,1683,918),"EEE":(11050,4420,2431,1326),"MECH":(14450,5780,3179,1734),"CIVIL":(17850,7140,3927,2142)},
    18: {"CSE":(4500,1800,990,540),"ECE":(8100,3240,1782,972),"EEE":(11700,4680,2574,1404),"MECH":(15300,6120,3366,1836),"CIVIL":(18900,7560,4158,2268)},
    19: {"CSE":(4750,1900,1045,570),"ECE":(8550,3420,1881,1026),"EEE":(12350,4940,2717,1482),"MECH":(16150,6460,3553,1938),"CIVIL":(19950,7980,4389,2394)},
    20: {"CSE":(5000,2000,1100,600),"ECE":(9000,3600,1980,1080),"EEE":(13000,5200,2860,1560),"MECH":(17000,6800,3740,2040),"CIVIL":(21000,8400,4620,2520)},
    21: {"CSE":(5250,2100,1155,630),"ECE":(9450,3780,2079,1134),"EEE":(13650,5460,3003,1638),"MECH":(17850,7140,3927,2142),"CIVIL":(22050,8820,4851,2646)},
    22: {"CSE":(5500,2200,1210,660),"ECE":(9900,3960,2178,1188),"EEE":(14300,5720,3146,1716),"MECH":(18700,7480,4114,2244),"CIVIL":(23100,9240,5082,2772)},
    23: {"CSE":(5750,2300,1265,690),"ECE":(10350,4140,2277,1242),"EEE":(14950,5980,3289,1794),"MECH":(19550,7820,4301,2346),"CIVIL":(24150,9660,5313,2898)},
}

IIT_SCH    = "100% tuition fee waiver for SC/ST/PwD and family income < ₹1 LPA; 66% remission for income ₹1–5 LPA; Institute Merit-cum-Means scholarship."
IIT_HIGHER = "World-class research labs; strong MS/PhD pipeline to Stanford, MIT, CMU, ETH Zurich and top global universities."
IIT_ENTRE  = "On-campus incubation cell with seed funding, alumni angel network and startup mentoring."

# ══════════════════════════════════════════════════════════════════════════════
# NIT DATA  (32 NITs × 5 branches = 160 records)
# ══════════════════════════════════════════════════════════════════════════════
NITS = [
    (24, "National Institute of Technology, Trichy",         "Tiruchirappalli, Tamil Nadu",  "NIT Trichy",        "Tier-1"),
    (25, "National Institute of Technology Karnataka, Surathkal","Surathkal, Karnataka",     "NIT Surathkal",     "Tier-1"),
    (26, "National Institute of Technology, Warangal",       "Warangal, Telangana",          "NIT Warangal",      "Tier-1"),
    (27, "Motilal Nehru National Institute of Technology, Allahabad","Prayagraj, Uttar Pradesh","MNNIT Allahabad","Tier-1"),
    (28, "Visvesvaraya National Institute of Technology, Nagpur","Nagpur, Maharashtra",       "VNIT Nagpur",       "Tier-1"),
    (29, "National Institute of Technology, Rourkela",       "Rourkela, Odisha",             "NIT Rourkela",      "Tier-1"),
    (30, "National Institute of Technology, Calicut",        "Kozhikode, Kerala",            "NIT Calicut",       "Tier-1"),
    (31, "Malaviya National Institute of Technology, Jaipur","Jaipur, Rajasthan",            "MNIT Jaipur",       "Tier-1"),
    (32, "Sardar Vallabhbhai National Institute of Technology, Surat","Surat, Gujarat",       "SVNIT Surat",       "Tier-1"),
    (33, "Maulana Azad National Institute of Technology, Bhopal","Bhopal, Madhya Pradesh",   "MANIT Bhopal",      "Tier-1"),
    (34, "National Institute of Technology, Kurukshetra",    "Kurukshetra, Haryana",         "NIT Kurukshetra",   "Tier-1"),
    (35, "Dr. B.R. Ambedkar National Institute of Technology, Jalandhar","Jalandhar, Punjab","NIT Jalandhar",     "Tier-2"),
    (36, "National Institute of Technology, Durgapur",       "Durgapur, West Bengal",        "NIT Durgapur",      "Tier-2"),
    (37, "National Institute of Technology, Jamshedpur",     "Jamshedpur, Jharkhand",        "NIT Jamshedpur",    "Tier-2"),
    (38, "National Institute of Technology, Silchar",        "Silchar, Assam",               "NIT Silchar",       "Tier-2"),
    (39, "National Institute of Technology, Patna",          "Patna, Bihar",                 "NIT Patna",         "Tier-2"),
    (40, "National Institute of Technology, Raipur",         "Raipur, Chhattisgarh",         "NIT Raipur",        "Tier-2"),
    (41, "Indian Institute of Engineering Science and Technology, Shibpur","Shibpur, West Bengal","IIEST Shibpur","Tier-2"),
    (42, "National Institute of Technology, Srinagar",       "Srinagar, J&K",                "NIT Srinagar",      "Tier-2"),
    (43, "National Institute of Technology, Hamirpur",       "Hamirpur, Himachal Pradesh",   "NIT Hamirpur",      "Tier-2"),
    (44, "National Institute of Technology, Uttarakhand",    "Srinagar Garhwal, Uttarakhand","NIT Uttarakhand",   "Tier-2"),
    (45, "National Institute of Technology, Delhi",          "Delhi",                        "NIT Delhi",         "Tier-2"),
    (46, "National Institute of Technology, Agartala",       "Agartala, Tripura",            "NIT Agartala",      "Tier-2"),
    (47, "National Institute of Technology, Meghalaya",      "Shillong, Meghalaya",          "NIT Meghalaya",     "Tier-2"),
    (48, "National Institute of Technology, Manipur",        "Imphal, Manipur",              "NIT Manipur",       "Tier-2"),
    (49, "National Institute of Technology, Nagaland",       "Dimapur, Nagaland",            "NIT Nagaland",      "Tier-2"),
    (50, "National Institute of Technology, Mizoram",        "Aizawl, Mizoram",              "NIT Mizoram",       "Tier-2"),
    (51, "National Institute of Technology, Arunachal Pradesh","Yupia, Arunachal Pradesh",   "NIT Arunachal",     "Tier-2"),
    (52, "National Institute of Technology, Sikkim",         "Ravangla, Sikkim",             "NIT Sikkim",        "Tier-2"),
    (53, "National Institute of Technology, Andhra Pradesh", "Tadepalligudem, Andhra Pradesh","NIT Andhra Pradesh","Tier-2"),
    (54, "National Institute of Technology, Goa",            "Ponda, Goa",                   "NIT Goa",           "Tier-2"),
    (55, "National Institute of Technology, Puducherry",     "Karaikal, Puducherry",         "NIT Puducherry",    "Tier-2"),
]

NIT_CUTOFFS = {
    24: {"CSE":(900,360,198,108),    "ECE":(1620,648,356,194),    "EEE":(2340,936,514,280),    "MECH":(3060,1224,673,367),   "CIVIL":(3780,1512,831,453)},
    25: {"CSE":(1800,720,396,216),   "ECE":(3240,1296,712,388),   "EEE":(4680,1872,1029,561),  "MECH":(6120,2448,1346,734),  "CIVIL":(7560,3024,1663,907)},
    26: {"CSE":(2700,1080,594,324),  "ECE":(4860,1944,1069,583),  "EEE":(7020,2808,1544,842),  "MECH":(9180,3672,2019,1101), "CIVIL":(11340,4536,2494,1360)},
    27: {"CSE":(4800,1920,1056,576), "ECE":(8640,3456,1900,1036), "EEE":(12480,4992,2745,1497),"MECH":(16320,6528,3590,1958),"CIVIL":(20160,8064,4435,2419)},
    28: {"CSE":(6000,2400,1320,720), "ECE":(10800,4320,2376,1296),"EEE":(15600,6240,3432,1872),"MECH":(20400,8160,4488,2448),"CIVIL":(25200,10080,5544,3024)},
    29: {"CSE":(7200,2880,1584,864), "ECE":(12960,5184,2851,1555),"EEE":(18720,7488,4118,2246),"MECH":(24480,9792,5385,2937),"CIVIL":(30240,12096,6652,3628)},
    30: {"CSE":(8400,3360,1848,1008),"ECE":(15120,6048,3326,1814),"EEE":(21840,8736,4804,2620),"MECH":(28560,11424,6283,3427),"CIVIL":(35280,14112,7761,4233)},
    31: {"CSE":(9600,3840,2112,1152),"ECE":(17280,6912,3801,2073),"EEE":(24960,9984,5491,2995),"MECH":(32640,13056,7180,3916),"CIVIL":(40320,16128,8870,4838)},
    32: {"CSE":(10800,4320,2376,1296),"ECE":(19440,7776,4276,2332),"EEE":(28080,11232,6177,3369),"MECH":(36720,14688,8078,4406),"CIVIL":(45360,18144,9979,5443)},
    33: {"CSE":(12000,4800,2640,1440),"ECE":(21600,8640,4752,2592),"EEE":(31200,12480,6864,3744),"MECH":(40800,16320,8976,4896),"CIVIL":(50400,20160,11088,6048)},
    34: {"CSE":(13200,5280,2904,1584),"ECE":(23760,9504,5227,2851),"EEE":(34320,13728,7550,4118),"MECH":(44880,17952,9873,5385),"CIVIL":(55440,22176,12196,6652)},
    35: {"CSE":(14400,5760,3168,1728),"ECE":(25920,10368,5702,3110),"EEE":(37440,14976,8236,4492),"MECH":(48960,19584,10771,5875),"CIVIL":(60480,24192,13305,7257)},
    36: {"CSE":(15600,6240,3432,1872),"ECE":(28080,11232,6177,3369),"EEE":(40560,16224,8923,4867),"MECH":(53040,21216,11668,6364),"CIVIL":(65520,26208,14414,7862)},
    37: {"CSE":(16800,6720,3696,2016),"ECE":(30240,12096,6652,3628),"EEE":(43680,17472,9609,5241),"MECH":(57120,22848,12566,6854),"CIVIL":(70560,28224,15523,8467)},
    38: {"CSE":(18000,7200,3960,2160),"ECE":(32400,12960,7128,3888),"EEE":(46800,18720,10296,5616),"MECH":(61200,24480,13464,7344),"CIVIL":(75600,30240,16632,9072)},
    39: {"CSE":(19200,7680,4224,2304),"ECE":(34560,13824,7603,4147),"EEE":(49920,19968,10982,5990),"MECH":(65280,26112,14361,7833),"CIVIL":(80640,32256,17740,9676)},
    40: {"CSE":(20400,8160,4488,2448),"ECE":(36720,14688,8078,4406),"EEE":(53040,21216,11668,6364),"MECH":(69360,27744,15259,8323),"CIVIL":(85680,34272,18849,10281)},
    41: {"CSE":(21600,8640,4752,2592),"ECE":(38880,15552,8553,4665),"EEE":(56160,22464,12355,6739),"MECH":(73440,29376,16156,8812),"CIVIL":(90720,36288,19958,10886)},
    42: {"CSE":(22800,9120,5016,2736),"ECE":(41040,16416,9028,4924),"EEE":(59280,23712,13041,7113),"MECH":(77520,31008,17054,9302),"CIVIL":(95760,38304,21067,11491)},
    43: {"CSE":(24000,9600,5280,2880),"ECE":(43200,17280,9504,5184),"EEE":(62400,24960,13728,7488),"MECH":(81600,32640,17952,9792),"CIVIL":(100800,40320,22176,12096)},
    44: {"CSE":(25200,10080,5544,3024),"ECE":(45360,18144,9979,5443),"EEE":(65520,26208,14414,7862),"MECH":(85680,34272,18849,10281),"CIVIL":(105840,42336,23284,12700)},
    45: {"CSE":(26400,10560,5808,3168),"ECE":(47520,19008,10454,5702),"EEE":(68640,27456,15100,8236),"MECH":(89760,35904,19747,10771),"CIVIL":(110880,44352,24393,13305)},
    46: {"CSE":(27600,11040,6072,3312),"ECE":(49680,19872,10929,5961),"EEE":(71760,28704,15787,8611),"MECH":(93840,37536,20644,11260),"CIVIL":(115920,46368,25502,13910)},
    47: {"CSE":(28800,11520,6336,3456),"ECE":(51840,20736,11404,6220),"EEE":(74880,29952,16473,8985),"MECH":(97920,39168,21542,11750),"CIVIL":(120960,48384,26611,14515)},
    48: {"CSE":(30000,12000,6600,3600),"ECE":(54000,21600,11880,6480),"EEE":(78000,31200,17160,9360),"MECH":(102000,40800,22440,12240),"CIVIL":(126000,50400,27720,15120)},
    49: {"CSE":(31200,12480,6864,3744),"ECE":(56160,22464,12355,6739),"EEE":(81120,32448,17846,9734),"MECH":(106080,42432,23337,12729),"CIVIL":(131040,52416,28828,15724)},
    50: {"CSE":(32400,12960,7128,3888),"ECE":(58320,23328,12830,6998),"EEE":(84240,33696,18532,10108),"MECH":(110160,44064,24235,13219),"CIVIL":(136080,54432,29937,16329)},
    51: {"CSE":(33600,13440,7392,4032),"ECE":(60480,24192,13305,7257),"EEE":(87360,34944,19219,10483),"MECH":(114240,45696,25132,13708),"CIVIL":(141120,56448,31046,16934)},
    52: {"CSE":(34800,13920,7656,4176),"ECE":(62640,25056,13780,7516),"EEE":(90480,36192,19905,10857),"MECH":(118320,47328,26030,14198),"CIVIL":(146160,58464,32155,17539)},
    53: {"CSE":(36000,14400,7920,4320),"ECE":(64800,25920,14256,7776),"EEE":(93600,37440,20592,11232),"MECH":(122400,48960,26928,14688),"CIVIL":(151200,60480,33264,18144)},
    54: {"CSE":(37200,14880,8184,4464),"ECE":(66960,26784,14731,8035),"EEE":(96720,38688,21278,11606),"MECH":(126480,50592,27825,15177),"CIVIL":(156240,62496,34372,18748)},
    55: {"CSE":(38400,15360,8448,4608),"ECE":(69120,27648,15206,8294),"EEE":(99840,39936,21964,11980),"MECH":(130560,52224,28723,15667),"CIVIL":(161280,64512,35481,19353)},
}

NIT_SCH    = "100% tuition fee waiver for SC/ST and family income < ₹1 LPA; 66% remission for income ₹1–5 LPA; post-matric and merit-cum-means scholarships."
NIT_HIGHER = "Active research culture; alumni pursuing MS at top US/European universities; strong GATE coaching ecosystem."
NIT_ENTRE  = "Campus incubation center with seed support; annual innovation expos and startup mentoring."

# ── Build IIT records ─────────────────────────────────────────────────────────
iit_records = []
for inst_id, college_name, location, short_name in IITS:
    tier = "Tier-1" if inst_id <= 7 else "Tier-2"
    for branch in ["CSE","ECE","EEE","MECH","CIVIL"]:
        oc,obc,sc,st = IIT_CUTOFFS[inst_id][branch]
        ews = round(oc * 0.75)
        rec = make_record(
            id_=f"IIT{inst_id}-{branch}",
            college_name=college_name,
            branch=branch,
            college_type="IIT",
            exam="JEE Advanced",
            location=location,
            tier=tier,
            tuition=200000,
            hostel_fee=42000,
            scholarships=IIT_SCH,
            higher=IIT_HIGHER,
            entre=IIT_ENTRE,
            general=oc, obc=obc, sc=sc, st=st, ews=ews,
            notes=f"JEE Advanced admission through JoSAA. {short_name} — {BRANCH_LABELS[branch]}."
        )
        iit_records.append(rec)

# ── Build NIT records ─────────────────────────────────────────────────────────
nit_records = []
for inst_id, college_name, location, short_name, tier in NITS:
    for branch in ["CSE","ECE","EEE","MECH","CIVIL"]:
        oc,obc,sc,st = NIT_CUTOFFS[inst_id][branch]
        ews = round(oc * 0.80)
        rec = make_record(
            id_=f"NIT{inst_id}-{branch}",
            college_name=college_name,
            branch=branch,
            college_type="NIT",
            exam="JEE Main",
            location=location,
            tier=tier,
            tuition=125000,
            hostel_fee=36000,
            scholarships=NIT_SCH,
            higher=NIT_HIGHER,
            entre=NIT_ENTRE,
            general=oc, obc=obc, sc=sc, st=st, ews=ews,
            notes=f"JEE Main admission through JoSAA (OS quota). {short_name} — {BRANCH_LABELS[branch]}."
        )
        nit_records.append(rec)

sample_records = iit_records + nit_records
with open(OUT_DIR / "sample_colleges.json", "w", encoding="utf-8") as f:
    json.dump(sample_records, f, indent=2, ensure_ascii=False)
print(f"sample_colleges.json written: {len(iit_records)} IIT + {len(nit_records)} NIT = {len(sample_records)} total")

# ══════════════════════════════════════════════════════════════════════════════
# AP EAPCET DATA  (30 colleges × 8 branches = 240 records)
# Source: CSV provided by user
# ══════════════════════════════════════════════════════════════════════════════
AP_SCH    = "AP government fee reimbursement for SC/ST/BC/EWS students with family income < ₹2.5 LPA; college-specific merit scholarships."
AP_HIGHER = "Research programs at AP universities; alumni in top IT companies and US graduate schools."
AP_ENTRE  = "College innovation cell; startup pitching events and industry collaboration programs."

# (college_name, code, location, tier, tuition, hostel_fee, notes)
AP_COLLEGES = {
    "JNTUK": ("JNTU College of Engineering, Kakinada",                          "Kakinada, Andhra Pradesh",              "Tier-1", 35000,  30000, "Premier JNTU constituent college. Highest ranked AP EAPCET government college."),
    "AUCE":  ("Andhra University College of Engineering, Visakhapatnam",         "Visakhapatnam, Andhra Pradesh",         "Tier-1", 40000,  32000, "Autonomous college under Andhra University; strong research heritage."),
    "SVUCE": ("Sri Venkateswara University College of Engineering, Tirupati",    "Tirupati, Andhra Pradesh",              "Tier-1", 38000,  28000, "One of the oldest engineering colleges in AP; strong alumni in IT sector."),
    "JNTUA": ("JNTU College of Engineering, Anantapur",                          "Anantapur, Andhra Pradesh",             "Tier-2", 35000,  28000, "JNTU Anantapur constituent college; strong in south AP region."),
    "VRSEC": ("VR Siddhartha Engineering College, Vijayawada",                   "Vijayawada, Andhra Pradesh",            "Tier-2", 90000,  55000, "Top private college in Vijayawada; good industry tie-ups."),
    "GMRIT": ("GMR Institute of Technology, Rajam",                              "Rajam, Andhra Pradesh",                 "Tier-2", 100000, 60000, "Industry-backed college with strong GMR Group support."),
    "GVPCE": ("Gayatri Vidya Parishad College of Engineering, Visakhapatnam",   "Visakhapatnam, Andhra Pradesh",         "Tier-2", 85000,  50000, "Established private college in Vizag with consistent placement outcomes."),
    "SRKR":  ("SRKR Engineering College, Bhimavaram",                            "Bhimavaram, Andhra Pradesh",            "Tier-2", 80000,  48000, "Established private college in West Godavari district."),
    "VVIT":  ("Vasireddy Venkatadri Institute of Technology, Guntur",            "Guntur, Andhra Pradesh",                "Tier-2", 85000,  52000, "Growing college in Guntur district with improving placement outcomes."),
    "VITB":  ("Vishnu Institute of Technology, Bhimavaram",                      "Bhimavaram, Andhra Pradesh",            "Tier-2", 90000,  55000, "Vishnu Group institution with consistent placement record."),
    "ANITS": ("Anil Neerukonda Institute of Technology and Sciences, Visakhapatnam","Visakhapatnam, Andhra Pradesh",      "Tier-2", 95000,  58000, "Well-known private college in Vizag with growing placement pipeline."),
    "MITS":  ("Madanapalle Institute of Technology and Science, Madanapalle",   "Madanapalle, Andhra Pradesh",           "Tier-2", 90000,  54000, "Autonomous institution with good research culture."),
    "RVRJC": ("RVR and JC College of Engineering, Guntur",                       "Guntur, Andhra Pradesh",                "Tier-2", 85000,  50000, "Well-established college in Guntur with strong alumni network."),
    "PVPSIT":("Prasad V. Potluri Siddhartha Institute of Technology, Vijayawada","Vijayawada, Andhra Pradesh",            "Tier-2", 92000,  56000, "Reputed private college near Vijayawada with good industry connections."),
    "AEC":   ("Aditya Engineering College, Surampalem",                          "Surampalem, Andhra Pradesh",            "Tier-2", 88000,  52000, "East Godavari district college with steady placement outcomes."),
    "SVEC":  ("Sree Vidyanikethan Engineering College, Tirupati",                "Tirupati, Andhra Pradesh",              "Tier-2", 88000,  52000, "College near Tirupati with good IT placement record."),
    "REC":   ("Raghu Engineering College, Visakhapatnam",                        "Visakhapatnam, Andhra Pradesh",         "Tier-2", 82000,  50000, "Vizag-based private college with growing industry connections."),
    "GPREC": ("G. Pulla Reddy Engineering College, Kurnool",                     "Kurnool, Andhra Pradesh",               "Tier-2", 80000,  48000, "Kurnool region college serving Rayalaseema students."),
    "JNTUV": ("JNTU College of Engineering, Vizianagaram",                       "Vizianagaram, Andhra Pradesh",          "Tier-2", 35000,  28000, "JNTU Vizianagaram constituent college; serves north AP students."),
    "SREC":  ("Santhiram Engineering College, Nandyal",                          "Nandyal, Andhra Pradesh",               "Tier-2", 78000,  46000, "Established college in Kurnool district."),
    "NEC":   ("Narasaraopeta Engineering College, Narasaraopet",                 "Narasaraopet, Andhra Pradesh",          "Tier-2", 76000,  44000, "Palnadu district college with decent regional placement."),
    "PACE":  ("Pace Institute of Technology and Sciences, Ongole",               "Ongole, Andhra Pradesh",                "Tier-2", 76000,  44000, "Prakasam district college serving local students."),
    "SRKIT": ("SRK Institute of Technology, Vijayawada",                         "Vijayawada, Andhra Pradesh",            "Tier-2", 80000,  48000, "Krishna district college near Vijayawada."),
    "LIET":  ("Lendi Institute of Engineering and Technology, Vizianagaram",     "Vizianagaram, Andhra Pradesh",          "Tier-2", 76000,  44000, "North AP college serving Vizianagaram and surrounding areas."),
    "VIIT":  ("Vignan's Institute of Information Technology, Visakhapatnam",     "Visakhapatnam, Andhra Pradesh",         "Tier-2", 88000,  54000, "Vignan Group institution in Vizag with IT focus."),
    "BVCE":  ("Bonam Venkata Chalamayya Engineering College, Odalarevu",         "Odalarevu, Andhra Pradesh",             "Tier-2", 74000,  42000, "East Godavari coastal region college."),
    "GIET":  ("Godavari Institute of Engineering and Technology, Rajahmundry",   "Rajahmundry, Andhra Pradesh",           "Tier-2", 80000,  48000, "East Godavari college with steady local placement."),
    "KITS":  ("Kakatiya Institute of Technology and Science, Warangal",          "Warangal, Telangana",                   "Tier-2", 82000,  50000, "Warangal-based college sometimes accessible for AP EAPCET students."),
    "ASCET": ("Audisankara College of Engineering and Technology, Gudur",        "Gudur, Andhra Pradesh",                 "Tier-2", 76000,  44000, "SPSR Nellore district college."),
    "QIS":   ("QIS College of Engineering and Technology, Ongole",               "Ongole, Andhra Pradesh",                "Tier-2", 74000,  42000, "Prakasam district college with good student intake."),
}

# All 30 colleges × 8 branches cutoff data from the CSV
AP_CUTOFFS = {
    "JNTUK": {"CSE":(927,1454,3769,7153),"ECE":(1240,1961,5068,7485),"EEE":(2177,3199,8811,13401),"MECH":(3079,4454,11880,17259),"CIVIL":(2816,4057,10451,15527),"IT":(1019,1784,4682,6149),"CSM":(1037,1652,4862,7515),"CSD":(1109,1931,4810,6996)},
    "AUCE":  {"CSE":(2429,3801,9285,14802),"ECE":(3703,5672,14285,19841),"EEE":(6157,8935,22397,32354),"MECH":(8879,12640,32556,46958),"CIVIL":(8972,12712,31996,46638),"IT":(3149,4691,12388,17449),"CSM":(2959,4377,11682,15883),"CSD":(3023,4567,11629,16370)},
    "SVUCE": {"CSE":(3993,5730,15040,21565),"ECE":(6621,9685,24579,35869),"EEE":(9985,14374,35643,52367),"MECH":(14835,20892,53099,75641),"CIVIL":(15195,21521,53763,78726),"IT":(5419,7737,19855,28664),"CSM":(4782,7119,18091,25657),"CSD":(4633,6775,17078,24594)},
    "JNTUA": {"CSE":(5743,8276,21318,31633),"ECE":(9249,13379,32944,48492),"EEE":(14125,19962,50483,73118),"MECH":(20925,29477,74210,106402),"CIVIL":(20938,29740,74487,106830),"IT":(7612,11106,27474,40786),"CSM":(6843,10077,24507,35684),"CSD":(6466,9313,23541,33878)},
    "VRSEC": {"CSE":(7033,10054,26050,38096),"ECE":(11790,16973,42087,60385),"EEE":(18135,25744,64377,93486),"MECH":(27129,38314,95597,137187),"CIVIL":(26871,37845,95310,136504),"IT":(9975,14199,36176,52072),"CSM":(8569,12394,30899,44586),"CSD":(8462,12016,30638,44320)},
    "GMRIT": {"CSE":(8646,12590,30809,45993),"ECE":(14156,19996,50688,72107),"EEE":(22148,31323,78628,111870),"MECH":(32997,46490,116599,166943),"CIVIL":(33070,46526,117239,167483),"IT":(11905,17115,42905,60759),"CSM":(10599,15212,38364,54541),"CSD":(10643,15328,38098,54443)},
    "GVPCE": {"CSE":(10350,14811,36886,53679),"ECE":(16701,23850,59849,85978),"EEE":(25934,36663,92049,131035),"MECH":(39059,54836,138097,175000),"CIVIL":(38952,54959,137351,175000),"IT":(14201,20059,50585,73566),"CSM":(12232,17500,44288,63754),"CSD":(12421,17489,44586,63768)},
    "SRKR":  {"CSE":(12050,16979,42789,63152),"ECE":(19485,27536,68942,98543),"EEE":(29923,42282,106199,150776),"MECH":(44843,63254,157947,175000),"CIVIL":(44835,63257,157967,175000),"IT":(16364,23074,58449,83793),"CSM":(14331,20247,50929,73735),"CSD":(14360,20420,51747,73233)},
    "VVIT":  {"CSE":(13676,19632,49113,70792),"ECE":(22002,31267,77826,111827),"EEE":(34143,48232,120382,172612),"MECH":(51064,71820,170000,175000),"CIVIL":(50915,71413,170000,175000),"IT":(18801,26704,66538,96210),"CSM":(16062,22589,56789,82759),"CSD":(16273,22912,57689,82503)},
    "VITB":  {"CSE":(15016,21291,53128,77132),"ECE":(24621,34711,87358,125099),"EEE":(37909,53448,133316,175000),"MECH":(57092,80323,170000,175000),"CIVIL":(57042,80166,170000,175000),"IT":(20749,29485,73562,105470),"CSM":(18066,25602,64209,93099),"CSD":(18223,25639,64969,93453)},
    "ANITS": {"CSE":(16930,23852,59817,86474),"ECE":(27472,38733,97471,140124),"EEE":(41855,58823,147188,175000),"MECH":(63074,88632,170000,175000),"CIVIL":(62893,88292,170000,175000),"IT":(22938,32439,81610,117454),"CSM":(20031,28193,70659,102490),"CSD":(20026,28143,71583,101321)},
    "MITS":  {"CSE":(18585,26240,65717,94757),"ECE":(29948,42273,105536,152510),"EEE":(46005,64536,161685,175000),"MECH":(68801,96620,170000,175000),"CIVIL":(69032,96890,170000,175000),"IT":(25474,36047,90336,129841),"CSM":(21899,30837,77340,111102),"CSD":(21761,30594,77256,111311)},
    "RVRJC": {"CSE":(20077,28238,71534,102027),"ECE":(32329,45385,114249,163621),"EEE":(50057,70450,170000,175000),"MECH":(75060,105225,170000,175000),"CIVIL":(74835,105173,170000,175000),"IT":(27420,38694,96592,140028),"CSM":(23841,33603,84535,121422),"CSD":(23570,33415,83078,119708)},
    "PVPSIT":{"CSE":(23067,32571,82136,116475),"ECE":(37625,52964,132478,175000),"EEE":(58024,81611,170000,175000),"MECH":(87113,122392,170000,175000),"CIVIL":(87141,122380,170000,175000),"IT":(32039,45007,113597,162993),"CSM":(27418,38620,96581,139912),"CSD":(27404,38845,96980,138338)},
    "AEC":   {"CSE":(24739,34878,87705,125126),"ECE":(40467,56928,142342,175000),"EEE":(62124,87208,170000,175000),"MECH":(92928,130225,170000,175000),"CIVIL":(93016,130463,170000,175000),"IT":(34070,48192,119878,172654),"CSM":(29384,41319,104103,148824),"CSD":(29532,41805,104299,149808)},
    "SVEC":  {"CSE":(26204,36842,92291,133955),"ECE":(43053,60450,151743,175000),"EEE":(65989,92782,170000,175000),"MECH":(99020,138793,170000,175000),"CIVIL":(98986,138700,170000,175000),"IT":(36207,51138,127479,175000),"CSM":(31202,43963,110505,158156),"CSD":(31358,44318,111020,158106)},
    "REC":   {"CSE":(27921,39272,99222,142243),"ECE":(45390,63856,159390,175000),"EEE":(70177,98517,170000,175000),"MECH":(105010,145000,170000,175000),"CIVIL":(104927,145000,170000,175000),"IT":(38659,54277,136197,175000),"CSM":(33069,46636,116468,166753),"CSD":(33285,46878,117309,169105)},
    "GPREC": {"CSE":(29516,41536,103830,149931),"ECE":(47998,67501,168829,175000),"EEE":(73835,103864,170000,175000),"MECH":(111128,145000,170000,175000),"CIVIL":(111074,145000,170000,175000),"IT":(40559,57015,142638,175000),"CSM":(35085,49238,123408,175000),"CSD":(35172,49516,124348,175000)},
    "JNTUV": {"CSE":(31160,43947,110180,157847),"ECE":(50559,71079,170000,175000),"EEE":(77897,109285,170000,175000),"MECH":(117023,145000,170000,175000),"CIVIL":(117075,145000,170000,175000),"IT":(43079,60787,151962,175000),"CSM":(37036,52170,130197,175000),"CSD":(37190,52335,131303,175000)},
    "SREC":  {"CSE":(32939,46277,116523,167538),"ECE":(53253,74913,170000,175000),"EEE":(82009,115079,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(45246,63827,159785,175000),"CSM":(39065,55082,137535,175000),"CSD":(39030,54742,137416,175000)},
    "NEC":   {"CSE":(34307,48349,121378,173722),"ECE":(56010,78849,170000,175000),"EEE":(86026,120762,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(47245,66506,166536,175000),"CSM":(40967,57624,143979,175000),"CSD":(41034,57667,144807,175000)},
    "PACE":  {"CSE":(35915,50482,126352,175000),"ECE":(58323,81877,170000,175000),"EEE":(90193,126407,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(49424,69368,170000,175000),"CSM":(42552,60056,150313,175000),"CSD":(42604,60143,150049,175000)},
    "SRKIT": {"CSE":(37490,52942,132245,175000),"ECE":(60925,85680,170000,175000),"EEE":(93862,131739,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(51726,72829,170000,175000),"CSM":(44708,62909,157828,175000),"CSD":(44730,62949,157973,175000)},
    "LIET":  {"CSE":(39380,55475,138790,175000),"ECE":(63884,89663,170000,175000),"EEE":(97941,137609,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(53820,75587,170000,175000),"CSM":(46626,65417,163832,175000),"CSD":(46468,65351,163848,175000)},
    "VIIT":  {"CSE":(40961,57554,143928,175000),"ECE":(66308,93100,170000,175000),"EEE":(102012,142947,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(56291,79201,170000,175000),"CSM":(48253,67834,169690,175000),"CSD":(48449,68142,170000,175000)},
    "BVCE":  {"CSE":(42576,59985,150335,175000),"ECE":(68812,96685,170000,175000),"EEE":(106023,145000,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(58339,81839,170000,175000),"CSM":(50163,70529,170000,175000),"CSD":(50489,70797,170000,175000)},
    "GIET":  {"CSE":(44019,61795,155453,175000),"ECE":(71393,100075,170000,175000),"EEE":(109967,145000,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(60515,84950,170000,175000),"CSM":(52290,73315,170000,175000),"CSD":(52076,73185,170000,175000)},
    "KITS":  {"CSE":(45435,64107,160502,175000),"ECE":(73920,103974,170000,175000),"EEE":(113926,145000,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(62611,87993,170000,175000),"CSM":(54342,76366,170000,175000),"CSD":(54260,76446,170000,175000)},
    "ASCET": {"CSE":(47398,66540,167380,175000),"ECE":(76555,107573,170000,175000),"EEE":(117959,145000,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(65021,91253,170000,175000),"CSM":(56245,78997,170000,175000),"CSD":(56157,78780,170000,175000)},
    "QIS":   {"CSE":(49000,68721,170000,175000),"ECE":(79319,111484,170000,175000),"EEE":(120000,145000,170000,175000),"MECH":(120000,145000,170000,175000),"CIVIL":(120000,145000,170000,175000),"IT":(67135,94451,170000,175000),"CSM":(57840,81451,170000,175000),"CSD":(58083,81554,170000,175000)},
}

AP_PLACEMENT = {
    "CSE":   (7.5, 82.0, ["TCS","Infosys","Wipro","Amazon","Zoho"]),
    "ECE":   (6.0, 75.0, ["Qualcomm","Samsung","TCS","Infosys","BSNL"]),
    "EEE":   (5.0, 68.0, ["APTRANSCO","BHEL","L&T","Siemens","NTPC"]),
    "MECH":  (4.5, 62.0, ["Tata Motors","L&T","BHEL","Ashok Leyland","JSW"]),
    "CIVIL": (4.0, 58.0, ["L&T Construction","NHAI","APSPDCL","Megha Engineering","NCC"]),
    "IT":    (7.0, 80.0, ["TCS","Infosys","Wipro","Tech Mahindra","HCL"]),
    "CSM":   (8.0, 83.0, ["TCS","Infosys","Amazon","Zoho","Freshworks"]),
    "CSD":   (7.5, 81.0, ["TCS","Infosys","Amazon","Flipkart","Walmart Labs"]),
}

def ap_cutoff_block(oc, bca, sc, st):
    cats = {
        "OC":   {"opening_rank": op(oc),  "closing_rank": oc},
        "BC-A": {"opening_rank": op(bca), "closing_rank": bca},
        "SC":   {"opening_rank": op(sc),  "closing_rank": sc},
        "ST":   {"opening_rank": op(st),  "closing_rank": st},
    }
    return {
        "category_cutoffs": {k: {"opening_rank": v["opening_rank"], "closing_rank": v["closing_rank"]} for k,v in cats.items()},
        "cutoff_history": {"2024": {"round": "Final Phase Closing", "categories": cats}}
    }

ap_records = []
for code, (college_name, location, tier, tuition, hostel_fee, notes) in AP_COLLEGES.items():
    for branch in ["CSE","ECE","EEE","MECH","CIVIL","IT","CSM","CSD"]:
        oc, bca, sc, st = AP_CUTOFFS[code][branch]
        lpa, pct, recruiters = AP_PLACEMENT[branch]
        cb = ap_cutoff_block(oc, bca, sc, st)
        rec = {
            "id": f"{code}-{branch}",
            "college_name": college_name,
            "branch_name": BRANCH_LABELS[branch],
            "college_type": "AP EAPCET",
            "exam": "AP EAPCET",
            "location": location,
            "tier_rating": tier,
            "annual_tuition_fee_inr": tuition,
            "hostel_available": True,
            "annual_hostel_fee_inr": hostel_fee,
            "scholarships": AP_SCH,
            "higher_study_opportunities": AP_HIGHER,
            "entrepreneurship_opportunities": AP_ENTRE,
            "cutoff_year_round": "2024 (Final Phase Closing)",
            "typical_roles": BRANCH_ROLES[branch],
            **cb,
            "curriculum_keywords": BRANCH_KEYWORDS[branch],
            "placement_stats": {
                "median_salary_lpa": lpa,
                "placement_percentage": pct,
                "top_recruiters": recruiters,
                "key_career_domains": [BRANCH_LABELS[branch].split()[0], "Engineering", "Technology"],
            },
            "admission_notes": notes,
        }
        ap_records.append(rec)

with open(OUT_DIR / "ap_eapcet_colleges.json", "w", encoding="utf-8") as f:
    json.dump(ap_records, f, indent=2, ensure_ascii=False)
print(f"ap_eapcet_colleges.json written: {len(ap_records)} records ({len(AP_COLLEGES)} colleges × 8 branches)")
print("Done.")
