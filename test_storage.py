from datetime import datetime
from google.cloud import storage

def main():
    client = storage.Client()
    bucket_name = "trailogo-dev-bucket-2025"
    bucket = client.bucket(bucket_name)

    # Nombre con timestamp
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    object_name = f"file_{ts}.txt"

    # Sube
    blob = bucket.blob(object_name)
    blob.upload_from_string(f"Subido {ts} desde TralioGo")

    print(f"Subido: gs://{bucket_name}/{object_name}")

    # Obtén metadatos para confirmar generación/etag
    blob.reload()
    print(f"   generation={blob.generation}, size={blob.size}, etag={blob.etag}")

    # Lista objetos y verifica aparición
    print("Listando objetos (primeros 20):")
    for i, b in enumerate(client.list_blobs(bucket_name), 1):
        print(f"  - {b.name}")
        if i >= 20:
            print("  ...")
            break

    # Relee el contenido del objeto recién subido
    data = bucket.blob(object_name).download_as_text()
    print("Contenido leído:", data)

if __name__ == "__main__":
    main()