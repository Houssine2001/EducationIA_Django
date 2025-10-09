"""
Script pour ajouter le champ source_type aux tests dans MongoDB
"""
from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient('localhost', 27017)
db = client['django_education']

def add_source_type_to_tests():
    """
    Ajoute le champ source_type='manual' à tous les tests qui n'en ont pas
    """
    print("🔄 Mise à jour des tests dans MongoDB...")
    
    collection = db['evaluation_test']
    
    # Compter les documents sans source_type
    count_without = collection.count_documents({'source_type': {'$exists': False}})
    print(f"📊 {count_without} tests sans source_type trouvés")
    
    if count_without > 0:
        # Ajouter source_type='manual' à tous les tests qui n'en ont pas
        result = collection.update_many(
            {'source_type': {'$exists': False}},
            {'$set': {'source_type': 'manual'}}
        )
        
        print(f"✅ {result.modified_count} tests mis à jour")
    else:
        print("✅ Tous les tests ont déjà un source_type")
    
    # Résumé
    total = collection.count_documents({})
    manual = collection.count_documents({'source_type': 'manual'})
    ai = collection.count_documents({'source_type': 'ai_generated'})
    
    print("\n📊 Résumé:")
    print(f"  Total tests: {total}")
    print(f"  Tests manuels: {manual}")
    print(f"  Tests IA: {ai}")
    
    # Afficher quelques exemples
    print("\n📝 Exemples de tests:")
    for test in collection.find().limit(5):
        source = test.get('source_type', '❓ Non défini')
        print(f"  - {test.get('title', 'Sans titre')} ({source})")

if __name__ == '__main__':
    add_source_type_to_tests()
    print("\n✅ Terminé !")
