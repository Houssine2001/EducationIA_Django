# 🚀 EduIA - Démarrage Ultra-Rapide

## ⚡ Démarrage en 1 Commande

```powershell
.\start.ps1
```

**C'est tout !** Le script :
- ✅ Démarre MongoDB automatiquement
- ✅ Active l'environnement virtuel
- ✅ Lance le serveur Django

## 🛑 Arrêt Propre

```powershell
# Dans le terminal du serveur : CTRL + C
# Puis pour arrêter MongoDB :
.\stop.ps1
```

## 🔐 Connexion

**URL :** http://127.0.0.1:8000/

**Comptes :**
- `etudiant1` / `pass123` → Score 86.7% ⭐⭐⭐
- `etudiant2` / `pass123` → Score 63.3% ⭐⭐
- `etudiant3` / `pass123` → Score 96.7% ⭐⭐⭐⭐
- `prof1` / `pass123` → Professeur

## ⚠️ Problème Courant

### Erreur "Cannot use MongoClient after close"

**Cause :** MongoDB s'est arrêté

**Solution :**
```powershell
.\start.ps1
```

Le script relancera automatiquement MongoDB si nécessaire.

---

**📚 Guides Détaillés :**
- `GUIDE_DEMARRAGE.md` - Guide complet
- `DEMARRAGE_RAPIDE.md` - Guide 5 minutes
- `GUIDE_DE_TEST.md` - Tests détaillés

**🎉 Bon développement !**
