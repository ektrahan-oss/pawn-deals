# Pawn deal scan: daily runbook

Followed each morning by Libby's "Pawn Deals Daily Update" scheduled task. The task prompt names the two email recipients; never email anyone else. Work efficiently; aim to finish within 25 minutes. Work unattended and do not ask questions.

## Goal
Find items at EZPawn and Cash America within about 100 miles of downtown Houston (so Bryan/College Station, Huntsville, Livingston, Bay City and Beaumont/Port Arthur/Orange are included) that can be flipped for a quick profit, plus firearms priced at least 40% below their going used price for Tony's personal buy-and-hold collection. Then update the "Pawn Flip Finder" dashboard artifact (https://claude.ai/artifact/TEdU12gj3zNKmbsXUwwGmt), update Tony's phone app (this repo, served at https://ektrahan-oss.github.io/pawn-deals/), and email a short digest by about 5:40 a.m. Tony has no Claude account and cannot open the dashboard, so the email and the app must stand on their own.

Flip rules: max purchase price per item is $500, except tools, which may go up to $1,000 (a standout over budget may be listed, marked "over budget"). Minimum estimated profit $75. Profit = low resale estimate x 0.87 (selling fees) minus price x 1.0825 (Texas sales tax). For gold, low resale = 85% of melt value with no fee deduction.

Categories: Gold, Jewelry (designer pieces), Watch, Bag (includes luggage), Tool, Other (includes name-brand knives), Gun gear (scopes, red dots, night vision and other firearm accessories, sold as flips), and Firearm (not a flip; see step 4).

## Step 1. Setup
Make a working folder outside the repo. The repo is this folder (if it is not already checked out, git clone --depth 1 https://github.com/ektrahan-oss/pawn-deals). The store table is the repo's stores.json (array of {store_key, chain, name, address, near, map_url, lat, lon, region, miles_from_downtown, location_note}). The repo's deals.json is yesterday's list: copy it to the working folder as previous_deals.json (for "new since yesterday"). Right away, test GitHub access with "git push --dry-run origin main" so you know early whether step 6B will work.

## Step 2. Gold price
curl https://metalcharts.org/1-oz-gold-price (or WebFetch it) and read today's gold spot in USD per troy ounce.

## Step 3. Scan
Run: python3 <repo>/pawn_scan.py --stores <repo>/stores.json --gold <spot> --out <working folder>. Takes about 4 to 5 minutes. It writes candidates.json (lists: gold_below_melt with grams, purity, melt, ratio; branded_jewelry; watches; bags (luggage carries kind "luggage"); tools; other (knives carry kind "knife"); firearms; gun_gear; each item has chain, title, details or brand/model, price, store, store_key, region, miles_from_downtown, link, item_no, store_grade) and scan_stats.json. If the sites fail (errors or zero items), email the recipients one line saying today's scan could not run and why, then stop. Do not try to work around blocked sites. Send at most one email per run.

## Step 4. Pick deals
Use python plus judgment. Keep your context small: filter and print compact lines, never dump whole lists.
- Gold: every gold_below_melt item. Plain chains, bracelets and bands = "Good"; pendants, earrings, rings, "misc" pieces (gross weight may include stones or non-gold parts) = "Check in person"; absurd prices like $10 = "Long shot", say call first.
- Jewelry (branded_jewelry): Tiffany & Co., Cartier, David Yurman, Van Cleef & Arpels, Bvlgari, John Hardy, Roberto Coin, Mikimoto and similar designer pieces priced well under their pre-owned resale value (eBay sold, Fashionphile or The RealReal). Fakes are common, so confidence is at most "Check in person", and check_first names a concrete authenticity check (hallmarks and "T&Co. 925" or "750" stamps, Cartier serial number and screw details, Yurman "DY" stamp, box and papers). Clear underpricing on a famous design (Cartier Love or Juste un Clou, VCA Alhambra, Tiffany Return to Tiffany, Yurman cable) is the target; very low prices for those = "Long shot", profit_basis "If genuine".
- Watches: flag genuine-looking underpricing (vintage Heuer 980.xxx references, Tag Heuer, Omega, Tudor, Rolex, Breitling, Cartier, Bvlgari, Longines, etc.). Very low prices on luxury brands usually mean counterfeit: "Long shot", profit_basis "If genuine".
- Bags and luggage: Louis Vuitton (a recorded date code like SD1105 is a good sign; Keepall and Horizon luggage too), Chanel, Gucci, Prada, Fendi, Dior, Hermes, Goyard, Saint Laurent, Balenciaga, Bottega Veneta, Celine, Loewe, plus quality luggage (Rimowa, Tumi, Briggs & Riley, Globe-Trotter, Zero Halliburton, Hartmann, MCM). Store grade BASIC is a bad sign.
- Tools (budget up to $1,000): Hilti, Snap-on, Mac, Matco, Cornwell, Fluke, Fieldpiece, Inficon, Testo, Knipex, Festool, Milwaukee ProPress and SeeSnake, Topcon, Trimble, Spectra, Leica, Hypertherm, Miller, Lincoln. Watch for mislabeled categories (e.g. a Hilti DX nail gun listed as "jackhammer" or "gas concrete saw").
- Other: clear underpricing on name-brand knives (Benchmade, Spyderco, Chris Reeve, Microtech, Zero Tolerance, Hinderer, collectible Buck/Case), guitars/amps (US-made Fender, Gibson, PRS, Martin, Taylor), pro cameras, DJI drones, coins/bullion vs. melt.
- Gun gear (gun_gear, flips): quality optics and accessories that resell quickly: Leupold, Vortex Razor/Viper, Nightforce, Trijicon (ACOG, RMR, MRO), Aimpoint, EOTech, Swarovski, Zeiss, Schmidt & Bender, Kahles, Holosun, Sig Sauer Romeo/Tango/Kilo, Steiner, and thermal or night vision (Pulsar, AGM, ATN, PVS). Use eBay sold prices for that exact model. Never include suppressors.
- Firearms (Cash America only; EZPawn does not list firearms online). These are for Tony's personal collection (buy and hold), not flips. The test is the price versus the GOING USED PRICE for that exact model. From the firearms list (about 1,800; rifles, shotguns, pistols and revolvers), shortlist about 15 that look most underpriced for their model, favoring collectible or strong-demand guns (e.g. Colt Python/Anaconda/Gold Cup, older Smith & Wesson revolvers like Models 19/27/29/586, Browning Hi-Power and Belgian Brownings, Sig P210/P226/P229, HK P7/USP, German Walther PPK, pre-64 Winchester 70/94, JM-stamped Marlin 336/1894, Kimber, Dan Wesson, CZ, Tikka/Sako, Benelli, and common models like Glock or Ruger priced well under market). For each, WebSearch (mode standard) the going used price (GunBroker sold/completed listings or used prices at large dealers). Keep only those where the price is no more than 60% of the going used price (at least 40% below) AND going used price minus price x 1.0825 is at least $100. No budget cap for firearms. At most 5 firearms per day, best savings first.
- For the top ~15 non-gold, non-firearm candidates use WebSearch (mode standard) for eBay sold prices to set resale_low and resale_high.

## Step 5. Build deals.json and scan.json
deals.json: array of objects with fields:
- id (letter + number, unique: G gold, J jewelry, W, B, T, O, A gun gear, F)
- category (Gold|Jewelry|Watch|Bag|Tool|Other|Gun gear|Firearm)
- item (plain readable name), listed_as (raw listing text), chain, store, store_key, region, location, miles_from_downtown
- price, cost_with_tax, resale_low, resale_high, est_profit (integer), melt_value (gold only)
- in_budget ("Yes"|"Over budget"; budget is $1,000 for Tool and $500 for every other flip; always "Yes" for Firearm)
- confidence ("Good"|"Check in person"|"Fair"|"Long shot"), why (1 plain sentence), check_first (1 plain sentence)
- link (EZPawn product URL; for Cash America https://search.cashamerica.com/#/search/<search_word>), item_no (Cash America longICN; "" for EZPawn)
- search_word and search_count (Cash America only: pick and verify the search word now as described in step 7; search_count = numberItemsTotal that word returns)
- new (true if the deal's link or item_no was not in previous_deals.json, else false)
- profit_basis ("Scrap value, if weight is right" for gold, "If genuine" for long-shot luxury, "Below going used price" for firearms, else "At the low resale estimate")
- flip_speed ("Fast"|"Medium"|"Slow"|"Hold"), flip_time ("1 to 3 days"|"1 to 2 weeks"|"2 to 6 weeks"|"Keep"), priority_score (integer)

Flip speed: gold, bullion, a genuine Rolex, pro tools = Fast; popular LV/Gucci bags, modern Tag Heuer, guitars, cameras, lasers, saws, knives, quality optics, Tiffany silver = Medium; vintage watches, less common bags, luggage, designer gold jewelry, anything needing third-party authentication = Slow. priority_score = round(est_profit x speed weight (Fast 1.0, Medium 0.7, Slow 0.4) x certainty weight (Good 1.0, Check in person 0.7, Fair 0.6, Long shot 0.2)). Keep only est_profit >= 75.

Firearms: category "Firearm", resale_low/resale_high = going used price range, est_profit = savings = round(going used price low - price x 1.0825), profit_basis "Below going used price", flip_speed "Hold", flip_time "Keep", confidence "Good" when the exact model and its used price are confirmed else "Fair", priority_score = round(savings x 0.3 x certainty weight), why = one line naming the going used price and the percent below it, check_first = e.g. "Check bore, action and that the model matches."

scan.json: rows {metric, value, note} with EXACTLY these metric names: "EZPawn items scanned", "Cash America items in range", "Cash America items checked", "Gold pieces priced vs. melt", "Gold listed below melt", "Deals flagged", "Gold price used ($/oz)" (values from scan_stats.json; Deals flagged = number of deals).

## Step 6. Update the dashboard
Upload deals.json and scan.json with the Artifact tool (action publish, url above, file_path, asset true). Then ArtifactData: get datasets/deals and datasets/scan for their versions and update each (if_version) with source = {kind:"file", url: new "/_blob/..." url, name} and updated = {at: now ISO, by: "Claude (daily scan)"}. Do not change files/index.html or datasets/stores. If the Artifact tools are unavailable, skip this step and continue.

## Step 6B. Update Tony's phone app
Copy deals.json into the repo. Write the repo's scan.json = the scan.json rows plus one more row {"metric": "Updated", "value": "Updated <Weekday abbrev> <h:mm am/pm>" using the current America/Chicago time (e.g. "Updated Tue 5:24 am"), "note": "Last scan time, Houston time"}. Change only deals.json and scan.json. Commit with git -c user.name="Pawn deal scan" -c user.email="ektrahan-oss@users.noreply.github.com" commit -m "Daily deals <YYYY-MM-DD>" (git add those two files first) and git push origin main. If the push fails, retry at most once. If it still fails, still send the email with a last line "The phone app could not be updated today.", and send Libby a push notification giving the exact git error and saying the repo ektrahan-oss/pawn-deals needs to be attached (with push access) to the "Pawn Deals Daily Update" scheduled task. Never use any other way to push (no tokens, no other repos).

## Step 7. Email the digest
Build an HTML email with a python script (escape all listing text with html.escape). Load the Gmail tools with ToolSearch ("select:mcp__Gmail__send_message") and send ONE email with mcp__Gmail__send_message to the recipients named in the task prompt, subject "Pawn deals for [Weekday Mon D]: N deals, gold $Y/oz" using today's date in America/Chicago time (if the run asks for a subject prefix like "TEST", add it), with htmlBody AND a plain-text body fallback (no Markdown). It is read on an iPhone, so:
- Start the HTML with <meta name="format-detection" content="telephone=no, address=no, date=no">. Simple single-column layout, inline styles only, font-size 16px, max-width 600px, no wide tables, no images, no em dashes, no hype.
- Store lines: EZPawn = bold "EZPawn City, street address". Cash America = bold "Cash America #N" followed by the store table's "near" text (e.g. "near Tomball (27 mi from downtown)"). Every store line ends with a "Map" link using the store table's map_url exactly. Add "(2 deals here)" when a store has 2+. Each area with 2+ stores also gets a "Route" link: https://www.google.com/maps/dir/<stop1>/<stop2>/... with URL-encoded stops (EZPawn address, or Cash America lat,lon) in priority order.
- EZPawn deals: the item name is an <a href> to the EZPawn product URL (full https URL).
- Cash America deals: Tony looks items up in the Cash America APP, whose search only matches ONE word or a model code (multi-word brand searches and item numbers return nothing). Pick search_word and VERIFY it by calling the API (PUT https://search.cashamerica.com/api/Items?key=D830382E436549369C2D0FE10333F63D with the same JSON body the scan script uses plus "SearchTerm": search_word and ResultsPerPage "50") and confirm the item's longICN appears: try first the model code after "M/" when specific (not NV, NA, NVMN, N/A); else a distinctive single word from the details or item name (e.g. "grandcarrera", "neverfull", "bracelet", "chain", "python"). Show it prominently as a bold line "Search in app: <search_word>", followed by "then look for $price at store #N" when the word returns more than ~10 items. After it, a small grey "(or online)" link to https://search.cashamerica.com/#/search/<search_word>. Also show "Counter item # 392&#8204;036&#8204;381" (groups of 3 separated by &#8204;, inside <span style="color:inherit;text-decoration:none">, so iPhones do not make it a phone link) and "Listed as: [itemName + details]" for the staff. In the plain-text body write "Search in app: <word>" and the number as "392-036-381".

Content:
1. Line 1: "N deals, X new. Gold is $Y/oz."
2. Line 2: "Quickest flips are listed first. Have gold weighed at the counter before buying."
3. Line 3: a bold link "Open the Pawn Deals app" to https://ektrahan-oss.github.io/pawn-deals/ with small grey text "(has Deals near me)".
4. Line 4 (small, grey): "Cash America app tip: search one word or model code, with your location set."
5. Up to 4 areas of flip deals in priority order (quickest flip first, then highest priority_score), leaving long shots and firearms out of this part (gun gear stays in as a flip): area name as a bold heading with its Route link; each store line; then that store's deals as bullets "Item, $price, est. +$profit, flip speed. Check: [few words]" plus, for Cash America, the Search in app line, item number and listing text; NEW marked in bold.
6. A "FIREARMS" section (only if any qualify): each as "Model, $price, going used about $X (Z% below), you save about $Y" with its store line and Map link, the Search in app line, counter item number, listing text and a few-word check; NEW in bold.
7. "Long shots worth a peek" with at most 2 items.
8. Final lines "Full list on the app: https://ektrahan-oss.github.io/pawn-deals/" and "Libby's dashboard: https://claude.ai/artifact/TEdU12gj3zNKmbsXUwwGmt (needs her Claude login)".

About 500 words max. Also put the plain-text digest in your final response.

## Limits
Send only this one email, only to the recipients in the task prompt. Never buy anything, contact stores or submit forms. The only git push allowed is the step 6B data update to this repo. Do not edit RUNBOOK.md, pawn_scan.py, stores.json or index.html during a run.
