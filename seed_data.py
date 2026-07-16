"""
Canonical CONCOR terminal seed data (committed to git).

Dummy container counts for demo charts — full terminal names (no abbreviations).
Used when ports.db is missing or empty on a new machine.
INSERT OR IGNORE when the table is empty (does not wipe local edits unless you reseed).
"""

# (port_terminal full name, containers) — 60 CONCOR-style ICDs / CFS / port terminals
SEED_PORTS: list[tuple[str, int]] = [
    # North & NCR (high volume hubs)
    ("ICD Tughlakabad, New Delhi", 14230),
    ("ICD Dadri, Greater Noida", 13680),
    ("ICD Ballabhgarh, Haryana", 11875),
    ("ICD Rai Sonepat, Haryana", 10250),
    ("ICD Panipat, Haryana", 9640),
    ("ICD Dhandari Kalan, Ludhiana", 9480),
    ("ICD Moradabad, Uttar Pradesh", 8950),
    ("ICD Agra, Uttar Pradesh", 8410),
    ("Multi Modal Logistics Park Kanpur", 8320),
    ("ICD Malanpur, Madhya Pradesh", 8155),
    # West — Gujarat & Maharashtra
    ("ICD Sabarmati, Ahmedabad", 12540),
    ("ICD Khodiyar, Ahmedabad", 10820),
    ("CFS Dronagiri, Navi Mumbai", 11560),
    ("CONCOR Port Terminal, Jawaharlal Nehru Port", 12200),
    ("ICD Mulund, Mumbai", 9340),
    ("ICD Vadodara, Gujarat", 7920),
    ("ICD Ankleshwar, Gujarat", 7640),
    ("ICD Gandhidham, Gujarat", 8855),
    ("ICD Morbi, Gujarat", 7120),
    ("MMLP Balli, Goa", 5480),
    ("ICD Bhusawal, Maharashtra", 6210),
    ("ICD Nagpur Container Terminal", 8740),
    ("ICD Pune, Maharashtra", 7560),
    ("ICD Aurangabad, Maharashtra", 5890),
    # South
    ("ICD Whitefield, Bengaluru", 11240),
    ("ICD Irugur, Coimbatore", 8360),
    ("ICD Sanathnagar, Hyderabad", 9780),
    ("ICD Thimmapur, Hyderabad", 8120),
    ("CFS Tuticorin, Tamil Nadu", 9240),
    ("ICD Chennai Port Side Terminal", 10580),
    ("ICD Tondiarpet, Chennai", 8670),
    ("CFS Cochin, Kerala", 7340),
    ("ICD Mangalore, Karnataka", 6890),
    ("ICD Hosur, Tamil Nadu", 6520),
    ("ICD Krishnapatnam, Andhra Pradesh", 7980),
    ("CFS Visakhapatnam, Andhra Pradesh", 8450),
    ("ICD Kakinada, Andhra Pradesh", 6120),
    ("ICD Madurai, Tamil Nadu", 5740),
    # East & Central
    ("ICD Kolkata Dock Terminal", 9120),
    ("ICD Shalimar, Howrah", 7840),
    ("ICD Amingaon, Guwahati", 4980),
    ("ICD Jamshedpur, Jharkhand", 6650),
    ("ICD Raxaul, Bihar", 5320),
    ("ICD Patna, Bihar", 6010),
    ("ICD Raipur, Chhattisgarh", 7280),
    ("ICD Naya Raipur, Chhattisgarh", 5940),
    ("ICD Bhubaneswar, Odisha", 6410),
    ("ICD Paradip Port Terminal", 7020),
    ("ICD Haldia, West Bengal", 7580),
    # Rajasthan & others
    ("ICD Jaipur, Rajasthan", 8210),
    ("ICD Jodhpur, Rajasthan", 6930),
    ("ICD Kota, Rajasthan", 5640),
    ("ICD Bhiwadi, Rajasthan", 6125),
    ("ICD Udaipur, Rajasthan", 5210),
    ("ICD Baddi, Himachal Pradesh", 4870),
    ("ICD Mandideep, Madhya Pradesh", 6380),
    ("ICD Indore Pithampur, Madhya Pradesh", 7710),
    ("ICD Rewari, Haryana", 8540),
    ("ICD Faridabad, Haryana", 8020),
    ("CFS Amritsar, Punjab", 5560),
]
