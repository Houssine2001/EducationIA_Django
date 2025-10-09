#!/usr/bin/env python
"""
Test de login HTTP pour vérifier le CSRF et l'authentification
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://127.0.0.1:8000'

print("=" * 70)
print("TEST DE LOGIN HTTP")
print("=" * 70)

# Créer une session pour garder les cookies
session = requests.Session()

# 1. Récupérer la page de login pour obtenir le CSRF token
print("\n1️⃣  Récupération de la page de login...")
try:
    response = session.get(f'{BASE_URL}/evaluation/login/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        # Extraire le CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_input:
            csrf_token = csrf_input['value']
            print(f"   ✅ CSRF token récupéré: {csrf_token[:20]}...")
            
            # 2. Tenter de se connecter
            print("\n2️⃣  Tentative de connexion avec prof1...")
            login_data = {
                'username': 'prof1',
                'password': 'pass123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            # Envoyer la requête de login
            login_response = session.post(
                f'{BASE_URL}/evaluation/login/',
                data=login_data,
                headers={'Referer': f'{BASE_URL}/evaluation/login/'}
            )
            
            print(f"   Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                if 'dashboard' in login_response.url or login_response.url.endswith('/'):
                    print(f"   ✅ Login réussi! Redirigé vers: {login_response.url}")
                else:
                    print(f"   ⚠️  Page de login encore affichée")
                    # Chercher les erreurs
                    soup = BeautifulSoup(login_response.text, 'html.parser')
                    errors = soup.find_all(class_='alert-danger')
                    for error in errors:
                        print(f"   ❌ Erreur: {error.text.strip()}")
            
            # 3. Vérifier l'accès au dashboard
            print("\n3️⃣  Vérification de l'accès au dashboard...")
            dashboard_response = session.get(f'{BASE_URL}/evaluation/dashboard/')
            print(f"   Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                if 'login' in dashboard_response.url:
                    print(f"   ❌ Redirigé vers login - Non authentifié")
                else:
                    print(f"   ✅ Accès au dashboard réussi!")
            else:
                print(f"   ❌ Erreur d'accès: {dashboard_response.status_code}")
                
        else:
            print(f"   ❌ CSRF token introuvable dans le HTML")
    else:
        print(f"   ❌ Impossible de charger la page de login")
        
except requests.exceptions.ConnectionError:
    print(f"   ❌ ERREUR: Serveur inaccessible sur {BASE_URL}")
    print(f"   ⚠️  Assurez-vous que le serveur Django est démarré:")
    print(f"       python manage.py runserver")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 70)
