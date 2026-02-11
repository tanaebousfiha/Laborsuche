Laborsuche DACH – Interaktive Karte für Gesundheitsanbieter


Dieses Projekt ist eine interaktive Webkarte, die Anbieter für DEXA-Body-Composition-, Knochenmessungen und Blutuntersuchungen visualisiert. Die Karte zeigt die Standorte, Details und Kontaktinformationen der Anbieter, um Nutzerinnen und Nutzern bei der Suche nach passenden Gesundheitsdienstleistungen zu helfen.

1. Data extraction:

- Um die Daten zu extrahieren, sollte man zunächst die REST-API-Methode verwenden. Allerdings kostet die Nutzung der API von Google etwa 300 $, weshalb ich diese Methode bisher vermieden habe.
Ich werde demnächst nach einer Scraping-Methode oder einem Tool recherchieren.

Ich habe mehrere Anbieter gefunden, die allerdings nicht kostenlos sind. Letztendlich habe ich den Instant Data Scraper verwendet, um Zeit zu sparen und möglichst viele Informationen zu erhalten.
- Da es nicht realistisch ist, alle Informationen ausschließlich mit einem Scraper-Tool zu sammeln, habe ich weiterhin manuell nach den benötigten Daten gesucht.
- Die Informationen habe ich in "data.json" gespeichert (also die gesammelten Daten).


2. Karte script: (data.py)

- Dieses Python-Skript übernimmt die vollständige Verarbeitung der gesammelten Standortdaten aus data.json und erzeugt daraus eine interaktive HTML-Karte (standorte_karte.html) mit Filter- und Cluster-Funktionalität.

2.1 Duplikaterkennung (Qualitätssicherung):
Geografische Distanz:
  -Berechnung mittels Haversine-Formel
  -Namensähnlichkeit: Vergleich mittels SequenceMatcher


2.3  Kartengenerierung (mit Folium)
Automatische Mittelpunkt-Berechnung:
Mittels fit_bounds(), um alle Standorte optimal darzustellen

2.4 MarkerCluster:
Zur Gruppierung nahegelegener Standorte

    
Farbcodierung:

      Blau: DEXA
      
      Rot: Blutlabor

Popup-Informationen:
Name
Kategorie
Adresse
Leistungen
Kontakt
Selbstzahler-Status
Preisinfo
Website

2.5 Automatische Kartenausrichtung

Am Ende wird fit_bounds() genutzt, um die Karte automatisch auf alle Marker zu zoomen.

3.  Output

Das Skript erzeugt die Datei:
standorte_karte.html
Diese enthält eine vollständig interaktive und filterbare Standortkarte.

4. Docker Setup

Das gesamte Projekt (inkl. Python-Skript, Abhängigkeiten und Datenverarbeitung) ist in einem Docker-Image gekapselt.
Das Image wurde getaggt und in Docker Hub gepusht, damit es überall verwendet werden kann.

 4.1 Pull the image :
 docker pull tanaebou/laboresuchedach:latest

 4.2 Run the container and generate the map:

 Linux / macOS : docker run --rm -v "$(pwd)":/app tanaebou/laboresuchedach:latest

 Windows PowerShell : docker run --rm -v "${PWD}:/app" tanaebou/laboresuchedach:latest

 4.3 Nach dem Lauf wird die Datei: standorte_karte.html



5. Open the map

Öffne standorte_karte.html einfach im Browser.


6. Designentscheidungen

Verzicht auf Google-API aufgrund der hohen Kosten

Kombination aus Scraping und manueller Recherche, um Datenqualität zu sichern

Implementierung einer Duplikaterkennung, um redundante Standorte zu vermeiden

Verwendung von Folium, da es eine einfache Integration in Python erlaubt

Dockerisierung, um reproduzierbare und plattformunabhängige Ausführung sicherzustellen


7. Was ich bei mehr Zeit noch verbessern würde:

Integration einer Suchfunktion für eine noch bessere Nutzerinteraktion.

Vollautomatisiertes, nachhaltiges Data-Scraping.

Erweiterung um weitere Filterfunktionen, z. B. nach Leistungsangeboten oder Öffnungszeiten.




























