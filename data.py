import json
import folium
from folium import Element
from folium.plugins import MarkerCluster
import html
from math import radians, sin, cos, sqrt, atan2
from difflib import SequenceMatcher

JSON_FILE = "data.json"
OUT_FILE = "standorte_karte.html"

ALLOWED_CATEGORIES = {"DEXA", "Blutlabor"}


def validate_location(s: dict) -> list[str]:
    errors = []

    if not s.get("id"):
        errors.append("missing id")
    if not s.get("name"):
        errors.append("missing name")

    kat = (s.get("kategorie") or "").strip()
    if kat not in ALLOWED_CATEGORIES:
        errors.append(f"invalid kategorie: {kat!r}")

    try:
        lat = s["koordinaten"]["lat"]
        lng = s["koordinaten"]["lng"]
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            errors.append("lat/lng not numeric")
        else:
            if not (-90 <= lat <= 90):
                errors.append("lat out of range")
            if not (-180 <= lng <= 180):
                errors.append("lng out of range")
    except Exception:
        errors.append("missing/invalid koordinaten")

    return errors


# -----------------------
# Helper: Dedup-Check
# -----------------------
def haversine_km(a: dict, b: dict) -> float:
    R = 6371.0
    lat1, lon1 = radians(a["lat"]), radians(a["lng"])
    lat2, lon2 = radians(b["lat"]), radians(b["lng"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    x = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(x), sqrt(1 - x))


def name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100


def find_duplicates(items: list[dict], max_km: float = 0.2, min_name_sim: float = 90.0):
    dups = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if (a.get("kategorie") or "").strip() != (b.get("kategorie") or "").strip():
                continue

            sim = name_similarity(a.get("name", ""), b.get("name", ""))
            dist = haversine_km(a["koordinaten"], b["koordinaten"])
            if sim >= min_name_sim and dist <= max_km:
                dups.append((a["id"], b["id"], round(sim, 1), round(dist, 3)))
    return dups


# -----------------------
# JSON laden
# -----------------------
with open(JSON_FILE, "r", encoding="utf-8") as f:
    standorte = json.load(f)

if not standorte:
    raise SystemExit("data.json ist leer.")

# -----------------------
# Validierung
# -----------------------
all_errors = []
ids_seen = set()
for s in standorte:
    sid = s.get("id")
    if sid in ids_seen:
        all_errors.append((sid, ["duplicate id"]))
    if sid:
        ids_seen.add(sid)

    errs = validate_location(s)
    if errs:
        all_errors.append((sid or "UNKNOWN_ID", errs))

if all_errors:
    print("\n[VALIDATION ERRORS]")
    for sid, errs in all_errors:
        print(f"- {sid}: {', '.join(errs)}")
    raise SystemExit("Validation failed.")

# -----------------------
# Dedup-Verdachtsliste
# -----------------------
dups = find_duplicates(standorte)
if dups:
    print("\n[POSSIBLE DUPLICATES] (bitte manuell prüfen)")
    for a, b, sim, dist in dups:
        print(f"- {a} <-> {b} | name_sim={sim}% | dist={dist} km")

# -----------------------
# Daten-Qualitäts Summary (Proof)
# -----------------------
total = len(standorte)

dexa_body_only = 0
dexa_knochen_only = 0
dexa_beide = 0

blut_selbstzahler = 0
blut_unbekannt = 0

for s in standorte:
    kat = (s.get("kategorie") or "").strip()
    leistungen_norm = {str(x).strip().lower() for x in (s.get("leistungen") or [])}

    has_body = "body composition" in leistungen_norm
    has_knochen = "knochendichtemessung" in leistungen_norm

    if kat == "DEXA":
        if has_body and has_knochen:
            dexa_beide += 1
        elif has_body:
            dexa_body_only += 1
        elif has_knochen:
            dexa_knochen_only += 1

    if kat == "Blutlabor":
        if s.get("selbstzahler_moeglich") is True:
            blut_selbstzahler += 1
        else:
            blut_unbekannt += 1

print("\n[DATA SUMMARY]")
print(f"Gesamt Standorte: {total}")
print(f"DEXA mit Body Composition (nur): {dexa_body_only}")
print(f"DEXA nur Knochendichte: {dexa_knochen_only}")
print(f"DEXA beide Leistungen: {dexa_beide}")
print(f"Blutlabor Selbstzahler verifiziert: {blut_selbstzahler}")
print(f"Blutlabor unklar/nicht verifiziert: {blut_unbekannt}")

# -----------------------
# Mittelpunkt berechnen
# -----------------------
lats = [s["koordinaten"]["lat"] for s in standorte]
lngs = [s["koordinaten"]["lng"] for s in standorte]
mean_lat = sum(lats) / len(lats)
mean_lng = sum(lngs) / len(lngs)

karte = folium.Map(location=[mean_lat, mean_lng], zoom_start=11)

# -----------------------
# CSS für LayerControl
# -----------------------
css = """
<style>
.leaflet-control-layers {
    font-size: 18px;
    min-width: 200px;
}
.leaflet-control-layers label {
    font-size: 18px;
    font-weight: 700;
}
.leaflet-control-layers input[type="checkbox"] {
    transform: scale(1.3);
    margin-right: 8px;
}
</style>
"""
karte.get_root().html.add_child(Element(css))

# -----------------------
# Cluster-Layer (deine Filter)
# -----------------------
cluster_all = MarkerCluster(name="Alles zusammen", show=True)
cluster_knochen = MarkerCluster(name="Knochenmessung", show=False)
cluster_body = MarkerCluster(name="Body composition", show=False)
cluster_beide = MarkerCluster(name="Beide", show=False)

# Blutlabor nur = nur verifizierte Selbstzahler (Challenge-Anforderung)
cluster_blut_only = MarkerCluster(name="Blutlabor nur (Selbstzahler)", show=False)

# -----------------------
# Marker hinzufügen
# -----------------------
for s in standorte:
    lat = s["koordinaten"]["lat"]
    lng = s["koordinaten"]["lng"]

    name = html.escape(s.get("name", "—"))
    kat = (s.get("kategorie") or "—").strip()
    adresse = html.escape(s.get("adresse", "—"))
    kontakt = html.escape(s.get("kontakt", "—"))
    preisinfo = html.escape(s.get("preisinfo", "—"))

    leistungen_list = s.get("leistungen") or []
    leistungen_norm = {str(x).strip().lower() for x in leistungen_list}

    has_knochen = "knochendichtemessung" in leistungen_norm
    has_body = "body composition" in leistungen_norm

    selbstzahler = s.get("selbstzahler_moeglich", None)
    selbstzahler_txt = "ja" if selbstzahler is True else "nein" if selbstzahler is False else "keine Angabe"

    leistungen_txt = ", ".join(html.escape(x) for x in leistungen_list) if leistungen_list else "—"

    popup_html = f"""
    <b>{name}</b><br>
    Kategorie: {html.escape(kat)}<br>
    Adresse: {adresse}<br>
    Leistungen: {leistungen_txt}<br>
    Kontakt: {kontakt}<br>
    Selbstzahler: {selbstzahler_txt}<br>
    Preisinfo: {preisinfo}<br>
    """

    if s.get("website"):
        website = html.escape(s["website"])
        popup_html += f"<a href='{website}' target='_blank' rel='noreferrer'>Website</a>"

    color = "red" if kat == "Blutlabor" else "blue" if kat == "DEXA" else "gray"

    def make_marker():
        return folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.Icon(color=color, icon="info-sign"),
        )

    # Alles zusammen: immer
    make_marker().add_to(cluster_all)

    # Blutlabor nur: nur verifizierte Selbstzahler
    if kat == "Blutlabor" and selbstzahler is True:
        make_marker().add_to(cluster_blut_only)

    # DEXA: nach Leistung
    if kat == "DEXA":
        if has_knochen and has_body:
            make_marker().add_to(cluster_beide)
        elif has_knochen:
            make_marker().add_to(cluster_knochen)
        elif has_body:
            make_marker().add_to(cluster_body)

# -----------------------
# Layer hinzufügen + Control
# -----------------------
cluster_all.add_to(karte)
cluster_knochen.add_to(karte)
cluster_body.add_to(karte)
cluster_beide.add_to(karte)
cluster_blut_only.add_to(karte)

folium.LayerControl(collapsed=False).add_to(karte)

# Fit-to-bounds
karte.fit_bounds([[min(lats), min(lngs)], [max(lats), max(lngs)]])

karte.save(OUT_FILE)
print(f"\nKarte erstellt: {OUT_FILE}")
