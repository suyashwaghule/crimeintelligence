#!/usr/bin/env python3
"""
Crime Analysis & Criminal Identification System — Complete Dataset Generator
Generates synthetic relational dataset for Pune, Maharashtra.
Outputs: SQLite DB (.db), CSV files, JSON profiles, GeoJSON hotspots.
Skips: CCTV Surveillance table (as requested).
"""

import os
import random
import sqlite3
import csv
import json
import struct
import time as time_mod
from datetime import datetime, date, timedelta
from collections import defaultdict

random.seed(42)

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_dataset")
FACES_DIR = os.path.join(OUTPUT_DIR, "mock_images", "faces")
DB_DIR = os.path.join(OUTPUT_DIR, "database")
CSV_DIR = os.path.join(OUTPUT_DIR, "csv")
JSON_DIR = os.path.join(OUTPUT_DIR, "json")
GEOJSON_DIR = os.path.join(OUTPUT_DIR, "geojson")

NUM_CRIMES = 20000
NUM_OFFICERS = 300

# ═══════════════════════════════════════════════════════════════════
# DATA POOLS
# ═══════════════════════════════════════════════════════════════════

MALE_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Krishna",
    "Ishaan","Shaurya","Atharva","Advait","Dhruv","Kabir","Arnav","Yash",
    "Om","Dev","Raj","Amit","Rahul","Sunil","Vijay","Anil","Sanjay","Ravi",
    "Prakash","Deepak","Manoj","Suresh","Rajesh","Mukesh","Dinesh","Mahesh",
    "Ganesh","Nilesh","Sachin","Tushar","Vishal","Kunal","Rohan","Nikhil",
    "Siddharth","Akash","Harsh","Gaurav","Varun","Karan","Pranav","Mayank",
    "Manish","Pankaj","Ajay","Naveen","Prashant","Santosh","Ashish","Abhishek",
    "Prateek","Vikram","Sameer","Nishant","Sumit","Mohit","Hitesh","Hemant",
    "Ramesh","Yogesh","Rakesh","Sandip","Pravin","Bharat","Chetan","Durgesh",
    "Girish","Jagdish","Kishore","Lalit","Mohan","Naresh","Omkar","Paresh",
    "Rupesh","Shekhar","Tejas","Umesh","Vinod","Wasim","Zaheer","Imran"
]

FEMALE_NAMES = [
    "Aadhya","Ananya","Diya","Myra","Saanvi","Ira","Avni","Priya","Sunita",
    "Kavita","Neha","Pooja","Swati","Anjali","Rekha","Shweta","Divya","Sneha",
    "Pallavi","Aarti","Kiran","Nisha","Rashmi","Shruti","Deepti","Aparna",
    "Smita","Jyoti","Geeta","Suman","Usha","Vandana","Sarita","Manju","Renu",
    "Asha","Seema","Rita","Anita","Sangeeta","Savita","Padma","Lakshmi",
    "Radha","Sita","Meena","Varsha","Manisha","Archana","Bhavana","Chhaya",
    "Durga","Ekta","Gauri","Hema","Indira","Jayshree","Komal","Madhuri","Nandini"
]

LAST_NAMES = [
    "Patil","Deshmukh","Jadhav","Kulkarni","Shinde","More","Pawar","Chavan",
    "Bhosale","Kadam","Gaikwad","Sawant","Yadav","Joshi","Deshpande","Mane",
    "Kale","Salve","Wagh","Shelke","Ghodke","Nikam","Suryawanshi","Thorat",
    "Khaire","Bhandari","Sharma","Gupta","Singh","Kumar","Verma","Tiwari",
    "Pandey","Dubey","Mishra","Mehta","Shah","Patel","Iyer","Nair","Reddy",
    "Das","Roy","Ghosh","Banerjee","Sen","Bose","Sheikh","Khan","Ansari",
    "Shaikh","Mulani","Pathan","Syed","Qureshi"
]

