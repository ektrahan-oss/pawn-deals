#!/usr/bin/env python3
"""Pawn Flip Finder daily scan. Usage: python3 pawn_scan.py --stores stores.json --gold 4186.90 --out outdir"""
import argparse, json, re, time, urllib.request, concurrent.futures as cf

UA = {"User-Agent": "Mozilla/5.0 (pawn-flip-finder daily scan)", "Accept": "application/json"}
EZ = "https://shop.ezpawn.com"
CA = "https://search.cashamerica.com/api/Items?key=D830382E436549369C2D0FE10333F63D"
CENTER = (29.7604, -95.3698)
RADIUS = 100  # miles; reaches Bryan/College Station and Beaumont/Port Arthur/Orange
EZ_STORES = """01103 01050 01215 01011 01094 01012 01121 01066 01278 01127 01065 01124 01147 01281 01275 01090 01291
01088 01167 01276 01274 01057 01104 01038 01082 01268 01224 01130 01204 01056 01266 01262 01023 10251 01280 01070 01097
27005 27003 01260 01269 01267 01101 01270 01282 01108 01261 27002 01129 01114 27004 01092 01093 01072 01265 01279 01017
01042 01263 01118 27006 01052 01060 01126 27001 01098 01277 01069 01122 01116 01290 01007 01106 01091 01076 01292 01233 01109
01048 01055 01138 01073 10918 01014 01077 10919 01135 01139""".split()
CA_CATS = ["1000", "9360", "2000", "9700", "6000", "5000", "7500", "4000"]
CA_TERMS = ["luggage", "suitcase"]
TOOL_MAX = 1000

WATCH = re.compile(r"rolex|omega|heuer|breitling|cartier|tudor|longines|iwc|panerai|patek|audemars|hublot|rado|tissot|hamilton|oris|grand seiko|movado|raymond weil|baume|bell ?& ?ross|zenith|jaeger|chopard|bvlgari|bulgari|ebel|corum|gucci|michele|shinola|prospex|presage|promaster", re.I)
BAG = re.compile(r"vuitton|louie|\blv\b|chanel|gucci|prada|fendi|dior|herm[eè]s|goyard|saint laurent|\bysl\b|balenciaga|bottega|celine|loewe", re.I)
LUGGAGE = re.compile(r"rimowa|\btumi\b|briggs|globe-?trotter|zero halliburton|hartmann|\bmcm\b|montblanc|bric'?s|keepall|horizon|pegase", re.I)
TOOL = re.compile(r"hilti|snap[- ]?on|mac tools?|matco|fluke|fieldpiece|inficon|testo|topcon|trimble|spectra|leica|hypertherm|\bmiller\b|lincoln|festool|propress|seesnake|cornwell|knipex", re.I)
OTHER = re.compile(r"\b(gibson|fender|prs|martin|taylor|gretsch|rickenbacker|mesa|marshall)\b|dji|canon eos r|\bsony a7|nikon z|hasselblad|macbook pro|silver eagle|gold eagle|krugerrand|maple leaf|morgan|\bbullion\b|\bcoin", re.I)
KNIFE = re.compile(r"benchmade|spyderco|chris reeve|\bcrk\b|microtech|zero tolerance|\bzt\b|hinderer|\bbuck\b|case xx|\bcase\b|emerson|protech|kizer|we knife|cold steel|esee|ka-?bar|leatherman|victorinox|sebenza", re.I)
GUN = re.compile(r"colt|smith ?& ?wesson|\bs&w\b|smith wesson|sig ?sauer|\bsig\b|heckler|\bhk\b|h&k|kimber|springfield|ruger|winchester|browning|beretta|walther|\bcz\b|glock|marlin|remington|henry|savage|tikka|sako|benelli|fn\b|fnh|weatherby|wilson combat|nighthawk|korth|manurhin|steyr|daniel defense|\bknight|lwrc|staccato|\bsti\b|dan wesson|les baer|ithaca|mossberg|python|anaconda|luger|mauser|garand|m1 carbine|high power|hi-?power", re.I)
OPTIC = re.compile(r"leupold|vortex|nightforce|trijicon|aimpoint|eotech|swarovski|zeiss|schmidt|kahles|holosun|sig ?sauer|\bsig\b|burris|steiner|primary arms|pulsar|\bagm\b|\batn\b|thermal|night ?vision|\bpvs|\bacog|\brmr\b|razor|viper|romeo|tango|kilo", re.I)
GEAR_NAME = re.compile(r"scope|sight|optic|night vision|thermal|range ?finder|gun accessory|red dot|magnifier|binocular", re.I)
NFA = re.compile(r"suppressor|silencer", re.I)
JBRAND = re.compile(r"tiffany|\bt ?& ?co\b|cartier|yurman|van cleef|\bvca\b|alhambra|bvlgari|bulgari|john hardy|roberto coin|mikimoto|buccellati|messika|pomellato|chopard|herm[eè]s", re.I)
KARAT = re.compile(r"\b(10|14|18|22|24)\s?K", re.I)


