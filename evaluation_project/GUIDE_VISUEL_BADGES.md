# 🎨 GUIDE VISUEL - BADGES TESTS MANUELS vs IA

## 📱 Dashboard Étudiant

### Avant les Modifications
```
┌────────────────────────────────────┐
│ Tests Disponibles                  │
├────────────────────────────────────┤
│ Test Algèbre Avancé               │
│ 📚 Mathématiques                  │
│ ❓ 10 questions │ 🕐 30 min       │
│                    [Commencer →]   │
│                                    │
│ Exercices Python                  │
│ 📚 Programmation                  │
│ ❓ 15 questions │ 🕐 45 min       │
│                    [Commencer →]   │
└────────────────────────────────────┘
```

### Après les Modifications ✨
```
┌────────────────────────────────────┐
│ Tests Disponibles                  │
├────────────────────────────────────┤
│ Test Algèbre Avancé  [👔 Manuel]  │
│ 📚 Mathématiques                  │
│ ❓ 10 questions │ 🕐 30 min       │
│                    [Commencer →]   │
│                                    │
│ Exercices Python  [🤖 IA Généré]  │
│ 📚 Programmation                  │
│ ❓ 15 questions │ 🕐 45 min       │
│                    [Commencer →]   │
└────────────────────────────────────┘
```

---

## 📄 Page Détails du Test

### Test Manuel
```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║  Test Algèbre Avancé  [👔 Test Manuel]              ║
║  ────────────────────────────────────────            ║
║                                                      ║
║  📚 Mathématiques │ ⭐ Moyen                         ║
║  🕐 30 minutes │ ❓ 10 questions                     ║
║  ✅ Score minimum : 50%                              ║
║                                                      ║
║  📝 Description                                      ║
║  Test créé par le professeur pour évaluer           ║
║  vos compétences en algèbre avancée.                ║
║                                                      ║
║  [🚀 Commencer le Test]                             ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

### Test IA
```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║  Exercices Python  [🤖 Généré par IA]               ║
║  ──────────────────────────────────                  ║
║  Badge violet avec dégradé                           ║
║                                                      ║
║  📚 Programmation │ ⭐ Facile                        ║
║  🕐 45 minutes │ ❓ 15 questions                     ║
║  ✅ Score minimum : 60%                              ║
║                                                      ║
║  📝 Description                                      ║
║  Test généré automatiquement à partir du            ║
║  document de cours "Introduction Python".           ║
║                                                      ║
║  [🚀 Commencer le Test]                             ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

---

## 🎨 Couleurs des Badges

### Manuel - Badge Gris
```css
Background: #f3f4f6 (gris clair)
Text: #1f2937 (gris foncé)
Icon: 👔 fas fa-user-tie
```

**Rendu** :
```
┌─────────────────┐
│ 👔 Manuel       │  ← Badge discret
└─────────────────┘
```

### IA Généré - Badge Violet
```css
Background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Text: white
Icon: 🤖 fas fa-robot
```

**Rendu** :
```
┌────────────────────┐
│ 🤖 Généré par IA   │  ← Badge dégradé violet
└────────────────────┘
```

---

## 📊 Comparaison Visuelle

### Dashboard - Liste Compacte
```
┌─────────────────────────────────────────────────┐
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ Test Python Débutant  [👔 Manuel]   │       │
│  │ ───────────────────────────────     │       │
│  │ 📚 Programmation                    │       │
│  │ ❓ 20 questions │ 🕐 60 min         │       │
│  │                    [Commencer →]    │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ Quiz React Hooks  [🤖 IA Généré]    │       │
│  │ ─────────────────────────────────   │       │
│  │ 📚 Framework Web                    │       │
│  │ ❓ 12 questions │ 🕐 30 min         │       │
│  │                    [Commencer →]    │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ Bases de Données SQL [👔 Manuel]    │       │
│  │ ───────────────────────────────     │       │
│  │ 📚 SQL                              │       │
│  │ ❓ 15 questions │ 🕐 45 min         │       │
│  │                    [Commencer →]    │       │
│  └─────────────────────────────────────┘       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Détails Techniques

### HTML - Badge Manuel
```html
<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
    <i class="fas fa-user-tie mr-1"></i> Manuel
</span>
```

### HTML - Badge IA
```html
<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
    <i class="fas fa-robot mr-1"></i> IA Généré
</span>
```

### Template Condition
```django
{% if test.source_type == 'ai_generated' %}
    <!-- Badge IA -->
{% else %}
    <!-- Badge Manuel -->
{% endif %}
```

---

## 📱 Responsive Design

### Mobile (< 768px)
```
┌───────────────────┐
│ Test Algèbre      │
│ [👔 Manuel]       │
│                   │
│ 📚 Maths          │
│ ❓ 10 │ 🕐 30min │
│                   │
│ [Commencer]       │
└───────────────────┘
```

### Desktop (≥ 768px)
```
┌─────────────────────────────────────────────┐
│ Test Algèbre Avancé [👔 Manuel]             │
│                                             │
│ 📚 Mathématiques │ ❓ 10 questions          │
│ 🕐 30 minutes │ ⭐ Moyen                    │
│                               [Commencer →] │
└─────────────────────────────────────────────┘
```

---

## 🎯 Résultats et Analytics

### Dashboard avec XP/Lacunes/Points Forts

```
┌─────────────────────────────────────────────────┐
│ 📊 Votre Progression                            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ⭐ Total XP : 2,450                            │
│  📈 Niveau : 5                                  │
│                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 75%              │
│  2,450 / 3,000 XP (prochain niveau)             │
│                                                 │
├─────────────────────────────────────────────────┤
│ 💪 Points Forts (basés sur TOUS les tests)     │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Algèbre               92%  [👔 Manuel]     │
│  2. Hooks React           88%  [🤖 IA]         │
│  3. SQL Joins             85%  [👔 Manuel]     │
│                                                 │
├─────────────────────────────────────────────────┤
│ 🎯 Lacunes Détectées                            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ⚠️ Géométrie            45%  [👔 Manuel]      │
│  ⚠️ Async JavaScript     52%  [🤖 IA]          │
│                                                 │
│  💡 3 recommandations disponibles               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🏆 Badges & Gamification

### Historique des Tests Complétés

```
┌─────────────────────────────────────────────────┐
│ 📜 Tests Récents                                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ✅ Test Python Avancé  [🤖 IA Généré]         │
│     Score : 92% │ XP : +150 │ Aujourd'hui     │
│                                                 │
│  ✅ Quiz Algèbre  [👔 Manuel]                  │
│     Score : 88% │ XP : +120 │ Hier            │
│                                                 │
│  ✅ Exercices React  [🤖 IA Généré]            │
│     Score : 75% │ XP : +80 │ Il y a 2 jours   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ✨ Animation et Effets

### Survol (Hover)
```
État Normal:
┌─────────────────────────┐
│ Test [👔 Manuel]        │
└─────────────────────────┘

État Survol:
┌─────────────────────────┐
│ Test [👔 Manuel]        │ ← Bordure bleue
│                         │   Ombre légère
│    [Commencer →]        │   Bouton levé
└─────────────────────────┘
```

---

## 📏 Dimensions

### Badges
- **Petits** (liste) : `px-2 py-1 text-xs`
- **Moyens** (détails) : `px-3 py-2 text-sm`
- **Grands** (en-tête) : `px-4 py-2 text-base`

### Icônes
- Taille : `16px` (liste), `20px` (détails)
- Espacement : `mr-1` (4px de marge droite)

---

**🎨 Design cohérent, moderne et intuitif pour distinguer facilement les tests manuels des tests générés par IA !**
