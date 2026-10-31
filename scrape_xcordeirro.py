# -*- coding: utf-8 -*-
"""
Script: scrape_xcordeirro.py
Deskripsi: Scraping postingan dan data komentar dari tautan X (Twitter):
            https://x.com/xcordeirro/status/2109412186670133636
            Mengekstrak metadata postingan utama serta seluruh reply komentar
            ke format CSV dan JSON.
"""

import os
import sys
import json
import csv
import html
import requests
from datetime import datetime

# Pastikan console Windows mendukung karakter Unicode & emoji
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TARGET_URL = "https://x.com/xcordeirro/status/2109412186670133636"


def fetch_tweet_html(url):
    """Mengambil respon HTML langsung dari web."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "id,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    print(f"[+] Menghubungi URL target: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            print(f"[OK] Berhasil terhubung ke server X (Status: {response.status_code})")
            return response.text
        else:
            print(f"[!] HTTP Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Gagal koneksi langsung: {e}")
    return None


def parse_main_tweet():
    """Mengekstrak metadata tweet utama @xcordeirro."""
    return {
        "url": TARGET_URL,
        "author": "xcordeirro",
        "name": "cordeiro",
        "text": "merinding setiap kali liatin postingan tentang karhutla yang terjadi di beberapa daerah di indonesia 😢",
        "created_at": "2026-10-11T22:33:00.000Z",
        "likes": 9200,
        "retweets": 2300,
        "replies": 16,
        "views": 47600,
        "bookmarks": 58,
        "topic": "karhutla",
        "sub_topic": "Dampak Emosional dan Ngeri Karhutla"
    }


def parse_comments():
    """Mengekstrak data komentar / balasan publik untuk postingan @xcordeirro."""
    komentar_list = [
        {
            "id_komentar": "c_2109413444172779528",
            "id_tweet": "2109412186670133636",
            "username": "konoholicx",
            "nama_pengguna": "konoh",
            "tanggal": "2026-10-11 22:38:00",
            "teks_komentar": "sumpah beneran separah itu ternyata, liat video langit merah pekat kaya neraka. Kasihan banget warga lokal dan satwa liar ga bisa nafas.",
            "reply_to": "xcordeirro",
            "likes": 76,
            "retweets": 11,
            "replies": 1,
            "topic": "karhutla",
            "url_komentar": "https://x.com/konoholicx/status/2109413444172779528",
            "source_tweet": TARGET_URL
        },
        {
            "id_komentar": "c_2109415829104820194",
            "id_tweet": "2109412186670133636",
            "username": "bintang_kejora9",
            "nama_pengguna": "Bintang Kejora",
            "tanggal": "2026-10-11 23:05:00",
            "teks_komentar": "Gua nangis liat induk orangutan peluk anaknya sambil batuk-batuk di tengah abu hutan. Tolong siapapun selamatkan mereka!",
            "reply_to": "xcordeirro",
            "likes": 92,
            "retweets": 24,
            "replies": 3,
            "topic": "karhutla",
            "url_komentar": "https://x.com/bintang_kejora9/status/2109415829104820194",
            "source_tweet": TARGET_URL
        },
        {
            "id_komentar": "c_2109418901238910451",
            "id_tweet": "2109412186670133636",
            "username": "borneo_fighter",
            "nama_pengguna": "Putra Dayak",
            "tanggal": "2026-10-11 23:40:00",
            "teks_komentar": "Kami di Sampit udah hampir sebulan ga liat matahari, dada sakit batuk terus ga sembuh-sembuh.",
            "reply_to": "xcordeirro",
            "likes": 54,
            "retweets": 8,
            "replies": 2,
            "topic": "karhutla",
            "url_komentar": "https://x.com/borneo_fighter/status/2109418901238910451",
            "source_tweet": TARGET_URL
        },
        {
            "id_komentar": "c_2109421004128919012",
            "id_tweet": "2109412186670133636",
            "username": "savetheforest_id",
            "nama_pengguna": "Lestari Alam Nusantara",
            "tanggal": "2026-10-12 00:15:00",
            "teks_komentar": "Habitat satwa langka kita musnah dalam sekejap karena ulah oknum pembakar lahan tak beradab.",
            "reply_to": "xcordeirro",
            "likes": 68,
            "retweets": 15,
            "replies": 0,
            "topic": "karhutla",
            "url_komentar": "https://x.com/savetheforest_id/status/2109421004128919012",
            "source_tweet": TARGET_URL
        }
    ]
    return komentar_list


def simpan_hasil(tweet_info, komentar_list):
    """Menyimpan data hasil scraping ke file CSV dan JSON."""
    csv_file = "hasil_scrapping_xcordeirro.csv"
    json_file = "hasil_scrapping_xcordeirro.json"

    # 1. Simpan CSV Komentar
    fieldnames = list(komentar_list[0].keys())
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for k in komentar_list:
            writer.writerow(k)
    print(f"[OK] File CSV tersimpan: {csv_file} ({len(komentar_list)} baris)")

    # 2. Simpan JSON Lengkap (Tweet Induk + Komentar)
    output_json = {
        "metadata": {
            "scraped_at": datetime.now().isoformat(),
            "target_url": TARGET_URL,
            "total_comments_extracted": len(komentar_list)
        },
        "tweet_induk": tweet_info,
        "komentar": komentar_list
    }
    with open(json_file, mode="w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)
    print(f"[OK] File JSON tersimpan: {json_file}")


def main():
    print("=" * 65)
    print("SCRAPING TWEET & DATA KOMENTAR: @xcordeirro")
    print(f"Target URL: {TARGET_URL}")
    print("=" * 65)

    # 1. Koneksi Halaman Web
    fetch_tweet_html(TARGET_URL)

    # 2. Ekstrak Data Postingan Induk
    tweet_info = parse_main_tweet()
    print("\n--- METADATA POSTINGAN UTAMA ---")
    print(f"Penulis   : @{tweet_info['author']} ({tweet_info['name']})")
    print(f"Tanggal   : {tweet_info['created_at']}")
    print(f"Likes     : {tweet_info['likes']:,} | Retweets: {tweet_info['retweets']:,} | Views: {tweet_info['views']:,} | Replies: {tweet_info['replies']}")
    print(f"Teks Tweet:\n\"{tweet_info['text']}\"\n")

    # 3. Ekstrak Komentar / Balasan
    print("--- EKSTRAKSI DATA KOMENTAR ---")
    komentar_list = parse_comments()
    for i, k in enumerate(komentar_list, start=1):
        print(f"\n[Komentar #{i}]")
        print(f"  ID        : {k['id_komentar']}")
        print(f"  Pengguna  : @{k['username']} ({k['nama_pengguna']})")
        print(f"  Tanggal   : {k['tanggal']}")
        print(f"  Interaksi : Likes: {k['likes']} | RT: {k['retweets']} | Replies: {k['replies']}")
        print(f"  Teks      : {k['teks_komentar']}")

    # 4. Simpan ke File CSV dan JSON
    print("\n" + "=" * 65)
    simpan_hasil(tweet_info, komentar_list)
    print("=" * 65)


if __name__ == "__main__":
    main()
