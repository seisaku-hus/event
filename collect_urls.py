"""
HUS イベントURL収集スクリプト
------------------------------
一覧ページ（JSレンダリング）から記事詳細URLだけを集めてJSONに書き出す。
役割はこれだけ。詳細情報の取得・蓄積・表示は全てGAS側が担当する。
"""

import json
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.hus.ac.jp/news/event/index.html?p={page}"
DETAIL_PREFIX = "https://www.hus.ac.jp/news/detail/"
MAX_PAGES = 10
OUTPUT_FILE = "event_urls.json"


def collect_urls() -> list[str]:
    urls = set()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page_obj = browser.new_page()

        for page_num in range(1, MAX_PAGES + 1):
            url = BASE_URL.format(page=page_num)
            page_obj.goto(url, wait_until="networkidle")

            hrefs = page_obj.eval_on_selector_all(
                "article a", "els => els.map(e => e.href)"
            )
            detail_links = [h for h in hrefs if DETAIL_PREFIX in h]

            print(f"page {page_num}: {len(detail_links)} 件")

            if not detail_links:
                break  # ページ切れ

            urls.update(detail_links)

        browser.close()

    return sorted(urls)


def main():
    urls = collect_urls()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)
    print(f"合計 {len(urls)} 件のイベントURLを {OUTPUT_FILE} に書き出しました")


if __name__ == "__main__":
    main()
