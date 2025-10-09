# 🎨 GUIDE VISUEL - Migration MongoDB

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│        🔄 MIGRATION SQLite → MongoDB EN 3 ÉTAPES           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📌 ÉTAPE 1 : INSTALLATION (10 min)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Télécharger│ →   │   Installer  │ →   │   Vérifier   │
│   MongoDB    │     │   MongoDB    │     │   Service    │
└──────────────┘     └──────────────┘     └──────────────┘
      📥                    ⚙️                   ✅
```

### Actions

```powershell
# 1. Télécharger
https://www.mongodb.com/try/download/community

# 2. Installer
# Double-clic → Complete → Install as Service → Finish

# 3. Vérifier
mongod --version
net start MongoDB
```

### Résultat attendu

```
✅ MongoDB version 7.0.x
✅ Service MongoDB démarré
✅ mongosh fonctionne
```

---

## 📌 ÉTAPE 2 : MIGRATION (15 min)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Setup      │ →   │   Migrate    │ →   │   Verify     │
│   Python     │     │   Data       │     │   MongoDB    │
└──────────────┘     └──────────────┘     └──────────────┘
      🐍                    🔄                   📊
```

### Actions

```powershell
# 1. Setup Python
.\setup_mongodb.ps1

# 2. Migrate Data
python migrate_to_mongodb.py

# 3. Verify (dans MongoDB Compass)
# Connexion: mongodb://localhost:27017
# Base: django_education
# Collections: 6 collections visibles
```

### Résultat attendu

```
📦 Backup créé: ./backup_sqlite/
✅ Users: 5
✅ Profiles: 5  
✅ Tests: 50
✅ Questions: 453
✅ Submissions: 122
✅ Results: 122
🎉 Migration réussie !
```

---

## 📌 ÉTAPE 3 : CONFIGURATION (5 min)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Configure  │ →   │   Restart    │ →   │   Test       │
│   Django     │     │   Server     │     │   Interface  │
└──────────────┘     └──────────────┘     └──────────────┘
      ⚙️                    🔄                   🌐
```

### Actions

```powershell
# 1. Configure
copy backend\settings_mongodb.py backend\settings.py

# 2. Restart
python manage.py runserver

# 3. Test
http://127.0.0.1:8000/
Login: etudiant1 / password123
```

### Résultat attendu

```
✅ Serveur démarre sans erreur
✅ Login fonctionne
✅ Dashboard s'affiche
✅ Données visibles
```

---

## 📊 VUE D'ENSEMBLE DU SYSTÈME

### Architecture Avant (SQLite)

```
┌─────────────────────────────────────────┐
│          Django Application             │
├─────────────────────────────────────────┤
│           SQLite (fichier)              │
│        db.sqlite3 (30 MB)              │
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │ Tables  │  │ Indexes │  │  Data  │ │
│  │ (SQL)   │  │ (B-Tree)│  │ (Rows) │ │
│  └─────────┘  └─────────┘  └────────┘ │
└─────────────────────────────────────────┘
```

### Architecture Après (MongoDB)

```
┌─────────────────────────────────────────┐
│          Django Application             │
│             (avec Djongo)               │
├─────────────────────────────────────────┤
│        MongoDB Server (localhost)       │
│        Base: django_education           │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │ Collections │  │    Documents      │ │
│  │  (6 total)  │  │    (JSON/BSON)   │ │
│  │             │  │                  │ │
│  │ • users     │  │  {_id, username, │ │
│  │ • profiles  │  │   strengths: [], │ │
│  │ • tests     │  │   badges: [],    │ │
│  │ • questions │  │   ...}           │ │
│  │ • submit... │  │                  │ │
│  │ • results   │  │                  │ │
│  └─────────────┘  └──────────────────┘ │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        Index (optimisé)          │  │
│  │  • username (unique)             │  │
│  │  • student_id + test_id          │  │
│  │  • date queries                  │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🔄 FLUX DE MIGRATION DÉTAILLÉ

```
                    MIGRATION
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌───────┐       ┌───────┐      ┌───────┐
    │Backup │       │Export │      │Import │
    │SQLite │  →    │  to   │  →   │  to   │
    │(copy) │       │ JSON  │      │MongoDB│
    └───────┘       └───────┘      └───────┘
        │               │               │
        ▼               ▼               ▼
    db.sqlite3    backup_sqlite/   django_education
    .backup       ├── users.json      (MongoDB)
                  ├── profiles.json
                  ├── tests.json
                  ├── questions.json
                  ├── submission.json
                  └── results.json
```

---

## 📁 STRUCTURE DES COLLECTIONS MONGODB

### Collection: auth_user

```json
{
  "_id": ObjectId("..."),
  "username": "etudiant1",
  "email": "etudiant1@example.com",
  "password": "hashed_password",
  "first_name": "Jean",
  "last_name": "Dupont",
  "is_staff": false,
  "is_active": true,
  "date_joined": ISODate("2025-10-01")
}
```

