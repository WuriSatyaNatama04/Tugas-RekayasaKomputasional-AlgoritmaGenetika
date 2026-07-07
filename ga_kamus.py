"""
==========================================================================
 TUGAS ALGORITMA GENETIKA
 Implementasi Genetic Algorithm (GA) untuk Pencarian Kata
 dalam Kamus Bahasa Daerah Luwu

 Alur mengikuti materi kuliah:
   1. Representasi Individu (kromosom = deretan huruf)
   2. Perhitungan Fitness (jumlah huruf yang cocok / panjang kata)
   3. Seleksi Roulette Wheel (probabilitas & interval kumulatif)
   4. Crossover satu titik (one-point crossover)
   5. Mutasi gen (mengganti satu huruf secara acak)
   6. Generasi baru & evaluasi ulang

 Silakan ganti KAMUS di bawah dengan bahasa daerah Anda sendiri
 (minimal 10 kata sesuai ketentuan tugas).
==========================================================================
"""

import random
import string

# --------------------------------------------------------------------
# 1. DATABASE KAMUS BAHASA DAERAH LUWU
#    -> GANTI dengan bahasa daerah asal Anda, minimal 10 data kata
# --------------------------------------------------------------------
KAMUS = [
    ("INDO",  "ibu"),
    ("AMBE",  "ayah"),
    ("PEA BARINI",  "anak kecil"),
    ("BANNA",  "rumah"),
    ("WAI",  "air"),
    ("MANO",  "ayam"),
    ("BETE",  "ikan"),
    ("NGENAN", "tempat"),
    ("PURA",  "sudah"),
    ("MADOTTA", "baik"),
    ("MATA",  "mata"),
    ("MITAWA","senyum"),
]

ALPHABET = string.ascii_uppercase   # huruf acak untuk populasi awal: A-Z

# --------------------------------------------------------------------
# STATE PROGRAM (menyimpan hasil tiap tahap agar bisa ditampilkan
# lewat menu 4-9 tanpa harus menjalankan ulang dari awal)
# --------------------------------------------------------------------
state = {
    "target": None,          # kata target (huruf kapital) yang dicari GA
    "population": [],        # populasi individu (list of string)
    "fitness": [],           # nilai fitness tiap individu
    "prob": [],              # probabilitas seleksi tiap individu
    "interval": [],          # interval kumulatif (untuk roulette wheel)
    "parents": [],           # pasangan induk hasil seleksi
    "children": [],          # anak hasil crossover
    "mutated": [],           # anak setelah mutasi
    "generation": 0,         # generasi ke berapa
    "pop_size": 6,           # ukuran populasi
    "mutation_rate": 0.1,    # peluang mutasi tiap gen
}


# ==========================================================
# FUNGSI-FUNGSI INTI ALGORITMA GENETIKA
# ==========================================================

def buat_individu_acak(panjang):
    """Membuat satu kromosom acak sepanjang kata target."""
    return "".join(random.choice(ALPHABET) for _ in range(panjang))


def buat_populasi(target, ukuran):
    """Langkah 1: Representasi Individu -> membuat populasi awal."""
    panjang = len(target)
    return [buat_individu_acak(panjang) for _ in range(ukuran)]


def hitung_fitness(individu, target):
    """
    Langkah 2: Perhitungan Fitness
    fitness = (jumlah huruf yang posisinya cocok dengan target) / panjang kata
    (persis seperti contoh kata 'KATA' pada materi slide 20-22)
    """
    cocok = sum(1 for a, b in zip(individu, target) if a == b)
    return cocok / len(target)


def seleksi_roulette(populasi, fitness):
    """
    Langkah 3: Seleksi Roulette Wheel
    - Hitung probabilitas tiap individu = fitness_i / total_fitness
    - Buat interval kumulatif
    - Undi angka acak [0,1) untuk memilih induk sebanyak ukuran populasi
    """
    total_fitness = sum(fitness)

    if total_fitness == 0:
        # semua individu fitness-nya 0 -> pilih acak merata
        prob = [1 / len(populasi)] * len(populasi)
    else:
        prob = [f / total_fitness for f in fitness]

    # interval kumulatif, sesuai cara di slide 9-10
    interval = []
    batas_bawah = 0.0
    for p in prob:
        batas_atas = batas_bawah + p
        interval.append((batas_bawah, batas_atas))
        batas_bawah = batas_atas

    # proses roulette: undi sejumlah individu sebagai induk terpilih
    terpilih = []
    for _ in range(len(populasi)):
        r = random.random()
        for i, (bawah, atas) in enumerate(interval):
            if bawah <= r < atas:
                terpilih.append(populasi[i])
                break
        else:
            terpilih.append(populasi[-1])  # fallback pembulatan r=1.0

    return prob, interval, terpilih


