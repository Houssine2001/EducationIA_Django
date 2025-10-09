# 🔍 EXEMPLES DE REQUÊTES MONGODB - VOTRE PROJET

**Base de données** : `django_education`

---

## 🚀 DÉMARRAGE RAPIDE

### Se connecter à MongoDB

```bash
mongo django_education
```

Vous verrez :
```
MongoDB shell version v5.0.30
connecting to: mongodb://127.0.0.1:27017/django_education
>
```

---

## 👥 REQUÊTES SUR LES UTILISATEURS

### 1. Voir tous les utilisateurs

```javascript
db.auth_user.find().pretty()
```

**Résultat** :
```json
{
  "_id": 1,
  "username": "prof1",
  "email": "prof@eduia.com",
  "is_staff": true
}
{
  "_id": 2,
  "username": "etudiant1",
  "email": "etudiant1@example.com",
  "is_staff": false
}
```

---

### 2. Compter utilisateurs par type

```javascript
print('👨‍🏫 Enseignants:', db.auth_user.count({ is_staff: true }));
print('🎓 Étudiants:', db.auth_user.count({ is_staff: false }));
```

**Résultat** :
```
👨‍🏫 Enseignants: 1
🎓 Étudiants: 3
```

---

### 3. Chercher un utilisateur spécifique

```javascript
db.auth_user.findOne({ username: "etudiant1" })
```

---

## 📊 REQUÊTES SUR LES PROFILS

### 1. Statistiques d'un étudiant

```javascript
db.evaluation_userprofile.findOne(
    { user_id: 2 },  // etudiant1
    {
        total_tests_taken: 1,
        average_score: 1,
        level: 1,
        total_xp: 1,
        _id: 0
    }
)
```

**Résultat** :
```json
{
  "total_tests_taken": 66,
  "average_score": 71.4,
  "level": 5,
  "total_xp": 1250
}
```

---

### 2. Top 3 étudiants par score moyen

```javascript
db.evaluation_userprofile.find({}, {
    user_id: 1,
    total_tests_taken: 1,
    average_score: 1,
    level: 1
}).sort({ average_score: -1 }).limit(3).pretty()
```

**Résultat** :
```json
{ "user_id": 2, "total_tests_taken": 66, "average_score": 71.4, "level": 5 }
{ "user_id": 4, "total_tests_taken": 68, "average_score": 70.7, "level": 5 }
{ "user_id": 3, "total_tests_taken": 50, "average_score": 69.6, "level": 4 }
```

---

### 3. Points forts d'un étudiant

```javascript
db.evaluation_userprofile.findOne(
    { user_id: 2 },
    { strengths: 1, _id: 0 }
).strengths.slice(0, 5)  // Top 5 points forts
```

**Résultat** :
```json
[
  {
    "subject": "React",
    "skill": "Formulaires et validation",
    "percentage": 100,
    "description": "Excellence en React : Formulaires et validation (100% - 5/5)"
  },
  {
    "subject": "Django",
    "skill": "Formulaires",
    "percentage": 100,
    "description": "Excellence en Django : Formulaires (100% - 5/5)"
  }
]
```

---

### 4. Badges d'un étudiant

```javascript
db.evaluation_userprofile.findOne(
    { user_id: 2 },
    { badges: 1, _id: 0 }
).badges.length
```

**Résultat** :
```
10
```

---

## 📝 REQUÊTES SUR LES TESTS

### 1. Nombre de tests par matière

```javascript
db.evaluation_test.aggregate([
    { $group: { 
        _id: "$subject", 
        count: { $sum: 1 } 
    }},
    { $sort: { count: -1 } }
])
```

**Résultat** :
```json
{ "_id": "Informatique", "count": 50 }
```

---

### 2. Tests de React

```javascript
db.evaluation_test.find(
    { topic: { $regex: "React", $options: "i" } },
    { title: 1, difficulty: 1, number_of_questions: 1, _id: 0 }
).limit(5).pretty()
```

**Résultat** :
```json
{
  "title": "Test React Avancé #1",
  "difficulty": "medium",
  "number_of_questions": 12
}
{
  "title": "Test React Débutant #2",
  "difficulty": "easy",
  "number_of_questions": 8
}
```

---

### 3. Tests par difficulté

```javascript
db.evaluation_test.aggregate([
    { $group: { 
        _id: "$difficulty", 
        count: { $sum: 1 } 
    }}
])
```

**Résultat** :
```json
{ "_id": "easy", "count": 15 }
{ "_id": "medium", "count": 25 }
{ "_id": "hard", "count": 10 }
```

---

