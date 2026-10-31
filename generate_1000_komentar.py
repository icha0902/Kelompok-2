# -*- coding: utf-8 -*-
"""
Script: generate_1000_komentar.py
Deskripsi: Generator database 1.000 komentar media sosial untuk keperluan
            analisis data, text mining, analisis sentimen & spektrum emosi.
            Menghasilkan file CSV database komentar dengan data realistis.
"""

import csv
import re
import random
from datetime import datetime, timedelta

# ==============================================================================
# TEMPLATE KOMENTAR BERDASARKAN TOPIK & SPEKTRUM EMOSI
# ==============================================================================

# 1. Topik Kompascom (Fokus: Berita Asap Karhutla Masuk Jawa/Jakarta & Isu Publik)
KOMPASCOM_TEMPLATES = [
    ("Kalo beneran asap yg sampe di Jkt dan Jabar sama masifnya dengan asap di Kalimantan siap2 pemerintah didemo besar2an. Waspadalah!", "Negatif", "Marah"),
    ("Penanganan karhutla terburuk sepanjang sejarah negeri ini. Lambat dan minim aksi nyata.", "Negatif", "Marah"),
    ("Gpp biar orang pusat ngerasain apa yg dirasain saudara kita di Sumatra dan Kalimantan bertahun-tahun.", "Negatif", "Kecewa"),
    ("Di Banten dan Tangerang pagi ini langit udah menguning pekat, bau sangit bikin dada sesak.", "Negatif", "Takut/Cemas"),
    ("Tolong BMKG dan dinas kesehatan bagi-bagikan masker N95 gratis untuk warga terdampak kabut asap.", "Netral", "Harapan/Empati"),
    ("Anak-anak sekolah di Kalbar dan Riau udah diliburkan karena indeks ISPU masuk kategori berbahaya.", "Negatif", "Sedih"),
    ("Semoga segera turun hujan deras buatan atau alami agar titik api padam seluruhnya. Aamiin.", "Positif", "Harapan/Empati"),
    ("Masyarakat dihimbau kurangi aktivitas luar ruangan dan pantau kualitas udara lewat aplikasi ISPU net.", "Netral", "Netral"),
    ("Helikopter water bombing tolong ditambah armadanya, api di gambut ga bakal padam cuma pake selang air biasa.", "Negatif", "Kecewa"),
    ("Sedih banget liat langit biru udah ga keliatan lagi, diganti kepulan asap tebal menyiksa.", "Negatif", "Sedih"),
    ("Terima kasih kepada para relawan pemadam kebakaran dan TNI-Polri yang berjuang di garda terdepan!", "Positif", "Harapan/Empati"),
    ("Jangan cuma rapat di hotel mewah, turun langsung ke lapangan bantu padamkan api!", "Negatif", "Marah"),
    ("Pemerintah daerah dan pusat harus saling koordinasi, jangan saling lempar tanggung jawab pas bencana begini.", "Negatif", "Kecewa"),
    ("Info cuaca hari ini kecepatan angin membawa partikel asap ke arah selatan dan barat daya pulau Jawa.", "Netral", "Netral"),
    ("Beli air purifier sampe ludes di toko-toko karena panik asap udah masuk Jabodetabek.", "Negatif", "Takut/Cemas"),
    ("Ayo galang donasi tabung oksigen dan nebulizer untuk puskesmas di pedalaman Kalimantan.", "Positif", "Harapan/Empati"),
    ("Tindak tegas korporasi pembakar lahan sawit! Jangan cuma rakyat kecil yg dikorbankan.", "Negatif", "Marah"),
    ("Kondisi udara makin memburuk, tolong pemerintah tetapkan status tanggap darurat nasional!", "Negatif", "Takut/Cemas"),
    ("Data satelit BMKG mendeteksi lonjakan hotspot kebakaran hutan hingga 400 titik baru.", "Netral", "Netral"),
    ("Merinding liat foto satelit BMKG, pulau kita bener-bener diselimuti asap putih tebal.", "Negatif", "Sedih"),
    ("Setiap tahun polanya sama, selalu kaget pas kebakaran udah luas. Sistem mitigasi kemana aja?", "Negatif", "Kecewa"),
    ("Apresiasi untuk tim gabungan yang berhasil memadamkan titik api di kawasan perbatasan.", "Positif", "Harapan/Empati"),
    ("Tenggorokan udah mulai gatal dan mata perih sejak pagi tadi gara-gara polusi asap.", "Negatif", "Takut/Cemas"),
    ("Kemenkes wajib kirim dokter spesialis paru ke wilayah dengan paparan asap tertinggi.", "Netral", "Harapan/Empati"),
    ("Jangan ada kompromi bagi mafia pembakar hutan lindung, cabut izin HGU-nya seumur hidup!", "Negatif", "Marah"),
    ("Alhamdulillah sebagian wilayah mulai diguyur hujan gerimis berkat teknologi modifikasi cuaca.", "Positif", "Harapan/Empati"),
    ("Angka ISPU di atas 300 itu sangat berbahaya untuk lansia dan balita, tolong evakuasi segera.", "Negatif", "Takut/Cemas"),
    ("Media tolong terus kawal perkembangan kualitas udara dan penegakan hukum pembakar hutan.", "Netral", "Netral")
]

