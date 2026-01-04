# seed_data.py (extended with categories, officers, ads)
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
services_col = db["services"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]

# Clear existing data
services_col.delete_many({})
categories_col.delete_many({})
officers_col.delete_many({})
ads_col.delete_many({})

# Seed categories
categories = [
    {"id": "cat_it", "name": {"en": "IT & Digital", "si": "තොරතුරු/ඩිජිටල්", "ta": "தகவல் மற்றும் டிஜிடல்"}, "ministry_ids": ["ministry_it"]},
    {"id": "cat_education", "name": {"en": "Education", "si": "අධ්‍යාපනය", "ta": "கல்வி"}, "ministry_ids": ["ministry_education"]},
    {"id": "cat_health", "name": {"en": "Health", "si": "සෞඛ්‍ය", "ta": "சுகாதாரம்"}, "ministry_ids": ["ministry_health"]},
    {"id": "cat_transport", "name": {"en": "Transport", "si": "ප්‍රවාහනය", "ta": "போக்குவரத்து"}, "ministry_ids": ["ministry_transport"]},
    {"id": "cat_immigration", "name": {"en": "Immigration", "si": "ආගමන", "ta": "குடிவரவு"}, "ministry_ids": ["ministry_imm"]},
    {"id": "cat_foreign", "name": {"en": "Foreign Affairs", "si": "විදේශ කටයුතු", "ta": "வெளியுறவு"}, "ministry_ids": ["ministry_foreign"]},
    {"id": "cat_finance", "name": {"en": "Finance", "si": "මුදල්", "ta": "நிதி"}, "ministry_ids": ["ministry_finance"]},
    {"id": "cat_labour", "name": {"en": "Labour", "si": "කම්කරු", "ta": "தொழிலாளர்"}, "ministry_ids": ["ministry_labour"]},
    {"id": "cat_public", "name": {"en": "Public Administration", "si": "රාජ්‍ය පරිපාලන", "ta": "பொது நிர்வாகம்"}, "ministry_ids": ["ministry_public"]},
    {"id": "cat_justice", "name": {"en": "Justice", "si": "යුක්තිය", "ta": "நீதி"}, "ministry_ids": ["ministry_justice"]},
    {"id": "cat_land", "name": {"en": "Land & Housing", "si": "භූමි/නිවාස", "ta": "நிலம் மற்றும் வீடுகள்"}, "ministry_ids": ["ministry_housing", "ministry_land"]},
    {"id": "cat_agriculture", "name": {"en": "Agriculture", "si": "කෘෂිකර්ම", "ta": "விவசாயம்"}, "ministry_ids": ["ministry_agri"]},
    {"id": "cat_youth", "name": {"en": "Youth Affairs", "si": "තරුණ කටයුතු", "ta": "இளைஞர் விவகாரம்"}, "ministry_ids": ["ministry_youth"]},
    {"id": "cat_defence", "name": {"en": "Defence", "si": "ආරක්ෂාව", "ta": "பாதுகாப்பு"}, "ministry_ids": ["ministry_defence"]},
    {"id": "cat_tourism", "name": {"en": "Tourism", "si": "සංචාරක", "ta": "சுற்றுலா"}, "ministry_ids": ["ministry_tourism"]},
    {"id": "cat_trade", "name": {"en": "Industry & Trade", "si": "කර්මාන්ත හා වෙළඳ", "ta": "தொழில் மற்றும் வர்த்தகம்"}, "ministry_ids": ["ministry_trade"]},
    {"id": "cat_energy", "name": {"en": "Power & Energy", "si": "බලශක්ති", "ta": "மின்சாரம் மற்றும் எரிசக்தி"}, "ministry_ids": ["ministry_energy"]},
    {"id": "cat_water", "name": {"en": "Water Supply", "si": "ජල සම්පාදන", "ta": "நீர் வழங்கல்"}, "ministry_ids": ["ministry_water"]},
    {"id": "cat_environment", "name": {"en": "Environment", "si": "පරිසරය", "ta": "சுற்றுச்சூழல்"}, "ministry_ids": ["ministry_env"]},
    {"id": "cat_culture", "name": {"en": "Culture", "si": "සංස්කෘතික", "ta": "கலாச்சாரம்"}, "ministry_ids": ["ministry_culture"]}
]
categories_col.insert_many(categories)
print(f"✅ Seeded {len(categories)} categories")