### Collection: evaluation_userprofile

```json
{
  "_id": ObjectId("..."),
  "user_id": 1,
  "student_id": "ETU001",
  "average_score": 71.4,
  "total_xp": 1250,
  "level": 5,
  "badges": [
    {
      "id": "expert",
      "name": "Expert",
      "description": "50 tests complétés",
      "icon": "👑",
      "earned_at": "2025-10-05"
    }
  ],
  "strengths": [
    {
      "subject": "React",
      "skill": "Hooks",
      "percentage": 92.0,
      "description": "Excellence en React : Hooks"
    }
  ],
  "weaknesses": [
    {
      "subject": "SQL",
      "skill": "Sous-requêtes",
      "percentage": 45.0
    }
  ]
}
```

---

## 🎯 COMPARAISON PERFORMANCES

### Requête : Récupérer un étudiant avec son profil

**SQLite (2 requêtes):**
```sql
SELECT * FROM auth_user WHERE id = 1;
SELECT * FROM evaluation_userprofile WHERE user_id = 1;
```
⏱️ Temps: ~5ms

**MongoDB (1 requête):**
```javascript
db.auth_user.aggregate([
  {$match: {_id: 1}},
  {$lookup: {
    from: "evaluation_userprofile",
    localField: "_id",
    foreignField: "user_id",
    as: "profile"
  }}
])
```
⏱️ Temps: ~2ms
✅ 2.5x plus rapide

---

## 📈 SCALABILITÉ

### SQLite

```
Étudiants     Taille DB    Performance
─────────────────────────────────────
100           10 MB        ✅ Excellent
1,000         100 MB       ✅ Bon
10,000        1 GB         ⚠️  Moyen
100,000       10 GB        ❌ Lent
```

### MongoDB

```
Étudiants     Taille DB    Performance
─────────────────────────────────────
100           5 MB         ✅ Excellent
1,000         50 MB        ✅ Excellent
10,000        500 MB       ✅ Excellent
100,000       5 GB         ✅ Bon
1,000,000     50 GB        ✅ Bon (sharding)
```

---

## 🛠️ OUTILS DISPONIBLES

### MongoDB Compass (Interface Graphique)

```
┌─────────────────────────────────────────┐
│  MongoDB Compass                     ×  │
├─────────────────────────────────────────┤
│  Connection: mongodb://localhost:27017  │
│                                         │
│  Databases                              │
│  ├── admin                              │
│  ├── config                             │
│  └── django_education          ◄────    │
│      ├── auth_user (5 docs)             │
│      ├── evaluation_userprofile (5)     │
│      ├── evaluation_test (50)           │
│      ├── evaluation_question (453)      │
│      ├── evaluation_submission (122)    │
│      └── evaluation_result (122)        │
│                                         │
│  [Queries] [Aggregations] [Schema]     │
└─────────────────────────────────────────┘
```

---

## ✅ CHECKLIST VISUELLE

### Installation

```
□ MongoDB téléchargé
□ MongoDB installé
□ Service démarré
□ mongosh testé
□ Compass installé (optionnel)
```

### Migration

```
□ setup_mongodb.ps1 exécuté
□ Packages Python installés
□ migrate_to_mongodb.py exécuté
□ Backup créé
□ Collections visibles dans Compass
□ Index créés
```

### Configuration

```
□ settings.py configuré
□ Serveur démarre
□ Login fonctionne
□ Dashboard OK
□ Tests passent
```

---

## 🆘 DÉPANNAGE RAPIDE

### Problème: MongoDB ne démarre pas

```
Symptôme: "net start MongoDB" échoue
         ↓
Solution: Vérifier logs
         ↓
C:\Program Files\MongoDB\Server\7.0\log\mongod.log
         ↓
Souvent: Port 27017 occupé
         ↓
netstat -ano | findstr :27017
         ↓
taskkill /PID <PID> /F
```

### Problème: Migration échoue

```
Symptôme: migrate_to_mongodb.py erreur
         ↓
Vérifier: MongoDB connecté?
         ↓
mongosh mongodb://localhost:27017
         ↓
Si OK → Vérifier backup_sqlite/
         ↓
Si fichiers vides → Problème SQLite
         ↓
copy db.sqlite3.backup db.sqlite3
```

---

## 📞 AIDE

**Documentation complète**: `MIGRATION_MONGODB_GUIDE.md`
**Commandes rapides**: `QUICK_MONGODB_COMMANDS.md`  
**Résumé**: `MIGRATION_MONGODB_RESUME.md`
**Index**: `INDEX_MIGRATION_MONGODB.md`

---

**Date**: 9 octobre 2025
**Version**: 1.0