def crossover(induk1, induk2, titik=None):
    """
    Langkah 4: Crossover satu titik (one-point crossover)
    Tukar potongan gen setelah 'titik' antara dua induk -> hasilkan 2 anak
    """
    panjang = len(induk1)
    if titik is None:
        titik = random.randint(1, panjang - 1)  # hindari titik di ujung
    anak1 = induk1[:titik] + induk2[titik:]
    anak2 = induk2[:titik] + induk1[titik:]
    return anak1, anak2, titik


def mutasi(individu, peluang_mutasi):
    """
    Langkah 5: Mutasi Gen
    Tiap gen (huruf) punya peluang 'peluang_mutasi' untuk diganti
    huruf acak lain (seperti contoh slide 17-18).
    """
    individu = list(individu)
    for i in range(len(individu)):
        if random.random() < peluang_mutasi:
            individu[i] = random.choice(ALPHABET)
    return "".join(individu)


# ==========================================================
# FUNGSI-FUNGSI MENU
# ==========================================================

def menu_tampilkan_kamus():
    print("\n=== Kamus Bahasa Daerah Luwu ===")
    print(f"{'No':<4}{'Kata':<10}{'Arti'}")
    for i, (kata, arti) in enumerate(KAMUS, start=1):
        print(f"{i:<4}{kata:<10}{arti}")


def menu_cari_kata():
    kunci = input("Masukkan kata atau arti yang dicari: ").strip().lower()
    hasil = [(k, a) for k, a in KAMUS if kunci in k.lower() or kunci in a.lower()]
    if hasil:
        print("\nDitemukan:")
        for k, a in hasil:
            print(f"  {k} -> {a}")
    else:
        print("Kata/arti tidak ditemukan dalam kamus.")


def pilih_kata_target():
    """Meminta pengguna memilih salah satu kata dari kamus sebagai target GA."""
    menu_tampilkan_kamus()
    idx = int(input("\nPilih NOMOR kata dari kamus di atas sebagai TARGET pencarian GA: "))
    kata, arti = KAMUS[idx - 1]
    return kata.upper()


def menu_jalankan_ga():
    """Langkah 3 sekaligus 4-9: menjalankan satu generasi penuh GA."""
    state["target"] = pilih_kata_target()
    target = state["target"]

    print(f"\nKata target yang dicari GA: {target}  (panjang {len(target)} huruf)")

    # 1) Populasi awal
    state["population"] = buat_populasi(target, state["pop_size"])

    # 2) Fitness
    state["fitness"] = [hitung_fitness(ind, target) for ind in state["population"]]

    # 3) Seleksi roulette wheel
    prob, interval, terpilih = seleksi_roulette(state["population"], state["fitness"])
    state["prob"] = prob
    state["interval"] = interval
    state["parents"] = terpilih

    # 4) Crossover berpasangan (induk 1&2, 3&4, dst)
    anak_semua = []
    titik_list = []
    for i in range(0, len(terpilih) - 1, 2):
        a1, a2, titik = crossover(terpilih[i], terpilih[i + 1])
        anak_semua.extend([a1, a2])
        titik_list.append(titik)
    if len(terpilih) % 2 == 1:
        anak_semua.append(terpilih[-1])  # individu ganjil dibawa langsung
    state["children"] = anak_semua
    state["crossover_points"] = titik_list

    # 5) Mutasi
    state["mutated"] = [mutasi(ind, state["mutation_rate"]) for ind in anak_semua]

    # 6) Generasi baru + evaluasi ulang
    state["generation"] += 1
    fitness_baru = [hitung_fitness(ind, target) for ind in state["mutated"]]
    state["population"] = state["mutated"]
    state["fitness"] = fitness_baru

    print(f"\n>> Generasi ke-{state['generation']} selesai dihitung.")
    print(">> Gunakan menu 4-9 untuk melihat rincian tiap tahap.")

    terbaik_idx = fitness_baru.index(max(fitness_baru))
    print(f">> Individu terbaik generasi ini: {state['mutated'][terbaik_idx]} "
          f"(fitness={fitness_baru[terbaik_idx]:.2f})")


def menu_tampilkan_populasi():
    if not state["population"]:
        print("Belum ada populasi. Jalankan menu 3 (Jalankan Algoritma Genetika) dahulu.")
        return
    print(f"\n=== Populasi (Generasi ke-{state['generation']}) - Target: {state['target']} ===")
    for i, ind in enumerate(state["population"], start=1):
        print(f"Individu {i}: {ind}")