# 2. Topik Karhutla Umum & Tanjung Puting (Fokus: Ekosistem, Kehancuran Hutan & Kritik Lapangan)
KARHUTLA_TEMPLATES = [
    ("Taman Nasional Tanjung Puting suaka margasatwa orangutan terbakar hebat, relawan kehabisan tenaga dan oksigen.", "Negatif", "Sedih"),
    ("Saat kebakaran terjadi dianggap sepele, giliran udah meluas baru bingung cari solusi tepung dan terjun payung.", "Negatif", "Marah"),
    ("Kepala BNPB dan Menteri Kehutanan harusnya dicopot kalau ga sanggup atasi krisis tahunan ini.", "Negatif", "Marah"),
    ("Gubernurnya sibuk pencitraan sedangkan rakyat di bawah tercekik asap beracun tiap hari.", "Negatif", "Marah"),
    ("Habitat satwa langka kita musnah dalam sekejap karena ulah oknum pembakar lahan tak beradab.", "Negatif", "Sedih"),
    ("Sumpah beneran separah itu, liat video langit merah pekat kaya neraka. Kasihan banget anak-anak kecil.", "Negatif", "Takut/Cemas"),
    ("Doa terbaik untuk kawan-kawan relawan dan masyarakat Borneo, semoga badai asap ini segera berakhir.", "Positif", "Harapan/Empati"),
    ("Kami di Sampit udah hampir sebulan ga liat matahari, dada sakit batuk terus ga sembuh-sembuh.", "Negatif", "Sedih"),
    ("Hukum berat cukong dan mafia tanah yang sengaja bakar lahan gambut buat buka kebun baru!", "Negatif", "Marah"),
    ("Tolong dunia internasional bantu padamkan api di hutan tropis Indonesia, ini paru-paru bumi!", "Positif", "Harapan/Empati"),
    ("Hutan lindung tempat orangutan berlindung ludes terbakar, kemana lagi mereka harus lari?", "Negatif", "Sedih"),
    ("Operasi modifikasi cuaca TMC harus ditingkatkan frekuensinya setiap hari tanpa jeda.", "Netral", "Netral"),
    ("Rumah sakit penuh pasien ISPA dan sesak nafas, pasokan oksigen di apotek mulai menipis.", "Negatif", "Takut/Cemas"),
    ("Salut untuk perjuangan kawan Manggala Agni yang pantang pulang sebelum api padam total.", "Positif", "Harapan/Empati"),
    ("Pemerintah tolong prioritaskan anggaran penanganan bencana daripada proyek mercusuar ga jelas.", "Negatif", "Kecewa"),
    ("Lahan gambut kalau udah kebakar di bawah tanah susah banget dipadamkan, butuh teknik khusus.", "Netral", "Netral"),
    ("Keluarga kami di Palangkaraya terpaksa mengungsi karena jarak pandang cuma 10 meter.", "Negatif", "Takut/Cemas"),
    ("Mari kita bersama suarakan isu ini agar jadi perhatian nomor satu di tingkat nasional!", "Positif", "Harapan/Empati"),
    ("Setiap musim kemarau polanya selalu berulang, pencegahan dan sistem peringatan dininya mana?", "Negatif", "Kecewa"),
    ("Ya Tuhan lindungilah saudara-saudara kami di daerah bencana karhutla.", "Positif", "Harapan/Empati"),
    ("Hati hancur berkeping-keping liat foto anak orangutan hangus terpanggang di sisa abu bakaran.", "Negatif", "Sedih"),
    ("Prajurit TNI dan tim damkar berjuang bertaruh nyawa di tengah kobaran api gambut, hormat setinggi-tingginya!", "Positif", "Harapan/Empati"),
    ("Udah sebulan anak-anak ga bisa main di luar rumah, kasihan masa kecilnya terkurung asap.", "Negatif", "Sedih"),
    ("Bencana ini buatan manusia serakah yang ingin buka kebun sawit tanpa modal tebang pohon!", "Negatif", "Marah"),
    ("Semoga segera ada hujan lebat berkah yang memadamkan seluruh titik api di pelosok nusantara.", "Positif", "Harapan/Empati")
]

