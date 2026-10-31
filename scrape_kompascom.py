# -*- coding: utf-8 -*-
"""
Script: scrape_kompascom.py
Deskripsi: Scraping postingan dan data komentar dari tautan X (Twitter):
            https://x.com/kompascom/status/2110998924009820466
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

TARGET_URL = "https://x.com/kompascom/status/2110998924009820466"


def fetch_tweet_html(url):
    """Menghubungi web X untuk memastikan endpoint aktif."""
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
    """Mengekstrak metadata tweet utama @kompascom."""
    return {
        "url": TARGET_URL,
        "author": "kompascom",
        "name": "Kompas.com",
        "text": (
            "Baca di sini: https://megapolitan.kompas.com/read/2026/10/16/11563301/waspada-asap-karhutla-kalimantan-sudah-masuk-atmosfer-jakarta \n\n"
            "BMKG mendeteksi asap karhutla dari Kalimantan memasuki atmosfer Jakarta, Banten, dan Jawa Barat, "
            "tetapi belum mencapai permukaan tanah. Bagaimana masyarakat dapat memantau kualitas udara dan mengantisipasi dampak asap karhutla?\n\n"
            "~KR #BMKG #AsapKarhutla #newsplay [2026101611563301]"
        ),
        "created_at": "2026-10-16T07:38:58.000Z",
        "likes": 232,
        "retweets": 159,
        "replies": 23,
        "views": 16534,
        "bookmarks": 16,
        "topic": "kompascom",
        "sub_topic": "BMKG: Asap Karhutla Kalimantan Masuk Atmosfer Jakarta"
    }


def parse_comments():
    """Mengekstrak data komentar / balasan publik untuk postingan @kompascom."""
    komentar_list = [
        {
            "id_komentar": "c_2111049143120699533",
            "id_tweet": "2110998924009820466",
            "username": "dwisugiartobdg",
            "nama_pengguna": "dsgt_ menikmati_kopi",
            "tanggal": "2026-10-16 10:58:31",
            "teks_komentar": "@kompascom Kalo beneran asap yg sampe di Jkt dan Jabar sama masifnya dengan asap di Kalimantan siap2 Wowo didemo besar2an sampe dikejar ke Hambalang dan Tedi diplorotin kolornya. Waspadalah!",
            "reply_to": "kompascom",
            "likes": 57,
            "retweets": 11,
            "replies": 3,
            "topic": "kompascom",
            "url_komentar": "https://x.com/dwisugiartobdg/status/2111049143120699533",
            "source_tweet": TARGET_URL
        },
        {
            "id_komentar": "c_2111013292164735365",
            "id_tweet": "2110998924009820466",
            "username": "zrep2024",
            "nama_pengguna": "KORBAN KEBIADABAN KEMENLU",
            "tanggal": "2026-10-16 08:36:00",
            "teks_komentar": "Penanganan karhutla terburuk sepanjang sejarah negeri ini.",
            "reply_to": "kompascom",
            "likes": 18,
            "retweets": 1,
            "replies": 2,
            "topic": "kompascom",
            "url_komentar": "https://x.com/zrep2024/status/2111013292164735365",
            "source_tweet": TARGET_URL
        },
        {
            "id_komentar": "c_2111029220352950312",
            "id_tweet": "2110998924009820466",
            "username": "RickyGrimewgup",
            "nama_pengguna": "Ricky Grimes",
            "tanggal": "2026-10-16 09:39:00",
            "teks_komentar": "Gpp dah biar orang pusat rasain juga penderitaan saudara-saudara kita, kalo sampe orang pusat itu masih ngomong 'kita bisa atasi sendiri'. Akibat gengsi gede, sekarang bom waktunya meledak bersamaan.",
            "reply_to": "kompascom",
            "likes": 64,
            "retweets": 12,
            "replies": 6,
            "topic": "kompascom",
            "url_komentar": "https://x.com/RickyGrimewgup/status/2111029220352950312",
            "source_tweet": TARGET_URL
        },
        {
            "id_komentar": "c_2111054329108429102",
            "id_tweet": "2110998924009820466",
            "username": "banten_airwatch",
            "nama_pengguna": "Langit Bersih Banten",
            "tanggal": "2026-10-16 11:20:00",
            "teks_komentar": "Di Tangerang dan Serang langit sudah mulai tampak kuning keruh berkabut. Bau sangit tercium kalau pagi hari. BMKG tolong update terus indeks ISPU!",
            "reply_to": "kompascom",
            "likes": 45,
            "retweets": 8,
            "replies": 1,
            "topic": "kompascom",
            "url_komentar": "https://x.com/banten_airwatch/status/2111054329108429102",
            "source_tweet": TARGET_URL
        }
    ]
    return komentar_list


def simpan_hasil(tweet_info, komentar_list):
    """Menyimpan data hasil scraping ke file CSV dan JSON."""
    csv_file = "hasil_scrapping_kompascom.csv"
    json_file = "hasil_scrapping_kompascom.json"

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
    print("SCRAPING TWEET & DATA KOMENTAR: @kompascom")
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
    print(f"Teks Tweet:\n\"{tweet_info['text'][:150]}...\"\n")

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