# Pune areas: (name, lat, lng, pincode, police_station)
PUNE_AREAS = [
    ("Shivajinagar",18.5308,73.8475,411005,"Shivajinagar PS"),
    ("Deccan Gymkhana",18.5185,73.8402,411004,"Deccan PS"),
    ("FC Road",18.5270,73.8410,411004,"Deccan PS"),
    ("JM Road",18.5210,73.8420,411004,"Deccan PS"),
    ("Kothrud",18.5074,73.8077,411038,"Kothrud PS"),
    ("Karvenagar",18.4972,73.8165,411052,"Kothrud PS"),
    ("Warje",18.4887,73.8028,411058,"Warje Malwadi PS"),
    ("Bavdhan",18.5128,73.7800,411021,"Warje Malwadi PS"),
    ("Sinhagad Road",18.4750,73.8200,411041,"Sinhagad Road PS"),
    ("Vadgaon Budruk",18.4780,73.8100,411041,"Sinhagad Road PS"),
    ("Dhayari",18.4600,73.8050,411041,"Sinhagad Road PS"),
    ("Katraj",18.4577,73.8553,411046,"Bharati Vidyapeeth PS"),
    ("Dhankawadi",18.4620,73.8480,411043,"Bharati Vidyapeeth PS"),
    ("Bharati Vidyapeeth",18.4570,73.8500,411046,"Bharati Vidyapeeth PS"),
    ("Bibvewadi",18.4810,73.8630,411037,"Bibvewadi PS"),
    ("Sahakarnagar",18.4750,73.8550,411009,"Sahakarnagar PS"),
    ("Parvati",18.4960,73.8510,411009,"Dattawadi PS"),
    ("Dattawadi",18.5000,73.8430,411030,"Dattawadi PS"),
    ("Sadashiv Peth",18.5100,73.8500,411030,"Vishrambaug PS"),
    ("Narayan Peth",18.5120,73.8530,411030,"Vishrambaug PS"),
    ("Tilak Road",18.5080,73.8490,411030,"Vishrambaug PS"),
    ("Budhwar Peth",18.5160,73.8570,411002,"Khadak PS"),
    ("Raviwar Peth",18.5140,73.8560,411002,"Khadak PS"),
    ("Laxmi Road",18.5130,73.8555,411002,"Khadak PS"),
    ("Kasba Peth",18.5170,73.8590,411011,"Faraskhana PS"),
    ("Somwar Peth",18.5180,73.8580,411011,"Faraskhana PS"),
    ("Shukrawar Peth",18.5150,73.8565,411002,"Faraskhana PS"),
    ("Swargate",18.5015,73.8625,411042,"Swargate PS"),
    ("Market Yard",18.4980,73.8680,411037,"Swargate PS"),
    ("Camp",18.5130,73.8800,411001,"Lashkar PS"),
    ("MG Road",18.5140,73.8780,411001,"Lashkar PS"),
    ("East Street",18.5160,73.8820,411001,"Lashkar PS"),
    ("Koregaon Park",18.5362,73.8930,411001,"Koregaon Park PS"),
    ("Boat Club Road",18.5320,73.8870,411001,"Koregaon Park PS"),
    ("Bund Garden",18.5340,73.8810,411001,"Bundgarden PS"),
    ("Pune Station",18.5285,73.8743,411001,"Bundgarden PS"),
    ("Yerawada",18.5580,73.8830,411006,"Yerawada PS"),
    ("Kalyani Nagar",18.5470,73.9020,411006,"Yerawada PS"),
    ("Aundh",18.5590,73.8070,411007,"Chaturshrungi PS"),
    ("Baner",18.5596,73.7870,411045,"Chaturshrungi PS"),
    ("Balewadi",18.5690,73.7750,411045,"Chaturshrungi PS"),
    ("Pashan",18.5380,73.7930,411021,"Chatushrungi PS"),
    ("Sus",18.5430,73.7600,411021,"Chatushrungi PS"),
    ("Hinjewadi",18.5913,73.7389,411057,"Hinjewadi PS"),
    ("Wakad",18.5990,73.7620,411057,"Hinjewadi PS"),
    ("Pimple Saudagar",18.5940,73.7820,411027,"Sangvi PS"),
    ("Pimple Nilakh",18.5830,73.7980,411027,"Sangvi PS"),
    ("Sangvi",18.5780,73.8100,411027,"Sangvi PS"),
    ("Dapodi",18.5670,73.8270,411012,"Pimpri PS"),
    ("Pimpri",18.6230,73.7960,411018,"Pimpri PS"),
    ("Chinchwad",18.6298,73.7997,411019,"Chinchwad PS"),
    ("Akurdi",18.6420,73.7860,411035,"Chinchwad PS"),
    ("Pradhikaran",18.6350,73.7730,411044,"Chinchwad PS"),
    ("Nigdi",18.6510,73.7700,411044,"Nigdi PS"),
    ("Bhosari",18.6330,73.8300,411039,"Nigdi PS"),
    ("Khadki",18.5580,73.8400,411003,"Vishrantwadi PS"),
    ("Vishrantwadi",18.5670,73.8550,411015,"Vishrantwadi PS"),
    ("Range Hills",18.5620,73.8350,411007,"Vishrantwadi PS"),
    ("Viman Nagar",18.5679,73.9143,411014,"Viman Nagar PS"),
    ("Dhanori",18.5780,73.9050,411015,"Viman Nagar PS"),
    ("Lohegaon",18.5920,73.9190,411032,"Viman Nagar PS"),
    ("Hadapsar",18.5089,73.9260,411028,"Hadapsar PS"),
    ("Magarpatta",18.5150,73.9270,411028,"Hadapsar PS"),
    ("Fursungi",18.4820,73.9350,412308,"Hadapsar PS"),
    ("Mundhwa",18.5340,73.9220,411036,"Mundhwa PS"),
    ("Keshav Nagar",18.5280,73.9340,411036,"Mundhwa PS"),
    ("Kharadi",18.5530,73.9380,411014,"Chandannagar PS"),
    ("Chandan Nagar",18.5580,73.9300,411014,"Chandannagar PS"),
    ("Kondhwa",18.4637,73.8803,411048,"Kondhwa PS"),
    ("NIBM",18.4650,73.8900,411048,"Kondhwa PS"),
    ("Undri",18.4510,73.8950,411060,"Kondhwa PS"),
    ("Wanowrie",18.4890,73.8880,411040,"Wanowrie PS"),
    ("Wagholi",18.5780,73.9630,412207,"Wagholi PS"),
    ("Wadgaon Sheri",18.5470,73.9180,411014,"Chandannagar PS"),
    ("Ambegaon",18.4440,73.8520,411046,"Bharati Vidyapeeth PS"),
    ("Nanded",18.4490,73.8390,411041,"Sinhagad Road PS"),
    ("Senapati Bapat Road",18.5250,73.8300,411016,"Deccan PS"),
    ("University Road",18.5280,73.8260,411007,"Shivajinagar PS"),
    ("Model Colony",18.5260,73.8350,411016,"Shivajinagar PS"),
    ("Law College Road",18.5200,73.8370,411004,"Deccan PS"),
    ("Erandwane",18.5100,73.8300,411004,"Deccan PS"),
    ("Tathawade",18.6060,73.7480,411033,"Hinjewadi PS"),
    ("Ravet",18.6450,73.7570,412101,"Nigdi PS"),
    ("Dehu Road",18.6750,73.7580,412101,"Dehu Road PS"),
    ("Talegaon",18.7260,73.6760,410507,"Talegaon PS"),
    ("Alandi",18.6770,73.8960,412105,"Alandi PS"),
    ("Chakan",18.7610,73.8630,410501,"Chakan PS"),
    ("Lonavala",18.7481,73.4072,410401,"Lonavala PS"),
    ("Saswad",18.3450,74.0320,412301,"Saswad PS"),
    ("Bopodi",18.5620,73.8280,411020,"Vishrantwadi PS"),
    ("Kondhwa Budruk",18.4600,73.8850,411048,"Kondhwa PS"),
    ("Upper Indira Nagar",18.4830,73.8680,411037,"Bibvewadi PS"),
    ("Padmavati",18.4770,73.8520,411009,"Sahakarnagar PS"),
    ("Prabhat Road",18.5160,73.8350,411004,"Deccan PS"),
    ("Ganeshkhind",18.5350,73.8300,411007,"Shivajinagar PS"),
    ("Gokhale Nagar",18.5300,73.8350,411016,"Shivajinagar PS"),
    ("Bhusari Colony",18.5050,73.8130,411038,"Kothrud PS"),
    ("Mayur Colony",18.5010,73.8200,411038,"Kothrud PS"),
    ("Dahanukar Colony",18.5070,73.8250,411029,"Kothrud PS"),
    ("Sassoon Road",18.5240,73.8700,411001,"Bundgarden PS"),
    ("Maan",18.5600,73.7400,411057,"Hinjewadi PS"),
    ("Lavale",18.5100,73.7100,411042,"Chatushrungi PS"),
    ("Manjri",18.5050,73.9500,412307,"Hadapsar PS"),
    ("Phursungi",18.4750,73.9420,412308,"Hadapsar PS"),
    ("Loni Kalbhor",18.4600,73.9600,412201,"Hadapsar PS"),
    ("Uruli Kanchan",18.4700,73.9800,412202,"Hadapsar PS"),
    ("Handewadi",18.4570,73.9280,411028,"Hadapsar PS"),
    ("Mohammadwadi",18.4680,73.9080,411060,"Kondhwa PS"),
    ("Pisoli",18.4380,73.9100,411060,"Kondhwa PS"),
    ("Yerwada",18.5530,73.8780,411006,"Yerawada PS"),
]