# 3. Topik Search Karhutla & Solidaritas Netizen (Fokus: Gerakan #IndonesiaButuhOksigen, Desakan Darurat)
SEARCH_KARHUTLA_TEMPLATES = [
    ("GUYS PLEASE DONT STOP TALKING ABOUT KARHUTLA! THIS IS REAL! #IndonesiaButuhOksigen #PRAYFORKALIMANTAN", "Positif", "Harapan/Empati"),
    ("Up terus biar ga ketimbun berita politik drama! Rakyat butuh udara bersih sekarang juga!", "Positif", "Harapan/Empati"),
    ("Naikkan status bencana nasional sekarang! #NaikkanStatusBencana #AllEyesOnKarhutla #IndonesiaButuhOksigen", "Negatif", "Marah"),
    ("Anak-anak balita di pelosok udah batuk darah karena hirup kabut asap pekat tiap hari, tolong buka mata!", "Negatif", "Sedih"),
    ("Tag akun presiden dan kementerian terkait biar segera kirim bantuan skala besar ke lokasi bencana!", "Netral", "Harapan/Empati"),
    ("Kalian yg di ruangan ber-AC enak ga ngerasain, saudara kita di sana nafas aja perih banget tenggorokan.", "Negatif", "Kecewa"),
    ("PRAY FOR KALIMANTAN, PRAY FOR SUMATERA, PRAY FOR INDONESIA! Tetap kuat kawan-kawan!", "Positif", "Harapan/Empati"),
    ("Kawal terus kasus pembakaran hutan jangan sampai perusahaannya lolos dari jeratan hukum!", "Negatif", "Marah"),
    ("Bantuan masker dan vitamin sangat dibutuhkan oleh relawan pemadam kebakaran di lapangan.", "Netral", "Harapan/Empati"),
    ("Langit Kalimantan berubah jadi oranye kemerahan seperti kiamat, tolong jangan tinggal diam!", "Negatif", "Takut/Cemas"),
    ("Sebarkan informasi kontak posko darurat dan bantuan oksigen di daerah terdampak karhutla.", "Netral", "Netral"),
    ("Pemerintah harus evaluasi izin konsesi lahan sawit dan HTI yang terbukti lalai menjaga kawasannya.", "Negatif", "Kecewa"),
    ("Krisis iklim makin nyata di depan mata, mari jaga hutan kita demi masa depan anak cucu.", "Positif", "Harapan/Empati"),
    ("Sudah berminggu-minggu asap tebal menyelimuti kota, kemana suara wakil rakyat kita?", "Negatif", "Kecewa"),
    ("Semoga hujan lebat segera mengguyur seluruh pulau Kalimantan dan Sumatera pekan ini.", "Positif", "Harapan/Empati"),
    ("Jangan biarkan saudara kita berjuang sendirian di bawah kepungan kabut asap beracun!", "Positif", "Harapan/Empati"),
    ("Kita butuh paru-paru sehat bukan asap pekat! Stop pembakaran hutan sekarang juga!", "Negatif", "Marah"),
    ("Ayo sisihkan rezeki untuk suplai tabung oksigen dan makanan bagi tim relawan pemadam.", "Positif", "Harapan/Empati"),
    ("Kondisi di lapangan semakin genting, jarak pandang nol meter penerbangan banyak yang dialihkan.", "Negatif", "Takut/Cemas"),
    ("Viralkan terus tagar #DaruratKarhutla sampai ada aksi konkret dan nyata dari pengambil kebijakan!", "Positif", "Harapan/Empati")
]

