# Terraink Batch Export per GitHub Actions

Dieses Repository startet Terraink automatisch in GitHub Actions und speichert die erzeugten Downloads als Artifact.

## Dateien

- `terraink_batch.py` - Playwright-Automatisierung
- `staedte.txt` - Standard-Staedteliste, eine Stadt pro Zeile
- `themes.txt` - Standard-Themes, ein Theme pro Zeile
- `.github/workflows/terraink.yml` - GitHub Actions Workflow

## Nutzung vom iPhone

1. Neues GitHub-Repository erstellen.
2. Alle Dateien aus diesem Paket in das Repository hochladen.
3. Im Repository auf **Actions** gehen.
4. Workflow **Terraink Batch Export** auswaehlen.
5. **Run workflow** antippen.
6. Optional Staedte und Themes direkt in die Eingabefelder kopieren.
7. Workflow starten.
8. Nach dem Lauf den Eintrag oeffnen und unten bei **Artifacts** `terraink_downloads` herunterladen.

## Listenformat

`staedte.txt`:

```text
Berlin, Deutschland
Hamburg, Deutschland
Wolfsburg, Deutschland
```

`themes.txt`:

```text
Carrara
Blush
Sandstone
Midnight Blue
```

## Hinweise

- Das Skript nutzt Headless Chromium ueber Playwright.
- Wenn Terraink die Bedienoberflaeche aendert, muessen ggf. Selektoren in `terraink_batch.py` angepasst werden.
- Falls ein Cookie-Popup oder eine Abfrage stoert, kann die Funktion `accept_popups()` erweitert werden.
- Die Downloads werden als GitHub Artifact bereitgestellt.
