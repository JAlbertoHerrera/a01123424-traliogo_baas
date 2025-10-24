#!/usr/bin/env python3
"""
ingestar_firestore.py — Ingesta de datos a Firestore para TralioGo
Permite cargar datos a las colecciones: users, history, objects, flags
desde archivos CSV/JSON o generar datos sintéticos.

Requisitos previos (local):
  pip install google-cloud-firestore
  gcloud auth application-default login
  gcloud auth application-default set-quota-project <PROJECT_ID>

Uso básico:
  # Desde CSV
  python ingestar_firestore.py --collection users --file users.csv
  # Desde JSON (lista de objetos)
  python ingestar_firestore.py --collection history --file history.json

  # Generar N registros sintéticos
  python ingestar_firestore.py --collection objects --generate 50

Opciones principales:
  --collection {users,history,objects,flags}     # Colección de destino
  --file <ruta>                                  # CSV o JSON
  --generate N                                   # Genera N documentos sintéticos
  --project <PROJECT_ID>                         # Fuerza el proyecto GCP
  --batch-size 500                               # Tamaño de lote (máx 500)
  --id-field id                                  # Nombre del campo que contiene el ID del doc
  --merge                                        # Usa set(..., merge=True) (upsert)
  --dry-run                                      # No escribe, solo valida y cuenta
"""

import argparse
import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from google.cloud import firestore

MAX_BATCH = 500

def now():
    return datetime.now(timezone.utc)

def chunked(iterable: Iterable[Dict[str, Any]], size: int):
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def normalize_bool(v: Any) -> Any:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true","1","yes","y","si","sí"): return True
        if s in ("false","0","no","n"): return False
    return v