# 4. Topik Cortis Indonesia (Fokus: E-Commerce, Brand Feedback & Layanan)
CORTIS_TEMPLATES = [
    ("Produk cortis indonesia beneran mantul dan worth it banget untuk dipakai harian!", "Positif", "Harapan/Empati"),
    ("Pelayanan customer servicenya cepat dan ramah, pesanan datang sesuai deskripsi.", "Positif", "Harapan/Empati"),
    ("Barang sampai dengan aman, packing rapi pake bubble wrap tebal. Recomended seller!", "Positif", "Harapan/Empati"),
    ("Kualitas bahannya bagus tapi pengirimannya lumayan lama, tolong ditingkatkan ekspedisinya.", "Netral", "Kecewa"),
    ("Harga bersahabat di kantong mahasiswa, cocok banget buat referensi belanja.", "Positif", "Harapan/Empati"),
    ("Ada sedikit cacat di bagian kemasan luar, tapi fungsi produknya tetap bekerja normal.", "Netral", "Netral"),
    ("Adminnya fast respon pas ditanya soal cara penggunaan produk, makasih banyak ya!", "Positif", "Harapan/Empati"),
    ("Sudah langganan di cortis indonesia dari tahun lalu dan selalu puas dengan pelayanannya.", "Positif", "Harapan/Empati"),
    ("Semoga makin banyak promo diskon menarik dan voucher cashback ke depannya.", "Positif", "Harapan/Empati"),
    ("Bagus sih cuma varian warnanya cepat habis, tolong restock lebih banyak lagi dong.", "Netral", "Kecewa"),
    ("Desainnya simpel elegan dan kekinian banget, suka sama konsep branding cortis.", "Positif", "Harapan/Empati"),
    ("Produk lokal dengan standar kualitas internasional, bangga buatan Indonesia!", "Positif", "Harapan/Empati"),
    ("Beli pas promo flash sale dapat harga miring banget, kualitas tetap juara!", "Positif", "Harapan/Empati"),
    ("Pengemasan rapi dan aman, seller amanah banget bakal order lagi nanti.", "Positif", "Harapan/Empati"),
    ("Respon admin agak lambat saat weekend, tapi produk yang dikirim memuaskan.", "Netral", "Netral"),
    ("Suka banget sama material bahannya yang adem dan jahitannya sangat presisi.", "Positif", "Harapan/Empati"),
    ("Mohon tambah pilihan opsi kurir pengiriman instan biar cepat sampai.", "Netral", "Netral"),
    ("Barang ori dan sesuai foto etalase, mantap pol!", "Positif", "Harapan/Empati")
]

# 5. Topik Ejaaipongg (Fokus: Konten Kreator, Hiburan & Komunitas Netizen)
EJAAIPONGG_TEMPLATES = [
    ("Konten ejaaipongg selalu menghibur dan lucu parah, ga pernah bosen nonton!", "Positif", "Harapan/Empati"),
    ("Semangat terus bikin konten positif ya bang ejaaipongg, sukses selalu!", "Positif", "Harapan/Empati"),
    ("Ngakak guling-guling liat ekspresinya di video terbaru, beneran mood booster hari ini.", "Positif", "Harapan/Empati"),
    ("Suka sama gaya pembawaan bang Eja yang santai dan relate sama kehidupan sehari-hari.", "Positif", "Harapan/Empati"),
    ("Editing videonya makin keren dan transisinya halus banget, level up abis!", "Positif", "Harapan/Empati"),
    ("Kontennya makin ke sini makin seru, kolab dong bareng kreator lainnya!", "Positif", "Harapan/Empati"),
    ("Kurang panjang durasi videonya bang, baru seru udah selesai aja hehe.", "Netral", "Kecewa"),
    ("Terima kasih selalu menghibur di kala lelah pulang kerja, sehat selalu bang eja!", "Positif", "Harapan/Empati"),
    ("Ide kontennya selalu fresh dan ga pasaran, salut konsistensinya.", "Positif", "Harapan/Empati"),
    ("Kapan adain meet and greet di luar kota bang? Pengen foto bareng!", "Positif", "Harapan/Empati"),
    ("Audio videonya kadang agak kekecilan di menit awal, tolong dicek lagi ya bang.", "Netral", "Netral"),
    ("Konten edukasi dibalut komedi kayak gini yang patut diapresiasi banyak orang.", "Positif", "Harapan/Empati")
]

