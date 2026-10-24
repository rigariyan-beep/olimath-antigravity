#!/usr/bin/env python3
"""
OliMath Adventure by antigravity - Daily Question Generator
Script ini menghasilkan 6 soal olimpiade matematika baru (1 soal per kelas: Kelas 1 - 6)
menggunakan Google Gemini API, memvalidasi formatnya, dan menambahkannya ke questions_db.json.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "questions_db.json")

def load_db():
    if not os.path.exists(DB_PATH):
        print(f"File database tidak ditemukan di {DB_PATH}, membuat database baru...")
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
    print(f"Sukses menyimpan {len(db['questions'])} soal ke {DB_PATH}")

def call_gemini_api(api_key, prompt):
    """Memanggil Gemini REST API dengan fallback model gemini-2.5-flash / gemini-1.5-flash."""
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
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
            print(f"Mencoba memanggil model: {model}...")
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if candidates:
                    text = candidates[0]["content"]["parts"][0]["text"]
                    return text
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"Error {model} ({e.code}): {err_msg}")
            last_error = err_msg
        except Exception as e:
            print(f"Exception {model}: {e}")
            last_error = str(e)
        time.sleep(2)

    raise RuntimeError(f"Gagal memanggil Gemini API di seluruh model: {last_error}")

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
    
    # Bersihkan markdown fence jika ada
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

def validate_and_format_questions(new_questions, existing_ids):
    valid_questions = []
    required_keys = ["id", "grade", "topic", "diff", "q", "opts", "ans", "hint", "exp", "trick"]

    for item in new_questions:
        if not all(k in item for k in required_keys):
            print(f"Peringatan: Melewatkan soal tidak lengkap: {item.get('id', 'unknown')}")
            continue

        # Pastikan id unik
        qid = item["id"]
        counter = 1
        while qid in existing_ids:
            qid = f"{item['id']}_{counter}"
            counter += 1
        item["id"] = qid
        existing_ids.add(qid)

        # Pastikan grade integer
        item["grade"] = int(item["grade"])

        # Tambahkan metadata tambahan
        item["date_added"] = datetime.now().strftime("%Y-%m-%d")
        if "source" not in item:
            item["source"] = "OliMath Daily AI"

        valid_questions.append(item)

    return valid_questions

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("PERINGATAN: Environment variable GEMINI_API_KEY tidak ditemukan!")
        print("Untuk testing lokal tanpa API key, Anda dapat menyetel env: set GEMINI_API_KEY=your_key")
        sys.exit(1)

    print("Memuat database soal...")
    db = load_db()
    existing_questions = db.get("questions", [])
    existing_ids = {q["id"] for q in existing_questions if "id" in q}
    print(f"Jumlah soal lama: {len(existing_questions)}")

    print("Memanggil Google Gemini API untuk generate soal olimpiade harian...")
    try:
        new_questions = generate_questions_with_gemini(api_key)
        validated = validate_and_format_questions(new_questions, existing_ids)
        print(f"Berhasil memvalidasi {len(validated)} soal baru!")

        # Gabungkan soal baru
        db["questions"].extend(validated)
        save_db(db)
        print("Auto-update soal harian selesai dengan sukses!")
    except Exception as e:
        print(f"Terjadi kesalahan saat generate soal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
