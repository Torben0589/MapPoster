import asyncio
import os
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

print("SCRIPT STARTET", flush=True)

START_URL = "https://terraink.app/"
BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "terraink_downloads"
OUT_DIR.mkdir(exist_ok=True)

AFTER_LOCATION_WAIT_MS = int(os.getenv("AFTER_LOCATION_WAIT_MS", "6000"))
AFTER_THEME_WAIT_MS = int(os.getenv("AFTER_THEME_WAIT_MS", "3000"))
HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"


def clean_filename(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_\-\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]", "", text)
    return text[:120] or "terraink"


def split_lines(value: str):
    return [x.strip() for x in value.splitlines() if x.strip() and not x.strip().startswith("#")]


def read_list(env_name: str, file_name: str):
    env_value = os.getenv(env_name, "").strip()
    if env_value:
        return split_lines(env_value)
    path = BASE / file_name
    if not path.exists():
        print(f"Fehlt: {file_name}")
        sys.exit(1)
    return split_lines(path.read_text(encoding="utf-8"))


async def click_first(page, candidates, timeout=2500):
    for locator in candidates:
        try:
            await locator.first.click(timeout=timeout)
            return True
        except Exception:
            pass
    return False


async def accept_popups(page):
    # Versucht haeufige Cookie-/Consent-Buttons zu schliessen, falls vorhanden.
    await click_first(page, [
        page.get_by_role("button", name=re.compile("accept|agree|ok|zustimmen|akzeptieren|alle akzeptieren", re.I)),
        page.get_by_text(re.compile("accept|agree|zustimmen|akzeptieren|alle akzeptieren", re.I)),
    ], timeout=1200)


async def fill_location(page, city):

    print("FUELLE ORTSFELD", flush=True)

    await page.locator("input.startup-location-input").first.fill(city, timeout=10000)

    await page.wait_for_timeout(1500)

    print("BESTAETIGE ORT", flush=True)

    # Autocomplete-Vorschlag auswaehlen, falls vorhanden
    try:
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)
    except Exception:
        pass

    # OK-Button im Startdialog klicken
    await page.locator("button.startup-location-action--confirm").first.click(timeout=10000)

    await page.wait_for_timeout(AFTER_LOCATION_WAIT_MS)


async def choose_layout_defaults(page):
    # Optional: hier kannst du spaeter Layout/Posterformat erweitern.
    return


async def choose_theme(page, theme):
    await click_first(page, [
        page.get_by_text(re.compile("theme", re.I)),
        page.locator('[aria-label*="Theme" i]'),
        page.locator('button:has-text("THEME")'),
    ], timeout=2000)

    clicked = await click_first(page, [
        page.get_by_text(re.compile(f"^{re.escape(theme)}$", re.I)),
        page.locator(f"text={theme}"),
    ], timeout=6000)

    if not clicked:
        raise RuntimeError(f"Theme nicht gefunden: {theme}")

    await page.wait_for_timeout(AFTER_THEME_WAIT_MS)


async def download_result(page, city, theme):
    target = OUT_DIR / f"{clean_filename(city)}_{clean_filename(theme)}.png"

    async with page.expect_download(timeout=30000) as download_info:
        clicked = await click_first(page, [
            page.get_by_role("button", name=re.compile("download|herunterladen", re.I)),
            page.get_by_text(re.compile("download|herunterladen", re.I)),
            page.locator('button:has-text("DOWNLOAD")'),
        ], timeout=6000)

        if not clicked:
            raise RuntimeError("Download-Button nicht gefunden")

    download = await download_info.value
    await download.save_as(target)
    print(f"OK: {target.name}")


async def main():
    print("MAIN STARTET", flush=True)
    
    cities = read_list("CITY_LIST", "staedte.txt")
    themes = read_list("THEME_LIST", "themes.txt")
    print(
        f"Start: {len(cities)} Staedte x {len(themes)} Themes = {len(cities) * len(themes)} Downloads",
        flush=True
    )
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-dev-shm-usage", "--no-sandbox"]
        )
        context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = await context.new_page()

        for city in cities:
            for theme in themes:
                print(f"Bearbeite: {city} | {theme}")
                try:
                    await page.goto(START_URL, wait_until="domcontentloaded", timeout=45000)
                    await page.wait_for_timeout(2500)
                    await fill_location(page, city)
                    await choose_layout_defaults(page)
                    await choose_theme(page, theme)
                    await download_result(page, city, theme)
                except PlaywrightTimeoutError as exc:
                    print(f"TIMEOUT: {city} | {theme}: {exc}")
                except Exception as exc:
                    print(f"FEHLER: {city} | {theme}: {exc}")

        await context.close()
        await browser.close()

    print("Fertig. Dateien liegen in terraink_downloads.")


if __name__ == "__main__":
    asyncio.run(main())