CRIME_TYPES = {
    "Theft": ["Chain Snatching","Pickpocketing","Shoplifting","Vehicle Theft",
              "Home Burglary","Mobile Theft","Bicycle Theft","Laptop Theft"],
    "Robbery": ["Armed Robbery","Bank Robbery","Highway Robbery","Store Robbery",
                "Home Invasion","ATM Robbery"],
    "Murder": ["Contract Killing","Crime of Passion","Gang Violence",
               "Domestic Dispute","Honor Killing"],
    "Assault": ["Physical Assault","Domestic Violence","Road Rage",
                "Aggravated Assault","Bar Fight"],
    "Cybercrime": ["Online Fraud","Hacking","Identity Theft","Phishing",
                   "Ransomware","UPI Fraud"],
    "Fraud": ["Financial Fraud","Insurance Fraud","Property Fraud","Forgery",
              "Cheque Bounce","Investment Scam"],
    "Drug Offense": ["Drug Trafficking","Drug Possession","Drug Manufacturing"],
    "Sexual Offense": ["Harassment","Stalking","Molestation","Eve Teasing"],
    "Kidnapping": ["Ransom Kidnapping","Child Abduction","Elopement"],
    "Extortion": ["Threatening","Protection Racket","Blackmail","Land Grabbing"]
}

WEAPONS = ["Knife","Pistol","Iron Rod","Machete","Cricket Bat","Chain",
           "Sword","Axe","Hammer","None","None","None","None"]

ENTRY_METHODS = ["Door break","Window break","Lock picking","Key duplication",
                 "Roof entry","Wall breach","Front door","Back door",
                 "Fire escape","Not applicable"]

TARGET_TYPES = ["House","Bank","Shop","Vehicle","Office","Mall","Hotel",
                "Restaurant","ATM","Jewelry Store","Warehouse","Person",
                "Street","Park","Highway"]

INJURY_LEVELS = ["None","None","Minor","Minor","Moderate","Severe","Fatal"]

EVIDENCE_POOL = ["Fingerprint found","Weapon recovered","CCTV footage available",
                 "Blood sample collected","DNA evidence","Eyewitness statement",
                 "Mobile phone records","Vehicle registration traced",
                 "Footprint analysis","Tool marks found","Digital evidence","None"]

CASE_STATUSES = ["Solved","Solved","Under Investigation","Under Investigation",
                 "Unsolved","Closed"]

BLOOD_GROUPS = ["A+","A-","B+","B-","O+","O-","AB+","AB-"]
RELIGIONS = ["Hindu","Hindu","Hindu","Muslim","Buddhist","Christian","Jain","Sikh"]
MARITAL = ["Single","Married","Married","Divorced","Widowed"]

EDUCATION = ["No Formal Education","Primary School","Secondary School",
             "Higher Secondary","Graduate","Post Graduate","Diploma","ITI"]

OCCUPATIONS = ["Unemployed","Daily Wage Worker","Auto Driver","Truck Driver",
               "Shop Owner","Factory Worker","Mechanic","Street Vendor","Farmer",
               "Construction Worker","Security Guard","Delivery Agent",
               "Scrap Dealer","Electrician","Plumber","Painter","Tailor",
               "Cook","Waiter","IT Professional","Business","Student"]

GANG_NAMES = ["Tiger Gang","Black Shadow","Red Hand","Snake Eyes","Iron Fist",
              "Night Wolves","Dark Angels","Silver Hawks","Blood Brothers",
              "Steel Vipers","Scorpion Crew","Ghost Riders","Shadow Syndicate",
              "Cobra Unit","Fire Eagles","Wagh Mandali","Shinde Group",
              "Patil Toli","Dhole Patti Gang","Vishrantwadi Boys"]

GANG_ROLES = ["Leader","Lieutenant","Member","Associate","Enforcer",
              "Lookout","Driver","Weapons Handler"]

EYE_COLORS = ["Brown","Dark Brown","Black","Hazel"]
HAIR_COLORS = ["Black","Dark Brown","Brown","Grey","Bald"]

BODY_MARKS = [
    "Scar on left cheek","Tattoo on right forearm","Burn mark on left hand",
    "Mole near right eye","Tattoo on chest","Scar on forehead",
    "Tattoo on neck","Birthmark on back","Scar on right arm",
    "Tattoo of snake on shoulder","Knife scar on abdomen",
    "Bullet wound scar on leg",None,None,None,None,None,None
]

BAIL_STATUSES = ["On Bail","Bail Denied","Not Applicable","Released"]

CRIMINAL_CATEGORIES = ["Violent","Non-violent","White Collar",
                       "Organized Crime","Habitual Offender"]

RISK_LEVELS = ["Low","Low","Medium","Medium","High","Critical"]

NICKNAMES_POOL = [
    "Chhota","Bada","Tiger","Scorpion","Shadow","Langda","Kala","Gora",
    "Dabang","Dada","Bhai","Don","Cobra","Bullet","Chain","Wrestler",
    "Boxer","Hawk","Eagle","Motu","Lucky","Angry","Devil","Ghost",
    "Rocket","Sultan","King","Prince","Boss","Captain",
    None,None,None,None,None,None,None,None,None,None
]

OFFICER_RANKS = ["Inspector","Sub-Inspector","Assistant Sub-Inspector",
                 "Head Constable","Police Constable","Senior Inspector",
                 "ACP","DCP"]

SPECIALIZATIONS = ["General Duty","Cybercrime","Homicide","Narcotics",
                   "Anti-Terrorism","Traffic","Women & Child Safety",
                   "Economic Offenses","Organized Crime","Intelligence"]

ESCAPE_METHODS = ["Bike escape","Car escape","On foot","Auto rickshaw",
                  "Bus","Train","Hiding in crowd","Through lanes","Taxi"]

TARGET_SELECTIONS = ["Jewelry shops","Banks","Isolated houses","ATMs",
                     "Women walking alone","Elderly people","Parked vehicles",
                     "Construction sites","Offices after hours","Street vendors",
                     "IT parks","College students","Festival crowds"]

CRIME_TIMINGS = ["Late night (11PM-3AM)","Early morning (3AM-6AM)",
                 "Morning (6AM-10AM)","Afternoon (12PM-3PM)",
                 "Evening (6PM-9PM)","Midnight","Dawn","Dusk"]

DRESS_PATTERNS = ["Black hoodie","Face mask and cap","Formal attire",
                  "Casual clothes","Uniform disguise","Sports wear",
                  "Workman overalls","Helmet and visor","Dark clothing"]

COMM_METHODS = ["Prepaid SIM","WhatsApp","Signal","Face to face",
                "Coded language","Telegram","Hand signals"]

VEHICLES = ["Motorcycle","Car","Auto rickshaw","Stolen vehicle",
            "Bicycle","Truck","On foot","Tempo","Van","SUV"]

PLANNING_LEVELS = ["Highly Planned","Moderately Planned","Impulsive",
                   "Opportunistic","Professional"]

