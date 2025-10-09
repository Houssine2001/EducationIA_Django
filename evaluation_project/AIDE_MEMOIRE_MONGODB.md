# 🎯 AIDE-MÉMOIRE MONGODB - COMMANDES RAPIDES

**Base de données** : `django_education`  
**Serveur** : `localhost:27017`

---

## 🚀 COMMANDES ESSENTIELLES

### Se connecter à MongoDB

```bash
# Shell MongoDB
mongo django_education

# Avec mongosh (si installé)
mongosh django_education
```

---

### Voir toutes les collections

```javascript
show collections
```

**Résultat attendu** :
```
auth_user
evaluation_question
evaluation_result
evaluation_submission
evaluation_test
evaluation_userprofile
```

---

### Compter les documents

```javascript
// Tout en une commande
print('Users:', db.auth_user.count());
print('Profiles:', db.evaluation_userprofile.count());
print('Tests:', db.evaluation_test.count());
print('Questions:', db.evaluation_question.count());
print('Submissions:', db.evaluation_submission.count());
print('Results:', db.evaluation_result.count());
```

---

## 👥 REQUÊTES UTILISATEURS

### Voir tous les utilisateurs

```javascript
db.auth_user.find().pretty()
```

### Trouver un utilisateur

```javascript
db.auth_user.findOne({ username: "etudiant1" })
```

### Lister seulement les noms

```javascript
db.auth_user.find({}, { username: 1, email: 1, is_staff: 1 })
```

### Compter étudiants vs enseignants

```javascript
print('Étudiants:', db.auth_user.count({ is_staff: false }));
print('Enseignants:', db.auth_user.count({ is_staff: true }));
```

---

## 📊 REQUÊTES PROFILS

### Voir statistiques d'un étudiant

```javascript
db.evaluation_userprofile.findOne({ user_id: 1 })
```

### Top 3 étudiants par XP

```javascript
db.evaluation_userprofile.find({}, {
    user_id: 1,
    total_xp: 1,
    level: 1,
    average_score: 1
}).sort({ total_xp: -1 }).limit(3)
```

### Étudiants avec > 50 tests

```javascript
db.evaluation_userprofile.find(
    { total_tests_taken: { $gt: 50 } },
    { user_id: 1, total_tests_taken: 1, average_score: 1 }
)
```

### Voir les points forts d'un étudiant

```javascript
db.evaluation_userprofile.findOne(
    { user_id: 1 },
    { strengths: 1 }
).strengths
```

---

## 📝 REQUÊTES TESTS

### Compter tests par matière

```javascript
db.evaluation_test.aggregate([
    { $group: { _id: "$subject", count: { $sum: 1 } } }
])
```

### Tests de React

```javascript
db.evaluation_test.find(
    { topic: { $regex: "React", $options: "i" } },
    { title: 1, difficulty: 1, number_of_questions: 1 }
)
```

### Tests difficiles

```javascript
db.evaluation_test.find({ difficulty: "hard" }).count()
```

### Dernier test créé

```javascript
db.evaluation_test.find().sort({ created_at: -1 }).limit(1).pretty()
```

---

## ❓ REQUÊTES QUESTIONS

### Questions d'un test

```javascript
db.evaluation_question.find({ test_id: 1 }).count()
```

### Questions par type

```javascript
db.evaluation_question.aggregate([
    { $group: { _id: "$question_type", count: { $sum: 1 } } }
])
```

### Questions difficiles

```javascript
db.evaluation_question.find({ difficulty_level: "hard" }).count()
```

---

## 📤 REQUÊTES SOUMISSIONS

### Soumissions d'un étudiant

```javascript
db.evaluation_submission.find({ student_id: 1 }).count()
```

### Dernières soumissions

```javascript
db.evaluation_submission.find().sort({ submitted_at: -1 }).limit(5)
```

### Soumissions par statut

```javascript
db.evaluation_submission.aggregate([
    { $group: { _id: "$status", count: { $sum: 1 } } }
])
```

### Temps moyen passé

```javascript
db.evaluation_submission.aggregate([
    { $group: { _id: null, avg_time: { $avg: "$time_spent" } } }
])
```

---

## 📈 REQUÊTES RÉSULTATS

### Résultats d'un étudiant

```javascript
db.evaluation_result.find(
    { student_id: 1 },
    { test_id: 1, percentage_score: 1, grade: 1 }
).sort({ created_at: -1 })
```

### Score moyen par étudiant

```javascript
db.evaluation_result.aggregate([
    { $group: {
        _id: "$student_id",
        avg_score: { $avg: "$percentage_score" },
        total_tests: { $sum: 1 }
    }},
    { $sort: { avg_score: -1 } }
])
```

