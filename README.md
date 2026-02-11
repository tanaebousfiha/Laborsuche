Laborsuche DACH – Interaktive Karte für Gesundheitsanbieter

Dieses Projekt ist eine interaktive Webkarte, die Anbieter für DEXA-Body-Composition-Messungen, Knochendichtemessungen und Blutuntersuchungen visualisiert.
Die Karte zeigt Standorte, Details und Kontaktinformationen der Anbieter, um Nutzerinnen und Nutzern bei der Suche nach passenden Gesundheitsdienstleistungen zu helfen.

Data Extraction

Zur Datenextraktion war ursprünglich die Nutzung der Google-REST-API geplant.
Da die Verwendung der Google-API jedoch mit Kosten von etwa 300 $ verbunden ist, wurde diese Methode zunächst nicht weiterverfolgt. Eine alternative Scraping-Methode oder ein geeignetes Tool soll künftig noch recherchiert werden.

Nach der Evaluation mehrerer (teilweise kostenpflichtiger) Anbieter wurde schließlich Instant Data Scraper verwendet, um effizient möglichst viele Informationen zu extrahieren.

Da es nicht realistisch ist, sämtliche benötigten Informationen ausschließlich mit einem Scraping-Tool zu erfassen, wurden ergänzend manuelle Recherchen durchgeführt.

Die gesammelten Daten wurden in folgender Datei gespeichert:

data.json

Kartenskript (data.py)

Das Python-Skript übernimmt die vollständige Verarbeitung der gesammelten Standortdaten aus data.json und erzeugt daraus eine interaktive HTML-Karte:

standorte_karte.html


Die Karte enthält Filter- und Cluster-Funktionalitäten.

2.1 Duplikaterkennung (Qualitätssicherung)

Zur Verbesserung der Datenqualität wurde eine Duplikaterkennung implementiert:

Geografische Distanz: Berechnung mittels Haversine-Formel

Namensähnlichkeit: Vergleich mittels SequenceMatcher

2.2 Kartengenerierung (mit Folium)

Die Kartenerstellung erfolgt mit der Python-Bibliothek Folium.

Automatische Mittelpunkt-Berechnung:
Nutzung von fit_bounds(), um alle Standorte optimal darzustellen.

2.3 MarkerCluster

Nahegelegene Standorte werden mithilfe von MarkerCluster gruppiert, um die Übersichtlichkeit zu erhöhen.

Farbcodierung:

Blau → DEXA

Rot → Blutlabor

Popup-Informationen

Jeder Marker enthält folgende Informationen:

Name

Kategorie

Adresse

Leistungen

Kontakt

Selbstzahler-Status

Preisinformationen

Website

Automatische Kartenausrichtung

Am Ende des Skripts wird erneut fit_bounds() verwendet, um die Karte automatisch auf alle Marker zu zoomen.

Output

Das Skript erzeugt folgende Datei:

standorte_karte.html


Diese enthält eine vollständig interaktive und filterbare Standortkarte.

Docker Setup

Das gesamte Projekt (inkl. Python-Skript, Abhängigkeiten und Datenverarbeitung) ist in einem Docker-Image gekapselt.
Das Image wurde getaggt und in Docker Hub veröffentlicht, sodass es plattformunabhängig verwendet werden kann.

4.1 Image herunterladen
docker pull tanaebou/laboresuchedach:latest

4.2 Container ausführen und Karte generieren

Linux / macOS

docker run --rm -v "$(pwd)":/app tanaebou/laboresuchedach:latest


Windows PowerShell

docker run --rm -v "${PWD}:/app" tanaebou/laboresuchedach:latest


Nach der Ausführung wird automatisch die Datei standorte_karte.html erzeugt.

Karte öffnen

Öffne die Datei standorte_karte.html einfach im Browser.

Designentscheidungen

Verzicht auf Google-API aufgrund der hohen Kosten

Kombination aus Scraping und manueller Recherche zur Sicherstellung der Datenqualität

Implementierung einer Duplikaterkennung zur Vermeidung redundanter Standorte

Verwendung von Folium aufgrund der einfachen Integration in Python

Dockerisierung zur reproduzierbaren und plattformunabhängigen Ausführung

Geplante Verbesserungen

Bei mehr Zeit würde ich folgende Erweiterungen umsetzen:

Integration einer Suchfunktion für eine verbesserte Nutzerinteraktion

Vollautomatisiertes und nachhaltiges Data-Scraping

Erweiterung um zusätzliche Filterfunktionen (z. B. nach Leistungsangeboten oder Öffnungszeiten)


