TECH_USED = ["GPS tracker","Hacking tools","Signal jammer","Night vision",
             "Lock pick set","Skeleton keys","Fake documents","None","None","None"]

CAPTURE_ANGLES = ["Front","Left Profile","Right Profile","45-degree Left",
                  "45-degree Right","Overhead"]

LIGHTING_CONDS = ["Bright","Normal","Low light","Artificial","Natural daylight"]
EXPRESSIONS = ["Neutral","Angry","Smiling","Serious","Fearful"]
SOURCE_TYPES = ["CCTV","Manual Upload","Arrest Photo","Surveillance","Social Media"]

JAILS = ["Yerawada Central Jail","Pune District Jail","Kolhapur Jail",
         "Nashik Road Central Jail","Taloja Central Jail","Arthur Road Jail"]

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def rphone():
    return f"+91{random.choice('6789')}{random.randint(100000000,999999999)}"

def raadhaar():
    return f"{random.randint(2000,9999)}{random.randint(1000,9999)}{random.randint(1000,9999)}"

def rpassport():
    return f"{random.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{random.randint(1000000,9999999)}"

def remail(first, last):
    doms = ["gmail.com","yahoo.com","hotmail.com","rediffmail.com","outlook.com"]
    return f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{random.choice(doms)}"

def rdate(sy=2022, ey=2025):
    s = date(sy,1,1); d = (date(ey,12,31)-s).days
    return s + timedelta(days=random.randint(0,d))

def rtime():
    return f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

def rdob(age):
    return date(2025-age, random.randint(1,12), random.randint(1,28))

def jitter(v, a=0.005):
    return round(v + random.uniform(-a,a), 6)

def raddress(area, pin):
    st = random.choice(["Main Road","Lane","Galli","Chowk","Nagar","Colony",
                         "Society","Apartments","Complex","Residency"])
    nm = random.choice(["Ganesh","Shivaji","Tilak","Nehru","Gandhi","Patel",
                         "Laxmi","Krishna","Sai","Ambedkar","Phule","Chhatrapati"])
    return f"{random.randint(1,500)}, {nm} {st}, {area}, Pune - {pin}"

def face_enc_bytes():
    return struct.pack('128f', *[random.gauss(0,0.3) for _ in range(128)])

def crime_desc(ctype, sub, area, target, tm):
    t = random.choice([
        f"A case of {sub} was reported at {area} at approximately {tm}. The suspect targeted a {target}. Local residents alerted police after noticing suspicious activity.",
        f"An incident of {ctype} ({sub}) occurred near {area}. The accused entered the {target} and committed the offense before fleeing the scene.",
        f"Police received a complaint regarding {sub} at {target} in {area} at {tm}. Investigation initiated and local CCTV footage is being examined.",
        f"A {ctype} case involving {sub} was registered at {area}. The victim reported the incident. Forensic team dispatched to the site.",
        f"Suspect(s) committed {sub} at a {target} in {area} during {tm}. Officers responded within minutes of the alert.",
    ])
    return t

def inv_notes(status, cctv):
    cn = "CCTV footage secured" if cctv else "No CCTV coverage at location"
    if status == "Solved":
        return f"Case solved. {cn}. Accused arrested. Evidence submitted to court."
    elif status == "Under Investigation":
        return f"Investigation ongoing. {cn}. Witness statements being recorded. Forensic reports awaited."
    elif status == "Closed":
        return f"Case closed — insufficient evidence. {cn}. All leads exhausted."
    return f"Case unsolved. {cn}. Special team assigned for re-investigation."

def crime_method_text(ctype, weapon, entry):
    m = {
        "Theft": f"Suspect gained entry via {entry} and stole valuables. Operated swiftly.",
        "Robbery": f"Armed with {weapon}, suspect threatened victims and demanded valuables via {entry}.",
        "Murder": f"Victim attacked with {weapon}. Fatal injuries sustained. Scene secured for forensics.",
        "Cybercrime": f"Digital means used to commit fraud. Traced through IP analysis and transaction records.",
        "Fraud": f"Fraudulent documents used. Financial transactions routed through multiple accounts.",
    }
    return m.get(ctype, f"Offense committed using {weapon}. Entry via {entry}. Under investigation.")

def prison_hist(conv):
    if conv == 0: return "No prior convictions"
    entries = []
    for _ in range(min(conv,3)):
        yr = random.randint(2010,2022); yrs = random.randint(1,5)
        entries.append(f"{random.choice(JAILS)} ({yrs}yr for {random.choice(list(CRIME_TYPES.keys()))}, {yr}-{yr+yrs})")
    return "; ".join(entries)

def crime_style_text(ctype, weapon):
    return random.choice([
        f"Operates during nighttime. Uses {weapon}. Targets isolated locations.",
        f"Works with accomplices. Uses stolen vehicles. Specializes in {ctype}.",
        f"Solo operator. Methodical planning. Avoids CCTV areas. Uses disguises.",
        f"Opportunistic. Strikes during festivals and crowded events. Blends in.",
        f"Tech-savvy offender. Uses digital tools. Known for {ctype} operations.",
    ])


# ═══════════════════════════════════════════════════════════════════
# SCAN EXISTING FACE IMAGES
# ═══════════════════════════════════════════════════════════════════

def scan_faces():
    """Scan faces directory and group images by criminal_id."""
    crim_images = defaultdict(list)
    if not os.path.exists(FACES_DIR):
        print(f"  [!] Faces directory not found: {FACES_DIR}")
        print(f"      Generating synthetic image paths instead.")
        return crim_images, False

    files = [f for f in os.listdir(FACES_DIR) if f.lower().endswith(('.jpg','.jpeg'))]
    for f in files:
        # Format: CRM-IND-XXXXX_mugshot.jpg or CRM-IND-XXXXX_face_N.jpg
        parts = f.split('_', 2)  # ['CRM-IND-XXXXX', 'mugshot.jpg'] or ['CRM-IND-XXXXX', 'face', 'N.jpg']
        if len(parts) >= 2:
            cid = parts[0]  # CRM-IND-XXXXX
            crim_images[cid].append(f)

    for cid in crim_images:
        crim_images[cid].sort()

    return crim_images, True


# ═══════════════════════════════════════════════════════════════════
# GENERATORS
# ═══════════════════════════════════════════════════════════════════

