import json
import folium
from folium import Element

JSON_FILE = "data.json"
OUT_FILE = "standorte_karte.html"

with open(JSON_FILE, "r", encoding="utf-8") as f:
    standorte = json.load(f)

if not standorte:
    raise SystemExit(" standorte.json ist leer.")

lats = [s["koordinaten"]["lat"] for s in standorte]
lngs = [s["koordinaten"]["lng"] for s in standorte]
mean_lat = sum(lats) / len(lats)
mean_lng = sum(lngs) / len(lngs)

karte = folium.Map(location=[mean_lat, mean_lng], zoom_start=11)

css = """
<style>
.leaflet-control-layers {
    font-size: 18px;
    min-width: 170px; /* optional: Box breiter */
}
.leaflet-control-layers label {
    font-size: 18px;
    font-weight: 700;
    line-height: 1.4;
}
.leaflet-control-layers input[type="checkbox"] {
    transform: scale(1.3);
    margin-right: 8px;
}
</style>
"""
karte.get_root().html.add_child(Element(css))

layer_dexa = folium.FeatureGroup(name="DEXA")
layer_blut = folium.FeatureGroup(name="Blutlabor")

for s in standorte:
    lat = s["koordinaten"]["lat"]
    lng = s["koordinaten"]["lng"]

    leistungen = ", ".join(s.get("leistungen", [])) if s.get("leistungen") else "—"
    selbstzahler = s.get("selbstzahler_moeglich", None)
    selbstzahler_txt = "ja" if selbstzahler is True else "nein" if selbstzahler is False else "keine Angabe"

    popup_html = f"""
    <b>{s.get("name","—")}</b><br>
    Kategorie: {s.get("kategorie","—")}<br>
    Adresse: {s.get("adresse","—")}<br>
    Leistungen: {leistungen}<br>
    Kontakt: {s.get("kontakt","—")}<br>
    Selbstzahler: {selbstzahler_txt}<br>
    Preisinfo: {s.get("preisinfo","—")}<br>
    """

    if s.get("website"):
        popup_html += f"<a href='{s['website']}' target='_blank' rel='noreferrer'>Website</a>"

    kat = s.get("kategorie", "")
    color = "blue" if kat == "DEXA" else "red"

    marker = folium.Marker(
        location=[lat, lng],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(color=color, icon="info-sign"),
    )

    if kat == "DEXA":
        marker.add_to(layer_dexa)
    else:
        marker.add_to(layer_blut)

layer_dexa.add_to(karte)
layer_blut.add_to(karte)

folium.LayerControl(collapsed=False).add_to(karte)

karte.fit_bounds([[min(lats), min(lngs)], [max(lats), max(lngs)]])
karte.save(OUT_FILE)
print(f"Karte erstellt: {OUT_FILE}")
