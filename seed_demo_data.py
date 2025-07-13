from pymongo import MongoClient
import os
import time

# --- MongoDB Atlas এর সাথে কানেকশন স্থাপন ---
# আপনার আসল কানেকশন স্ট্রিং এখানে ব্যবহার করুন অথবা এনভায়রনমেন্ট ভ্যারিয়েবল থেকে নিন
MONGO_CONNECTION_STRING = os.environ.get('MONGO_URI', "mongodb+srv://msahid:msahid123@cluster1.s4ndmbd.mongodb.net/")

try:
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client['political_violence_db'] 
    incidents_collection = db['incidents'] 
    print("MongoDB connection successful.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    exit()

# --- ডেমো ডেটার তালিকা ---
# এই ডেটাগুলো বাস্তবসম্মত এবং বাংলাদেশের বিভিন্ন স্থানের উপর ভিত্তি করে তৈরি
demo_incidents = [
    {
  "news_title": "ফেনীতে যুবলীগের দুই সদস্যকে হত্যা",
  "news_url": "https://en.wikipedia.org/wiki/Bangladesh_post-resignation_violence_(2024%E2%80%93present)",
  "source": "Wikipedia",
  "location_name": "ফেনী",
  "latitude": 23.0186,
  "longitude": 91.3966,
  "fatalities": 2,
  "injuries": 0,
  "summary": "ফেনীতে যুবলীগের দুই সদস্যকে হত্যা করা হয়।",
  "incident_date": "2024-08-05 00:00:00",
  "political_party_name": "যুবলীগ (ভুক্তভোগী)"
},{
  "news_title": "বগুড়ায় যুবলীগের দুই নেতাকে হত্যা",
  "news_url": "https://en.wikipedia.org/wiki/Bangladesh_post-resignation_violence_(2024%E2%80%93present)",
  "source": "Wikipedia",
  "location_name": "বগুড়া জেলা",
  "latitude": 24.85,
  "longitude": 89.37,
  "fatalities": 2,
  "injuries": 0,
  "summary": "বগুড়া জেলায় যুবলীগের দুই নেতাকে হত্যা করা হয়।",
  "incident_date": "2024-08-05 00:00:00",
  "political_party_name": "যুবলীগ (ভুক্তভোগী)"
},
{
  "news_title": "পাবনায় টিসিবি কার্ড নিয়ে বিএনপি-জামায়াত সংঘর্ষ, ৮ জন আহত",
  "news_url": "https://en.wikipedia.org/wiki/Bangladesh_post-resignation_violence_(2024%E2%80%93present)",
  "source": "Wikipedia",
  "location_name": "ঈশ্বরদী, পাবনা",
  "latitude": 24.15,
  "longitude": 89.07,
  "fatalities": 0,
  "injuries": 8,
  "summary": "পাবনার ঈশ্বরদীতে টিসিবি (ট্রেডিং কর্পোরেশন অফ বাংলাদেশ) কার্ড বিতরণ নিয়ে বিএনপি ও জামায়াত কর্মীদের মধ্যে গোলাগুলি ও সংঘর্ষে ৮ জন আহত হন।",
  "incident_date": "2024-10-09 00:00:00",
  "political_party_name": "বিএনপি, জামায়াতে ইসলামী"
},
{
  "news_title": "গাজীপুরে শিক্ষার্থী ও আওয়ামী লীগ সমর্থকদের সংঘর্ষে ১ ছাত্র নিহত",
  "news_url": "https://reliefweb.int/report/bangladesh/acled-regional-overview-asia-pacific-march-2025",
  "source": "ACLED",
  "location_name": "গাজীপুর",
  "latitude": 24.0023,
  "longitude": 90.4241,
  "fatalities": 1,
  "injuries": 0,
  "summary": "গাজীপুরে শিক্ষার্থী ও আওয়ামী লীগ সমর্থকদের মধ্যে সংঘর্ষে একজন ছাত্র নিহত হয়। এই ঘটনাটি ঘটেছিল সাবেক প্রধানমন্ত্রী শেখ হাসিনার ভার্চুয়াল ভাষণের পর, যা রাজনৈতিক উত্তেজনা বাড়িয়ে দিয়েছিল।",
  "incident_date": "2025-02-06 00:00:00",
  "political_party_name": "আওয়ামী লীগ, ছাত্র"
},
{
  "news_title": "কুয়েটে ছাত্রদল ও ছাত্র আন্দোলনের কর্মীদের মধ্যে সংঘর্ষ, শতাধিক আহত",
  "news_url": "https://en.wikipedia.org/wiki/2025_Khulna_JCD%E2%80%93SAD_clash",
  "source": "Wikipedia, Prothom Alo",
  "location_name": "খুলনা প্রকৌশল ও প্রযুক্তি বিশ্ববিদ্যালয় (কুয়েট), খুলনা",
  "latitude": 22.8988,
  "longitude": 89.5050,
  "fatalities": 0,
  "injuries": 150,
  "summary": "খুলনা প্রকৌশল ও প্রযুক্তি বিশ্ববিদ্যালয় (কুয়েট) ক্যাম্পাসে বাংলাদেশ জাতীয়তাবাদী ছাত্রদল (জেসিডি) এবং বৈষম্যবিরোধী ছাত্র আন্দোলনের কর্মীদের মধ্যে ব্যাপক সংঘর্ষ হয়। জেসিডি ক্যাম্পাসে সদস্য সংগ্রহের চেষ্টা করলে 'রাজনীতিমুক্ত ক্যাম্পাস' চাওয়া শিক্ষার্থীরা তাদের বিরোধিতা করে, যা থেকে সহিংসতার সূত্রপাত হয়। এতে শতাধিক শিক্ষার্থী আহত হয় এবং পরিস্থিতি নিয়ন্ত্রণে বিজিবি মোতায়েন করা হয়।",
  "incident_date": "2025-02-18 00:00:00",
  "political_party_name": "ছাত্রদল (জেসিডি), বৈষম্যবিরোধী ছাত্র আন্দোলন (SAD), শিবির"
},
{
  "news_title": "নর্থ সাউথ ইউনিভার্সিটিতে ছাত্রদল ও শিক্ষার্থীদের মধ্যে সংঘর্ষ",
  "news_url": "https://www.scholarsatrisk.org/regions/southern-asia/bangladesh/",
  "source": "Scholars at Risk",
  "location_name": "নর্থ সাউথ ইউনিভার্সিটি, ঢাকা",
  "latitude": 23.8153,
  "longitude": 90.4255,
  "fatalities": 0,
  "injuries": 10,
  "summary": "নর্থ সাউথ ইউনিভার্সিটিতে (এনএসইউ) বেসরকারি বিশ্ববিদ্যালয়ের শিক্ষার্থী এবং জাতীয়তাবাদী ছাত্রদলের (জেসিডি) সদস্যদের মধ্যে সংঘর্ষ হয়, এতে বেশ কয়েকজন শিক্ষার্থী আহত হন।",
  "incident_date": "2025-03-05 00:00:00",
  "political_party_name": "ছাত্রদল (জেসিডি)"
},
{
  "news_title": "নারায়ণগঞ্জে বিএনপির অভ্যন্তরীণ কোন্দলে যুবদল কর্মী নিহত",
  "news_url": "https://www.dhakatribune.com/bangladesh/politics/384025/74-dead-in-bnp%E2%80%99s-internal-clashes-since-august-5",
  "source": "Dhaka Tribune",
  "location_name": "রূপগঞ্জ, নারায়ণগঞ্জ",
  "latitude": 23.7939,
  "longitude": 90.5152,
  "fatalities": 1,
  "injuries": 0,
  "summary": "নারায়ণগঞ্জের রূপগঞ্জে বিএনপির দুটি প্রতিদ্বন্দ্বী গোষ্ঠীর মধ্যে সংঘর্ষের সময় যুবদলের ৩৫ বছর বয়সী কর্মী মামুন ভুঁইয়াকে গুলি করে হত্যা করা হয়।",
  "incident_date": "2025-06-10 00:00:00",
  "political_party_name": "বিএনপি, যুবদল"
},
{
  "news_title": "যশোরে রাজনৈতিক বিরোধে বিএনপি কর্মী খুন",
  "news_url": "https://www.dhakatribune.com/bangladesh/politics/384025/74-dead-in-bnp%E2%80%99s-internal-clashes-since-august-5",
  "source": "Dhaka Tribune",
  "location_name": "শার্শা, যশোর",
  "latitude": 23.0736,
  "longitude": 88.8783,
  "fatalities": 1,
  "injuries": 0,
  "summary": "যশোরের শার্শায় রাজনৈতিক বিরোধের জেরে ৩০ বছর বয়সী বিএনপি কর্মী লিটন হোসেনকে কুপিয়ে হত্যা করা হয়।",
  "incident_date": "2025-06-10 00:00:00",
  "political_party_name": "বিএনপি"
},
{
  "news_title": "পাবনার সুজানগরে বিএনপির দুই গ্রুপের সংঘর্ষ",
  "news_url": "https://thefinancialexpress.com.bd/national/politics/some-political-parties-trying-to-take-advantage-of-mitford-incident-rizvi",
  "source": "The Financial Express",
  "location_name": "সুজানগর, পাবনা",
  "latitude": 23.9139,
  "longitude": 89.4283,
  "fatalities": 0,
  "injuries": 0,
  "summary": "পাবনার সুজানগরে বিএনপির দুটি গোষ্ঠীর মধ্যে সংঘর্ষ হয়। ঘটনার পরপরই জড়িতদের দল থেকে বহিষ্কার করা হয়।",
  "incident_date": "2025-07-11 00:00:00",
  "political_party_name": "বিএনপি"
}
    
]

def insert_demo_data():
    """ডেমো ডেটা ডেটাবেসে যোগ করে।"""
    print("\nStarting to seed demo data...")
    inserted_count = 0
    for incident in demo_incidents:
        # ডেটাবেসে এই URL আগে থেকেই আছে কিনা তা চেক করা
        if incidents_collection.find_one({'news_url': incident['news_url']}):
            print(f"Skipping already existing demo data: {incident['news_title']}")
            continue

        # নতুন ডেটা যোগ করা
        incidents_collection.insert_one(incident)
        inserted_count += 1
        print(f"Inserted: {incident['news_title']}")
        time.sleep(0.5) # ছোট বিরতি

    if inserted_count > 0:
        print(f"\nSuccessfully inserted {inserted_count} new demo documents.")
    else:
        print("\nNo new demo data to insert. All demo data already exists.")

    client.close()
    print("Process finished.")

if __name__ == '__main__':
    insert_demo_data()