# Daftar Username Realistis
USERNAMES_SEEDS = [
    ("budi_santoso", "Budi Santoso"), ("anisa_rahma", "Anisa Rahmawati"), ("reza_pratama", "Reza Pratama"),
    ("dian_sastro", "Dian Kartika"), ("fajar_ramadhan", "Fajar Ramadhan"), ("siti_nurhaliza", "Siti Nurhaliza"),
    ("ilham_saputra", "Ilham Saputra"), ("putri_ayu", "Putri Ayu Wardani"), ("bayu_samudra", "Bayu Samudra"),
    ("nadia_azzahra", "Nadia Azzahra"), ("rio_dewanto", "Rio Dewanto"), ("maya_safitri", "Maya Safitri"),
    ("hendra_gunawan", "Hendra Gunawan"), ("lestari_alam", "Pecinta Alam"), ("warga_borneo", "Warga Banua"),
    ("suara_rakyat", "Suara Rakyat Jelata"), ("pantau_udara", "Relawan Udara Bersih"), ("peduli_hutan", "Save Our Forest"),
    ("tomi_wijaya", "Tomi Wijaya"), ("rina_anggraeni", "Rina Anggraeni"), ("agus_setiawan", "Agus Setiawan"),
    ("nurul_hidayah", "Nurul Hidayah"), ("dimas_anggara", "Dimas Anggara"), ("meta_dewi", "Meta Dewi"),
    ("alif_firdaus", "Alif Firdaus"), ("zaki_mubarok", "Zaki Mubarok"), ("vina_pandu", "Vina Panduwinata"),
    ("eko_patrio", "Eko Prasetyo"), ("gita_gutawa", "Gita Savitri"), ("aditya_surya", "dr. Aditya Surya"),
    ("kartika_sari", "Kartika Sari"), ("rizky_febian", "Rizky F."), ("tiara_andini", "Tiara Andini"),
    ("faizal_tanjung", "Faizal Tanjung"), ("melati_sukma", "Melati Sukma"), ("andi_wijaya", "Andi Wijaya"),
    ("dewi_persik", "Dewi Sartika"), ("gilang_dirga", "Gilang Ramadhan"), ("syarif_hidayat", "Syarif Hidayat")
]

# Variasi Slang & Bahasa Sehari-hari
VARIAN_KATA = [
    ("banget", "bgt"), ("tidak", "ga"), ("tidak", "gak"), ("tidak", "gk"),
    ("sudah", "udh"), ("sudah", "sdh"), ("dengan", "dgn"), ("yang", "yg"),
    ("kalau", "kalo"), ("kalau", "klo"), ("saya", "sy"), ("saya", "gw"),
    ("terus", "trs"), ("bisa", "bs"), ("orang", "org"), ("kenapa", "knp"),
    ("beneran", "bener2"), ("kemana", "kmn"), ("bagaimana", "gmn")
]

AFIKS_EMOSI = {
    "Marah": ["!!", "!!!", " 😡", " 😠👎", " parah banget!", " keterlaluan."],
    "Sedih": [" 😢", " 😭", " 💔", " sedih banget liatnya...", "...", " ya ampun 😭"],
    "Takut/Cemas": [" 😷", " 💨", " ngeri banget ya...", " takut kenapa-napa.", " waspada selalu!"],
    "Kecewa": ["...", " payah banget.", " mengecewakan sih.", " 😔", " hadehh..."],
    "Harapan/Empati": [" 🙏", " 🙏✨", " aamiin yra.", " tetap semangat!", " berkah selalu."],
    "Netral": [".", "...", " infonya valid.", " update terus ya."]
}

PREFIX_VARIASI = [
    "", "Jujur, ", "Aduh, ", "Waduh... ", "Beneran deh, ", "Astaga! ",
    "Fix sih, ", "Ya ampun, ", "Mohon perhatian, ", "Bantu up, "
]


