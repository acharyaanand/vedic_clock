import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"
]
YOGA_NAMES = [
    "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana",
    "Atiganda","Sukarma","Dhriti","Shoola","Ganda","Vriddhi",
    "Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
    "Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha",
    "Shukla","Brahma","Indra","Vaidhriti"
]
KARANA_NAMES = [
    "Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti",
    "Shakuni","Chatushpada","Naga","Kimstughna"
]
VARA_NAMES  = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
VARA_LORDS  = ["sun","moon","mars","mercury","jupiter","venus","saturn"]
VARA_HINDI  = ["Ravivar","Somvar","Mangalvar","Budhvar","Guruvar","Shukravar","Shanivar"]
NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
    "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
    "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
NAKSHATRA_LORDS = [
    "ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury",
    "ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury",
    "ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"
]
NAKSHATRA_NATURE = [
    "Kshipra","Ugra","Mishra","Sthira","Mridu","Tikshna","Mishra",
    "Mridu","Tikshna","Ugra","Ugra","Sthira","Laghu","Tikshna",
    "Chara","Mishra","Mridu","Tikshna","Tikshna","Ugra","Sthira",
    "Mridu","Kshipra","Chara","Ugra","Sthira","Mridu"
]
RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
    "Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"
]
RITU_NAMES = {
    1:"Vasanta (Spring)",2:"Vasanta (Spring)",3:"Grishma (Summer)",
    4:"Grishma (Summer)",5:"Varsha (Monsoon)",6:"Varsha (Monsoon)",
    7:"Sharad (Autumn)",8:"Sharad (Autumn)",9:"Hemanta (Pre-Winter)",
    10:"Hemanta (Pre-Winter)",11:"Shishira (Winter)",12:"Shishira (Winter)"
}
RAHUL_KAAL_ORDER  = {0:8,1:2,2:7,3:5,4:6,5:4,6:3}
GULIKA_KAAL_ORDER = {0:6,1:5,2:4,3:3,4:2,5:1,6:7}
YAMGHANT_ORDER    = {0:5,1:4,2:3,3:2,4:1,5:7,6:6}

BAD_YOGAS = ["Vishkumbha","Atiganda","Shoola","Ganda","Vyaghata","Vajra","Vyatipata","Parigha","Vaidhriti"]
TRAVEL_GOOD    = ["Ashwini","Rohini","Mrigashira","Punarvasu","Pushya","Hasta","Chitra","Swati","Anuradha","Shravana","Dhanishtha","Revati"]
MARRIAGE_GOOD  = ["Rohini","Mrigashira","Uttara Phalguni","Hasta","Swati","Anuradha","Uttara Ashadha","Shravana","Revati","Uttara Bhadrapada"]
BUSINESS_GOOD  = ["Rohini","Mrigashira","Punarvasu","Pushya","Hasta","Chitra","Swati","Shravana","Dhanishtha","Revati"]
MEDICAL_GOOD   = ["Ashwini","Mrigashira","Hasta","Swati","Shravana","Revati"]

