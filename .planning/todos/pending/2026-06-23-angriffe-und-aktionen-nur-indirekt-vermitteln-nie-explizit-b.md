---
created: 2026-06-23T08:15:19.915Z
title: Angriffe und Aktionen nur indirekt vermitteln, nie explizit benennen
area: docs
files:
  - ANGRIFFSKARTEN.md
  - MODERATIONSSKRIPT.md
  - MODERATORENLEITFADEN.md
  - simulation_config.json
---

## Problem

Angriffe (Welle 1-3) und die Events/Aktionen zwischen den Wellen werden Spielern aktuell mit expliziten technischen Bezeichnungen vermittelt statt "durch die Blume" (allusiv/euphemistisch). Konkrete Fundstellen:

- `ANGRIFFSKARTEN.md`: Kartentitel benennen den Angriff direkt — "RANSOMWARE-ANGRIFF" (Welle 1, ca. Zeile 8), "OT-STOERUNG (PRODUKTIONSAUSFALL)" (Welle 2, ca. Zeile 117), "DATENEXFILTRATION (IP-DIEBSTAHL)" (Welle 3, ca. Zeile 228). Narrative nennen zusätzlich Technik-Begriffe wie "Emotet-Malware", "Phishing-Link", "Siemens Sinumerik SPS-Schwachstelle", "APT-ähnlicher Angreifer".
- `MODERATIONSSKRIPT.md`: Moderator liest Angriffe wortwörtlich mit Technikbegriffen vor, z.B. Welle 1 (ca. Zeile 107-109): "Ein Mitarbeiter klickt auf einen Phishing-Link. Emotet-Trojaner installiert sich. Der File-Server wird verschlüsselt." Analog für Welle 2 (SPS-Schwachstelle) und Welle 3 (kompromittierter Lieferanten-Zugang/CAD-Diebstahl).
- `MODERATORENLEITFADEN.md` (ca. Zeile 200-201): verweist nur auf die Narrative aus ANGRIFFSKARTEN.md, ohne Hinweis auf allusive/verschleiernde Sprache.
- `simulation_config.json` (ca. Zeile 39, 58, 77): Angriffs-"name"-Felder sind technisch explizit ("Ransomware", "OT-Stoerung", "Exfiltration"). Events zwischen den Wellen (ca. Zeile 228-307, z.B. "Phishing-Kampagne entdeckt", "OEM-Sicherheitsaudit", "NIS2/KRITIS-Prüfung") sind ebenfalls direkt benannt.

Spieler sollen aus den vorgelesenen/gedruckten Texten nie den exakten Angriffstyp oder die exakte Zwischen-Aktion erfahren — nur über Umschreibungen/Indizien darauf schließen können (z.B. "merkwürdige E-Mail mit Anhang" statt "Phishing/Emotet").

## Solution

TBD — Vorschlag: Kartentitel und Moderationstext durch neutrale/blumige Formulierungen ersetzen (z.B. "Vorfall A/B/C" als sichtbarer Titel, technische Details nur in einem separaten, für Moderator:innen internen Auflösungstext). Reihenfolge laut CLAUDE.md: zuerst `simulation_config.json` (name-Felder, Event-Texte) anpassen, dann `README.md`/Karten/Skripte synchron nachziehen. Nach Änderung `simulate_outcomes.py` + `balance_analysis.py` laufen lassen, um sicherzustellen, dass nur Text-/Darstellungsebene betroffen ist und keine Mechanik/Werte verändert wurden.
</content>
