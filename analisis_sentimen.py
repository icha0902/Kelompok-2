# -*- coding: utf-8 -*-
"""
Script: analisis_sentimen.py
Deskripsi: Melakukan pembersihan teks, analisis sentimen, analisis spektrum emosi,
            pembuatan wordcloud keluhan masyarakat, serta visualisasi grafik
            distribusi sentimen dan spektrum emosi (PNG & CSV).
"""

import os
import sys
import re
import string
import pandas as pd
import numpy as np

# Pastikan output console mendukung karakter Unicode di Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import matplotlib
matplotlib.use('Agg')  # Mode headless backend untuk rendering grafik tanpa GUI
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Set style visualisasi
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Stopwords Bahasa Indonesia
STOPWORDS_ID = set([
    'yang', 'di', 'dan', 'dari', 'ini', 'untuk', 'pada', 'ke', 'dengan', 'itu',
    'atau', 'adalah', 'akan', 'bisa', 'ada', 'juga', 'oleh', 'saat', 'para',
    'kita', 'mereka', 'karena', 'sudah', 'telah', 'dalam', 'lebih', 'harus',
    'kami', 'saya', 'dia', 'bila', 'jika', 'lalu', 'seperti', 'masih', 'bukan',
    'saja', 'hanya', 'lagi', 'pun', 'dapat', 'belum', 'tentang', 'setelah',
    'kalian', 'siapa', 'mana', 'kenapa', 'bagaimana', 'apa', 'sangat', 'sekali',
    'deh', 'sih', 'dong', 'kok', 'tuh', 'nih', 'kan', 'nya', 'ya', 'aja', 'lah',
    'yuk', 'up', 'guys', 'please', 'the', 'is', 'not', 'of', 'and', 'in', 'to'
])

# Kamus Normalisasi Slang / Kata Baku Bahasa Indonesia
SLANG_DICT = {
    'yg': 'yang', 'dgn': 'dengan', 'sdh': 'sudah', 'udh': 'sudah', 'udah': 'sudah',
    'ga': 'tidak', 'gak': 'tidak', 'gk': 'tidak', 'tdk': 'tidak', 'nggak': 'tidak',
    'bgt': 'banget', 'beneran': 'benar', 'bgt': 'banget', 'bener': 'benar',
    'dr': 'dari', 'utk': 'untuk', 'klo': 'kalau', 'kalo': 'kalau', 'sm': 'sama',
    'sy': 'saya', 'gw': 'saya', 'gua': 'saya', 'lu': 'kamu', 'lo': 'kamu',
    'jkt': 'jakarta', 'jabar': 'jawa barat', 'banten': 'banten', 'bgmn': 'bagaimana',
    'gmn': 'bagaimana', 'trs': 'terus', 'bapack': 'bapak', 'org': 'orang',
    'dpt': 'dapat', 'sampe': 'sampai', 'liat': 'lihat', 'ngerasa': 'merasa',
    'ngerasain': 'merasakan', 'pake': 'pakai', 'bikin': 'membuat', 'aja': 'saja'
}

# Leksikon Kata Kunci Sentimen & Emosi Bahasa Indonesia
LEKSIKON_POSITIF = set([
    'bagus', 'keren', 'mantul', 'hebat', 'terima kasih', 'makasih', 'salut', 'doa',
    'semoga', 'aamiin', 'terbaik', 'berjuang', 'semangat', 'berhasil', 'pulih',
    'bantuan', 'peduli', 'solidaritas', 'bangga', 'cepat', 'ramah', 'aman', 'recomended',
    'lestari', 'lindungilah', 'bersih', 'beres', 'jaya', 'mantap', 'membaik'
])

LEKSIKON_NEGATIF = set([
    'parah', 'buruk', 'terburuk', 'lambat', 'sesak', 'asap', 'kebakaran', 'terbakar',
    'rusak', 'kecewa', 'marah', 'lalai', 'bencana', 'bahaya', 'berbahaya', 'beracun',
    'ispa', 'batuk', 'sakit', 'musnah', 'ludes', 'neraka', 'menyerah', 'sepele',
    'cacat', 'telat', 'mafia', 'cukong', 'korporasi', 'pencitraan', 'demo', 'darurat'
])

