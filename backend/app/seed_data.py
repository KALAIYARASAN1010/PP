import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from .models import User, Proposal, DecisionHistory, AuditLog
from .auth import hash_password
from .audit import log_audit_event
from .engine import precedent_engine

def seed_database(db: Session):
    """
    Seeds the database with Puducherry Police personnel, 28+ fictional police proposals
    customized for Traffic, Cybercrime, Law & Order, Coastal Marine, and Communications.
    All figures are in Indian Rupees (₹).
    """
    # Check if already seeded
    if db.query(User).count() > 0:
        return

    print("Initializing Puducherry Police institutional database seed...")

    # 1. Seed Puducherry Police Users
    users_data = [
        {
            "username": "insp_balamurugan",
            "password": "Password123!",
            "full_name": "Inspector R. Balamurugan",
            "role": "Submitter",
            "department": "Law & Order (Grand Bazaar PS)",
            "badge_number": "PY-1402"
        },
        {
            "username": "si_jayasri",
            "password": "Password123!",
            "full_name": "Sub-Inspector K. Jayasri",
            "role": "Submitter",
            "department": "Cyber Crime Police Station Puducherry",
            "badge_number": "PY-2180"
        },
        {
            "username": "sp_anandharaj",
            "password": "Password123!",
            "full_name": "Superintendent of Police S. Anandharaj",
            "role": "Reviewer",
            "department": "Traffic & Coastal Security Wing",
            "badge_number": "PY-0321"
        },
        {
            "username": "ssp_mukherjee",
            "password": "Password123!",
            "full_name": "Senior SP / DIG Ananya Mukherjee",
            "role": "Reviewer",
            "department": "Executive Review & Police Headquarters",
            "badge_number": "PY-0105"
        },
        {
            "username": "admin_senthil",
            "password": "Password123!",
            "full_name": "Administrator V. Senthil",
            "role": "Admin",
            "department": "Police Computer Wing & Records (Dumas St)",
            "badge_number": "PY-0012"
        }
    ]

    user_objs = {}
    for ud in users_data:
        u = User(
            username=ud["username"],
            hashed_password=hash_password(ud["password"]),
            full_name=ud["full_name"],
            role=ud["role"],
            department=ud["department"],
            badge_number=ud["badge_number"],
            is_active=True
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        user_objs[ud["username"]] = u

        # Audit initial user setup
        log_audit_event(
            db=db,
            user_name="SYSTEM_BOOTSTRAP",
            action="CREATE_USER",
            entity_type="User",
            entity_id=str(u.id),
            details={"username": u.username, "role": u.role, "badge": u.badge_number}
        )

    # 2. Seed 28 Fictional Puducherry Police Proposals
    raw_proposals = [
        # --- Resubmission Chain: Beach Road Promenade Tourist Safety BWC ---
        {
            "code": "PROP-PY-2023-0002",
            "title": "[DEMO] Beach Road Promenade Body-Worn Camera Fleet Phase 1",
            "category": "Procurement",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 1450000.0,  # ₹14.50 Lakh
            "desc": "Procurement of 50 body-worn cameras for weekend Promenade Beach and Goubert Avenue tourist patrol squads to document public safety incidents.",
            "just": "High footfall during weekend tourist hours creates frequent public altercations and lost property disputes along the coastal stretch.",
            "submitter": "insp_balamurugan",
            "days_offset": 450,
            "status": "Rejected",
            "parent_id": None,
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Rejected",
                "reason": "Lacks coastal marine salt-spray weatherproofing and requires high proprietary recurring cloud licensing fees (₹4.5L/year).",
                "days_offset": 435
            },
            "outcome": None,
            "lessons": "Coastal atmospheric salt corrosion must be addressed with IP68 marine-grade casing before proposal submittal."
        },
        {
            "code": "PROP-PY-2023-0018",
            "title": "[DEMO] Coastal Weatherproof BWC with On-Premise Gorimedu Server Storage",
            "category": "Procurement",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 1180000.0,  # ₹11.80 Lakh
            "desc": "Revised proposal for 50 IP68 salt-resistant body-worn cameras utilizing Gorimedu Police Complex local secure storage server.",
            "just": "Direct revision of PROP-PY-2023-0002 addressing salt corrosion and eliminating recurring vendor cloud subscriptions.",
            "submitter": "insp_balamurugan",
            "days_offset": 390,
            "status": "Changes Requested",
            "parent_code": "PROP-PY-2023-0002",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Changes Requested",
                "reason": "Shift battery capacity indicates 7 hours; continuous festival shifts during Bastille Day and New Year exceed 12 hours. Specify extended battery packs.",
                "days_offset": 380
            },
            "outcome": None,
            "lessons": "Shift hours during Puducherry festival and tourist seasons demand 12-hour continuous battery standby."
        },
        {
            "code": "PROP-PY-2024-0003",
            "title": "[DEMO] Promenade & French Quarter Comprehensive BWC Deployment (Final Revision)",
            "category": "Procurement",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 1245000.0,  # ₹12.45 Lakh
            "desc": "Final revision including 50 IP68 body cameras with 14-hour hot-swap batteries, coastal dock mounts, and Union Territory Police Modernization Grant funding.",
            "just": "Fulfills all requirements from PROP-PY-2023-0018 with 60% Ministry of Home Affairs modernization grant co-funding.",
            "submitter": "insp_balamurugan",
            "days_offset": 320,
            "status": "Approved",
            "parent_code": "PROP-PY-2023-0018",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "All coastal hardware and battery specifications verified; MHA modernization grant reduces UT financial liability.",
                "days_offset": 305
            },
            "outcome": "Deployed to Promenade Beach and French Quarter patrols. Tourist dispute resolution time dropped from 35 days to 6 days. Zero corrosion faults.",
            "lessons_learned": "Centralized docking at Grand Bazaar station ensured battery charging was completed before night shift changeover."
        },

        # --- Conflicting Precedent Pair: ANPR Cameras ---
        {
            "code": "PROP-PY-2023-0004",
            "title": "[DEMO] Fixed ANPR Optical Cameras at Grand Canal & Boulevard Intersections",
            "category": "Technical",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 1850000.0,  # ₹18.50 Lakh
            "desc": "Installation of 12 high-resolution stationary Automated Number Plate Recognition (ANPR) optical cameras at key Boulevard entrance bridges.",
            "just": "Enables automatic vehicle tracking for stolen two-wheelers and suspect vehicles exiting Boulevard town into Villupuram/Cuddalore borders.",
            "submitter": "si_jayasri",
            "days_offset": 410,
            "status": "Approved",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Approved",
                "reason": "Complies with UT surveillance guidelines with local 30-day purged retention and access restricted to Inspector rank and above.",
                "days_offset": 395
            },
            "outcome": "Recovered 38 stolen motorcycles within 90 days across Boulevard border checkpoints. Zero citizen privacy disputes.",
            "lessons_learned": "Camera angles required recalibration for monsoon glare on registration plates."
        },
        {
            "code": "PROP-PY-2024-0008",
            "title": "[DEMO] Mobile ANPR Cameras Mounted on Highway Patrol Cruisers",
            "category": "Technical",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 1920000.0,  # ₹19.20 Lakh
            "desc": "Procurement of dual-lens mobile roof-mounted ANPR units for 6 highway interceptor patrol cruisers with external cloud sync.",
            "just": "Expands plate recognition dynamically across East Coast Road (ECR) and Villupuram highway sectors.",
            "submitter": "insp_balamurugan",
            "days_offset": 280,
            "status": "Rejected",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Rejected",
                "reason": "Commercial vendor clause for out-of-state private cloud storage violates UT Puducherry Police Data Sovereignty and Security Norms.",
                "days_offset": 265
            },
            "outcome": None,
            "lessons_learned": "Vendor data-sharing clauses must explicitly mandate hosting on National Informatics Centre (NIC) or Gorimedu servers."
        },

        # --- Near-Duplicate Drone Surveillance Pair ---
        {
            "code": "PROP-PY-2024-0010",
            "title": "[DEMO] Drone Quadcopters for Coastal & Festival Crowd Monitoring",
            "category": "Operational",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 650000.0,  # ₹6.50 Lakh
            "desc": "Acquisition of 3 commercial quadcopters with 4K optical cameras for Sri Aurobindo Ashram zone, temple car festivals, and coastal fishermen safety.",
            "just": "Provides overhead situational visibility to Law & Order commanders during dense public gatherings without placing personnel in crowd crush.",
            "submitter": "si_jayasri",
            "days_offset": 240,
            "status": "Rejected",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Rejected",
                "reason": "Lacks DGCA certified remote pilot training licenses, maritime coastal wind-resistance testing, and SOP for coastal airspace permissions.",
                "days_offset": 225
            },
            "outcome": None,
            "lessons_learned": "DGCA pilot licensing and coastal wind gust ratings (Level 6) must precede hardware drone procurement."
        },
        {
            "code": "PROP-PY-2024-0022",
            "title": "[DEMO] Coastal Surveillance Tactical Drones with Thermal Optics (Karaikal & PY)",
            "category": "Operational",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 720000.0,  # ₹7.20 Lakh
            "desc": "Procurement of 2 enterprise drones with FLIR radiometric thermal cameras and high wind-resistance for nighttime coastal search and rescue operations.",
            "just": "Supports Coastal Marine Police in tracking unauthorized maritime landings and search operations during rough sea conditions.",
            "submitter": "si_jayasri",
            "days_offset": 170,
            "status": "Under Review",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        },

        # --- Additional Puducherry Police Proposals ---
        {
            "code": "PROP-PY-2023-0012",
            "title": "[DEMO] Cyber Crime Forensics Audio-Video Redaction & Deepfake Lab",
            "category": "Technical",
            "dept": "Cyber Crime Police Station Puducherry",
            "cost": 2400000.0,  # ₹24.00 Lakh
            "desc": "High-performance forensic computing workstation with automated face and identity redaction software for judicial electronic evidence submission.",
            "just": "Current evidentiary redactions in cyber harassment and online extortion cases take 21 days manually, delaying charge-sheet filing in trial courts.",
            "submitter": "si_jayasri",
            "days_offset": 360,
            "status": "Approved",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Approved",
                "reason": "Essential forensics capability meeting Indian Evidence Act (Sec 65B) integrity standards and accelerating cyber trial submissions.",
                "days_offset": 345
            },
            "outcome": "Electronic evidence processing turnaround reduced from 21 days to 3 days across all cyber harassment complaints.",
            "lessons_learned": "Periodic forensic software license maintenance agreements must be renewed before fiscal year closure."
        },
        {
            "code": "PROP-PY-2023-0015",
            "title": "[DEMO] Coastal Marine Interceptor Speedboat Radar & VHF Link",
            "category": "Infrastructure",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 3800000.0,  # ₹38.00 Lakh
            "desc": "Installation of coastal marine radar transponders and marine-band VHF digital repeaters at Puducherry and Karaikal port police outposts.",
            "just": "Blind spots in maritime communication during rough weather between fishing hamlets and the coastal police command post.",
            "submitter": "insp_balamurugan",
            "days_offset": 350,
            "status": "Approved",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "Directly strengthens UT coastal security grid and inter-agency coordination with Indian Coast Guard station.",
                "days_offset": 338
            },
            "outcome": "Zero coastal communication dropouts recorded across 18 joint coastal security drills with Indian Coast Guard.",
            "lessons_learned": "Lightning surge arrestors required on mastheads due to intense Bay of Bengal monsoon electrical storms."
        },
        {
            "code": "PROP-PY-2024-0001",
            "title": "[DEMO] Sniffer Dog Unit Belgian Malinois Expansion & Kennel Upgrade",
            "category": "Procurement",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 960000.0,  # ₹9.60 Lakh
            "desc": "Acquisition and explosive/narcotics detection training of 2 Belgian Malinois canines for VIP security and railway station sweeps.",
            "just": "Current service dogs are approaching retirement age; replaces capabilities ahead of major UT public festivals and national dignitary visits.",
            "submitter": "insp_balamurugan",
            "days_offset": 300,
            "status": "Approved",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Approved",
                "reason": "Approved kennel expansion and certified handler pairing plan meeting National Canine Training Center protocols.",
                "days_offset": 288
            },
            "outcome": "Both canines completed certified 24-week kennel training; deployed in 64 VIP sanitization details without incident.",
            "lessons_learned": "Air-cooled transport kennels prevented handler fatigue during high-humidity coastal summer months."
        },
        {
            "code": "PROP-PY-2024-0005",
            "title": "[DEMO] Barcode Evidence Management System for Police Stations",
            "category": "Technical",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 580000.0,  # ₹5.80 Lakh
            "desc": "Digitization of Malkhana (property room) evidence with 2D barcode handheld scanners and digital chain-of-custody tracking across 16 police stations.",
            "just": "Eliminates delays in retrieving case exhibits during judicial trials and ensures transparent accountability during departmental inspections.",
            "submitter": "si_jayasri",
            "days_offset": 290,
            "status": "Approved",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Approved",
                "reason": "Major administrative efficiency upgrade preventing mishandling of physical court exhibits.",
                "days_offset": 275
            },
            "outcome": "100% property audit accuracy across 12,000 recorded judicial exhibits during annual Chief Judicial Magistrate inspection.",
            "lessons_learned": "Moisture-resistant barcode stickers required for narcotics and chemical storage lockers."
        },
        {
            "code": "PROP-PY-2024-0012",
            "title": "[DEMO] Tourist Police Bicycle Squad for Heritage French Quarter",
            "category": "Operational",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 320000.0,  # ₹3.20 Lakh
            "desc": "Deployment of 12 police-geared hybrid bicycles, high-visibility reflective uniforms, and tourist assistance kits for White Town patrol.",
            "just": "Narrow heritage streets in the French Quarter are inaccessible to PCR four-wheelers, causing slow response to tourist inquiries and petty theft.",
            "submitter": "insp_balamurugan",
            "days_offset": 210,
            "status": "Approved",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "High public goodwill initiative; minimal capital outlay providing visible community policing in sensitive tourist clusters.",
                "days_offset": 198
            },
            "outcome": "Petty theft incidents in the heritage grid reduced by 44%; tourist assistance satisfaction ratings exceeded 92%.",
            "lessons_learned": "Equipping each bicycle with bilingual Tamil-French-English emergency cards assisted international visitors."
        },
        {
            "code": "PROP-PY-2024-0015",
            "title": "[DEMO] Boulevard Automated Traffic Signal Adaptive Sync System",
            "category": "Technical",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 2850000.0,  # ₹28.50 Lakh
            "desc": "AI camera-based traffic density adaptive traffic light controllers across 8 primary Boulevard junctions (Raja Street, Mission Street, Anna Salai).",
            "just": "Alleviates severe peak-hour bottlenecks during school opening and weekend tourist entry onto MG Road and Nehru Street.",
            "submitter": "insp_balamurugan",
            "days_offset": 190,
            "status": "Rejected",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Rejected",
                "reason": "Excessive cost quote; smart city project already has concurrent funding allocated for Boulevard corridor signals.",
                "days_offset": 178
            },
            "outcome": None,
            "lessons_learned": "Verify Puducherry Smart City Development Limited (PSCDL) master plan before submitting municipal signal modernization proposals."
        },
        {
            "code": "PROP-PY-2024-0018",
            "title": "[DEMO] Dial 112 PCR Patrol Van Ruggedized Mobile Terminals",
            "category": "Technical",
            "dept": "Police Computer Wing & Records",
            "cost": 1980000.0,  # ₹19.80 Lakh
            "desc": "Procurement of 25 ruggedized touchscreen in-vehicle mobile data terminals for frontline PCR vans with real-time GPS CAD dispatch.",
            "just": "Replaces failing 7-year-old dispatch terminals experiencing reboot delays during emergency distress calls.",
            "submitter": "si_jayasri",
            "days_offset": 160,
            "status": "Approved",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "Critical emergency response infrastructure ensuring emergency dispatch turnaround stays under 8 minutes.",
                "days_offset": 145
            },
            "outcome": "Average PCR van scene arrival time dropped from 12.4 minutes to 6.8 minutes across Puducherry town.",
            "lessons_learned": "Vehicle power isolation converters prevented vehicle engine crank voltage drops from rebooting terminals."
        },
        {
            "code": "PROP-PY-2024-0020",
            "title": "[DEMO] Personnel Stress Management & De-escalation Academy",
            "category": "Administrative",
            "dept": "Executive Review & Police Headquarters",
            "cost": 450000.0,  # ₹4.50 Lakh
            "desc": "Comprehensive wellness and psychological resilience training for 150 frontline constables partnered with JIPMER psychiatry faculty.",
            "just": "Improves public interaction quality and mitigates occupational stress during long festival bandobast duties.",
            "submitter": "insp_balamurugan",
            "days_offset": 150,
            "status": "Approved",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "Exemplary welfare initiative partnering with premier medical institution (JIPMER).",
                "days_offset": 140
            },
            "outcome": "Public conduct grievances dropped by 34%; voluntary officer counseling attendance grew steadily.",
            "lessons_learned": "Conducting sessions in non-uniform civilian settings at Gorimedu complex improved officer openness."
        },
        {
            "code": "PROP-PY-2024-0025",
            "title": "[DEMO] Electric Two-Wheeler Fleet for Women Police Station Patrolling",
            "category": "Operational",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 1280000.0,  # ₹12.80 Lakh
            "desc": "Procurement of 14 electric scooters with built-in siren and GPS tracking for the All Women Police Station (AWPS) neighborhood patrols.",
            "just": "Enhances visibility and safety response outside women's colleges, schools, and textile mill residential corridors.",
            "submitter": "insp_balamurugan",
            "days_offset": 120,
            "status": "Changes Requested",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Changes Requested",
                "reason": "Include dedicated fast-charging points at AWPS Villianur and AWPS Puducherry and battery replacement warranty terms.",
                "days_offset": 110
            },
            "outcome": None,
            "lessons_learned": "Dedicated solar charging shed required at station premises to avoid tripping standard office electrical boards."
        },
        {
            "code": "PROP-PY-2024-0028",
            "title": "[DEMO] Portable Speed Display Radar Trailers for ECR Highway",
            "category": "Operational",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 620000.0,  # ₹6.20 Lakh
            "desc": "Purchase of 3 solar-powered portable digital speed feedback displays for ECR and Puducherry-Villupuram highway blackspots.",
            "just": "Curbs fatal weekend speeding accidents along coastal tourist transit corridors without tying down stationary constables.",
            "submitter": "insp_balamurugan",
            "days_offset": 100,
            "status": "Approved",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Approved",
                "reason": "High-impact speed calming measure with minimal operating overhead.",
                "days_offset": 90
            },
            "outcome": "Over-speeding violations at Kalapet university stretch decreased by 28% within 60 days.",
            "lessons_learned": "Anti-theft GPS lock collars prevented roadside tampering."
        },
        {
            "code": "PROP-PY-2024-0030",
            "title": "[DEMO] Heavy Armored Riot Control Vehicle for Special Operations",
            "category": "Procurement",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 6500000.0,  # ₹65.00 Lakh
            "desc": "Acquisition of an armored steel troop carrier with water cannon for civil disturbance response.",
            "just": "Department lacks heavy armored transport during major inter-state border tension incidents.",
            "submitter": "insp_balamurugan",
            "days_offset": 85,
            "status": "Rejected",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Rejected",
                "reason": "Exorbitant capital cost (₹65 Lakhs) for low-frequency requirement; mutual aid arrangement with Tamil Nadu Police covers rare large-scale armored support.",
                "days_offset": 75
            },
            "outcome": None,
            "lessons_learned": "Examine neighboring state mutual aid protocols before proposing high-cost specialized heavy machinery."
        },
        {
            "code": "PROP-PY-2024-0033",
            "title": "[DEMO] Coastal Radar & AIS Hamper Monitoring at Karaikal Outpost",
            "category": "Infrastructure",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 1520000.0,  # ₹15.20 Lakh
            "desc": "Automated Identification System (AIS) receiver antenna and shore radar integration at Karaikal Coastal Police Station.",
            "just": "Enables automated detection of mechanized fishing trawlers crossing international maritime boundary line (IMBL).",
            "submitter": "si_jayasri",
            "days_offset": 60,
            "status": "Approved",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "Critical coastal security enhancement complying with National Maritime Security Coordinator directives.",
                "days_offset": 50
            },
            "outcome": "Automated tracking achieved for 850 registered fishing vessels operating from Karaikal harbor.",
            "lessons_learned": "Regular marine battery desulfation schedule was essential during salty sea-breeze periods."
        },
        {
            "code": "PROP-PY-2024-0035",
            "title": "[DEMO] Student Police Cadet (SPC) Leadership Camps across Puducherry Schools",
            "category": "Administrative",
            "dept": "Executive Review & Police Headquarters",
            "cost": 360000.0,  # ₹3.60 Lakh
            "desc": "Civic education, road safety drills, and anti-drug youth empowerment programs across 20 government higher secondary schools.",
            "just": "Deters youth narcotics vulnerability and builds positive trust between youth and police.",
            "submitter": "insp_balamurugan",
            "days_offset": 45,
            "status": "Approved",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Approved",
                "reason": "High-value community outreach initiative directly combating youth drug abuse.",
                "days_offset": 35
            },
            "outcome": "Over 800 student cadets completed civic discipline camps; 38 road safety school wardens certified.",
            "lessons_learned": "Engaging Physical Education teachers as school coordinators ensured high daily drill attendance."
        },
        {
            "code": "PROP-PY-2024-0038",
            "title": "[DEMO] Real-Time Facial Recognition on Public Promenade CCTV Feeds",
            "category": "Technical",
            "dept": "Cyber Crime Police Station Puducherry",
            "cost": 2300000.0,  # ₹23.00 Lakh
            "desc": "Procurement of real-time algorithmic facial recognition software linked to municipal beach surveillance cameras.",
            "just": "Intended to identify wanted interstate robbery suspects and missing persons automatically.",
            "submitter": "si_jayasri",
            "days_offset": 40,
            "status": "Rejected",
            "decision": {
                "reviewer": "sp_anandharaj",
                "action": "Rejected",
                "reason": "Violates Supreme Court Puttaswamy privacy guidelines; high false-positive rate under night promenade lighting conditions.",
                "days_offset": 30
            },
            "outcome": None,
            "lessons_learned": "Public algorithmic biometric scanning requires prior judicial privacy compliance clearance."
        },
        {
            "code": "PROP-PY-2024-0040",
            "title": "[DEMO] High-Intensity LED Warning Signboards for ECR Monsoon Detours",
            "category": "Procurement",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 480000.0,  # ₹4.80 Lakh
            "desc": "Acquisition of 4 solar-powered variable matrix LED signboards for cyclone waterlogging and diversion alerts on coastal highways.",
            "just": "Improves roadway visibility during heavy North-East Monsoon rains and coastal depressions.",
            "submitter": "insp_balamurugan",
            "days_offset": 25,
            "status": "Approved",
            "decision": {
                "reviewer": "ssp_mukherjee",
                "action": "Approved",
                "reason": "Proven officer safety equipment during annual monsoon emergency operations.",
                "days_offset": 18
            },
            "outcome": "Zero flood-related vehicle pileups occurred on designated diversion routes during Cyclone Mandous.",
            "lessons_learned": "Sim-card enabled remote programming saved officers from traveling to highway trailers during cyclonic gale winds."
        },

        # --- Active In-Flight Proposals ---
        {
            "code": "PROP-PY-2024-0042",
            "title": "[DEMO] Law & Order PCR Cruiser Dual Dashcam & Audio Logging System",
            "category": "Procurement",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 1780000.0,  # ₹17.80 Lakh
            "desc": "Installation of front-facing 4K road camera and wide-angle prisoner compartment cameras across 20 frontline patrol cruisers.",
            "just": "Protects officers from false custodial harassment allegations and documents vehicle stops transparently.",
            "submitter": "insp_balamurugan",
            "days_offset": 20,
            "status": "Under Review",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        },
        {
            "code": "PROP-PY-2024-0045",
            "title": "[DEMO] Gorimedu Police Training School (PTS) Virtual Firearms Simulator",
            "category": "Infrastructure",
            "dept": "Police Computer Wing & Records",
            "cost": 2200000.0,  # ₹22.00 Lakh
            "desc": "Virtual Reality 180-degree judgmental shoot/no-shoot decision-making simulator theater for recruit constables and sub-inspectors.",
            "just": "Allows continuous firearms safety drill practice without expensive live ammunition expenditure.",
            "submitter": "si_jayasri",
            "days_offset": 15,
            "status": "Submitted",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        },
        {
            "code": "PROP-PY-2024-0048",
            "title": "[DEMO] Mahe & Yanam Enclaves Digital VHF Encrypted Link Modernization",
            "category": "Technical",
            "dept": "Police Computer Wing & Records",
            "cost": 1040000.0,  # ₹10.40 Lakh
            "desc": "Digital P25 secure voice and IP repeater gateways connecting distant Mahe and Yanam regional police superintendents directly to Gorimedu HQ.",
            "just": "Eliminates reliance on commercial telecom landlines during extreme coastal cyclones and natural disasters.",
            "submitter": "si_jayasri",
            "days_offset": 10,
            "status": "Submitted",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        },
        {
            "code": "PROP-PY-2024-0050",
            "title": "[DEMO] Coastal Jet-Ski Sea-Rescue Patrol for Promenade and Paradise Beach",
            "category": "Operational",
            "dept": "Traffic & Coastal Security Wing",
            "cost": 1400000.0,  # ₹14.00 Lakh
            "desc": "Procurement of 2 rescue-grade marine personal watercraft for life-saving patrol at Paradise Beach and Promenade rocky shoreline.",
            "just": "Reduces accidental drowning fatalities among tourists venturing into hazardous rip currents.",
            "submitter": "insp_balamurugan",
            "days_offset": 6,
            "status": "Under Review",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        },
        {
            "code": "PROP-PY-2024-0052",
            "title": "[DEMO] Gorimedu Central Armory Biometric Access & RFID Weapon Vault",
            "category": "Infrastructure",
            "dept": "Police Computer Wing & Records",
            "cost": 840000.0,  # ₹8.40 Lakh
            "desc": "Biometric fingerprint and RFID weapon tag inventory locker system for automatic issuance and return logging of service weapons.",
            "just": "Guarantees zero discrepancy in round count and firearm assignment during election and VIP deployments.",
            "submitter": "si_jayasri",
            "days_offset": 3,
            "status": "Draft",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        },
        {
            "code": "PROP-PY-2024-0055",
            "title": "[DEMO] Tourist Assistance Kiosks at Sri Aurobindo Ashram & Railway Station",
            "category": "Operational",
            "dept": "Law & Order (Grand Bazaar PS)",
            "cost": 300000.0,  # ₹3.00 Lakh
            "desc": "Installation of 2 modular air-conditioned tourist facilitation kiosks staffed by multilingual constables with interactive map terminals.",
            "just": "Provides safe lost-and-found registration, lodging verification, and crime reporting for national and international tourists.",
            "submitter": "insp_balamurugan",
            "days_offset": 2,
            "status": "Draft",
            "decision": None,
            "outcome": None,
            "lessons_learned": None
        }
    ]

    print(f"Seeding {len(raw_proposals)} Puducherry Police proposals (All in ₹ INR)...")

    proposal_objs = {}

    for pdata in raw_proposals:
        submitter_user = user_objs[pdata["submitter"]]
        created_time = datetime.now(timezone.utc) - timedelta(days=pdata["days_offset"])

        p = Proposal(
            proposal_code=pdata["code"],
            title=pdata["title"],
            description=pdata["desc"],
            category=pdata["category"],
            department=pdata["dept"],
            cost=pdata["cost"],
            justification=pdata["just"],
            date=created_time,
            status=pdata["status"],
            submitter_id=submitter_user.id,
            implementation_outcome=pdata.get("outcome"),
            lessons_learned=pdata.get("lessons") or pdata.get("lessons_learned"),
            created_at=created_time,
            updated_at=created_time
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        proposal_objs[pdata["code"]] = p

        # Precompute embedding vector for instant retrieval performance
        corpus_text = f"{p.title}. {p.category} {p.department}. {p.description} {p.justification}"
        emb = precedent_engine.encode(corpus_text)
        if emb:
            p.embedding_json = json.dumps(emb)
            db.commit()

        # Audit proposal creation
        log_audit_event(
            db=db,
            user_name=submitter_user.username,
            action="CREATE_PROPOSAL",
            entity_type="Proposal",
            entity_id=p.proposal_code,
            details={
                "code": p.proposal_code,
                "title": p.title,
                "category": p.category,
                "cost_inr": p.cost,
                "status": p.status
            },
            user_id=submitter_user.id
        )

        # Add DecisionHistory if decision recorded
        if pdata.get("decision"):
            dinfo = pdata["decision"]
            reviewer_user = user_objs[dinfo["reviewer"]]
            dec_time = datetime.now(timezone.utc) - timedelta(days=dinfo["days_offset"])
            
            prev_status = "Under Review" if dinfo["action"] in {"Approved", "Rejected", "Changes Requested"} else "Submitted"
            
            decision = DecisionHistory(
                proposal_id=p.id,
                reviewer_id=reviewer_user.id,
                action=dinfo["action"],
                reason=dinfo["reason"],
                previous_status=prev_status,
                new_status=dinfo["action"],
                created_at=dec_time
            )
            db.add(decision)
            db.commit()
            db.refresh(decision)

            # Audit decision
            log_audit_event(
                db=db,
                user_name=reviewer_user.username,
                action=f"DECISION_{dinfo['action'].upper().replace(' ', '_')}",
                entity_type="Decision",
                entity_id=p.proposal_code,
                details={
                    "proposal_code": p.proposal_code,
                    "action": dinfo["action"],
                    "reason": dinfo["reason"],
                    "reviewer": reviewer_user.full_name
                },
                user_id=reviewer_user.id
            )

    # 3. Connect parent-child resubmission relationships
    for pdata in raw_proposals:
        if pdata.get("parent_code"):
            p = proposal_objs[pdata["code"]]
            parent = proposal_objs.get(pdata["parent_code"])
            if parent:
                p.parent_proposal_id = parent.id
                db.commit()

    print(f"Puducherry Police repository seeded successfully with {len(raw_proposals)} proposals and chained audit logs.")