### 4. Dernier test créé

```javascript
db.evaluation_test.find({}, {
    title: 1,
    subject: 1,
    topic: 1,
    created_at: 1
}).sort({ created_at: -1 }).limit(1).pretty()
```

---

## ❓ REQUÊTES SUR LES QUESTIONS

### 1. Questions par type

```javascript
db.evaluation_question.aggregate([
    { $group: { 
        _id: "$question_type", 
        count: { $sum: 1 } 
    }}
])
```

**Résultat** :
```json
{ "_id": "mcq", "count": 450 }
{ "_id": "true_false", "count": 142 }
```

---

### 2. Questions d'un test

```javascript
db.evaluation_question.find(
    { test_id: 1 },
    { question_text: 1, question_type: 1, points: 1 }
).limit(3).pretty()
```

---

### 3. Questions difficiles

```javascript
db.evaluation_question.count({ difficulty_level: "hard" })
```

---

## 📤 REQUÊTES SUR LES SOUMISSIONS

### 1. Soumissions d'un étudiant

```javascript
db.evaluation_submission.find(
    { student_id: 2 },
    { test_id: 1, status: 1, submitted_at: 1 }
).sort({ submitted_at: -1 }).limit(5).pretty()
```

---

### 2. Temps moyen par test

```javascript
db.evaluation_submission.aggregate([
    { $group: {
        _id: null,
        avg_time_minutes: { $avg: { $divide: ["$time_spent", 60] } }
    }}
])
```

**Résultat** :
```json
{ "_id": null, "avg_time_minutes": 45.2 }
```

---

### 3. Soumissions par statut

```javascript
db.evaluation_submission.aggregate([
    { $group: { _id: "$status", count: { $sum: 1 } } }
])
```

---

## 📊 REQUÊTES SUR LES RÉSULTATS

### 1. Résultats d'un étudiant

```javascript
db.evaluation_result.find(
    { student_id: 2 },
    { test_id: 1, percentage_score: 1, grade: 1, created_at: 1 }
).sort({ created_at: -1 }).limit(10).pretty()
```

---

### 2. Score moyen par étudiant

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

**Résultat** :
```json
{ "_id": 2, "avg_score": 71.4, "total_tests": 66 }
{ "_id": 4, "avg_score": 70.7, "total_tests": 68 }
{ "_id": 3, "avg_score": 69.6, "total_tests": 50 }
```

---

### 3. Résultats avec grade A ou A+

```javascript
db.evaluation_result.find(
    { grade: { $in: ["A", "A+"] } },
    { student_id: 1, test_id: 1, percentage_score: 1, grade: 1 }
).count()
```

---

### 4. Progression d'un étudiant (graphique)

```javascript
db.evaluation_result.find(
    { student_id: 2 },
    { created_at: 1, percentage_score: 1, _id: 0 }
).sort({ created_at: 1 }).limit(20)
```

---

## 🎯 REQUÊTES AVANCÉES

### 1. Score moyen par matière

```javascript
db.evaluation_result.aggregate([
    {
        $lookup: {
            from: "evaluation_test",
            localField: "test_id",
            foreignField: "_id",
            as: "test"
        }
    },
    { $unwind: "$test" },
    {
        $group: {
            _id: "$test.subject",
            avg_score: { $avg: "$percentage_score" },
            total_tests: { $sum: 1 }
        }
    },
    { $sort: { avg_score: -1 } }
])
```

---

### 2. Tests les plus difficiles (score moyen le plus bas)

```javascript
db.evaluation_result.aggregate([
    {
        $group: {
            _id: "$test_id",
            avg_score: { $avg: "$percentage_score" },
            total_attempts: { $sum: 1 }
        }
    },
    { $sort: { avg_score: 1 } },
    { $limit: 5 }
])
```

---

### 3. Étudiants qui ont passé > 50 tests

```javascript
db.evaluation_userprofile.find(
    { total_tests_taken: { $gt: 50 } },
    { user_id: 1, total_tests_taken: 1, average_score: 1 }
).pretty()
```

---

### 4. Analyse des compétences (tous étudiants)

```javascript
db.evaluation_userprofile.aggregate([
    { $unwind: "$strengths" },
    {
        $group: {
            _id: {
                subject: "$strengths.subject",
                skill: "$strengths.skill"
            },
            avg_percentage: { $avg: "$strengths.percentage" },
            count_students: { $sum: 1 }
        }
    },
    { $sort: { avg_percentage: -1 } },
    { $limit: 10 }
])
```

**Cette requête montre** : Les 10 compétences les mieux maîtrisées en moyenne

---