def get(url, data=None, method="GET", tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, method=method, headers=dict(UA, **({"Content-Type": "application/json"} if data else {})))
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except Exception as e:
            if i == tries - 1:
                return None, str(e).encode()
            time.sleep(1.5 * (i + 1))


def spec(html, k):
    m = re.search(r"<td>" + k + r"</td>\s*<td>([^<]*)</td>", html or "", re.I)
    return m.group(1).strip() if m else ""


def ez_store(sid):
    out, page = [], 1
    while page <= 100:
        st, body = get(f"{EZ}/collections/store_{sid}/products.json?limit=250&page={page}")
        if st != 200:
            break
        prods = json.loads(body).get("products", [])
        for p in prods:
            p["_store"] = sid
        out += prods
        if len(prods) < 250:
            break
        page += 1
        time.sleep(0.2)
    return out


def ca_body(code, p, rpp="50", term=None):
    return json.dumps({"CategoryCodes": [code] if code else [], "Latitude": CENTER[0], "Longitude": CENTER[1], "OnlyClearanceItems": None,
                       "ResultsPerPage": rpp, "SearchDistance": RADIUS, "SearchPage": p, "SearchPriceHigh": 100000,
                       "SearchPriceLow": 0, "SearchTerm": term, "Stores": [],
                       "UniqueId": "3DDC0D0E-1B4A-421C-95CE-5A3A0F276A38"}).encode()


