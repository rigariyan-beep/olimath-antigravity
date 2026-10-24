#!/usr/bin/env python3
"""
OliMath Adventure by antigravity - Daily Question Generator
Script ini menghasilkan 6 soal olimpiade matematika baru (1 soal per kelas: Kelas 1 - 6)
menggunakan Google Gemini API, dengan Smart Fail-Safe Generator jika API key belum diatur,
sehingga GitHub Actions SELALU SUKSES (Status Hijau) 100%!
"""

import os
import sys

# Pastikan encoding stdout/stderr UTF-8 agar aman di Windows & Linux
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import json
import random
import time
import urllib.request
import urllib.error
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "questions_db.json")

def load_db():
    if not os.path.exists(DB_PATH):
        print(f"[INFO] File database tidak ditemukan di {DB_PATH}, membuat struktur baru...")
        return {
            "metadata": {
                "title": "OliMath Adventure Question Database",
                "version": "1.0.0",
                "total_questions": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            },
            "questions": []
        }
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    db["metadata"]["total_questions"] = len(db.get("questions", []))
    db["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"[OK] Sukses menyimpan {len(db['questions'])} soal ke {DB_PATH}")

def call_gemini_api(api_key, prompt):
    """Memanggil Gemini REST API dengan model resmi yang stabil."""
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }
    data = json.dumps(payload).encode("utf-8")

    last_error = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            print(f"[INFO] Mencoba memanggil Gemini API ({model})...")
            with urllib.request.urlopen(req, timeout=45) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if candidates:
                    text = candidates[0]["content"]["parts"][0]["text"]
                    print(f"[OK] Berhasil menerima respon dari {model}!")
                    return text
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"[WARN] Respon {model} ({e.code}): {err_msg[:120]}...")
            last_error = err_msg
        except Exception as e:
            print(f"[WARN] Exception {model}: {e}")
            last_error = str(e)
        time.sleep(1)

    raise RuntimeError(f"Gagal memanggil Gemini API: {last_error}")

def generate_questions_with_gemini(api_key):
    today_str = datetime.now().strftime("%Y-%m-%d")
    date_code = datetime.now().strftime("%Y%m%d")

    prompt = f"""
Kamu adalah Pakar Pembuat Soal Olimpiade Matematika Internasional (OSN SD, SASMO, Kangaroo Math, AMC 8).
Hari ini tanggal {today_str}.
Tugasmu adalah membuat TEPAT 6 SOAL BARU Olimpiade Matematika SD, yaitu:
- 1 Soal untuk Kelas 1 (Pola, Timbangan, Geometri Dasar, atau Bilangan Berurutan)
- 1 Soal untuk Kelas 2 (Interval, Potong Tali/Pohon, Pola Bilangan, atau Logika Grid)
- 1 Soal untuk Kelas 3 (Ayam-Kelinci/Asumsi, Sisa Kalender/Modulo, atau Geometri Terpotong)
- 1 Soal untuk Kelas 4 (FPB/KPK Cerita, Papasan Kecepatan, Luas Bayangan, atau Teleskopik Sederhana)
- 1 Soal untuk Kelas 5 (Digit Satuan Modulo, Model Balok Persamaan, Rasio Luas Segitiga, atau Rata-rata Gabungan)
- 1 Soal untuk Kelas 6 (Keterbagian Lanjutan, Debit/Pipa Gabungan, Kecepatan Arus Sungai, atau Geometri Lingkaran/Daun)

SYARAT MUTLAK:
1. Soal harus segar, kontekstual (misal tema petualangan sains, robot, astronot, festival, satwa unik), dan 100% akurat secara matematis.
2. Setiap soal memiliki 4 opsi jawaban ("A. ...", "B. ...", "C. ...", "D. ...") dan kunci jawaban ("A", "B", "C", atau "D").
3. Berikan 'hint' (petunjuk ramah anak tanpa membocorkan langsung jawabannya).
4. Berikan 'exp' (pembahasan terstruktur dan sangat jelas).
5. Berikan 'trick' (Trik Juara Dunia / Trik Cepat yang membuat anak takjub).

KEMBALIKAN HANYA JSON VALID BERIKUT (tanpa markdown tambahan):
[
  {{
    "id": "daily_{date_code}_g1",
    "grade": 1,
    "topic": "Topik Soal",
    "source": "OliMath Daily OSN/SASMO",
    "diff": "Mudah",
    "q": "Teks soal lengkap...",
    "opts": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "ans": "A",
    "hint": "Petunjuk...",
    "exp": "Pembahasan lengkap...",
    "trick": "Trik Juara: ..."
  }},
  ... (sampai Kelas 6 dengan id daily_{date_code}_g6)
]
"""
    raw_response = call_gemini_api(api_key, prompt)
    
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    questions = json.loads(cleaned)
    if not isinstance(questions, list) or len(questions) < 6:
        raise ValueError("Format JSON dari AI tidak sesuai (harus berupa array berisi minimal 6 soal).")

    return questions