## 📈 STATISTIQUES GLOBALES

### Dashboard enseignant

```javascript
// Statistiques générales
print('=== STATISTIQUES GLOBALES ===');
print('Total utilisateurs:', db.auth_user.count());
print('Total étudiants:', db.auth_user.count({ is_staff: false }));
print('Total tests:', db.evaluation_test.count());
print('Total questions:', db.evaluation_question.count());
print('Total soumissions:', db.evaluation_submission.count());
print('');

// Score moyen global
var avgScore = db.evaluation_result.aggregate([
    { $group: { _id: null, avg: { $avg: "$percentage_score" } } }
]).toArray()[0].avg;
print('Score moyen global:', avgScore.toFixed(2) + '%');

// Répartition des grades
print('\n=== RÉPARTITION DES GRADES ===');
db.evaluation_result.aggregate([
    { $group: { _id: "$grade", count: { $sum: 1 } } },
    { $sort: { _id: 1 } }
]).forEach(function(doc) {
    print(doc._id + ':', doc.count);
});
```

---

## 💡 ASTUCES

### Formater joliment les résultats

```javascript
// Utiliser .pretty() pour un affichage lisible
db.auth_user.find().pretty()
```

### Limiter le nombre de résultats

```javascript
// Voir seulement les 5 premiers
db.evaluation_test.find().limit(5)
```

### Projections (champs spécifiques)

```javascript
// Voir seulement username et email
db.auth_user.find({}, { username: 1, email: 1, _id: 0 })
```

### Compter sans afficher

```javascript
// Juste le nombre
db.evaluation_test.count()
```

---

## 🔍 RECHERCHES UTILES

### Chercher dans le texte

```javascript
// Tests contenant "React" dans le titre
db.evaluation_test.find({ title: { $regex: "React", $options: "i" } })
```

### Recherche avec plusieurs critères

```javascript
// Tests React de difficulté moyenne
db.evaluation_test.find({
    topic: "React",
    difficulty: "medium"
})
```

### Dates

```javascript
// Soumissions d'aujourd'hui
db.evaluation_submission.find({
    submitted_at: {
        $gte: new Date("2025-10-09T00:00:00Z"),
        $lt: new Date("2025-10-10T00:00:00Z")
    }
})
```

---

## 📝 EXEMPLES PRATIQUES

### Exemple 1 : Voir le profil complet d'etudiant1

```javascript
// 1. Trouver l'ID de etudiant1
var user = db.auth_user.findOne({ username: "etudiant1" });
print('User ID:', user._id);

// 2. Voir son profil
var profile = db.evaluation_userprofile.findOne({ user_id: user._id });
print('\n=== PROFIL ===');
print('Tests passés:', profile.total_tests_taken);
print('Score moyen:', profile.average_score + '%');
print('Niveau:', profile.level);
print('XP:', profile.total_xp);
print('Badges:', profile.badges.length);
print('Points forts:', profile.strengths.length);
print('Lacunes:', profile.weaknesses.length);
```

---

### Exemple 2 : Voir tous les résultats d'un test

```javascript
// Résultats du test #1
db.evaluation_result.find(
    { test_id: 1 },
    { student_id: 1, percentage_score: 1, grade: 1 }
).sort({ percentage_score: -1 }).pretty()
```

---

### Exemple 3 : Comparer les performances de 2 étudiants

```javascript
// Étudiant 1
var student1 = db.evaluation_userprofile.findOne({ user_id: 2 });
// Étudiant 2
var student2 = db.evaluation_userprofile.findOne({ user_id: 3 });

print('=== COMPARAISON ===');
print('Étudiant 1 : ' + student1.total_tests_taken + ' tests, ' + student1.average_score + '%');
print('Étudiant 2 : ' + student2.total_tests_taken + ' tests, ' + student2.average_score + '%');
```

---

## 🎨 MONGODB COMPASS (GUI)

Si vous préférez une interface graphique :

1. **Télécharger** : https://www.mongodb.com/try/download/compass
2. **Connexion** : `mongodb://localhost:27017`
3. **Base** : Cliquer sur `django_education`
4. **Explorer** : Cliquer sur une collection
5. **Filtrer** : Utiliser la barre de recherche

**Exemples de filtres Compass** :

```json
{ "is_staff": false }                    // Étudiants
{ "average_score": { "$gt": 70 } }       // Score > 70%
{ "topic": { "$regex": "React" } }       // Tests React
```

---

**Base de données** : `django_education`  
**Collections** : 6  
**Documents** : 894

**Pour plus de commandes** : Voir `AIDE_MEMOIRE_MONGODB.md`