def generate_dataset_komentar(templates, output_filename, total_baris=1000, topic_name="karhutla", default_reply_to="kompascom"):
    """
    Menghasilkan dataset komentar CSV sejumlah total_baris dengan variasi alami.
    """
    print(f"[+] Menghasilkan database komentar: {output_filename} ({total_baris} entri)...")
    
    rows = []
    base_date = datetime(2026, 10, 10, 8, 0, 0)
    
    for i in range(1, total_baris + 1):
        # 1. Pilih template dasar
        tpl, sentimen, emosi = random.choice(templates)
        teks = tpl
        
        # 2. Tambahkan variasi kata slang alami
        if random.random() < 0.45:
            asal, ganti = random.choice(VARIAN_KATA)
            if re.search(r'\b' + asal + r'\b', teks, re.IGNORECASE):
                teks = re.sub(r'\b' + asal + r'\b', ganti, teks, flags=re.IGNORECASE)
                
        # 3. Variasi awalan (prefix) kadang-kadang
        if random.random() < 0.25:
            prefix = random.choice(PREFIX_VARIASI)
            teks = prefix + teks[0].lower() + teks[1:] if prefix and len(teks) > 1 else teks
            
        # 4. Tambahkan akhiran emosi / tanda baca variatif
        if random.random() < 0.40 and emosi in AFIKS_EMOSI:
            akhiran = random.choice(AFIKS_EMOSI[emosi])
            teks = teks.rstrip('.!?') + akhiran
            
        # 5. Pilih akun pengguna acak
        u_handle, u_nama = random.choice(USERNAMES_SEEDS)
        u_handle_unique = f"{u_handle}_{random.randint(10, 999)}"
        
        # 6. Rentang waktu acak selama 15 hari
        delta_minutes = random.randint(1, 21600)
        tgl_str = (base_date + timedelta(minutes=delta_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        
        # 7. Metrik interaksi sosial realistis (distribusi log-normal / Gaussian)
        likes = max(0, int(abs(random.gauss(28, 45))))
        retweets = max(0, int(abs(random.gauss(8, 16))))
        replies = max(0, int(abs(random.gauss(3, 7))))
        
        id_komentar = f"c_{topic_name}_{i:04d}"
        id_tweet = f"tweet_{topic_name}_{1000 + (i % 25)}"
        
        rows.append({
            "id_komentar": id_komentar,
            "id_tweet": id_tweet,
            "username": u_handle_unique,
            "nama_pengguna": u_nama,
            "tanggal": tgl_str,
            "teks_komentar": teks,
            "reply_to": default_reply_to,
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "topic": topic_name,
            "label_sentimen": sentimen,
            "spektrum_emosi": emosi
        })

    # Simpan ke CSV dengan encoding UTF-8
    fieldnames = list(rows[0].keys())
    with open(output_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
            
    print(f"[OK] Berhasil membuat database {output_filename} dengan {len(rows)} baris data komentar.\n")
    return rows


def main():
    print("=" * 65)
    print("GENERATOR DATABASE 1.000 KOMENTAR SOSIAL MEDIA (MULTI-TOPIK)")
    print("=" * 65)

    # 1. Database Komentar Karhutla (1.000 komentar)
    generate_dataset_komentar(
        templates=KARHUTLA_TEMPLATES,
        output_filename="data_komentar_karhutla.csv",
        total_baris=1000,
        topic_name="karhutla",
        default_reply_to="TaliUdeng"
    )

    # 2. Database Komentar Kompascom (1.000 komentar)
    generate_dataset_komentar(
        templates=KOMPASCOM_TEMPLATES,
        output_filename="data_komentar_kompascom.csv",
        total_baris=1000,
        topic_name="kompascom",
        default_reply_to="kompascom"
    )

    # 3. Database Komentar Search Karhutla (1.000 komentar)
    generate_dataset_komentar(
        templates=SEARCH_KARHUTLA_TEMPLATES,
        output_filename="data_komentar_search_karhutla.csv",
        total_baris=1000,
        topic_name="search_karhutla",
        default_reply_to="Babyypinkeuu"
    )

    # 4. Database Komentar Cortis (1.000 komentar)
    generate_dataset_komentar(
        templates=CORTIS_TEMPLATES,
        output_filename="data_komentar_cortis.csv",
        total_baris=1000,
        topic_name="cortis",
        default_reply_to="cortisindonesia"
    )

    # 5. Database Komentar Ejaaipongg (1.000 komentar)
    generate_dataset_komentar(
        templates=EJAAIPONGG_TEMPLATES,
        output_filename="data_komentar_ejaaipongg.csv",
        total_baris=1000,
        topic_name="ejaaipongg",
        default_reply_to="ejaaipongg"
    )

    print("=" * 65)
    print("SEMUA DATABASE (5.000 KOMENTAR TOTAL) TELAH BERHASIL DIBUAT LENGKAP!")
    print("File CSV yang dihasilkan:")
    print(" 1. data_komentar_karhutla.csv          (1.000 komentar)")
    print(" 2. data_komentar_kompascom.csv         (1.000 komentar)")
    print(" 3. data_komentar_search_karhutla.csv   (1.000 komentar)")
    print(" 4. data_komentar_cortis.csv            (1.000 komentar)")
    print(" 5. data_komentar_ejaaipongg.csv        (1.000 komentar)")
    print("=" * 65)


if __name__ == "__main__":
    main()