def coerce_types(collection: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza tipos por colección (campos opcionales soportados)."""
    data = dict(row)

    if collection == "users":
        # Campos: email(str), displayName(str), avatarUrl(str), role(str), createdAt(ts)
        if "createdAt" not in data or not data["createdAt"]:
            data["createdAt"] = now()
    elif collection == "history":
        # Campos: userId(str), sourceLang(str), targetLang(str), inputType(str), text(str), result(str), ts(ts)
        if "ts" not in data or not data["ts"]:
            data["ts"] = now()
    elif collection == "objects":
        # Campos: label(str), confidence(float), imageUrl(str), langs(list[str]), createdBy(str), ts(ts)
        if "confidence" in data:
            try: data["confidence"] = float(data["confidence"])
            except: pass
        if "langs" in data and isinstance(data["langs"], str):
            # admite "es,en" o '["es","en"]'
            s = data["langs"].strip()
            if s.startswith("["):
                try:
                    data["langs"] = json.loads(s)
                except:
                    data["langs"] = [p.strip() for p in s.strip("[]").split(",") if p.strip()]
            else:
                data["langs"] = [p.strip() for p in s.split(",") if p.strip()]
        if "ts" not in data or not data["ts"]:
            data["ts"] = now()
    elif collection == "flags":
        # Campos: key(str), value(any), type(bool|str|num|json), scope(str), updatedAt(ts)
        if "type" in data:
            t = str(data["type"]).lower()
            if t == "bool":
                data["value"] = normalize_bool(data.get("value"))
            elif t == "num":
                try: data["value"] = float(data.get("value"))
                except: pass
            elif t == "json":
                v = data.get("value")
                if isinstance(v, str):
                    try: data["value"] = json.loads(v)
                    except: pass
        if "updatedAt" not in data or not data["updatedAt"]:
            data["updatedAt"] = now()
    return data

def parse_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [ {k: v for k, v in row.items()} for row in reader ]

def parse_json(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            return data["items"]
        if isinstance(data, list):
            return data
        raise ValueError("JSON debe ser una lista de objetos o un objeto con clave 'items'.")

def generate_synthetic(collection: str, n: int) -> List[Dict[str, Any]]:
    rng = random.Random(1234)  # determinista
    items = []
    if collection == "users":
        first = ["Adriana","Néstor","Carlos","José","Paty","Vale","Luis","Ana","Roberto","Lucía"]
        roles = ["student","admin","teacher"]
        for i in range(n):
            name = rng.choice(first)
            email = f"{name.lower()}.{i}@example.com"
            items.append({
                "email": email,
                "displayName": f"{name} #{i}",
                "avatarUrl": f"https://example.com/{name.lower()}{i}.png",
                "role": rng.choice(roles),
                "createdAt": now()
            })
    elif collection == "history":
        langs = ["es","en","fr","de","it"]
        for i in range(n):
            s = rng.choice(langs); t = rng.choice([l for l in langs if l != s])
            txt = rng.choice(["hola","adiós","árbol","casa","gracias","perro","gato"])
            items.append({
                "userId": f"uid_{rng.randint(100,999)}",
                "sourceLang": s,
                "targetLang": t,
                "inputType": "text",
                "text": txt,
                "result": txt[::-1],  # demo
                "ts": now()
            })
    elif collection == "objects":
        labels = ["bottle","cat","dog","laptop","book","phone"]
        for i in range(n):
            lab = rng.choice(labels)
            items.append({
                "label": lab,
                "confidence": round(rng.uniform(0.7, 0.99), 2),
                "imageUrl": f"https://example.com/img/{lab}{i}.png",
                "langs": rng.sample(["es","en","fr"], rng.randint(1,3)),
                "createdBy": f"uid_{rng.randint(100,999)}",
                "ts": now()
            })
    elif collection == "flags":
        for i in range(n):
            key = rng.choice(["feature_x","feature_y","max_items","beta_ui"])
            type_ = rng.choice(["bool","num","str"])
            val: Any = True
            if type_ == "num": val = rng.randint(1, 100)
            elif type_ == "str": val = rng.choice(["on","off","gray"])
            else: val = rng.choice([True, False])
            items.append({
                "key": key,
                "type": type_,
                "value": val,
                "scope": rng.choice(["global","user"]),
                "updatedAt": now()
            })
    return items

def load_source(collection: str, file: Optional[str], generate: Optional[int]) -> List[Dict[str, Any]]:
    if file:
        p = Path(file)
        if not p.exists():
            raise FileNotFoundError(f"No existe el archivo: {file}")
        if p.suffix.lower() == ".csv":
            rows = parse_csv(p)
        elif p.suffix.lower() == ".json":
            rows = parse_json(p)
        else:
            raise ValueError("Formato no soportado. Usa .csv o .json")
    elif generate:
        rows = generate_synthetic(collection, int(generate))
    else:
        raise ValueError("Debes especificar --file o --generate N")
    # normalizar tipos por colección
    return [coerce_types(collection, r) for r in rows]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", "-c", required=True, choices=["users","history","objects","flags"])
    ap.add_argument("--file", "-f", help="Ruta a CSV o JSON (lista de objetos)")
    ap.add_argument("--generate", "-g", type=int, help="Genera N documentos sintéticos")
    ap.add_argument("--project", help="Override del PROJECT_ID")
    ap.add_argument("--batch-size", type=int, default=500, help="Lote de escrituras (<=500)")
    ap.add_argument("--id-field", default=None, help="Campo que contiene el ID del doc")
    ap.add_argument("--merge", action="store_true", help="Upsert con merge=True")
    ap.add_argument("--dry-run", action="store_true", help="No escribe, solo valida")
    args = ap.parse_args()

    if args.batch_size > MAX_BATCH or args.batch_size <= 0:
        ap.error(f"--batch-size debe ser 1..{MAX_BATCH}")

    # Cliente Firestore
    if args.project:
        db = firestore.Client(project=args.project)
    else:
        db = firestore.Client()

    docs = load_source(args.collection, args.file, args.generate)
    print(f"Documentos a procesar: {len(docs)} en colección '{args.collection}'")

    if args.dry_run:
        print("Dry-run habilitado. No se escribirán documentos.")
        sys.exit(0)

    written = 0
    for group in chunked(docs, args.batch_size):
        batch = db.batch()
        for d in group:
            # ID explícito si --id-field y existe
            if args.id_field and args.id_field in d and d[args.id_field]:
                doc_ref = db.collection(args.collection).document(str(d[args.id_field]))
            else:
                doc_ref = db.collection(args.collection).document()  # auto-ID
            payload = {k: v for k, v in d.items() if k != args.id_field}
            if args.merge:
                batch.set(doc_ref, payload, merge=True)
            else:
                batch.set(doc_ref, payload)
        batch.commit()
        written += len(group)
        print(f"  -> Commit de {len(group)} docs (total: {written})")

    print(f"Ingesta completada: {written} documentos en '{args.collection}'.")

if __name__ == "__main__":
    main()