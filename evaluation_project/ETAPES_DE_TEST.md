# 📋 ÉTAPES DE TEST - Résumé Rapide

## 🚀 Option 1 : Test Automatique Complet (RECOMMANDÉ)

### Windows PowerShell
```powershell
# Tout en une seule commande !
.\run_tests.ps1
```

Ce script fait TOUT automatiquement :
- ✅ Vérifie Python et MongoDB
- ✅ Vérifie les dépendances
- ✅ Applique les migrations
- ✅ Crée les données de test (3 étudiants + 3 tests)
- ✅ Vérifie le système
- ✅ Propose de lancer le serveur

**Durée : ~30 secondes**

---

## 🔧 Option 2 : Test Manuel Étape par Étape

### Étape 1 : Préparation (2 min)
```powershell
# 1. Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# 2. Vérifier MongoDB
Get-Process -Name mongod
# Si pas démarré : mongod --dbpath "C:\data\db"
```

### Étape 2 : Migrations (1 min)
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Étape 3 : Créer les données de test (30 sec)
```powershell
python create_test_data.py
```

### Étape 4 : Vérifier le système (10 sec)
```powershell
python verify_system.py
```

### Étape 5 : Lancer le serveur (instantané)
```powershell
python manage.py runserver
```

---

## 🌐 Test dans le Navigateur

### 1. Dashboard Étudiant (2 min)
```
URL : http://127.0.0.1:8000/student/dashboard/
Compte : etudiant1 / pass123
```

**À vérifier** :
- [ ] 4 cards statistiques (Score 80%, Tests 3, Niveau 4, Classement #2)
- [ ] Section badges (2 badges affichés)
- [ ] Recommandations IA (suggestions pour Physique)
- [ ] Performances par matière (3 cards : Maths, Physique, Info)
- [ ] Classement général (3 étudiants avec médailles)

### 2. Page de Progression (2 min)
```
URL : http://127.0.0.1:8000/student/progress/
```

**À vérifier** :
- [ ] 3 graphiques Chart.js s'affichent
- [ ] Graphique de progression (line chart bleu)
- [ ] Graphique par matière (bar chart coloré)
- [ ] Analyse détaillée par matière (3 cards avec mini graphiques)
- [ ] Analyse IA des faiblesses (section gradient purple)

### 3. Responsive Design (1 min)
```
DevTools (F12) → Toggle Device Toolbar
```

**À tester** :
- [ ] Mobile (375px) : Sidebar cachée, bouton hamburger
- [ ] Tablet (768px) : 2 colonnes
- [ ] Desktop (1920px) : 4 colonnes, sidebar fixe

---

## 📊 Résultats Attendus

### Comptes Créés
| Username | Password | Rôle | Score Moyen | Niveau | Classement |
|----------|----------|------|-------------|--------|------------|
| etudiant1 | pass123 | Étudiant | 80% | 4 (Compétent) | #2 🥈 |
| etudiant2 | pass123 | Étudiant | 60% | 2 (Apprenti) | #3 🥉 |
| etudiant3 | pass123 | Étudiant | 93.3% | 5 (Expert) | #1 🥇 |
| prof1 | pass123 | Enseignant | - | - | - |

### Tests Créés
1. **Algèbre Niveau 1** (Mathématiques) - 5 questions
2. **Forces et Mouvement** (Physique) - 5 questions
3. **Introduction Python** (Informatique) - 5 questions

### Résultats Simulés (etudiant1)
- Mathématiques : 80% (4/5) - 15 minutes
- Physique : 60% (3/5) - 25 minutes
- Informatique : 100% (5/5) - 10 minutes

---

## ✅ Checklist Rapide

### Backend
- [ ] MongoDB connecté
- [ ] Migrations appliquées
- [ ] 4 utilisateurs créés
- [ ] 3 tests créés
- [ ] 9 résultats enregistrés (3 étudiants × 3 tests)

### Frontend - Dashboard
- [ ] Tailwind CSS chargé (styles appliqués)
- [ ] Sidebar visible et fonctionnelle
- [ ] 4 cards statistiques avec valeurs correctes
- [ ] Badges affichés avec icônes
- [ ] Recommandations IA visibles
- [ ] Performances par matière (3 cards)
- [ ] Classement avec médailles colorées

### Frontend - Progression
- [ ] 3 graphiques Chart.js chargés
- [ ] Graphique progression (3 points visibles)
- [ ] Graphique matières (3 barres colorées)
- [ ] Tooltips interactifs fonctionnent
- [ ] Mini graphiques dans les cards
- [ ] Analyse IA affichée

### Analytics
- [ ] Score moyen : 80% (etudiant1)
- [ ] Tests complétés : 3
- [ ] Heures d'étude : 0.8h
- [ ] Tendance calculée
- [ ] Performances par matière groupées

### Gamification
- [ ] XP attribué (etudiant1 : ~540 XP)
- [ ] Badges obtenus (First Test, Perfect Score)
- [ ] Niveau calculé (Niveau 4)
- [ ] Classement correct (#1, #2, #3)
- [ ] Médailles colorées

---

## 🐛 Dépannage Rapide

### Erreur : MongoDB not connected
```powershell
# Démarrer MongoDB
mongod --dbpath "C:\data\db"
```

### Erreur : Module not found
```powershell
pip install -r requirements.txt
```

### Page blanche
```
1. F12 → Console → Vérifier les erreurs
2. Ctrl+Shift+Delete → Vider le cache
3. Recharger la page
```

### Graphiques ne s'affichent pas
```
1. F12 → Network → Vérifier que Chart.js charge
2. Console → Vérifier les erreurs JavaScript
```

---

## 📚 Documentation

- **README.md** : Vue d'ensemble du projet
- **DEMARRAGE_RAPIDE.md** : Guide de démarrage (5 min)
- **GUIDE_DE_TEST.md** : Tests complets et détaillés (30+ pages)
- **create_test_data.py** : Script de création de données
- **verify_system.py** : Script de vérification
- **run_tests.ps1** : Script PowerShell automatique

---

## 🎯 Scénario de Test Complet (5 min)

1. **Lancer** `.\run_tests.ps1`
2. **Ouvrir** http://127.0.0.1:8000/student/dashboard/
3. **Se connecter** avec `etudiant1` / `pass123`
4. **Vérifier** les 4 cards statistiques
5. **Cliquer** sur "Ma progression"
6. **Vérifier** les 3 graphiques
7. **Tester** le responsive (F12 → Device Toolbar)
8. **Se déconnecter** et tester avec `etudiant3` (score 93%)

**Résultat attendu** : ✅ Tout fonctionne sans erreur

---

## 🚀 Commandes Utiles

```powershell
# Créer des données de test
python create_test_data.py

# Vérifier le système
python verify_system.py

# Lancer le serveur
python manage.py runserver

# Ouvrir l'admin Django
http://127.0.0.1:8000/admin/

# Voir les logs MongoDB
# (dans le terminal où mongod tourne)

# Tests complets automatiques
.\run_tests.ps1
```

---

**⏱️ Temps total de test : ~10 minutes**
**✅ Taux de réussite attendu : 100%**

Bon test ! 🎉