EMOSI_KEYWORDS = {
    'Marah': ['marah', 'copot', 'pecat', 'demo', 'pencitraan', 'hukum', 'tindak', 'korporasi', 'cukong', 'bakar', 'parah', 'gengsi'],
    'Sedih': ['sedih', 'nangis', 'orangutan', 'satwa', 'musnah', 'ludes', 'kasihan', 'batuk darah', 'ispa', 'meninggal', 'tercekik'],
    'Takut/Cemas': ['takut', 'cemas', 'waspada', 'berbahaya', 'merinding', 'neraka', 'pekat', 'sesak', 'racun', 'panik', 'jarak pandang'],
    'Kecewa': ['kecewa', 'lambat', 'lempar', 'telat', 'kurang', 'sayang', 'lalai', 'sepele', 'hanya', 'sia-sia'],
    'Harapan/Empati': ['semoga', 'aamiin', 'doa', 'salut', 'bantuan', 'donasi', 'semangat', 'kuat', 'tolong', 'terima kasih', 'kawal'],
    'Netral': ['bmkg', 'ispu', 'satelit', 'data', 'informasi', 'angin', 'indeks', 'info', 'himbauan', 'aplikasi']
}


def bersihkan_teks(teks):
    """Membersihkan teks komentar: hilangkan URL, mention, hashtag, simbol, dan normalisasi."""
    if not isinstance(teks, str):
        return ""
    # Lowercase
    t = teks.lower()
    # Hilangkan URL
    t = re.sub(r'http\S+|www\S+|https\S+', '', t, flags=re.MULTILINE)
    # Hilangkan mention @username
    t = re.sub(r'@\w+', '', t)
    # Hilangkan hashtag #tagar
    t = re.sub(r'#\w+', '', t)
    # Hilangkan angka dan karakter khusus
    t = re.sub(r'\d+', '', t)
    t = t.translate(str.maketrans('', '', string.punctuation))
    # Normalisasi kata slang
    kata_list = t.split()
    kata_normal = [SLANG_DICT.get(k, k) for k in kata_list if k not in STOPWORDS_ID and len(k) > 1]
    return " ".join(kata_normal)


def analisis_skor_sentimen(teks_bersih, default_label=None):
    """Menghitung skor sentimen berdasarkan kamus leksikon."""
    if default_label in ["Positif", "Negatif", "Netral"]:
        # Jika dataset sudah memiliki label seed, gunakan dengan confidence tinggi
        score = 0.8 if default_label == "Positif" else (-0.8 if default_label == "Negatif" else 0.0)
        return default_label, score

    tokens = teks_bersih.split()
    pos_count = sum(1 for w in tokens if w in LEKSIKON_POSITIF)
    neg_count = sum(1 for w in tokens if w in LEKSIKON_NEGATIF)

    if pos_count > neg_count:
        return "Positif", round((pos_count - neg_count) / (pos_count + neg_count + 1), 3)
    elif neg_count > pos_count:
        return "Negatif", round(-(neg_count - pos_count) / (pos_count + neg_count + 1), 3)
    else:
        return "Netral", 0.0


def deteksi_spektrum_emosi(teks_bersih, default_emosi=None):
    """Mendeteksi spektrum emosi dominan dalam teks."""
    if default_emosi in EMOSI_KEYWORDS:
        return default_emosi

    tokens = teks_bersih.split()
    skor_emosi = {k: 0 for k in EMOSI_KEYWORDS}
    
    for emosi, keywords in EMOSI_KEYWORDS.items():
        for kw in keywords:
            if kw in tokens:
                skor_emosi[emosi] += 1
                
    max_emosi = max(skor_emosi, key=skor_emosi.get)
    if skor_emosi[max_emosi] > 0:
        return max_emosi
    return "Netral"