def gen_police_officers(num):
    print(f"  [*] Generating {num} police officers...")
    stations = list(set(a[4] for a in PUNE_AREAS))
    officers = []
    for i in range(1, num+1):
        gender = random.choice(["Male","Male","Male","Female"])
        first = random.choice(MALE_NAMES if gender == "Male" else FEMALE_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        station = random.choice(stations)
        # Find an area for this station
        station_areas = [a[0] for a in PUNE_AREAS if a[4] == station]
        rank = random.choice(OFFICER_RANKS)
        officers.append({
            "officer_id": f"PO-{i:04d}",
            "officer_name": name,
            "rank": rank,
            "badge_number": f"MH-PUN-{random.randint(10000,99999)}",
            "phone_number": rphone(),
            "email": remail(first, last),
            "police_station": station,
            "assigned_area": random.choice(station_areas),
            "solved_cases": random.randint(5,200),
            "active_cases": random.randint(0,25),
            "specialization": random.choice(SPECIALIZATIONS),
            "duty_status": random.choices(["Active","Off Duty","On Leave"],
                                          weights=[80,15,5])[0],
        })
    return officers


def gen_criminal_records(crim_images, has_real_images):
    """Generate criminal records. If images exist, use actual criminal IDs from files."""
    if has_real_images and crim_images:
        criminal_ids = sorted(crim_images.keys())
    else:
        criminal_ids = [f"CRM-IND-{i:05d}" for i in range(1, 5750)]

    num = len(criminal_ids)
    print(f"  [*] Generating {num} criminal records...")
    criminals = []

    for idx, cid in enumerate(criminal_ids):
        gender = random.choices(["Male","Female"], weights=[85,15])[0]
        first = random.choice(MALE_NAMES if gender == "Male" else FEMALE_NAMES)
        last = random.choice(LAST_NAMES)
        age = random.randint(18, 65)
        area_data = random.choice(PUNE_AREAS)
        area_name, lat, lng, pin, ps = area_data

        arrest_c = random.randint(1, 15)
        conv_c = random.randint(0, arrest_c)
        common_crime = random.choice(list(CRIME_TYPES.keys()))
        weapon = random.choice(WEAPONS)
        nickname = random.choice(NICKNAMES_POOL)
        is_gang = random.random() < 0.2

        # Image paths
        if has_real_images and cid in crim_images:
            imgs = crim_images[cid]
            mugshot = f"mock_images/faces/{cid}_mugshot.jpg"
            face_img = f"mock_images/faces/{imgs[0]}"
        else:
            mugshot = f"mock_images/faces/{cid}_mugshot.jpg"
            face_img = f"mock_images/faces/{cid}_face_1.jpg"

        criminals.append({
            "criminal_id": cid,
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}",
            "nickname": nickname if nickname else "",
            "gender": gender,
            "age": age,
            "dob": rdob(age).isoformat(),
            "blood_group": random.choice(BLOOD_GROUPS),
            "nationality": "Indian",
            "religion": random.choice(RELIGIONS),
            "marital_status": random.choice(MARITAL),
            "phone_number": rphone(),
            "email": remail(first, last),
            "aadhaar_number": raadhaar(),
            "passport_number": rpassport() if random.random() < 0.3 else "",
            "address": raddress(area_name, pin),
            "area_name": area_name,
            "city": "Pune",
            "state": "Maharashtra",
            "pincode": pin,
            "latitude": jitter(lat),
            "longitude": jitter(lng),
            "gang_name": random.choice(GANG_NAMES) if is_gang else "",
            "gang_role": random.choice(GANG_ROLES) if is_gang else "",
            "education_level": random.choice(EDUCATION),
            "occupation": random.choice(OCCUPATIONS),
            "criminal_category": random.choice(CRIMINAL_CATEGORIES),
            "risk_level": random.choice(RISK_LEVELS),
            "fingerprint_id": f"FP-{cid.split('-')[-1]}",
            "dna_profile_id": f"DNA-{cid.split('-')[-1]}",
            "eye_color": random.choice(EYE_COLORS),
            "hair_color": random.choice(HAIR_COLORS),
            "height_cm": round(random.gauss(170, 10), 1),
            "weight_kg": round(random.gauss(70, 12), 1),
            "body_marks": random.choice(BODY_MARKS) or "",
            "face_image_path": face_img,
            "mugshot_image": mugshot,
            "last_known_location": area_name,
            "last_seen_date": rdate(2024,2025).isoformat(),
            "arrest_count": arrest_c,
            "conviction_count": conv_c,
            "prison_history": prison_hist(conv_c),
            "bail_status": random.choice(BAIL_STATUSES),
            "most_common_crime": common_crime,
            "crime_style": crime_style_text(common_crime, weapon),
            "preferred_weapon": weapon,
            "active_status": random.choices([1,0], weights=[60,40])[0],
            "wanted_status": random.choices([1,0], weights=[25,75])[0],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        if (idx+1) % 1000 == 0:
            print(f"      ...{idx+1}/{num} criminals generated")

    return criminals


def gen_crime_records(criminals, officers, num_crimes):
    print(f"  [*] Generating {num_crimes} crime records...")
    # Build lookup: station -> list of officer names
    station_officers = defaultdict(list)
    for o in officers:
        station_officers[o["police_station"]].append(o["officer_name"])

    all_stations = list(station_officers.keys())
    criminal_ids = [c["criminal_id"] for c in criminals]
    crimes = []
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    months = ["January","February","March","April","May","June","July",
              "August","September","October","November","December"]

    for i in range(1, num_crimes+1):
        ctype = random.choice(list(CRIME_TYPES.keys()))
        subtype = random.choice(CRIME_TYPES[ctype])
        area_data = random.choice(PUNE_AREAS)
        area_name, lat, lng, pin, ps = area_data

        d = rdate()
        t = rtime()
        weapon = random.choice(WEAPONS)
        entry = random.choice(ENTRY_METHODS)
        target = random.choice(TARGET_TYPES)
        status = random.choice(CASE_STATUSES)
        cctv = random.choices([1,0], weights=[55,45])[0]

        # Link to criminal if solved
        has_criminal = status in ("Solved","Closed") and random.random() < 0.85
        crim_id = random.choice(criminal_ids) if has_criminal else ""
        arrest = 1 if has_criminal and status == "Solved" else 0

        # Pick officer from matching station or nearest
        if ps in station_officers:
            officer = random.choice(station_officers[ps])
        else:
            officer = random.choice(station_officers[random.choice(all_stations)])

        victim_gender = random.choice(["Male","Female","Male","Male"])
        victim_age = random.randint(12, 80)

        crimes.append({
            "crime_id": f"CR-{d.year}-{i:05d}",
            "crime_type": ctype,
            "crime_subtype": subtype,
            "crime_date": d.isoformat(),
            "crime_time": t,
            "crime_day": days[d.weekday()],
            "crime_month": months[d.month-1],
            "crime_year": d.year,
            "crime_location": raddress(area_name, pin),
            "area_name": area_name,
            "city": "Pune",
            "state": "Maharashtra",
            "pincode": pin,
            "latitude": jitter(lat),
            "longitude": jitter(lng),
            "crime_description": crime_desc(ctype, subtype, area_name, target, t),
            "weapon_used": weapon,
            "entry_method": entry,
            "crime_method": crime_method_text(ctype, weapon, entry),
            "target_type": target,
            "victim_count": random.randint(1, 5),
            "victim_gender": victim_gender,
            "victim_age": victim_age,
            "injury_level": random.choice(INJURY_LEVELS),
            "property_loss_amount": round(random.uniform(500, 5000000), 2) if ctype in ("Theft","Robbery","Fraud","Cybercrime") else 0.0,
            "suspect_count": random.randint(1, 5),
            "cctv_available": cctv,
            "evidence_found": random.choice(EVIDENCE_POOL),
            "police_station": ps,
            "officer_assigned": officer,
            "case_status": status,
            "fir_number": f"FIR/{d.year}/{ps[:3].upper()}/{i:05d}",
            "arrest_made": arrest,
            "criminal_id": crim_id,
            "investigation_notes": inv_notes(status, cctv),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        if i % 5000 == 0:
            print(f"      ...{i}/{num_crimes} crimes generated")

    return crimes


def gen_modus_operandi(criminals):
    num = len(criminals)
    print(f"  [*] Generating {num} modus operandi records...")
    mos = []
    for i, c in enumerate(criminals, 1):
        ctype = c["most_common_crime"]
        mos.append({
            "mo_id": i,
            "criminal_id": c["criminal_id"],
            "crime_type": ctype,
            "entry_method": random.choice(ENTRY_METHODS),
            "escape_method": random.choice(ESCAPE_METHODS),
            "target_selection": random.choice(TARGET_SELECTIONS),
            "crime_timing": random.choice(CRIME_TIMINGS),
            "weapon_used": c["preferred_weapon"],
            "dress_pattern": random.choice(DRESS_PATTERNS),
            "communication_method": random.choice(COMM_METHODS),
            "vehicle_used": random.choice(VEHICLES),
            "accomplice_count": random.randint(0, 6),
            "victim_selection": random.choice(TARGET_SELECTIONS),
            "planning_level": random.choice(PLANNING_LEVELS),
            "technology_used": random.choice(TECH_USED),
            "repeat_pattern": f"Known to repeat {ctype} offenses in similar areas with consistent timing patterns.",
            "special_notes": f"Subject classified as {c['risk_level']} risk. {c['criminal_category']} offender. {'Gang affiliated: '+c['gang_name']+'.' if c['gang_name'] else 'No gang affiliation.'}",
        })
    return mos


def gen_face_recognition(criminals, crim_images, has_real_images):
    print(f"  [*] Generating face recognition data...")
    faces = []
    fid = 0

    for c in criminals:
        cid = c["criminal_id"]

        if has_real_images and cid in crim_images:
            image_files = crim_images[cid]
        else:
            # Synthetic: mugshot + 1-5 face images
            n_extra = random.randint(1, 5)
            image_files = [f"{cid}_mugshot.jpg"] + [f"{cid}_face_{j}.jpg" for j in range(1, n_extra+1)]

        for img_file in image_files:
            fid += 1
            is_mugshot = "mugshot" in img_file
            faces.append({
                "face_id": fid,
                "criminal_id": cid,
                "image_path": f"mock_images/faces/{img_file}",
                "face_encoding": face_enc_bytes(),
                "image_resolution": "250x250",
                "capture_angle": "Front" if is_mugshot else random.choice(CAPTURE_ANGLES),
                "lighting_condition": random.choice(LIGHTING_CONDS),
                "facial_expression": "Neutral" if is_mugshot else random.choice(EXPRESSIONS),
                "beard_status": random.choices([1,0], weights=[30,70])[0],
                "glasses_status": random.choices([1,0], weights=[20,80])[0],
                "mask_status": 0 if is_mugshot else random.choices([1,0], weights=[5,95])[0],
                "capture_date": rdate(2022,2025).isoformat(),
                "source_type": "Arrest Photo" if is_mugshot else random.choice(SOURCE_TYPES),
                "confidence_score": round(random.uniform(0.75, 0.99) if is_mugshot else random.uniform(0.55, 0.95), 4),
            })

    print(f"      ...{fid} face records generated")
    return faces


def compute_area_stats(crimes):
    print(f"  [*] Computing area crime statistics...")
    area_map = {a[0]: a for a in PUNE_AREAS}
    stats_data = defaultdict(lambda: defaultdict(int))

    for cr in crimes:
        a = cr["area_name"]
        stats_data[a]["total"] += 1
        ct = cr["crime_type"]
        if ct == "Murder": stats_data[a]["murder"] += 1
        elif ct == "Robbery": stats_data[a]["robbery"] += 1
        elif ct == "Theft": stats_data[a]["theft"] += 1
        elif ct == "Cybercrime": stats_data[a]["cyber"] += 1
        elif ct == "Sexual Offense": stats_data[a]["women"] += 1
        elif ct == "Drug Offense": stats_data[a]["drug"] += 1

        if cr["criminal_id"]: stats_data[a]["repeat"] += 1

        hour = int(cr["crime_time"].split(":")[0])
        if hour >= 20 or hour < 6:
            stats_data[a]["night"] += 1
        else:
            stats_data[a]["day"] += 1

        vage = cr["victim_age"]
        if vage < 18: stats_data[a]["juvenile"] += 1

    results = []
    for aid, (aname, alat, alng, apin, aps) in enumerate(PUNE_AREAS, 1):
        s = stats_data.get(aname, defaultdict(int))
        total = s["total"] or 0
        mx_crime = max(
            [("Theft",s["theft"]),("Robbery",s["robbery"]),("Murder",s["murder"]),
             ("Cybercrime",s["cyber"])],
            key=lambda x: x[1]
        )[0] if total > 0 else "None"

        results.append({
            "area_id": aid,
            "area_name": aname,
            "city": "Pune",
            "state": "Maharashtra",
            "latitude": alat,
            "longitude": alng,
            "total_crimes": total,
            "murder_count": s["murder"],
            "robbery_count": s["robbery"],
            "theft_count": s["theft"],
            "cybercrime_count": s["cyber"],
            "women_crime_count": s["women"],
            "juvenile_crime_count": s["juvenile"],
            "night_crime_count": s["night"],
            "day_crime_count": s["day"],
            "repeat_offender_count": s["repeat"],
            "hotspot_score": round(min(total / 20.0, 10.0), 2) if total else 0.0,
            "most_common_crime": mx_crime,
            "safest_time": "2:00 AM - 5:00 AM",
            "dangerous_time": "9:00 PM - 1:00 AM" if s["night"] > s["day"] else "12:00 PM - 6:00 PM",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return results


# ═══════════════════════════════════════════════════════════════════
# OUTPUT: SQLite
# ═══════════════════════════════════════════════════════════════════

def save_sqlite(criminals, crimes, mos, faces, areas, officers):
    os.makedirs(DB_DIR, exist_ok=True)
    db_path = os.path.join(DB_DIR, "crime_analysis.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    print(f"  [*] Writing SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # --- criminal_records ---
    c.execute("""CREATE TABLE criminal_records (
        criminal_id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, full_name TEXT,
        nickname TEXT, gender TEXT, age INTEGER, dob TEXT, blood_group TEXT,
        nationality TEXT, religion TEXT, marital_status TEXT, phone_number TEXT,
        email TEXT, aadhaar_number TEXT, passport_number TEXT, address TEXT,
        area_name TEXT, city TEXT, state TEXT, pincode INTEGER,
        latitude REAL, longitude REAL, gang_name TEXT, gang_role TEXT,
        education_level TEXT, occupation TEXT, criminal_category TEXT, risk_level TEXT,
        fingerprint_id TEXT, dna_profile_id TEXT, eye_color TEXT, hair_color TEXT,
        height_cm REAL, weight_kg REAL, body_marks TEXT, face_image_path TEXT,
        mugshot_image TEXT, last_known_location TEXT, last_seen_date TEXT,
        arrest_count INTEGER, conviction_count INTEGER, prison_history TEXT,
        bail_status TEXT, most_common_crime TEXT, crime_style TEXT,
        preferred_weapon TEXT, active_status INTEGER, wanted_status INTEGER,
        created_at TEXT
    )""")

    cols_cr = list(criminals[0].keys())
    ph = ",".join(["?"]*len(cols_cr))
    c.executemany(f"INSERT INTO criminal_records ({','.join(cols_cr)}) VALUES ({ph})",
                  [tuple(r[k] for k in cols_cr) for r in criminals])
    print(f"      criminal_records: {len(criminals)} rows")

    # --- crime_records ---
    c.execute("""CREATE TABLE crime_records (
        crime_id TEXT PRIMARY KEY, crime_type TEXT, crime_subtype TEXT,
        crime_date TEXT, crime_time TEXT, crime_day TEXT, crime_month TEXT,
        crime_year INTEGER, crime_location TEXT, area_name TEXT, city TEXT,
        state TEXT, pincode INTEGER, latitude REAL, longitude REAL,
        crime_description TEXT, weapon_used TEXT, entry_method TEXT,
        crime_method TEXT, target_type TEXT, victim_count INTEGER,
        victim_gender TEXT, victim_age INTEGER, injury_level TEXT,
        property_loss_amount REAL, suspect_count INTEGER, cctv_available INTEGER,
        evidence_found TEXT, police_station TEXT, officer_assigned TEXT,
        case_status TEXT, fir_number TEXT, arrest_made INTEGER,
        criminal_id TEXT, investigation_notes TEXT, created_at TEXT,
        FOREIGN KEY (criminal_id) REFERENCES criminal_records(criminal_id)
    )""")

    cols_cm = list(crimes[0].keys())
    ph = ",".join(["?"]*len(cols_cm))
    c.executemany(f"INSERT INTO crime_records ({','.join(cols_cm)}) VALUES ({ph})",
                  [tuple(r[k] for k in cols_cm) for r in crimes])
    print(f"      crime_records: {len(crimes)} rows")

    # --- crime_modus_operandi ---
    c.execute("""CREATE TABLE crime_modus_operandi (
        mo_id INTEGER PRIMARY KEY, criminal_id TEXT, crime_type TEXT,
        entry_method TEXT, escape_method TEXT, target_selection TEXT,
        crime_timing TEXT, weapon_used TEXT, dress_pattern TEXT,
        communication_method TEXT, vehicle_used TEXT, accomplice_count INTEGER,
        victim_selection TEXT, planning_level TEXT, technology_used TEXT,
        repeat_pattern TEXT, special_notes TEXT,
        FOREIGN KEY (criminal_id) REFERENCES criminal_records(criminal_id)
    )""")

    cols_mo = list(mos[0].keys())
    ph = ",".join(["?"]*len(cols_mo))
    c.executemany(f"INSERT INTO crime_modus_operandi ({','.join(cols_mo)}) VALUES ({ph})",
                  [tuple(r[k] for k in cols_mo) for r in mos])
    print(f"      crime_modus_operandi: {len(mos)} rows")

    # --- face_recognition_data ---
    c.execute("""CREATE TABLE face_recognition_data (
        face_id INTEGER PRIMARY KEY, criminal_id TEXT, image_path TEXT,
        face_encoding BLOB, image_resolution TEXT, capture_angle TEXT,
        lighting_condition TEXT, facial_expression TEXT, beard_status INTEGER,
        glasses_status INTEGER, mask_status INTEGER, capture_date TEXT,
        source_type TEXT, confidence_score REAL,
        FOREIGN KEY (criminal_id) REFERENCES criminal_records(criminal_id)
    )""")

    cols_fc = list(faces[0].keys())
    ph = ",".join(["?"]*len(cols_fc))
    c.executemany(f"INSERT INTO face_recognition_data ({','.join(cols_fc)}) VALUES ({ph})",
                  [tuple(r[k] for k in cols_fc) for r in faces])
    print(f"      face_recognition_data: {len(faces)} rows")

    # --- area_crime_statistics ---
    c.execute("""CREATE TABLE area_crime_statistics (
        area_id INTEGER PRIMARY KEY, area_name TEXT, city TEXT, state TEXT,
        latitude REAL, longitude REAL, total_crimes INTEGER,
        murder_count INTEGER, robbery_count INTEGER, theft_count INTEGER,
        cybercrime_count INTEGER, women_crime_count INTEGER,
        juvenile_crime_count INTEGER, night_crime_count INTEGER,
        day_crime_count INTEGER, repeat_offender_count INTEGER,
        hotspot_score REAL, most_common_crime TEXT, safest_time TEXT,
        dangerous_time TEXT, last_updated TEXT
    )""")

    cols_as = list(areas[0].keys())
    ph = ",".join(["?"]*len(cols_as))
    c.executemany(f"INSERT INTO area_crime_statistics ({','.join(cols_as)}) VALUES ({ph})",
                  [tuple(r[k] for k in cols_as) for r in areas])
    print(f"      area_crime_statistics: {len(areas)} rows")

    # --- police_officers ---
    c.execute("""CREATE TABLE police_officers (
        officer_id TEXT PRIMARY KEY, officer_name TEXT, rank TEXT,
        badge_number TEXT, phone_number TEXT, email TEXT,
        police_station TEXT, assigned_area TEXT, solved_cases INTEGER,
        active_cases INTEGER, specialization TEXT, duty_status TEXT
    )""")

    cols_po = list(officers[0].keys())
    ph = ",".join(["?"]*len(cols_po))
    c.executemany(f"INSERT INTO police_officers ({','.join(cols_po)}) VALUES ({ph})",
                  [tuple(r[k] for k in cols_po) for r in officers])
    print(f"      police_officers: {len(officers)} rows")

    conn.commit()
    conn.close()
    print(f"  [+] SQLite database saved.")


# ═══════════════════════════════════════════════════════════════════
# OUTPUT: CSV
# ═══════════════════════════════════════════════════════════════════

def save_csv(name, rows):
    os.makedirs(CSV_DIR, exist_ok=True)
    path = os.path.join(CSV_DIR, f"{name}.csv")
    if not rows:
        return

    # For face data, replace binary encoding with placeholder in CSV
    if name == "face_recognition_data":
        rows_copy = []
        for r in rows:
            rc = dict(r)
            rc["face_encoding"] = f"<128d_vector_blob>"
            rows_copy.append(rc)
        rows = rows_copy

    keys = list(rows[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"      {name}.csv: {len(rows)} rows")


# ═══════════════════════════════════════════════════════════════════
# OUTPUT: JSON
# ═══════════════════════════════════════════════════════════════════

def save_json(criminals, crimes, mos, faces):
    os.makedirs(JSON_DIR, exist_ok=True)
    print(f"  [*] Writing JSON profiles...")

    # Build lookups
    crimes_by_cid = defaultdict(list)
    for cr in crimes:
        if cr["criminal_id"]:
            crimes_by_cid[cr["criminal_id"]].append({
                "crime_id": cr["crime_id"],
                "crime_type": cr["crime_type"],
                "crime_subtype": cr["crime_subtype"],
                "crime_date": cr["crime_date"],
                "area_name": cr["area_name"],
                "case_status": cr["case_status"],
            })

    mo_by_cid = {}
    for m in mos:
        mo_by_cid[m["criminal_id"]] = {k:v for k,v in m.items() if k != "criminal_id"}

    face_by_cid = defaultdict(list)
    for f in faces:
        face_by_cid[f["criminal_id"]].append({
            "face_id": f["face_id"],
            "image_path": f["image_path"],
            "capture_angle": f["capture_angle"],
            "confidence_score": f["confidence_score"],
            "source_type": f["source_type"],
        })

    profiles = []
    for c in criminals:
        cid = c["criminal_id"]
        profile = {k: v for k, v in c.items()}
        profile["crimes"] = crimes_by_cid.get(cid, [])
        profile["modus_operandi"] = mo_by_cid.get(cid, {})
        profile["face_data"] = face_by_cid.get(cid, [])
        profiles.append(profile)

    path = os.path.join(JSON_DIR, "criminal_profiles.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    print(f"      criminal_profiles.json: {len(profiles)} profiles")


# ═══════════════════════════════════════════════════════════════════
# OUTPUT: GeoJSON
# ═══════════════════════════════════════════════════════════════════

def save_geojson(crimes, areas):
    os.makedirs(GEOJSON_DIR, exist_ok=True)
    print(f"  [*] Writing GeoJSON files...")

    # Crime hotspots (sample 5000 crimes to keep file reasonable)
    sample = random.sample(crimes, min(5000, len(crimes)))
    features = []
    for cr in sample:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [cr["longitude"], cr["latitude"]]
            },
            "properties": {
                "crime_id": cr["crime_id"],
                "crime_type": cr["crime_type"],
                "crime_subtype": cr["crime_subtype"],
                "crime_date": cr["crime_date"],
                "area_name": cr["area_name"],
                "case_status": cr["case_status"],
                "injury_level": cr["injury_level"],
            }
        })

    geojson = {"type": "FeatureCollection", "features": features}
    path = os.path.join(GEOJSON_DIR, "crime_hotspots.geojson")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
    print(f"      crime_hotspots.geojson: {len(features)} features")

    # Area statistics as points
    area_features = []
    for a in areas:
        area_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [a["longitude"], a["latitude"]]
            },
            "properties": {
                "area_name": a["area_name"],
                "total_crimes": a["total_crimes"],
                "hotspot_score": a["hotspot_score"],
                "most_common_crime": a["most_common_crime"],
                "dangerous_time": a["dangerous_time"],
            }
        })

    geojson2 = {"type": "FeatureCollection", "features": area_features}
    path2 = os.path.join(GEOJSON_DIR, "area_hotspots.geojson")
    with open(path2, 'w', encoding='utf-8') as f:
        json.dump(geojson2, f, indent=2)
    print(f"      area_hotspots.geojson: {len(area_features)} features")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  Crime Analysis & Criminal Identification System")
    print("  Dataset Generator")
    print("=" * 65)

    start = time_mod.time()

    # Step 1: Scan existing face images
    print("\n[1/8] Scanning face images directory...")
    crim_images, has_real = scan_faces()
    if has_real:
        print(f"  [+] Found {len(crim_images)} criminals with images in faces directory.")
    
    # Step 2: Generate police officers (needed before crimes)
    print("\n[2/8] Generating police officers...")
    officers = gen_police_officers(NUM_OFFICERS)

    # Step 3: Generate criminal records
    print("\n[3/8] Generating criminal records...")
    criminals = gen_criminal_records(crim_images, has_real)

    # Step 4: Generate crime records
    print("\n[4/8] Generating crime records...")
    crimes = gen_crime_records(criminals, officers, NUM_CRIMES)

    # Step 5: Generate modus operandi
    print("\n[5/8] Generating modus operandi records...")
    mos = gen_modus_operandi(criminals)

    # Step 6: Generate face recognition data
    print("\n[6/8] Generating face recognition data...")
    faces = gen_face_recognition(criminals, crim_images, has_real)

    # Step 7: Compute area statistics
    print("\n[7/8] Computing area crime statistics...")
    areas = compute_area_stats(crimes)

    # Step 8: Save all outputs
    print("\n[8/8] Saving outputs...")

    print("\n  --- SQLite Database ---")
    save_sqlite(criminals, crimes, mos, faces, areas, officers)

    print("\n  --- CSV Files ---")
    save_csv("criminal_records", criminals)
    save_csv("crime_records", crimes)
    save_csv("crime_modus_operandi", mos)
    save_csv("face_recognition_data", faces)
    save_csv("area_crime_statistics", areas)
    save_csv("police_officers", officers)

    print("\n  --- JSON Profiles ---")
    save_json(criminals, crimes, mos, faces)

    print("\n  --- GeoJSON Maps ---")
    save_geojson(crimes, areas)

    elapsed = time_mod.time() - start

    # Summary
    total_records = len(criminals) + len(crimes) + len(mos) + len(faces) + len(areas) + len(officers)
    print("\n" + "=" * 65)
    print("  DATASET GENERATION COMPLETE!")
    print("=" * 65)
    print(f"  criminal_records:       {len(criminals):>8,} records")
    print(f"  crime_records:          {len(crimes):>8,} records")
    print(f"  crime_modus_operandi:   {len(mos):>8,} records")
    print(f"  face_recognition_data:  {len(faces):>8,} records")
    print(f"  area_crime_statistics:  {len(areas):>8,} records")
    print(f"  police_officers:        {len(officers):>8,} records")
    print(f"  {'-'*40}")
    print(f"  TOTAL RECORDS:          {total_records:>8,}")
    print(f"  Time taken:             {elapsed:>7.1f}s")
    print(f"\n  Output directory: {OUTPUT_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
