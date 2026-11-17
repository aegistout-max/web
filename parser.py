# Парсер объявлений с Farpost.
# Авито и Циан отдают антибот-страницу, поэтому берётся открытая выдача:
# https://www.farpost.ru/vladivostok/realty/rent_flats/
# Страницу открывает Firefox через Selenium. Дальше разбирается уже
# готовый HTML из браузера, кодировку windows-1251 обрабатывать не нужно.
#
# Карточка — блок с data-bulletin-id. Из неё берутся название, цена,
# строка под названием, ссылка на фото. Район, комнаты и площадь
# достаются из этой строки и из заголовка. Если куска нет — поле None,
# объявление всё равно попадает в список.
#
# Зависимость: pip install selenium. Драйвер Firefox подтягивает сам Selenium.

import json
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

HERE = Path(__file__).resolve().parent
URL = "https://www.farpost.ru/vladivostok/realty/rent_flats/"
OUT = HERE / "src" / "listings.js"


def plain(fragment):
    if not fragment:
        return None
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def digits(value):
    if not value:
        return None
    # в атрибуте после суммы идёт тег со знаком рубля, его отрезаем
    head = value.split("<", 1)[0]
    found = re.sub(r"\D", "", head)
    return int(found) if found else None


def district_from_note(note):
    if not note:
        return None
    match = re.search(r"^(.*?),\s*(?:агентство|частное лицо)\b", note, re.I)
    if match:
        return match.group(1).strip() or None
    return note.split(",")[0].strip() or None


def rooms_from_title(title):
    if not title:
        return None
    match = re.search(r"(\d+)\s*-?\s*комн", title, re.I)
    if match:
        return int(match.group(1))
    low = title.lower()
    if low.startswith("студ") or low.startswith("гостин"):
        return 1
    return None


def area_from_text(text):
    if not text:
        return None
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*кв", text)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def parse_card(card):
    id_match = re.match(r"(\d+)", card)
    title = plain(re.search(r'class="bulletinLink[^"]*"[^>]*>(.*?)</a>', card, re.S).group(1)) if re.search(
        r'class="bulletinLink', card
    ) else None
    if not id_match or not title:
        return None

    price_tag = re.search(r'data-price="([^"]*)"', card)
    photo = re.search(r'<img[^>]+src="(https://static\.baza\.farpost\.ru/[^"]+)"', card)
    note = plain(
        re.search(r'class="bull-item__annotation-row">(.*?)</div>', card, re.S).group(1)
        if re.search(r'class="bull-item__annotation-row">', card)
        else None
    )
    district = district_from_note(note)

    return {
        "id": id_match.group(1),
        "title": title,
        "price": digits(price_tag.group(1)) if price_tag else None,
        "district": district or None,
        "rooms": rooms_from_title(title),
        "area": area_from_text(note),
        "description": note,
        "photos": [photo.group(1)] if photo else [],
    }


def parse_page(html):
    listings = []
    seen = set()
    for chunk in html.split('data-bulletin-id="')[1:]:
        item = parse_card(chunk)
        if item and item["id"] not in seen:
            seen.add(item["id"])
            listings.append(item)
    return listings


def load_page():
    options = Options()
    options.add_argument("-headless")
    options.add_argument("--width=1280")
    options.add_argument("--height=900")
    options.set_preference("intl.accept_languages", "ru-RU, ru")
    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(30)
    try:
        driver.get(URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-bulletin-id]"))
        )
        return driver.page_source
    finally:
        driver.quit()


def main():
    html = load_page()
    listings = parse_page(html)
    payload = json.dumps(listings, ensure_ascii=False, indent=2)
    OUT.write_text("export default " + payload + "\n", encoding="utf-8")
    print(f"{len(listings)} объявлений -> {OUT.name}")


if __name__ == "__main__":
    main()