def visualisasikan_distribusi_sentimen(df, output_img, judul="Distribusi Sentimen Publik"):
    """Membuat visualisasi pie/donut chart dan bar chart distribusi sentimen."""
    counts = df['sentimen_prediksi'].value_counts()
    for cat in ['Negatif', 'Positif', 'Netral']:
        if cat not in counts:
            counts[cat] = 0

    ordered_labels = ['Negatif', 'Netral', 'Positif']
    ordered_values = [counts.get(l, 0) for l in ordered_labels]
    colors = ['#e74c3c', '#95a5a6', '#2ecc71']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#ffffff')

    # Donut Chart
    wedges, texts, autotexts = ax1.pie(
        ordered_values,
        labels=ordered_labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        textprops=dict(color="#2c3e50", fontsize=11, fontweight='bold')
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color('#ffffff')
    ax1.set_title(f"{judul} (Persentase)", fontsize=14, fontweight='bold', pad=15, color='#2c3e50')

    # Bar Chart
    bars = ax2.bar(ordered_labels, ordered_values, color=colors, width=0.5, edgecolor='#333333', linewidth=0.5)
    ax2.set_title(f"{judul} (Jumlah Komentar)", fontsize=14, fontweight='bold', pad=15, color='#2c3e50')
    ax2.set_ylabel("Jumlah Komentar", fontsize=11)
    ax2.set_ylim(0, max(ordered_values) * 1.15 if max(ordered_values) > 0 else 10)

    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:,}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4),  # offset vertical
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2c3e50')

    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Visualisasi Sentimen tersimpan: {output_img}")


def visualisasikan_spektrum_emosi(df, output_img, judul="Spektrum Emosi Komentar"):
    """Membuat visualisasi horizontal bar chart untuk spektrum emosi."""
    counts = df['spektrum_emosi'].value_counts()
    
    kategori_emosi = ['Marah', 'Sedih', 'Takut/Cemas', 'Kecewa', 'Harapan/Empati', 'Netral']
    values = [counts.get(k, 0) for k in kategori_emosi]
    palette = ['#c0392b', '#8e44ad', '#d35400', '#f39c12', '#27ae60', '#7f8c8d']

    plt.figure(figsize=(10, 6))
    bars = plt.barh(kategori_emosi, values, color=palette, edgecolor='#333333', linewidth=0.5, height=0.6)
    plt.title(f"{judul}\n(Analisis Kategori Emosi Masyarakat)", fontsize=14, fontweight='bold', pad=15, color='#2c3e50')
    plt.xlabel("Frekuensi Komentar", fontsize=11, color='#2c3e50')
    plt.xlim(0, max(values) * 1.15 if max(values) > 0 else 10)
    plt.gca().invert_yaxis()

    total = sum(values)
    for bar in bars:
        width = bar.get_width()
        pct = (width / total * 100) if total > 0 else 0
        plt.annotate(f' {int(width):,} ({pct:.1f}%)',
                     xy=(width, bar.get_y() + bar.get_height() / 2),
                     xytext=(5, 0),
                     textcoords="offset points",
                     ha='left', va='center', fontsize=10, fontweight='bold', color='#2c3e50')

    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Visualisasi Spektrum Emosi tersimpan: {output_img}")