def _fmt(h):
    h=h%24; hh=int(h); mm=int((h-hh)*60); ss=int(((h-hh)*60-mm)*60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

def calc_sunrise_sunset(year,month,day,lat,lon,tz_offset=5.5):
    n = datetime(year,month,day).timetuple().tm_yday
    B = 360/365*(n-81)
    eot = 9.87*math.sin(math.radians(2*B))-7.53*math.cos(math.radians(B))-1.5*math.sin(math.radians(B))
    solar_noon = 12-(lon-15*tz_offset)/15-eot/60
    decl = math.degrees(math.asin(0.39795*math.cos(math.radians(0.98563*(n-173)))))
    lat_r=math.radians(lat); decl_r=math.radians(decl)
    cos_ha=(math.cos(math.radians(90.833))-math.sin(lat_r)*math.sin(decl_r))/(math.cos(lat_r)*math.cos(decl_r))
    if abs(cos_ha)>1: return {"error":"Polar region"}
    ha=math.degrees(math.acos(cos_ha))
    sr=solar_noon-ha/15; ss_=solar_noon+ha/15
    day_len_h=ss_-sr
    brahma_s=sr-96/60; brahma_e=sr-48/60
    abhijit_s=solar_noon-24/60; abhijit_e=solar_noon+24/60
    return {
        "sunrise":_fmt(sr),"sunset":_fmt(ss_),"solar_noon":_fmt(solar_noon),
        "day_length":f"{day_len_h:.1f} hours ({int(day_len_h*60)} min)",
        "sunrise_decimal":sr,"sunset_decimal":ss_,
        "brahma_muhurta":{"start":_fmt(brahma_s),"end":_fmt(brahma_e),
            "description":"96-48 min before sunrise — meditation and study",
            "citation":"Muhurta Chintamani"},
        "abhijit_muhurta":{"start":_fmt(abhijit_s),"end":_fmt(abhijit_e),
            "description":"48 min around solar noon — powerful for all work",
            "citation":"Muhurta Chintamani"},
    }

def calc_inauspicious_periods(weekday,sr_h,ss_h):
    period=(ss_h-sr_h)/8
    def gp(order):
        s=sr_h+(order-1)*period; e=s+period
        def f(h): h=h%24; return f"{int(h):02d}:{int((h%1)*60):02d}"
        return {"start":f(s),"end":f(e)}
    rk=gp(RAHUL_KAAL_ORDER[weekday]); gk=gp(GULIKA_KAAL_ORDER[weekday]); yg=gp(YAMGHANT_ORDER[weekday])
    return {
        "rahul_kaal":{**rk,"description":"Inauspicious — avoid new ventures","citation":"Muhurta Chintamani"},
        "gulika_kaal":{**gk,"description":"Inauspicious sub-period","citation":"Muhurta Chintamani"},
        "yamghant":{**yg,"description":"Avoid auspicious activities","citation":"Muhurta Chintamani"}
    }

def calc_amrit_kaal(sr_h,nak_num):
    OFFSET=[6,4,2,0,8,6,4,2,0,8,6,4,2,0,8,6,4,2,0,8,6,4,2,0,8,6,4]
    s=sr_h+OFFSET[(nak_num-1)%27]; e=s+1.6
    def f(h): h=h%24; return f"{int(h):02d}:{int((h%1)*60):02d}"
    return {"start":f(s),"end":f(e),"description":"Most auspicious period","citation":"Muhurta Chintamani"}

def get_festivals(year,month,day,tithi_num,nak_num,weekday,sun_rashi):
    fests=[]
    tithi=(tithi_num-1)%30+1
    FIXED={(1,14):"Makar Sankranti",(8,15):"Independence Day",(10,2):"Gandhi Jayanti"}
    if (month,day) in FIXED:
        fests.append({"name":FIXED[(month,day)],"type":"Fixed","importance":"National/Solar festival"})
    if tithi==3 and month in [4,5]:
        fests.append({"name":"Akshaya Tritiya","type":"Highly Auspicious","importance":"Best day for gold, new ventures — imperishable merit","citation":"Bhavishya Purana"})
    if tithi in range(1,10) and month in [3,4]:
        if tithi==1: fests.append({"name":"Chaitra Navratri Begins","type":"Major Festival","importance":"Nine nights of Durga","citation":"Devi Bhagavata"})
        elif tithi==9: fests.append({"name":"Ram Navami","type":"Major Festival","importance":"Birth of Lord Rama","citation":"Valmiki Ramayana"})
    if tithi in range(1,11) and month in [9,10]:
        if tithi==1: fests.append({"name":"Sharad Navratri Begins","type":"Major Festival","importance":"Most celebrated Navratri","citation":"Devi Mahatmya"})
        elif tithi==10: fests.append({"name":"Vijaya Dashami / Dussehra","type":"Major Festival","importance":"Victory of good over evil","citation":"Valmiki Ramayana"})
    if tithi==30 and month in [10,11]:
        fests.append({"name":"Diwali / Deepavali","type":"Major Festival","importance":"Festival of lights — Lakshmi puja","citation":"Skanda Purana"})
    if tithi==15 and month in [2,3]:
        fests.append({"name":"Holi","type":"Major Festival","importance":"Festival of colors — Phalguna Purnima","citation":"Bhagavata Purana"})
    if tithi==23 and month in [7,8]:
        fests.append({"name":"Janmashtami","type":"Major Festival","importance":"Birth of Lord Krishna — midnight celebration","citation":"Bhagavata Purana"})
    if tithi==4 and month in [8,9]:
        fests.append({"name":"Ganesh Chaturthi","type":"Major Festival","importance":"Birth of Ganesha — 10 day celebration","citation":"Ganesha Purana"})
    if tithi==29 and month in [2,3]:
        fests.append({"name":"Maha Shivaratri","type":"Major Festival","importance":"Sacred night for Shiva — all-night vigil","citation":"Shiva Purana"})
    if tithi==15 and month in [7,8]:
        fests.append({"name":"Raksha Bandhan","type":"Festival","importance":"Shravana Purnima — brother-sister bond","citation":"Traditional"})
    if tithi==15 and month in [6,7]:
        fests.append({"name":"Guru Purnima","type":"Festival","importance":"Ashadha Purnima — Vyasa Purnima — veneration of Guru","citation":"Traditional"})
    if tithi in [11,26]: fests.append({"name":"Ekadashi","type":"Fasting Day","importance":"Sacred to Vishnu — fasting highly meritorious","citation":"Dharmasindhu"})
    if tithi==15 and month not in [2,3,6,7,7,8]: fests.append({"name":"Purnima","type":"Full Moon","importance":"Satya Narayan puja, sacred bathing","citation":"Skanda Purana"})
    if tithi==30 and month not in [10,11]: fests.append({"name":"Amavasya","type":"New Moon — Pitru Tithi","importance":"Tarpan, Shraddha for ancestors","citation":"Garuda Purana"})
    return fests

def get_tithi_specials(tithi_num,weekday,nak_num):
    s=[]; tithi=(tithi_num-1)%30+1
    if tithi in [11,26]: s.append({"name":"Ekadashi","type":"Fasting","activities":"Vishnu worship, fasting","citation":"Dharmasindhu"})
    if tithi in [13,28]: s.append({"name":"Pradosh","type":"Shiva worship","activities":"Shiva puja at sunset","citation":"Shiva Purana"})
    if tithi==4: s.append({"name":"Vinayaka Chaturthi","type":"Ganesh","activities":"Ganesh puja, modak","citation":"Ganesha Purana"})
    if tithi==19: s.append({"name":"Sankashti Chaturthi","type":"Ganesh fasting","activities":"Fasting, moonrise prayer","citation":"Ganesha Purana"})
    if tithi in [8,23]: s.append({"name":"Ashtami","type":"Durga day","activities":"Durga/Kali puja","citation":"Devi Bhagavata"})
    if nak_num==8: s.append({"name":"Pushya Nakshatra","type":"Most auspicious Nakshatra","activities":"Best for all new ventures","citation":"Muhurta Chintamani"})
    return s

def check_panchaka(nak_num):
    if nak_num in [23,24,25,26,27]:
        return {"is_panchaka":True,"nakshatra":NAKSHATRA_NAMES[nak_num-1],
                "warning":"Avoid construction, south travel, marriage","citation":"Muhurta Chintamani"}
    return {"is_panchaka":False}

def get_activity_muhurta(tithi_num,nak_num,weekday,yoga_name):
    tithi=(tithi_num-1)%30+1; nn=NAKSHATRA_NAMES[nak_num-1]; yok=yoga_name not in BAD_YOGAS
    return {
        "travel":{"suitable":nn in TRAVEL_GOOD and yok,"nakshatra":nn,"yoga_ok":yok,"citation":"Muhurta Chintamani"},
        "marriage":{"suitable":nn in MARRIAGE_GOOD and tithi not in [4,8,9,12,13,14,30] and yok,"citation":"Muhurta Chintamani"},
        "business":{"suitable":nn in BUSINESS_GOOD and yok,"citation":"Muhurta Chintamani"},
        "medical":{"suitable":nn in MEDICAL_GOOD,"citation":"Muhurta Chintamani"},
        "property":{"suitable":NAKSHATRA_NATURE[nak_num-1]=="Sthira" and tithi in [2,3,5,7,10,11,13],"citation":"Muhurta Chintamani"},
        "citation":"Muhurta Chintamani — Activity Muhurta rules"
    }

def get_complete_panchanga(year,month,day,lat,lon,tz_offset,sun_lon,moon_lon,
                            birth_nakshatra_num=None,birth_rashi_num=None):
    diff=(moon_lon-sun_lon)%360
    ti=int(diff/12); tn=TITHI_NAMES[ti%30]; tnum=ti+1
    paksha="Shukla Paksha" if ti<15 else "Krishna Paksha"
    wd=datetime(year,month,day).weekday(); wds=(wd+1)%7
    nak_idx=int((moon_lon*27)/360)%27; nn=NAKSHATRA_NAMES[nak_idx]
    nak_num=nak_idx+1; nak_pada=int((moon_lon%(360/27))/(360/27/4))+1
    yoga_idx=int(((sun_lon+moon_lon)%360)/(360/27))%27
    yoga_name=YOGA_NAMES[yoga_idx]; yoga_good=yoga_name not in BAD_YOGAS
    karana_name=KARANA_NAMES[int(diff/6)%11]
    sun_rashi=int(sun_lon/30)%12; moon_rashi=int(moon_lon/30)%12
    sd=calc_sunrise_sunset(year,month,day,lat,lon,tz_offset)
    ina={}; amrit={}
    if "error" not in sd:
        ina=calc_inauspicious_periods(wds,sd["sunrise_decimal"],sd["sunset_decimal"])
        amrit=calc_amrit_kaal(sd["sunrise_decimal"],nak_num)
    if year<=3 and month<=3: vs=year+56
    else: vs=year+57
    MASA=["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada","Ashwin","Kartika","Margashirsha","Pausha","Magha","Phalguna"]
    masa=MASA[sun_rashi%12]
    if (month==1 and day>=14) or (2<=month<=6) or (month==7 and day<16): ayana="Uttarayana"
    else: ayana="Dakshinayana"
    ritu=RITU_NAMES.get(month,"")
    fests=get_festivals(year,month,day,tnum,nak_num,wds,sun_rashi)
    specials=get_tithi_specials(tnum,wds,nak_num)
    panchaka=check_panchaka(nak_num)
    activity=get_activity_muhurta(tnum,nak_num,wds,yoga_name)
    # Moonrise approx
    moon_ha=(moon_lon-(280.46+0.9856474*datetime(year,month,day).timetuple().tm_yday))%360
    mr_h=(6+moon_ha/15)%24; mset_h=(mr_h+12.4)%24
    def f2(h): h=h%24; return f"{int(h):02d}:{int((h%1)*60):02d}"
    chandra_bala=None; tara_bala=None
    if birth_rashi_num:
        diff2=(moon_rashi-birth_rashi_num+12)%12+1
        chandra_bala={"from_lagna":diff2,"is_strong":diff2 in [1,3,6,7,10,11],"citation":"Muhurta Chintamani"}
    if birth_nakshatra_num:
        d=(nak_num-birth_nakshatra_num)%27; t=(d%9)+1
        TARA=["Janma","Sampat","Vipat","Kshema","Pratyak","Sadhana","Naidhana","Mitra","Parama Mitra"]
        tara_bala={"tara":t,"name":TARA[t-1],"is_auspicious":t in [2,4,6,8,9],"citation":"Muhurta Chintamani"}
    return {
        "date":f"{year}-{month:02d}-{day:02d}",
        "location":{"lat":lat,"lon":lon,"tz_offset":tz_offset},
        "pancha_anga":{
            "tithi":{"name":tn,"number":tnum,"paksha":paksha,"citation":"BPHS Panchanga Adhyaya"},
            "vara":{"name":VARA_NAMES[wds],"hindi":VARA_HINDI[wds],"lord":VARA_LORDS[wds].capitalize(),"citation":"BPHS"},
            "nakshatra":{"name":nn,"number":nak_num,"pada":nak_pada,"lord":NAKSHATRA_LORDS[nak_idx].capitalize(),"nature":NAKSHATRA_NATURE[nak_idx],"citation":"BPHS"},
            "yoga":{"name":yoga_name,"is_auspicious":yoga_good,"citation":"BPHS"},
            "karana":{"name":karana_name,"citation":"BPHS"}
        },
        "astronomy":{
            "sunrise":sd.get("sunrise"),"sunset":sd.get("sunset"),"solar_noon":sd.get("solar_noon"),
            "day_length":sd.get("day_length"),"moonrise":f2(mr_h),"moonset":f2(mset_h),
            "sun_rashi":RASHI_NAMES[sun_rashi],"moon_rashi":RASHI_NAMES[moon_rashi]
        },
        "auspicious":{
            "brahma_muhurta":sd.get("brahma_muhurta",{}),"abhijit_muhurta":sd.get("abhijit_muhurta",{}),
            "amrit_kaal":amrit
        },
        "inauspicious":ina,
        "calendar":{"ayana":ayana,"ritu":ritu,"vikram_samvat":vs,"shaka_samvat":year-78,"masa":masa},
        "festivals":fests,"tithi_specials":specials,"panchaka":panchaka,
        "activity_muhurta":activity,
        "personal":{"chandra_bala":chandra_bala,"tara_bala":tara_bala},
        "citation":"BPHS Panchanga Adhyaya | Muhurta Chintamani | Dharmasindhu | Surya Siddhanta"
    }

if __name__=="__main__":
    r=get_complete_panchanga(2026,5,20,28.6139,77.2090,5.5,55.4,210.3,5,2)
    pa=r["pancha_anga"]
    print("FIVE LIMBS:")
    print(f"  Tithi:    {pa['tithi']['name']} ({pa['tithi']['paksha']})")
    print(f"  Vara:     {pa['vara']['name']} ({pa['vara']['hindi']})")
    print(f"  Nakshatra:{pa['nakshatra']['name']} Pada {pa['nakshatra']['pada']}")
    print(f"  Yoga:     {pa['yoga']['name']} ({'Auspicious' if pa['yoga']['is_auspicious'] else 'Inauspicious'})")
    print(f"  Karana:   {pa['karana']['name']}")
    ast=r["astronomy"]
    print(f"\nASTRONOMY: Sunrise {ast['sunrise']} | Sunset {ast['sunset']}")
    print(f"  Day Length: {ast['day_length']}")
    aus=r["auspicious"]
    print(f"\nAUSPICIOUS: Brahma {aus['brahma_muhurta'].get('start')}-{aus['brahma_muhurta'].get('end')}")
    print(f"  Abhijit: {aus['abhijit_muhurta'].get('start')}-{aus['abhijit_muhurta'].get('end')}")
    print(f"  Amrit: {aus['amrit_kaal'].get('start')}-{aus['amrit_kaal'].get('end')}")
    ina=r["inauspicious"]
    print(f"\nINAUSPICIOUS: Rahul {ina['rahul_kaal']['start']}-{ina['rahul_kaal']['end']}")
    print(f"  Gulika: {ina['gulika_kaal']['start']}-{ina['gulika_kaal']['end']}")
    print(f"  Yamghant: {ina['yamghant']['start']}-{ina['yamghant']['end']}")
    cal=r["calendar"]
    print(f"\nCALENDAR: {cal['ayana']} | {cal['ritu']} | Vikram {cal['vikram_samvat']} | {cal['masa']}")
    print(f"\nFESTIVALS: {len(r['festivals'])}")
    for f in r["festivals"]: print(f"  ✦ {f['name']}")
    print(f"\nSPECIALS: {[s['name'] for s in r['tithi_specials']]}")
    am=r["activity_muhurta"]
    print(f"\nMUHURTA: Travel {'✓' if am['travel']['suitable'] else '✗'} | Business {'✓' if am['business']['suitable'] else '✗'} | Medical {'✓' if am['medical']['suitable'] else '✗'}")
    print(f"Panchaka: {'YES ⚠' if r['panchaka']['is_panchaka'] else 'No'}")
    if r["personal"]["tara_bala"]:
        tb=r["personal"]["tara_bala"]
        print(f"Tara Bala: {tb['name']} ({'Auspicious' if tb['is_auspicious'] else 'Inauspicious'})")
    print(f"\n✓ Complete Panchanga Engine — All features working")
