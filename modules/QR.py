import qr
import base64
from io import BytesIO
from pymongo import MongoClient

class QRCodeUpdater:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def generate_qr_base64(self, data: str) -> str:
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

    def update_urls_with_qr(self):
        cursor = self.collection.find({})
        for doc in cursor:
            shortlink = doc.get('shortlink')
            if not shortlink:
                print(f"Skipping document {doc['_id']} because 'shortlink' is missing.")
                continue

            qr_code_base64 = self.generate_qr_base64(shortlink)
            self.collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'qrCodeBase64': qr_code_base64}}
            )
            print(f"Updated QR for document {doc['_id']}")