def menu_hasil_fitness():
    if not state["fitness"]:
        print("Belum ada data fitness. Jalankan menu 3 dahulu.")
        return
    print(f"\n=== Hasil Fitness (Target: {state['target']}) ===")
    print(f"{'Individu':<10}{'Kromosom':<12}{'Fitness'}")
    for i, (ind, f) in enumerate(zip(state["population"], state["fitness"]), start=1):
        print(f"I{i:<9}{ind:<12}{f:.2f}")


def menu_seleksi_roulette():
    if not state["prob"]:
        print("Belum ada data seleksi. Jalankan menu 3 dahulu.")
        return
    print("\n=== Tabel Probabilitas & Interval Seleksi Roulette Wheel ===")
    print(f"{'Individu':<10}{'Fitness':<10}{'Probabilitas':<14}{'Interval'}")
    for i, (f, p, (bawah, atas)) in enumerate(
            zip(state["fitness"], state["prob"], state["interval"]), start=1):
        print(f"I{i:<9}{f:<10.2f}{p:<14.2f}{bawah:.2f} - {atas:.2f}")
    print("\nInduk terpilih hasil roulette:")
    for i, p in enumerate(state["parents"], start=1):
        print(f"  Induk {i}: {p}")


def menu_crossover():
    if not state["children"]:
        print("Belum ada data crossover. Jalankan menu 3 dahulu.")
        return
    print("\n=== Hasil Crossover (One-Point) ===")
    parents = state["parents"]
    for idx, titik in enumerate(state["crossover_points"]):
        p1, p2 = parents[idx * 2], parents[idx * 2 + 1]
        c1, c2 = state["children"][idx * 2], state["children"][idx * 2 + 1]
        print(f"Induk 1: {p1}  x  Induk 2: {p2}  (titik potong setelah huruf ke-{titik})")
        print(f"  -> Anak 1: {c1}")
        print(f"  -> Anak 2: {c2}")


def menu_mutasi():
    if not state["mutated"]:
        print("Belum ada data mutasi. Jalankan menu 3 dahulu.")
        return
    print(f"\n=== Hasil Mutasi (peluang mutasi = {state['mutation_rate']}) ===")
    for i, (sebelum, sesudah) in enumerate(zip(state["children"], state["mutated"]), start=1):
        tanda = "  <-- ada gen berubah" if sebelum != sesudah else ""
        print(f"Anak {i}: {sebelum}  ->  {sesudah}{tanda}")


def menu_generasi_baru():
    if not state["population"]:
        print("Belum ada generasi baru. Jalankan menu 3 dahulu.")
        return
    print(f"\n=== Populasi Generasi ke-{state['generation']} (setelah mutasi) ===")
    print(f"{'Individu':<10}{'Kromosom':<12}{'Fitness'}")
    for i, (ind, f) in enumerate(zip(state["population"], state["fitness"]), start=1):
        print(f"I{i:<9}{ind:<12}{f:.2f}")
    terbaik_idx = state["fitness"].index(max(state["fitness"]))
    print(f"\nIndividu terbaik: {state['population'][terbaik_idx]} "
          f"(fitness={state['fitness'][terbaik_idx]:.2f}) "
          f"| Target: {state['target']}")
    if state["population"][terbaik_idx] == state["target"]:
        print(">> GA BERHASIL menemukan kata target!")
    else:
        print(">> Kata target belum ditemukan persis, perlu generasi berikutnya "
              "(silakan jalankan menu 3 lagi untuk generasi lanjutan).")


# ==========================================================
# MAIN MENU
# ==========================================================

def main():
    while True:
        print("\n=== Kamus Bahasa Daerah Luwu ===")
        print("1. Tampilkan Kamus")
        print("2. Cari Kata")
        print("3. Jalankan Algoritma Genetika")
        print("4. Tampilkan Populasi")
        print("5. Hasil Fitness")
        print("6. Seleksi Roulette")
        print("7. Cross Over")
        print("8. Mutasi")
        print("9. Generasi Baru")
        print("10. Keluar")

        pilihan = input("Pilih menu (1-10): ").strip()

        if pilihan == "1":
            menu_tampilkan_kamus()
        elif pilihan == "2":
            menu_cari_kata()
        elif pilihan == "3":
            menu_jalankan_ga()
        elif pilihan == "4":
            menu_tampilkan_populasi()
        elif pilihan == "5":
            menu_hasil_fitness()
        elif pilihan == "6":
            menu_seleksi_roulette()
        elif pilihan == "7":
            menu_crossover()
        elif pilihan == "8":
            menu_mutasi()
        elif pilihan == "9":
            menu_generasi_baru()
        elif pilihan == "10":
            print("Program selesai. Terima kasih.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    main()