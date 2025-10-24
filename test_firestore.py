from google.cloud import firestore

def main():
    print("Conectando a Firestore...")
    db = firestore.Client(project="trailogo-dev")

    doc_ref = db.collection("traliogo_test").document("demo")
    doc_ref.set({
        "nombre": "TralioGo",
        "estado": "Conectado con éxito desde Python",
    })

    print("Documento creado")
    doc = doc_ref.get()
    print("Contenido recuperado:", doc.to_dict())

if __name__ == "__main__":
    main()