# Seed officers
officers = [
    {"id": "off_it_01", "name": "Ms. Nayana Perera", "role": "Director - Digital Services", "ministry_id": "ministry_it", "contact": {"email": "nayana@it.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_it_02", "name": "Mr. Amal Fernando", "role": "Deputy Director - IT Certificates", "ministry_id": "ministry_it", "contact": {"email": "amal@it.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_edu_01", "name": "Dr. Kamal Jayasinghe", "role": "Secretary - Education", "ministry_id": "ministry_education", "contact": {"email": "kamal@edu.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_health_01", "name": "Dr. Priya Kumar", "role": "Director - Health Services", "ministry_id": "ministry_health", "contact": {"email": "priya@health.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_transport_01", "name": "Mr. Ruwan Silva", "role": "Commissioner - Motor Traffic", "ministry_id": "ministry_transport", "contact": {"email": "ruwan@transport.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_imm_01", "name": "Ms. Thilini Perera", "role": "Controller - Immigration", "ministry_id": "ministry_imm", "contact": {"email": "thilini@immigration.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_finance_01", "name": "Mr. Nimal Gunasekera", "role": "Director - Inland Revenue", "ministry_id": "ministry_finance", "contact": {"email": "nimal@finance.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_labour_01", "name": "Ms. Dilani Wijesinghe", "role": "Commissioner of Labour", "ministry_id": "ministry_labour", "contact": {"email": "dilani@labour.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_public_01", "name": "Mr. Saman Bandara", "role": "Secretary - Public Admin", "ministry_id": "ministry_public", "contact": {"email": "saman@publicadmin.gov.lk", "phone": "011-2XXXXXX"}},
    {"id": "off_justice_01", "name": "Ms. Ramani Jayawardena", "role": "Registrar General", "ministry_id": "ministry_justice", "contact": {"email": "ramani@justice.gov.lk", "phone": "011-2XXXXXX"}}
]
officers_col.insert_many(officers)
print(f"✅ Seeded {len(officers)} officers")

# Seed ads/announcements
ads = [
    {"id": "ad_courses_01", "title": "Free Digital Skills Course", "body": "Enroll now for government digital skills training. Limited seats available for citizens.", "link": "https://digitalskills.gov.lk/courses", "image": "/static/img/course-card.png", "active": True},
    {"id": "ad_exams_01", "title": "Exam Results Portal", "body": "Check latest A/L and O/L exam results online. Fast and secure access.", "link": "https://doenets.lk/results", "active": True},
    {"id": "ad_passport_01", "title": "Online Passport Application", "body": "Apply for your passport online and track application status 24/7.", "link": "https://epassport.gov.lk", "active": True},
    {"id": "ad_tax_01", "title": "e-Filing Tax Returns", "body": "File your income tax returns online before the deadline. Save time!", "link": "https://ird.gov.lk/efiling", "active": True},
    {"id": "ad_job_fair_01", "title": "National Job Fair 2026", "body": "1000+ job opportunities. Register now for the largest government job fair.", "link": "https://jobfair.gov.lk", "active": True},
    {"id": "ad_training_01", "title": "Vocational Training Programs", "body": "Free vocational training in IT, Hospitality, and Construction sectors.", "link": "https://vocational.gov.lk", "active": True}
]
ads_col.insert_many(ads)
print(f"✅ Seeded {len(ads)} ads/announcements")

# Comprehensive set of 20 ministries with subservices (with category field)
docs = [
    {
        "id": "ministry_it",
        "category": "cat_it",
        "name": {"en": "Ministry of IT & Digital Affairs", "si": "තොරතුරු තාක්ෂණ අමාත්‍යංශය", "ta": "தகவல் தொழில்நுட்ப அமைச்சு"},
        "subservices": [
            {"id": "it_cert", "name": {"en": "IT Certificates", "si": "අයිටී සහතික", "ta": "ஐடி சான்றிதழ்கள்"},
             "questions": [
                 {"q": {"en": "How to apply for an IT certificate?", "si": "IT සහතිකය සඳහා ඉල්ලීම් කරන ආකාරය?", "ta": "ஐடி சான்றிதழுக்கு விண்ணப்பிப்பது எப்படி?"},
                  "answer": {"en": "Fill online form and upload NIC.", "si": "ඔන්ලයින් ෆෝරමය පිරවුවාට සහ NIC උඩුගත කරන්න.", "ta": "ஆன்லைனில் படிவத்தை நிரப்பி NIC ஐ பதிவேற்று."},
                  "downloads": ["/static/forms/it_cert_form.pdf"],
                  "location": "https://maps.google.com/?q=Ministry+of+IT",
                  "instructions": "Visit the digital portal, register and submit application."}
             ]}
        ]
    },
    {
        "id": "ministry_education",
        "category": "cat_education",
        "name": {"en": "Ministry of Education", "si": "අධ්‍යාපන අමාත්‍යංශය", "ta": "கல்வி அமைச்சு"},
        "subservices": [
            {"id": "schools", "name": {"en": "Schools", "si": "පාසල්", "ta": "பள்ளிகள்"},
             "questions": [
                 {"q": {"en": "How to register a school?", "si": "පාසලක් ලියා දංචි කිරීම?", "ta": "பள்ளியை பதிவு செய்வது எப்படி?"},
                  "answer": {"en": "Complete registration form and submit documents.", "si": "ලියා දංචි ෆෝරමය පුරවා ලේඛන දමන්න.", "ta": "பதிவு படிவத்தை பூர்த்தி செய்து ஆவணங்களை சமர்ப்பிக்கவும்."},
                  "downloads": ["/static/forms/school_reg.pdf"],
                  "location": "https://maps.google.com/?q=Ministry+of+Education",
                  "instructions": "Follow the guidelines on the education portal."}
             ]},
            {"id": "exams", "name": {"en": "Exams & Results", "si": "විභාග & ප්‍රතිඵල", "ta": "பரீட்சைகள் மற்றும் முடிவுகள்"},
             "questions": [
                 {"q": {"en": "How to apply for national exam?", "si": "ජාතික විභාගයට අයදුම් කරන ආකාරය?", "ta": "தேசிய தேர்விற்கு எப்படி விண்ணப்பிப்பது?"},
                  "answer": {"en": "Register via examination portal.", "si": "විභාග පෝර්ටල් හරහා ලියා දංචි වන්න.", "ta": "பரீட்சை போர்ட்டலின் மூலம் பதிவு செய்யவும்."},
                  "downloads": [], "location": "", "instructions": "Check exam schedule and fee."},
                 {"q": {"en": "Where can I download exam results?", "si": "විභාග ප්‍රතිඵල බාගත කරන්නේ කොහෙන්ද?", "ta": "தேர்வு முடிவுகளை எங்கே பதிவிறக்கம் செய்யலாம்?"},
                  "answer": {"en": "Visit doenets.lk for official exam results.", "si": "නිල විභාග ප්‍රතිඵල සඳහා doenets.lk වෙත පිවිසෙන්න.", "ta": "அதிகாரப்பூர்வ தேர்வு முடிவுகளுக்கு doenets.lk ஐப் பார்வையிடவும்."},
                  "downloads": [], "location": "https://doenets.lk", "instructions": "Enter your index number to view results."}
             ]}
        ]
    },
    {
        "id": "ministry_health",
        "category": "cat_health",
        "name": {"en": "Ministry of Health", "si": "සෞඛ්‍ය අමාත්‍යංශය", "ta": "சுகாதார அமைச்சு"},
        "subservices": [
            {"id": "health_general", "name": {"en": "General Health Services", "si": "සාමාන්‍ය සෞඛ්‍ය සේවා", "ta": "பொது சுகாதார சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to get a medical certificate?", "si": "වෛද්‍ය සහතිකයක් ලබා ගන්නේ කෙසේද?", "ta": "மருத்துவ சான்றிதழ் பெறுவது எப்படி?"},
                  "answer": {"en": "Visit nearest government hospital with NIC.", "si": "ජාතික හැඳුනුම්පත සමඟ ආසන්නතම රජයේ රෝහල වෙත යන්න.", "ta": "தேசிய அடையாள அட்டையுடன் அருகிலுள்ள அரசு மருத்துவமனைக்கு செல்லவும்."},
                  "downloads": [], "location": "https://maps.google.com/?q=Government+Hospital", "instructions": "Bring NIC and previous medical records if any."}
             ]}
        ]
    },
    {
        "id": "ministry_transport",
        "category": "cat_transport",
        "name": {"en": "Ministry of Transport", "si": "ප්‍රවාහන අමාත්‍යංශය", "ta": "போக்குவரத்து அமைச்சு"},
        "subservices": [
            {"id": "driving_license", "name": {"en": "Driving License", "si": "රියදුරු බලපත්‍රය", "ta": "ஓட்டுநர் உரிமம்"},
             "questions": [
                 {"q": {"en": "How to apply for a driving license?", "si": "රියදුරු බලපත්‍රයක් සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "ஓட்டுநர் உரிமத்திற்கு விண்ணப்பிப்பது எப்படி?"},
                  "answer": {"en": "Complete application form at DMT office.", "si": "DMT කාර්යාලයේ අයදුම්පත් පුරවන්න.", "ta": "DMT அலுவலகத்தில் விண்ணப்ப படிவத்தை பூர்த்தி செய்யவும்."},
                  "downloads": ["/static/forms/driving_license.pdf"], "location": "https://maps.google.com/?q=DMT+Office", "instructions": "Bring NIC, medical certificate, and passport photos."}
             ]}
        ]
    },
    {
        "id": "ministry_imm",
        "category": "cat_immigration",
        "name": {"en": "Ministry of Immigration", "si": "ආගමන හා විගමන අමාත්‍යංශය", "ta": "குடிவரவு அமைச்சு"},
        "subservices": [
            {"id": "passport", "name": {"en": "Passport Services", "si": "ගමන් බලපත්‍ර සේවා", "ta": "கடவுச்சீட்டு சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to apply for a passport?", "si": "ගමන් බලපත්‍රයක් සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "கடவுச்சீட்டுக்கு விண்ணப்பிப்பது எப்படி?"},
                  "answer": {"en": "Apply online and visit immigration office for biometrics.", "si": "ඔන්ලයින් අයදුම් කර ජීව මිතික සඳහා ආගමන කාර්යාලයට යන්න.", "ta": "ஆன்லைனில் விண்ணப்பித்து பயோமெட்ரிக்ஸுக்காக குடிவரவு அலுவலகத்திற்கு செல்லவும்."},
                  "downloads": ["/static/forms/passport_form.pdf"], "location": "https://maps.google.com/?q=Immigration+Office", "instructions": "Bring birth certificate, NIC, and proof of address."},
                 {"q": {"en": "What is the process for passport renewal?", "si": "ගමන් බලපත්‍රය අලුත් කිරීමේ ක්‍රියාවලිය කුමක්ද?", "ta": "கடவுச்சீட்டு புதுப்பிப்பு செயல்முறை என்ன?"},
                  "answer": {"en": "Apply online at immigration.gov.lk, submit old passport and new photos.", "si": "immigration.gov.lk හි ඔන්ලයින් අයදුම් කරන්න, පැරණි ගමන් බලපත්‍රය සහ නව ඡායාරූප ඉදිරිපත් කරන්න.", "ta": "immigration.gov.lk இல் ஆன்லைனில் விண்ணப்பிக்கவும், பழைய கடவுச்சீட்டு மற்றும் புதிய புகைப்படங்களை சமர்ப்பிக்கவும்."},
                  "downloads": [], "location": "https://immigration.gov.lk", "instructions": "Processing takes 2-3 weeks."}
             ]}
        ]
    },
    {
        "id": "ministry_foreign",
        "category": "cat_foreign",
        "name": {"en": "Ministry of Foreign Affairs", "si": "විදේශ කටයුතු අමාත්‍යංශය", "ta": "வெளியுறவு அமைச்சு"},
        "subservices": [
            {"id": "visa", "name": {"en": "Visa Services", "si": "වීසා සේවා", "ta": "விசா சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to get a visa for travel?", "si": "සංචාරය සඳහා වීසා ලබා ගන්නේ කෙසේද?", "ta": "பயணத்திற்கு விசா பெறுவது எப்படி?"},
                  "answer": {"en": "Apply through embassy website of destination country.", "si": "ගමනාන්ත රටේ තානාපති කාර්යාල වෙබ් අඩවිය හරහා අයදුම් කරන්න.", "ta": "இலக்கு நாட்டின் தூதரக வலைத்தளம் மூலம் விண்ணப்பிக்கவும்."},
                  "downloads": [], "location": "", "instructions": "Check specific embassy requirements."}
             ]}
        ]
    },
    {
        "id": "ministry_finance",
        "category": "cat_finance",
        "name": {"en": "Ministry of Finance", "si": "මුදල් අමාත්‍යංශය", "ta": "நிதி அமைச்சு"},
        "subservices": [
            {"id": "tax", "name": {"en": "Tax Services", "si": "බදු සේවා", "ta": "வரி சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to file income tax?", "si": "ආදායම් බදු ගොනු කරන්නේ කෙසේද?", "ta": "வருமான வரி தாக்கல் செய்வது எப்படி?"},
                  "answer": {"en": "Register on Inland Revenue portal and submit returns online.", "si": "අභ්‍යන්තර ආදායම් පෝර්ටලයේ ලියාපදිංචි වී ඔන්ලයින් ප්‍රතිලාභ ඉදිරිපත් කරන්න.", "ta": "உள்நாட்டு வருவாய் போர்ட்டலில் பதிவு செய்து ஆன்லைனில் வருமானத்தை சமர்ப்பிக்கவும்."},
                  "downloads": ["/static/forms/tax_form.pdf"], "location": "", "instructions": "Keep all income documents ready."}
             ]}
        ]
    },
    {
        "id": "ministry_labour",
        "category": "cat_labour",
        "name": {"en": "Ministry of Labour", "si": "කම්කරු අමාත්‍යංශය", "ta": "தொழிலாளர் அமைச்சு"},
        "subservices": [
            {"id": "employment", "name": {"en": "Employment Services", "si": "රැකියා සේවා", "ta": "வேலைவாய்ப்பு சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to register for job placement?", "si": "රැකියා ස්ථානගත කිරීම සඳහා ලියාපදිංචි වන්නේ කෙසේද?", "ta": "வேலை வாய்ப்புக்கு பதிவு செய்வது எப்படி?"},
                  "answer": {"en": "Visit nearest employment exchange office.", "si": "ආසන්නතම රැකියා හුවමාරු කාර්යාලයට යන්න.", "ta": "அருகிலுள்ள வேலைவாய்ப்பு பரிமாற்ற அலுவலகத்திற்கு செல்லவும்."},
                  "downloads": [], "location": "https://maps.google.com/?q=Employment+Office", "instructions": "Bring educational certificates and NIC."}
             ]}
        ]
    },
    {
        "id": "ministry_public",
        "category": "cat_public",
        "name": {"en": "Ministry of Public Administration", "si": "රාජ්‍ය පරිපාලන අමාත්‍යංශය", "ta": "பொது நிர்வாக அமைச்சு"},
        "subservices": [
            {"id": "nic", "name": {"en": "NIC Services", "si": "ජාතික හැඳුනුම්පත් සේවා", "ta": "தேசிய அடையாள அட்டை சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to change my NIC details?", "si": "මගේ NIC තොරතුරු වෙනස් කරන්නේ කෙසේද?", "ta": "எனது NIC விவரங்களை மாற்றுவது எப்படி?"},
                  "answer": {"en": "Submit application with supporting documents to Registrar of Persons office.", "si": "පුද්ගලයින් ලියාපදිංචි කිරීමේ කාර්යාලයට ආධාරක ලියවිලි සමඟ අයදුම්පත ඉදිරිපත් කරන්න.", "ta": "ஆதார ஆவணங்களுடன் விண்ணப்பத்தை நபர்கள் பதிவாளர் அலுவலகத்தில் சமர்ப்பிக்கவும்."},
                  "downloads": [], "location": "https://maps.google.com/?q=Registrar+of+Persons", "instructions": "Bring original documents for verification."}
             ]},
            {"id": "public_general", "name": {"en": "General Services", "si": "සාමාන්‍ය සේවා", "ta": "பொதுச் சேவைகள்"},
             "questions": [
                 {"q": {"en": "What services are offered?", "si": "ඔබට ලබාදෙන සේවාවන් මොනවාද?", "ta": "கொடுக்கப்படும் சேவைகள் என்ன?"},
                  "answer": {"en": "Please check the service list on the portal.", "si": "පෝර්ටලයේහි සේවා ලැයිස්තුව බලන්න.", "ta": "போர்ட்டலில் சேவை பட்டியலை பார்க்கவும்."},
                  "downloads": [], "location": "", "instructions": "Use contact details to get more info."}
             ]}
        ]
    },
    {
        "id": "ministry_justice",
        "category": "cat_justice",
        "name": {"en": "Ministry of Justice", "si": "යුක්ති අමාත්‍යංශය", "ta": "நீதி அமைச்சு"},
        "subservices": [
            {"id": "legal", "name": {"en": "Legal Services", "si": "නීතිමය සේවා", "ta": "சட்ட சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to get legal aid?", "si": "නීති ආධාර ලබා ගන්නේ කෙසේද?", "ta": "சட்ட உதவி பெறுவது எப்படி?"},
                  "answer": {"en": "Contact Legal Aid Commission.", "si": "නීති ආධාර කොමිෂන් සභාව අමතන්න.", "ta": "சட்ட உதவி ஆணையத்தை தொடர்பு கொள்ளவும்."},
                  "downloads": [], "location": "https://maps.google.com/?q=Legal+Aid+Commission", "instructions": "Bring relevant documents and NIC."}
             ]}
        ]
    },
    {
        "id": "ministry_housing",
        "category": "cat_land",
        "name": {"en": "Ministry of Housing", "si": "නිවාස අමාත්‍යංශය", "ta": "வீட்டுவசதி அமைச்சு"},
        "subservices": [
            {"id": "housing_schemes", "name": {"en": "Housing Schemes", "si": "නිවාස යෝජනා ක්‍රම", "ta": "வீட்டுவசதி திட்டங்கள்"},
             "questions": [
                 {"q": {"en": "How to apply for government housing?", "si": "රජයේ නිවාස සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "அரசு வீட்டுவசதிக்கு விண்ணப்பிப்பது எப்படி?"},
                  "answer": {"en": "Fill application at housing ministry office.", "si": "නිවාස අමාත්‍යාංශ කාර්යාලයේ අයදුම්පත් පුරවන්න.", "ta": "வீட்டுவசதி அமைச்சு அலுவலகத்தில் விண்ணப்பத்தை பூர்த்தி செய்யவும்."},
                  "downloads": ["/static/forms/housing_form.pdf"], "location": "https://maps.google.com/?q=Housing+Ministry", "instructions": "Bring income proof and NIC."},
                 {"q": {"en": "How to apply for a building permit?", "si": "ගොඩනැගිලි අවසරයක් සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "கட்டிட அனுமதிக்கு விண்ணப்பிப்பது எப்படி?"},
                  "answer": {"en": "Submit building plans to local authority with application form.", "si": "අයදුම්පත සමඟ ප්‍රාදේශීය බලධාරියට ගොඩනැගිලි සැලසුම් ඉදිරිපත් කරන්න.", "ta": "விண்ணப்ப படிவத்துடன் கட்டிட திட்டங்களை உள்ளூர் அதிகாரிகளிடம் சமர்ப்பிக்கவும்."},
                  "downloads": [], "location": "", "instructions": "Include land ownership documents."}
             ]}
        ]
    },
    {
        "id": "ministry_agri",
        "category": "cat_agriculture",
        "name": {"en": "Ministry of Agriculture", "si": "කෘෂිකර්ම අමාත්‍යංශය", "ta": "விவசாய அமைச்சு"},
        "subservices": [
            {"id": "farming", "name": {"en": "Farming Support", "si": "ගොවිතැන් සහාය", "ta": "விவசாய ஆதரவு"},
             "questions": [
                 {"q": {"en": "How to get farming subsidies?", "si": "ගොවිතැන් සහනාධාර ලබා ගන්නේ කෙසේද?", "ta": "விவசாய மானியங்களை பெறுவது எப்படி?"},
                  "answer": {"en": "Register with Agrarian Service Center.", "si": "ගොවිජන සේවා මධ්‍යස්ථානයේ ලියාපදිංචි වන්න.", "ta": "விவசாய சேவை மையத்தில் பதிவு செய்யவும்."},
                  "downloads": [], "location": "https://maps.google.com/?q=Agrarian+Service+Center", "instructions": "Bring land ownership documents."}
             ]}
        ]
    },
    {
        "id": "ministry_youth",
        "category": "cat_youth",
        "name": {"en": "Ministry of Youth Affairs", "si": "තරුණ කටයුතු අමාත්‍යංශය", "ta": "இளைஞர் விவகார அமைச்சு"},
        "subservices": [
            {"id": "youth_programs", "name": {"en": "Youth Programs", "si": "තරුණ වැඩසටහන්", "ta": "இளைஞர் திட்டங்கள்"},
             "questions": [
                 {"q": {"en": "What youth programs are available?", "si": "තරුණ වැඩසටහන් මොනවාද?", "ta": "இளைஞர் திட்டங்கள் என்ன?"},
                  "answer": {"en": "Check youth ministry website for current programs.", "si": "වත්මන් වැඩසටහන් සඳහා තරුණ අමාත්‍යාංශ වෙබ් අඩවිය පරීක්ෂා කරන්න.", "ta": "தற்போதைய திட்டங்களுக்கு இளைஞர் அமைச்சு வலைத்தளத்தை சரிபார்க்கவும்."},
                  "downloads": [], "location": "", "instructions": "Visit youth ministry portal."},
                 {"q": {"en": "What training courses are available in digital skills?", "si": "ඩිජිටල් කුසලතා පිළිබඳ පුහුණු පාඨමාලා මොනවාද?", "ta": "டிஜிட்டல் திறன்களில் என்ன பயிற்சி படிப்புகள் உள்ளன?"},
                  "answer": {"en": "Free digital skills courses available through ICTA and youth ministry programs.", "si": "ICTA සහ තරුණ අමාත්‍යාංශ වැඩසටහන් හරහා නොමිලේ ඩිජිටල් කුසලතා පාඨමාලා ලබාගත හැකිය.", "ta": "ICTA மற்றும் இளைஞர் அமைச்சு திட்டங்கள் மூலம் இலவச டிஜிட்டல் திறன் படிப்புகள் கிடைக்கின்றன."},
                  "downloads": [], "location": "https://icta.lk/training", "instructions": "Register online on ICTA website."}
             ]}
        ]
    },
    {
        "id": "ministry_defence",
        "category": "cat_defence",
        "name": {"en": "Ministry of Defence", "si": "ආරක්ෂක අමාත්‍යංශය", "ta": "பாதுகாப்பு அமைச்சு"},
        "subservices": [
            {"id": "defence_general", "name": {"en": "General Services", "si": "සාමාන්‍ය සේවා", "ta": "பொதுச் சேவைகள்"},
             "questions": [
                 {"q": {"en": "What services are offered?", "si": "ඔබට ලබාදෙන සේවාවන් මොනවාද?", "ta": "கொடுக்கப்படும் சேவைகள் என்ன?"},
                  "answer": {"en": "Please check the service list on the portal.", "si": "පෝර්ටලයේහි සේවා ලැයිස්තුව බලන්න.", "ta": "போர்ட்டலில் சேவை பட்டியலை பார்க்கவும்."},
                  "downloads": [], "location": "", "instructions": "Use contact details to get more info."}
             ]}
        ]
    },
    {
        "id": "ministry_tourism",
        "category": "cat_tourism",
        "name": {"en": "Ministry of Tourism", "si": "සංචාරක අමාත්‍යංශය", "ta": "சுற்றுலா அமைச்சு"},
        "subservices": [
            {"id": "tourism_info", "name": {"en": "Tourism Information", "si": "සංචාරක තොරතුරු", "ta": "சுற்றுலா தகவல்"},
             "questions": [
                 {"q": {"en": "How to get tourist guide license?", "si": "සංචාරක මාර්ගෝපදේශක බලපත්‍රය ලබා ගන්නේ කෙසේද?", "ta": "சுற்றுலா வழிகாட்டி உரிமம் பெறுவது எப்படி?"},
                  "answer": {"en": "Apply through tourism ministry website.", "si": "සංචාරක අමාත්‍යාංශ වෙබ් අඩවිය හරහා අයදුම් කරන්න.", "ta": "சுற்றுலா அமைச்சு வலைத்தளம் மூலம் விண்ணப்பிக்கவும்."},
                  "downloads": ["/static/forms/tourist_guide.pdf"], "location": "", "instructions": "Complete training course first."}
             ]}
        ]
    },
    {
        "id": "ministry_trade",
        "category": "cat_trade",
        "name": {"en": "Ministry of Industry & Trade", "si": "කර්මාන්ත හා වෙළඳ අමාත්‍යංශය", "ta": "தொழில் மற்றும் வர்த்தக அமைச்சு"},
        "subservices": [
            {"id": "business_reg", "name": {"en": "Business Registration", "si": "ව්‍යාපාර ලියාපදිංචිය", "ta": "வணிக பதிவு"},
             "questions": [
                 {"q": {"en": "How to register a business?", "si": "ව්‍යාපාරයක් ලියාපදිංචි කරන්නේ කෙසේද?", "ta": "வணிகத்தை பதிவு செய்வது எப்படி?"},
                  "answer": {"en": "Register online through ROC website.", "si": "ROC වෙබ් අඩවිය හරහා ඔන්ලයින් ලියාපදිංචි වන්න.", "ta": "ROC வலைத்தளம் மூலம் ஆன்லைனில் பதிவு செய்யவும்."},
                  "downloads": ["/static/forms/business_reg.pdf"], "location": "", "instructions": "Prepare business plan and required documents."}
             ]}
        ]
    },
    {
        "id": "ministry_energy",
        "category": "cat_energy",
        "name": {"en": "Ministry of Power & Energy", "si": "බලශක්ති අමාත්‍යංශය", "ta": "மின்சாரம் மற்றும் எரிசக்தி அமைச்சு"},
        "subservices": [
            {"id": "electricity", "name": {"en": "Electricity Services", "si": "විදුලි සේවා", "ta": "மின்சார சேவைகள்"},
             "questions": [
                 {"q": {"en": "How to get new electricity connection?", "si": "නව විදුලි සම්බන්ධතාවයක් ලබා ගන්නේ කෙසේද?", "ta": "புதிய மின்சார இணைப்பு பெறுவது எப்படி?"},
                  "answer": {"en": "Apply through CEB office.", "si": "CEB කාර්යාලය හරහා අයදුම් කරන්න.", "ta": "CEB அலுவலகம் மூலம் விண்ணப்பிக்கவும்."},
                  "downloads": ["/static/forms/electricity_form.pdf"], "location": "https://maps.google.com/?q=CEB+Office", "instructions": "Bring property ownership documents."}
             ]}
        ]
    },
    {
        "id": "ministry_water",
        "category": "cat_water",
        "name": {"en": "Ministry of Water Supply", "si": "ජල සම්පාදන අමාත්‍යංශය", "ta": "நீர் வழங்கல் அமைச்சு"},
        "subservices": [
            {"id": "water_supply", "name": {"en": "Water Connection", "si": "ජල සම්බන්ධතාව", "ta": "நீர் இணைப்பு"},
             "questions": [
                 {"q": {"en": "How can I get water connection?", "si": "ජල සම්බන්ධතාවයක් ලබා ගන්නේ කෙසේද?", "ta": "நீர் இணைப்பு பெறுவது எப்படி?"},
                  "answer": {"en": "Apply at NWSDB office.", "si": "NWSDB කාර්යාලයේ අයදුම් කරන්න.", "ta": "NWSDB அலுவலகத்தில் விண்ணப்பிக்கவும்."},
                  "downloads": ["/static/forms/water_form.pdf"], "location": "https://maps.google.com/?q=NWSDB+Office", "instructions": "Bring property documents and NIC."}
             ]}
        ]
    },
    {
        "id": "ministry_env",
        "category": "cat_environment",
        "name": {"en": "Ministry of Environment", "si": "පරිසර අමාත්‍යංශය", "ta": "சுற்றுச்சூழல் அமைச்சு"},
        "subservices": [
            {"id": "env_permits", "name": {"en": "Environmental Permits", "si": "පාරිසරික බලපත්‍ර", "ta": "சுற்றுச்சூழல் அனுமதிகள்"},
             "questions": [
                 {"q": {"en": "How to get environmental clearance?", "si": "පාරිසරික අනුමැතිය ලබා ගන්නේ කෙසේද?", "ta": "சுற்றுச்சூழல் அனுமதி பெறுவது எப்படி?"},
                  "answer": {"en": "Submit project proposal to CEA.", "si": "CEA වෙත ව්‍යාපෘති යෝජනාව ඉදිරිපත් කරන්න.", "ta": "CEA க்கு திட்ட முன்மொழிவை சமர்ப்பிக்கவும்."},
                  "downloads": [], "location": "https://maps.google.com/?q=CEA+Office", "instructions": "Prepare environmental impact assessment."}
             ]}
        ]
    },
    {
        "id": "ministry_culture",
        "category": "cat_culture",
        "name": {"en": "Ministry of Culture", "si": "සංස්කෘතික අමාත්‍යංශය", "ta": "கலாச்சார அமைச்சு"},
        "subservices": [
            {"id": "cultural_events", "name": {"en": "Cultural Events", "si": "සංස්කෘතික උත්සව", "ta": "கலாச்சார நிகழ்வுகள்"},
             "questions": [
                 {"q": {"en": "What cultural events are available?", "si": "සංස්කෘතික උත්සව මොනවාද?", "ta": "கலாச்சார நிகழ்வுகள் என்ன?"},
                  "answer": {"en": "Check ministry website for event calendar.", "si": "උත්සව දින දර්ශනය සඳහා අමාත්‍යාංශ වෙබ් අඩවිය පරීක්ෂා කරන්න.", "ta": "நிகழ்வு காலண்டருக்கு அமைச்சு வலைத்தளத்தை சரிபார்க்கவும்."},
                  "downloads": [], "location": "", "instructions": "Visit cultural ministry portal."}
             ]}
        ]
    },
    {
        "id": "ministry_road_safety",
        "category": "cat_transport",
        "name": {"en": "Road Safety Authority", "si": "මාර්ග ආරක්ෂණ අධිකාරිය", "ta": "சாலை பாதுகாப்பு ஆணையம்"},
        "subservices": [
            {"id": "road_safety", "name": {"en": "Road Safety Complaints", "si": "මාර්ග ආරක්ෂණ පැමිණිලි", "ta": "சாலை பாதுகாப்பு புகார்கள்"},
             "questions": [
                 {"q": {"en": "Where to report a road safety complaint?", "si": "මාර්ග ආරක්ෂණ පැමිණිල්ලක් වාර්තා කරන්නේ කොහේද?", "ta": "சாலை பாதுகாப்பு புகாரை எங்கு புகாரளிப்பது?"},
                  "answer": {"en": "Report to nearest police station or call 119.", "si": "ආසන්නතම පොලිස් ස්ථානයට වාර්තා කරන්න හෝ 119 අමතන්න.", "ta": "அருகிலுள்ள காவல் நிலையத்தில் புகாரளிக்கவும் அல்லது 119 ஐ அழைக்கவும்."},
                  "downloads": [], "location": "", "instructions": "Note the location and time of incident."}
             ]}
        ]
    }
]

services_col.insert_many(docs)
print(f"✅ Seeded {services_col.count_documents({})} ministries with services successfully!")

# Build FAISS index automatically
print("\n🔄 Building AI vector index...")
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import json
    import pathlib
    
    # Try to import faiss
    try:
        import faiss
        FAISS_AVAILABLE = True
    except Exception:
        FAISS_AVAILABLE = False
    
    INDEX_PATH = pathlib.Path("./data/faiss.index")
    META_PATH = pathlib.Path("./data/faiss_meta.json")
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Load embedding model
    print("   Loading embedding model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # Build documents for indexing
    docs_to_index = []
    for svc in services_col.find():
        svc_id = svc.get("id")
        svc_name = svc.get("name", {}).get("en") or str(svc.get("name"))
        for sub in svc.get("subservices", []):
            sub_id = sub.get("id")
            sub_name = sub.get("name", {}).get("en") or str(sub.get("name"))
            for q in sub.get("questions", []):
                q_text = q.get("q", {}).get("en") or str(q.get("q"))
                a_text = q.get("answer", {}).get("en") or str(q.get("answer"))
                content = " | ".join([svc_name or "", sub_name or "", q_text or "", a_text or ""])
                docs_to_index.append({
                    "doc_id": f"{svc_id}::{sub_id}::{q_text[:80]}",
                    "service_id": svc_id,
                    "subservice_id": sub_id,
                    "title": q_text,
                    "content": content,
                    "metadata": {
                        "downloads": q.get("downloads", []),
                        "location": q.get("location"),
                        "instructions": q.get("instructions")
                    }
                })
    
    # Create embeddings
    print(f"   Creating embeddings for {len(docs_to_index)} documents...")
    texts = [d["content"] for d in docs_to_index]
    if texts:
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms
        
        if FAISS_AVAILABLE:
            dim = embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(embeddings.astype(np.float32))
            faiss.write_index(index, str(INDEX_PATH))
            print(f"   ✅ FAISS index saved to {INDEX_PATH}")
        else:
            np.save("data/embeddings.npy", embeddings)
            print("   ✅ Embeddings saved (FAISS not available, using fallback)")
        
        # Save metadata
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(docs_to_index, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Metadata saved to {META_PATH}")
        print(f"\n🎉 AI index built successfully with {len(docs_to_index)} documents!")
    else:
        print("   ⚠️ No documents to index")
except Exception as e:
    print(f"   ❌ Error building index: {e}")
    print("   You can manually build the index from the admin panel after running app.py")

print("\n🎉 Seed complete! Run 'python app.py' to start the application.")
