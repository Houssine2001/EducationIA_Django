import pymongo

c = pymongo.MongoClient()
db = c.django_education
doc = db.course_documents.find_one()

if doc:
    print(f"_id: {doc['_id']}")
    print(f"id: {doc.get('id', 'MISSING')}")
    print(f"title: {doc.get('title', 'N/A')}")
else:
    print("No document found")