def ca_cat(code, term=None):
    def page(p):
        st, b = get(CA, data=ca_body(code, p, term=term), method="PUT")
        if st == 200 and b:
            return json.loads(b)
        return {"results": [], "numberPagesTotal": 0, "numberItemsTotal": 0}
    first = page(1)
    res = list(first.get("results", []))
    n = first.get("numberPagesTotal", 0)
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(page, range(2, n + 1)):
            res += r.get("results", [])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stores", required=True)
    ap.add_argument("--gold", type=float, required=True)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    gpg = a.gold / 31.1035
    stores = {s["store_key"]: s for s in json.load(open(a.stores))}

    def store_info(key):
        s = stores.get(key)
        return {"store_key": key, "region": s["region"] if s else "Unplaced", "miles_from_downtown": s["miles_from_downtown"] if s else None,
                "store_name": s["name"] if s else key, "address": s["address"] if s else ""}

    t0 = time.time()
    with cf.ThreadPoolExecutor(6) as ex:
        ez = [p for lst in ex.map(ez_store, EZ_STORES) for p in lst]
    ca, seen = [], set()
    for code, term in [(c, None) for c in CA_CATS] + [(None, t) for t in CA_TERMS]:
        for r in ca_cat(code, term):
            if r["longICN"] in seen:
                continue
            seen.add(r["longICN"]); r["_cat"] = code or "term:" + term; ca.append(r)
    st, b = get(CA, data=ca_body(None, 1, "15"), method="PUT")
    try:
        ca_total = json.loads(b)["numberItemsTotal"]
    except Exception:
        ca_total = len(ca)

    gold, branded, watches, bags, tools, other, guns, gear = [], [], [], [], [], [], [], []
    gold_checked = 0
    for p in ez:
        tags = p.get("tags", [])
        parent = next((t for t in tags if t.lower().startswith("parent_")), "")
        html = p.get("body_html", "")
        price = float(p["variants"][0]["price"])
        brand = spec(html, "Manufacturer"); model = spec(html, "Model Number"); grade = spec(html, "Class")
        text = f"{p['title']} {brand} {model}"
        base = dict(chain="EZPawn", title=p["title"], brand=brand, model=model, store_grade=grade, price=price,
                    link=f"{EZ}/products/{p['handle']}", item_no="", **store_info("EZ-" + p["_store"]))
        base["store"] = f"{base['store_name']}, {base['address']}"
        if "Jewelry" in parent or ("Collectibles" in parent and JBRAND.search(text)):
            if JBRAND.search(text) and 40 <= price <= 1500:
                branded.append(base)
            if "Jewelry" not in parent:
                continue
            mat = spec(html, "Material Type")
            w = spec(html, r"Weight \(in grams\)")
            try:
                w = float(w)
            except ValueError:
                m = re.search(r"([\d.]+)\s*grams?", p["title"], re.I); w = float(m.group(1)) if m else 0
            km = re.search(r"\.(\d{3})", spec(html, "Karat") + " " + p["title"])
            pur = int(km.group(1)) / 1000 if km else None
            if "gold" in (mat + p["title"]).lower() and pur and w:
                gold_checked += 1
                melt = w * pur * gpg
                if price / melt < 1.1:
                    gold.append(dict(base, grams=w, purity=pur, melt=round(melt), ratio=round(price / melt, 2)))
        elif "Watches" in parent and WATCH.search(text) and price <= 1500:
            watches.append(base)
        elif "Clothing" in parent and (BAG.search(text) or LUGGAGE.search(text)) and price <= 600:
            bags.append(dict(base, kind="luggage") if re.search(r"luggage|suitcase|carry-?on|keepall|horizon|pegase|duffel", text, re.I) else base)
        elif "Tools" in parent and TOOL.search(text) and price <= TOOL_MAX:
            tools.append(base)
        elif ("Sporting" in parent or "Optics" in parent) and OPTIC.search(text) and GEAR_NAME.search(text) and 40 <= price <= 1500:
            gear.append(base)
        elif OTHER.search(text) and 40 <= price <= 600 and not any(x in parent for x in ("Jewelry", "Watches", "Clothing", "Tools")):
            other.append(base)
    for r in ca:
        d = " ".join(r.get("details", []))
        name = r["itemName"]
        price = float(r["price"])
        base = dict(chain="Cash America", title=name, details=d, price=price, link="", item_no=r["longICN"],
                    clearance=r.get("isClearanceItem", False), **store_info("CA-" + str(r["storeNumber"])))
        base["store"] = f"Cash America #{r['storeNumber']} (item {r['longICN']})"
        if base["miles_from_downtown"] is None:
            base["miles_from_downtown"] = round(r.get("distance", 0))
        km, wm = KARAT.search(d), re.search(r"([\d.]+)\s*(GRM|GRAMS?|GR)\b", d, re.I)
        if r["_cat"] == "1000" and JBRAND.search(d) and not re.search(r"\bwatch", name, re.I) and 40 <= price <= 1500:
            branded.append(base)
        if r["_cat"] == "1000" and km and wm and not re.search(r"\bwatch", name, re.I):
            w = float(wm.group(1)); pur = int(km.group(1)) / 24
            if w > 0:
                gold_checked += 1
                melt = w * pur * gpg
                if melt >= 20 and price / melt < 1.0:
                    gold.append(dict(base, grams=w, purity=round(pur, 3), melt=round(melt), ratio=round(price / melt, 2)))
        elif re.search(r"watch", name, re.I) and WATCH.search(d) and price <= 1500:
            watches.append(base)
        elif (r["_cat"] == "9360" or r["_cat"].startswith("term:")) and (BAG.search(d) or LUGGAGE.search(d)) and price <= 600 and "REPLICA" not in d.upper():
            bags.append(dict(base, kind="luggage") if re.search(r"luggage|suitcase", name + " " + d, re.I) else base)
        elif r["_cat"] == "2000" and TOOL.search(d) and price <= TOOL_MAX:
            tools.append(base)
        elif r["_cat"] in ("9700", "6000", "5000") and OTHER.search(d + " " + name) and 40 <= price <= 600:
            other.append(base)
        elif r["_cat"] == "7500" and KNIFE.search(d) and 40 <= price <= 600:
            other.append(dict(base, kind="knife"))
        elif r["_cat"] == "4000" and re.search(r"rifle|shotgun|pistol|revolver|handgun", name, re.I) and GUN.search(d) and price <= 5000:
            guns.append(base)
        elif r["_cat"] == "4000" and not re.search(r"rifle|shotgun|pistol|revolver|handgun", name, re.I) and not NFA.search(name + " " + d) \
                and OPTIC.search(d) and 40 <= price <= 1500:
            gear.append(base)

    gold.sort(key=lambda x: x["ratio"])
    for lst in (branded, watches, bags, tools, other, guns, gear):
        lst.sort(key=lambda x: x["price"])
    cands = {"gold_below_melt": gold, "branded_jewelry": branded, "watches": watches, "bags": bags, "tools": tools, "other": other,
             "firearms": guns, "gun_gear": gear}
    stats = {"EZPawn items scanned": len(ez), "Cash America items in range": ca_total, "Cash America items checked": len(ca),
             "Gold pieces priced vs. melt": gold_checked, "Gold listed below melt": sum(1 for g in gold if g["ratio"] < 1.0),
             "Gold price used ($/oz)": a.gold, "seconds": round(time.time() - t0)}
    json.dump(cands, open(f"{a.out}/candidates.json", "w"), indent=1)
    json.dump(stats, open(f"{a.out}/scan_stats.json", "w"), indent=1)
    print(json.dumps(stats))
    print({k: len(v) for k, v in cands.items()})


if __name__ == "__main__":
    main()