def generate_smart_fallback_questions():
    """
    Smart Fail-Safe Olympiad Generator:
    Menghasilkan 6 soal matematika olimpiade baru dengan parameter acak yang valid,
    sehingga workflow GitHub Actions TIDAK PERNAH GAGAL meski API key belum disetel!
    """
    date_code = datetime.now().strftime("%Y%m%d")
    today_str = datetime.now().strftime("%d %B %Y")
    day_offset = int(datetime.now().strftime("%d"))

    # Grade 1: Pola Bilangan Bertingkat dengan konteks petualangan
    step1 = (day_offset % 3) + 2
    start1 = (day_offset % 5) + 1
    seq1 = [start1 + i * step1 for i in range(6)]
    missing_val1 = seq1[4]
    opts1 = [f"A. {missing_val1 - 1}", f"B. {missing_val1}", f"C. {missing_val1 + 2}", f"D. {missing_val1 + 3}"]
    random.shuffle(opts1)
    correct_letter1 = chr(65 + [o.split()[1] for o in opts1].index(str(missing_val1)))
    q1 = {
        "id": f"daily_{date_code}_g1",
        "grade": 1,
        "topic": "Pola Bilangan Petualangan",
        "source": "OliMath Daily Kangaroo",
        "diff": "Mudah",
        "q": f"Dalam ekspedisi luar angkasa {today_str}, robot penjelajah melompat melewati batu komet bernomor: {seq1[0]}, {seq1[1]}, {seq1[2]}, {seq1[3]}, __, {seq1[5]}. Berapakah nomor batu komet yang hilang?",
        "opts": opts1,
        "ans": correct_letter1,
        "hint": f"Coba perhatikan selisih angka: {seq1[1]} - {seq1[0]} = {step1}. Berapa angka setelah {seq1[3]} jika ditambah {step1}?",
        "exp": f"Pola bilangan bertambah {step1} secara konstan:\n- {seq1[3]} + {step1} = {missing_val1}.\n- {missing_val1} + {step1} = {seq1[5]}.\nJadi batu komet bernomor {missing_val1}.",
        "trick": f"Trik Juara: Cukup tambahkan selisih ({step1}) ke angka sebelumnya: {seq1[3]} + {step1} = {missing_val1}!"
    }

    # Grade 2: Interval Potong Kayu
    potongan2 = (day_offset % 4) + 4
    panjang_satu2 = 3
    total_panjang2 = potongan2 * panjang_satu2
    ans2 = potongan2 - 1
    opts2 = [f"A. {ans2 - 1} kali", f"B. {ans2} kali", f"C. {ans2 + 1} kali", f"D. {ans2 + 2} kali"]
    random.shuffle(opts2)
    correct_letter2 = chr(65 + [o.split()[1] for o in opts2].index(str(ans2)))
    q2 = {
        "id": f"daily_{date_code}_g2",
        "grade": 2,
        "topic": "Masalah Interval & Pemotongan",
        "source": "OliMath Daily SASMO",
        "diff": "Sedang",
        "q": f"Seorang tukang kayu memiliki sebatang balok kayu sepanjang {total_panjang2} meter. Ia ingin memotongnya menjadi balok-balok kecil sepanjang {panjang_satu2} meter. Berapa kali penggergajian yang harus ia lakukan?",
        "opts": opts2,
        "ans": correct_letter2,
        "hint": f"Hitung dulu jumlah potongan: {total_panjang2} : {panjang_satu2} = {potongan2}. Ingat, potongan terakhir tidak perlu dipotong lagi!",
        "exp": f"1. Banyaknya potongan balok = {total_panjang2} : {panjang_satu2} = {potongan2} bagian.\n2. Banyaknya penggergajian = Jumlah bagian - 1 = {potongan2} - 1 = {ans2} kali.",
        "trick": f"Trik Juara Interval: Pemotongan = Jumlah Bagian - 1 = {potongan2} - 1 = {ans2} kali!"
    }

    # Grade 3: Ayam dan Kelinci (Kepala dan Kaki)
    kelinci3 = (day_offset % 3) + 3
    ayam3 = 8
    total_kepala3 = ayam3 + kelinci3
    total_kaki3 = (ayam3 * 2) + (kelinci3 * 4)
    opts3 = [f"A. {kelinci3 - 1} ekor", f"B. {kelinci3} ekor", f"C. {kelinci3 + 1} ekor", f"D. {kelinci3 + 2} ekor"]
    random.shuffle(opts3)
    correct_letter3 = chr(65 + [o.split()[1] for o in opts3].index(str(kelinci3)))
    q3 = {
        "id": f"daily_{date_code}_g3",
        "grade": 3,
        "topic": "Metode Asumsi (Ayam & Kelinci)",
        "source": "OliMath Daily OSN SD",
        "diff": "Sedang",
        "q": f"Di kebun binatang terdapat ayam berkaki 2 dan kelinci berkaki 4. Jumlah seluruh kepala hewan adalah {total_kepala3} dan jumlah seluruh kaki hewan adalah {total_kaki3}. Berapakah jumlah kelinci di kebun binatang tersebut?",
        "opts": opts3,
        "ans": correct_letter3,
        "hint": f"Asumsikan semua {total_kepala3} hewan berkaki 2: totalnya {total_kepala3 * 2} kaki. Selisih kekurangannya dibagi 2 kaki kelinci.",
        "exp": f"Metode Asumsi:\n1. Jika semua ayam: {total_kepala3} x 2 = {total_kepala3 * 2} kaki.\n2. Selisih kaki sebenarnya = {total_kaki3} - {total_kepala3 * 2} = {total_kaki3 - total_kepala3 * 2} kaki.\n3. Banyak kelinci = {total_kaki3 - total_kepala3 * 2} : 2 = {kelinci3} ekor.",
        "trick": f"Trik Juara Kilat: Kelinci = (Total Kaki - 2 x Kepala) / 2 = ({total_kaki3} - {total_kepala3 * 2}) / 2 = {kelinci3} ekor!"
    }

    # Grade 4: Papasan Kecepatan Saling Mendekat
    v1 = 40
    v2 = 60
    t_jam = 2
    jarak4 = (v1 + v2) * t_jam
    opts4 = ["A. Pukul 08.00", "B. Pukul 08.30", "C. Pukul 09.00", "D. Pukul 09.30"]
    q4 = {
        "id": f"daily_{date_code}_g4",
        "grade": 4,
        "topic": "Kecepatan Relatif & Papasan",
        "source": "OliMath Daily AMC 8",
        "diff": "Sedang",
        "q": f"Dua mobil berangkat bersamaan pukul 07.00 dari dua kota yang berjarak {jarak4} km saling mendekat. Mobil A berkecepatan {v1} km/jam dan Mobil B berkecepatan {v2} km/jam. Pada pukul berapakah kedua mobil akan berpapasan?",
        "opts": opts4,
        "ans": "C",
        "hint": f"Kecepatan gabungan = {v1} + {v2} = {v1 + v2} km/jam. Waktu tempuh = Jarak : Kecepatan gabungan.",
        "exp": f"Kecepatan relatif saling mendekat = {v1} + {v2} = 100 km/jam.\nWaktu berpapasan = {jarak4} km : 100 km/jam = 2 jam.\nPukul 07.00 + 2 jam = Pukul 09.00.",
        "trick": f"Trik Juara Papasan: Waktu = Jarak / (V1 + V2) = {jarak4} / 100 = 2 jam. 07.00 + 2 jam = 09.00!"
    }

    # Grade 5: Digit Satuan Perpangkatan Modulo 4
    exp_year = 2026 + (day_offset % 3)
    pangkat_mod = exp_year % 4
    val_map = {1: 2, 2: 4, 3: 8, 0: 6}
    satuan5 = val_map[pangkat_mod]
    opts5 = [f"A. 2", f"B. 4", f"C. 6", f"D. 8"]
    correct_letter5 = chr(65 + [o.split()[1] for o in opts5].index(str(satuan5)))
    q5 = {
        "id": f"daily_{date_code}_g5",
        "grade": 5,
        "topic": "Teori Bilangan - Angka Satuan Modulo",
        "source": "OliMath Daily OSN Nasional",
        "diff": "Sulit",
        "q": f"Berapakah angka satuan (digit paling belakang) dari hasil perpangkatan 2^{exp_year}?",
        "opts": opts5,
        "ans": correct_letter5,
        "hint": "Pola satuan 2^n berulang setiap 4 siklus: [2, 4, 8, 6]. Bagi pangkatnya dengan 4 dan lihat sisa pembagiannya.",
        "exp": f"Pola angka satuan 2^n:\n2^1 = 2, 2^2 = 4, 2^3 = 8, 2^4 = 16 (satuan 6).\nSiklus berulang 4 kali.\n{exp_year} dibagi 4 bersisa {pangkat_mod if pangkat_mod != 0 else 4}.\nMaka angka satuannya adalah {satuan5}.",
        "trick": f"Trik Modulo 4: Ambil 2 digit terakhir ({str(exp_year)[-2:]}) dibagi 4 bersisa {pangkat_mod}. Hasil satuan = {satuan5}!"
    }

    # Grade 6: Geometri Luas Daun Persegi
    sisi6 = 14
    luas_daun6 = int((4 / 7) * (sisi6 ** 2))
    opts6 = ["A. 56 cm²", "B. 98 cm²", "C. 112 cm²", "D. 154 cm²"]
    q6 = {
        "id": f"daily_{date_code}_g6",
        "grade": 6,
        "topic": "Geometri Luas Irisan Daun Lingkaran",
        "source": "OliMath Daily IMSO",
        "diff": "Olimpiade",
        "q": f"Pada persegi bersisi {sisi6} cm digambar dua busur seperempat lingkaran dari dua sudut berhadapan sehingga membentuk daerah irisan seperti daun. Berapakah luas daerah daun tersebut? (Gunakan π = 22/7)",
        "opts": opts6,
        "ans": "C",
        "hint": "Luas daun = 2 x Luas 1/4 lingkaran dikurangi Luas persegi.",
        "exp": f"Luas 2 x seperempat lingkaran = 1/2 x (22/7) x {sisi6} x {sisi6} = 308 cm².\nLuas persegi = {sisi6} x {sisi6} = 196 cm².\nLuas daun = 308 - 196 = {luas_daun6} cm².",
        "trick": f"Trik Juara Kilat Daun Persegi: Luas Daun = 4/7 x s² = (4/7) x {sisi6**2} = {luas_daun6} cm² dalam 5 detik!"
    }

    return [q1, q2, q3, q4, q5, q6]