def visualisasikan_wordcloud_keluhan(df, output_img, judul="WordCloud Keluhan"):
    """Membuat gambar WordCloud dari komentar keluhan dan isu darurat."""
    # Prioritaskan komentar bersentimen negatif atau emosi marah/sedih/takut/kecewa
    keluhan_df = df[df['sentimen_prediksi'].isin(['Negatif', 'Netral'])]
    if keluhan_df.empty:
        keluhan_df = df

    all_text = " ".join(keluhan_df['teks_bersih'].dropna().tolist())
    if not all_text.strip():
        all_text = "asap kebakaran hutan karhutla sesak nafas ispa bantuan masker pemerintah kalimantan sumatera"

    wc = WordCloud(
        width=1200,
        height=650,
        background_color='#ffffff',
        colormap='inferno',
        max_words=120,
        contour_width=1,
        contour_color='#e74c3c',
        random_state=42,
        collocations=False
    ).generate(all_text)

    plt.figure(figsize=(12, 6.5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(f"{judul} - Isu & Keluhan Utama Masyarakat", fontsize=15, fontweight='bold', pad=15, color='#c0392b')
    plt.tight_layout(pad=0)
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] WordCloud tersimpan: {output_img}")


def proses_analisis_dataset(csv_path, prefix_name, judul_grafik):
    """Memproses satu file dataset komentar secara komprehensif."""
    if not os.path.exists(csv_path):
        print(f"[!] File {csv_path} tidak ditemukan, lewati proses.")
        return None

    print(f"\n---> Memproses Analisis Data: {csv_path}...")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"     Jumlah total komentar dibaca: {len(df):,} baris")

    # 1. Pembersihan Teks
    df['teks_bersih'] = df['teks_komentar'].apply(bersihkan_teks)

    # 2. Klasifikasi Sentimen & Skor
    sentimen_list = []
    skor_list = []
    for idx, row in df.iterrows():
        default_lbl = row.get('label_sentimen', None)
        lbl, scr = analisis_skor_sentimen(row['teks_bersih'], default_lbl)
        sentimen_list.append(lbl)
        skor_list.append(scr)

    df['sentimen_prediksi'] = sentimen_list
    df['skor_sentimen'] = skor_list

    # 3. Klasifikasi Spektrum Emosi
    emosi_list = []
    for idx, row in df.iterrows():
        default_ems = row.get('spektrum_emosi', None)
        ems = deteksi_spektrum_emosi(row['teks_bersih'], default_ems)
        emosi_list.append(ems)

    df['spektrum_emosi'] = emosi_list

    # 4. Simpan Hasil Analisis ke CSV
    out_csv = f"hasil_analisis_sentimen_{prefix_name}.csv" if prefix_name else "hasil_analisis_sentimen.csv"
    df.to_csv(out_csv, index=False, encoding='utf-8')
    print(f"[OK] File hasil analisis tersimpan: {out_csv}")

    # 5. Buat dan Simpan Visualisasi Grafik
    suffix = f"_{prefix_name}" if prefix_name else ""
    
    img_sentimen = f"grafik_distribusi_sentimen{suffix}.png"
    visualisasikan_distribusi_sentimen(df, img_sentimen, f"Distribusi Sentimen {judul_grafik}")

    img_emosi = f"grafik_spektrum_emosi{suffix}.png"
    visualisasikan_spektrum_emosi(df, img_emosi, f"Spektrum Emosi {judul_grafik}")

    img_wc = f"grafik_wordcloud_keluhan{suffix}.png"
    visualisasikan_wordcloud_keluhan(df, img_wc, f"WordCloud {judul_grafik}")

    return df


def main():
    print("=" * 60)
    print("SISTEM ANALISIS SENTIMEN & SPEKTRUM EMOSI SOSIAL MEDIA")
    print("=" * 60)

    # 1. Dataset Utama / Gabungan Karhutla
    df_utama = proses_analisis_dataset("data_komentar_karhutla.csv", prefix_name="", judul_grafik="Isu Karhutla Nasional")

    # 2. Dataset Kompascom
    proses_analisis_dataset("data_komentar_kompascom.csv", prefix_name="kompascom", judul_grafik="Kompas.com (Karhutla)")

    # 3. Dataset Search Karhutla
    proses_analisis_dataset("data_komentar_search_karhutla.csv", prefix_name="search_karhutla", judul_grafik="Pencarian Karhutla X")

    # 4. Dataset Cortis (Struktur Kelompok)
    proses_analisis_dataset("data_komentar_cortis.csv", prefix_name="cortis", judul_grafik="Cortis Indonesia")

    # 5. Dataset Ejaaipongg (Struktur Kelompok)
    proses_analisis_dataset("data_komentar_ejaaipongg.csv", prefix_name="ejaaipongg", judul_grafik="Ejaaipongg (Kreator Konten)")

    print("\n" + "=" * 60)
    print("SEMUA ANALISIS, GRAFIK, DAN WORDCLOUD BERHASIL DIBUAT LENGKAP!")
    print("=" * 60)


if __name__ == "__main__":
    main()
