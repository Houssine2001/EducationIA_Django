# 🚀 Guide de Démarrage Rapide - EduIA

## ⚡ Démarrage en 5 Minutes

### Prérequis
- ✅ Python 3.10+ installé
- ✅ MongoDB installé et démarré
- ✅ Git installé

---

## 📋 Étapes de Démarrage

### 1️⃣ Activer l'Environnement Virtuel
```powershell
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
.\.venv\Scripts\Activate.ps1
```

### 2️⃣ Vérifier MongoDB
```powershell
# Vérifier si MongoDB tourne
Get-Process -Name mongod

# Si non, démarrez-le (dans un nouveau terminal)
mongod --dbpath "C:\data\db"
```

### 3️⃣ Appliquer les Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4️⃣ Créer les Données de Test (AUTOMATIQUE)
```powershell
# Ce script crée automatiquement:
# - 3 étudiants (etudiant1, etudiant2, etudiant3)
# - 1 enseignant (prof1)
# - 3 tests avec questions
# - Résultats simulés pour chaque étudiant

python create_test_data.py
```

**⏱️ Durée : ~10 secondes**

### 5️⃣ Vérifier le Système
```powershell
# Script de vérification automatique
python verify_system.py
```

Ce script vérifie :
- ✅ Connexion MongoDB
- ✅ Modèles Django
- ✅ Analytics
- ✅ Gamification
- ✅ Templates

### 6️⃣ Lancer le Serveur
```powershell
python manage.py runserver
```

Le serveur démarre sur : **http://127.0.0.1:8000/**

---

## 🔐 Comptes de Test Créés

### Étudiants
| Username | Password | Score Moyen | Niveau |
|----------|----------|-------------|--------|
| etudiant1 | pass123 | 80% | Compétent |
| etudiant2 | pass123 | 60% | Apprenti |
| etudiant3 | pass123 | 93% | Expert |

### Enseignant
| Username | Password | Rôle |
|----------|----------|------|
| prof1 | pass123 | Enseignant (Staff) |

---

## 🎯 Test Rapide (2 minutes)

### Test 1 : Dashboard Étudiant
1. **Ouvrir** : http://127.0.0.1:8000/student/dashboard/
2. **Se connecter** : `etudiant1` / `pass123`
3. **Vérifier** :
   - ✅ 4 cards statistiques (Score, Tests, Niveau, Classement)
   - ✅ Section Badges
   - ✅ Recommandations IA
   - ✅ Performances par matière (3 cards)
   - ✅ Classement général (top 3)

### Test 2 : Page de Progression
1. **Cliquer** sur "Ma progression" dans la sidebar
2. **Vérifier** :
   - ✅ 3 graphiques Chart.js
   - ✅ Analyse détaillée par matière
   - ✅ Analyse IA des faiblesses
   - ✅ Historique complet

### Test 3 : Responsive
1. **Ouvrir DevTools** (F12)
2. **Tester résolutions** :
   - 📱 Mobile (375px) : Sidebar cachée, bouton hamburger
   - 💻 Desktop (1920px) : Sidebar fixe, 4 colonnes

---

## 📊 Données de Test Créées

### Tests Disponibles
1. **Algèbre Niveau 1** (Mathématiques)
   - 5 questions
   - 30 minutes
   - Difficulté : Débutant

2. **Forces et Mouvement** (Physique)
   - 5 questions
   - 45 minutes
   - Difficulté : Intermédiaire

3. **Introduction Python** (Informatique)
   - 5 questions
   - 20 minutes
   - Difficulté : Débutant

### Résultats Simulés

**etudiant1** :
- Mathématiques : 80% (15 min)
- Physique : 60% (25 min)
- Informatique : 100% (10 min)
- **Score moyen : 80%**
- **Badges** : First Test, Perfect Score
- **Niveau** : 4 (Compétent)

**etudiant2** :
- Mathématiques : 60% (20 min)
- Physique : 40% (30 min)
- Informatique : 80% (15 min)
- **Score moyen : 60%**
- **Niveau** : 2 (Apprenti)

**etudiant3** :
- Mathématiques : 100% (12 min)
- Physique : 80% (20 min)
- Informatique : 100% (8 min)
- **Score moyen : 93.3%**
- **Niveau** : 5 (Expert)
- **Classement** : #1 🥇

---

## 🎨 Fonctionnalités à Tester

### Dashboard Étudiant
- [ ] Statistiques principales (4 cards)
- [ ] Badges obtenus
- [ ] Recommandations IA personnalisées
- [ ] Performances par matière
- [ ] Tests disponibles
- [ ] Classement général avec médailles
- [ ] Résultats récents

### Page de Progression
- [ ] Vue d'ensemble (5 cards)
- [ ] Graphique progression temporelle (line chart)
- [ ] Graphique par matière (bar chart)
- [ ] Graphique temps d'étude (bar chart)
- [ ] Analyse détaillée par matière (3 cards)
- [ ] Mini graphiques dans les cards
- [ ] Analyse IA des faiblesses
- [ ] Historique complet (tableau)

### Design & Interface
- [ ] Tailwind CSS appliqué
- [ ] Sidebar responsive
- [ ] Animations fluides (hover, fadeIn)
- [ ] Gradients modernes
- [ ] Icônes FontAwesome
- [ ] Couleurs cohérentes
- [ ] Mobile responsive

---

## 🐛 Dépannage Rapide

### Erreur : "No module named 'djongo'"
```powershell
pip install djongo pymongo
```

### Erreur : "MongoDB not connected"
```powershell
# Démarrer MongoDB
mongod --dbpath "C:\data\db"
```

### Erreur : "Template not found"
```powershell
# Vérifier que les templates existent
ls templates/evaluation/student/
```

### Page blanche / Pas de style
1. Vérifier que Tailwind CSS charge (DevTools → Network)
2. Vider le cache du navigateur (Ctrl+Shift+Delete)

### Graphiques ne s'affichent pas
1. Vérifier que Chart.js charge (DevTools → Console)
2. Vérifier les données dans la vue (ajouter `print(progression_chart_data)`)

---

## 📚 Documentation Complète

Pour des tests approfondis, consultez :
- **GUIDE_DE_TEST.md** : Guide complet de test (30+ pages)
- **create_test_data.py** : Script de création de données
- **verify_system.py** : Script de vérification système

---

## 🚀 Prochaines Étapes

Après avoir testé le système :

1. **Créer de vrais tests** (en tant que prof1)
2. **Tester avec de vrais étudiants**
3. **Personnaliser les couleurs** (dans base.html)
4. **Ajouter plus de matières**
5. **Configurer la production**

---

## ✅ Checklist de Vérification Rapide

Avant de dire que tout fonctionne :

- [ ] Serveur démarre sans erreur
- [ ] Dashboard s'affiche avec le design Tailwind
- [ ] Statistiques sont calculées correctement
- [ ] 3 graphiques Chart.js s'affichent
- [ ] Badges sont visibles
- [ ] Recommandations IA apparaissent
- [ ] Classement affiche les 3 étudiants
- [ ] Mobile responsive fonctionne

---

**🎉 Félicitations ! Votre système EduIA est opérationnel !**

Pour toute question, consultez GUIDE_DE_TEST.md ou vérifiez les erreurs dans le terminal.