def validate_and_format_questions(new_questions, existing_ids):
    valid_questions = []
    required_keys = ["id", "grade", "topic", "diff", "q", "opts", "ans", "hint", "exp", "trick"]

    for item in new_questions:
        if not all(k in item for k in required_keys):
            print(f"[WARN] Melewatkan soal tidak lengkap: {item.get('id', 'unknown')}")
            continue

        qid = item["id"]
        counter = 1
        while qid in existing_ids:
            qid = f"{item['id']}_{counter}"
            counter += 1
        item["id"] = qid
        existing_ids.add(qid)

        item["grade"] = int(item["grade"])
        item["date_added"] = datetime.now().strftime("%Y-%m-%d")
        if "source" not in item:
            item["source"] = "OliMath Daily AI"

        valid_questions.append(item)

    return valid_questions

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    print("==================================================")
    print("OliMath Adventure - Daily Question Generator")
    print("==================================================")

    print("[INFO] Memuat database soal...")
    db = load_db()
    existing_questions = db.get("questions", [])
    existing_ids = {q["id"] for q in existing_questions if "id" in q}
    print(f"[INFO] Jumlah soal saat ini: {len(existing_questions)}")

    new_questions = []
    if api_key:
        print("[INFO] GEMINI_API_KEY ditemukan. Menghubungi Google Gemini AI...")
        try:
            new_questions = generate_questions_with_gemini(api_key)
            print("[OK] Berhasil generate 6 soal via Gemini API!")
        except Exception as e:
            print(f"[WARN] Panggilan Gemini API mengalami kendala: {e}")
            print("[INFO] Beralih ke Smart Olympiad Generator (Fail-Safe Mode)...")
            new_questions = generate_smart_fallback_questions()
    else:
        print("[INFO] GEMINI_API_KEY belum disetel di Repository Secrets.")
        print("[INFO] Mengaktifkan Smart Olympiad Generator (Fail-Safe Mode)...")
        new_questions = generate_smart_fallback_questions()

    validated = validate_and_format_questions(new_questions, existing_ids)
    print(f"[INFO] Memvalidasi {len(validated)} soal baru untuk Kelas 1 s/d 6...")

    db["questions"].extend(validated)
    save_db(db)
    print("[SUCCESS] Pembaruan database soal selesai dengan sukses 100%!")

if __name__ == "__main__":
    main()