### Résultats avec grade A ou A+

```javascript
db.evaluation_result.find(
    { grade: { $in: ["A", "A+"] } },
    { student_id: 1, test_id: 1, percentage_score: 1 }
)
```

### Tests les plus difficiles

```javascript
db.evaluation_result.aggregate([
    { $group: {
        _id: "$test_id",
        avg_score: { $avg: "$percentage_score" },
        total_attempts: { $sum: 1 }
    }},
    { $sort: { avg_score: 1 } },
    { $limit: 5 }
])
```

---

## 🔍 REQUÊTES AVANCÉES

### Performance par matière

```javascript
db.evaluation_result.aggregate([
    { $lookup: {
        from: "evaluation_test",
        localField: "test_id",
        foreignField: "_id",
        as: "test_info"
    }},
    { $unwind: "$test_info" },
    { $group: {
        _id: "$test_info.subject",
        avg_score: { $avg: "$percentage_score" },
        total_tests: { $sum: 1 }
    }},
    { $sort: { avg_score: -1 } }
])
```

### Progression d'un étudiant

```javascript
db.evaluation_result.find(
    { student_id: 1 },
    { created_at: 1, percentage_score: 1 }
).sort({ created_at: 1 })
```

### Analyse des compétences

```javascript
db.evaluation_result.aggregate([
    { $project: {
        student_id: 1,
        skills: { $objectToArray: "$skills_breakdown" }
    }},
    { $unwind: "$skills" },
    { $group: {
        _id: {
            student_id: "$student_id",
            skill: "$skills.k"
        },
        avg_score: { $avg: "$skills.v" }
    }},
    { $sort: { avg_score: -1 } }
])
```

---

## 🛠️ MAINTENANCE

### Backup de la base

```bash
# Créer backup
mongodump --db django_education --out ./backup_mongo

# Restaurer backup
mongorestore --db django_education ./backup_mongo/django_education
```

### Export en JSON

```bash
# Exporter une collection
mongoexport --db django_education --collection auth_user --out users.json

# Importer
mongoimport --db django_education --collection auth_user --file users.json
```

### Statistiques de la base

```javascript
db.stats()
```

### Taille des collections

```javascript
db.auth_user.stats().size
db.evaluation_test.stats().size
db.evaluation_question.stats().size
```

---

## 🧹 NETTOYAGE (ATTENTION!)

### Supprimer soumissions incomplètes

```javascript
db.evaluation_submission.deleteMany({ status: "in_progress" })
```

### Supprimer vieux tests (exemple)

```javascript
db.evaluation_test.deleteMany({
    created_at: { $lt: new Date("2024-01-01") }
})
```

### Supprimer TOUTE la collection (DANGER!)

```javascript
db.evaluation_test.drop()  // ⚠️ Supprime TOUT!
```

---

## 🐍 DEPUIS PYTHON

### Script rapide

```python
from pymongo import MongoClient

# Connexion
client = MongoClient('mongodb://localhost:27017/')
db = client['django_education']

# Stats
print(f"Users: {db.auth_user.count_documents({})}")
print(f"Tests: {db.evaluation_test.count_documents({})}")

# Requête
for user in db.auth_user.find({}, {'username': 1}):
    print(user['username'])

client.close()
```

---

## 🖥️ MONGODB COMPASS

### Télécharger

https://www.mongodb.com/try/download/compass

### Se connecter

```
mongodb://localhost:27017
```

### Filtres GUI

**Étudiants seulement** :
```json
{ "is_staff": false }
```

**Tests React** :
```json
{ "topic": { "$regex": "React", "$options": "i" } }
```

**Scores > 80%** :
```json
{ "percentage_score": { "$gt": 80 } }
```

---

## 📞 AIDE RAPIDE

### Problème de connexion ?

```bash
# Vérifier si MongoDB tourne
net start MongoDB

# Ou
Get-Service MongoDB
```

### Django ne se connecte pas ?

```python
# Dans Python shell
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
client.server_info()  # Devrait afficher infos serveur
```

### Voir les logs MongoDB

```
C:\Program Files\MongoDB\Server\7.0\log\mongod.log
```

---

## 🔗 RESSOURCES

- **MongoDB Docs** : https://docs.mongodb.com/
- **PyMongo** : https://pymongo.readthedocs.io/
- **Djongo** : https://www.djongomapper.com/
- **MongoDB Compass** : https://www.mongodb.com/products/compass

---

**Base de données** : `django_education`  
**Collections** : 6  
**Documents** : 894  
**Statut** : ✅ Opérationnel
