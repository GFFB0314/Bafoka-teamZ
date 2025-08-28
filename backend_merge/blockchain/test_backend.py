# test_backend.py - Script de test pour identifier les problèmes
import sys
import os

print("🔍 Test du Backend Flask - Diagnostic des Problèmes")
print("=" * 50)

# Test 1: Vérifier Python et Flask
try:
    import flask
    print("✅ Flask installé - Version:", flask.__version__)
except ImportError as e:
    print("❌ Flask non installé:", e)
    sys.exit(1)

# Test 2: Vérifier les autres dépendances
dependencies = ['flask_sqlalchemy', 'dotenv', 'requests']
for dep in dependencies:
    try:
        __import__(dep)
        print(f"✅ {dep} installé")
    except ImportError as e:
        print(f"❌ {dep} non installé: {e}")

# Test 3: Vérifier la structure des fichiers
print("\n📁 Vérification de la structure des fichiers:")
backend_path = "Bafoka-teamZ-back/backend_merge"
files_to_check = [
    "app_corrected.py",
    "models.py", 
    "core_logic.py",
    "db.py",
    "bafoka_integration.py"
]

for file in files_to_check:
    file_path = os.path.join(backend_path, file)
    if os.path.exists(file_path):
        print(f"✅ {file} trouvé")
    else:
        print(f"❌ {file} manquant")

# Test 4: Test d'import des modules
print("\n🔧 Test d'import des modules:")
try:
    sys.path.append(backend_path)
    
    # Test db.py
    try:
        from db import db
        print("✅ db.py importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import db.py: {e}")
    
    # Test models.py
    try:
        from models import User, Offer, Agreement
        print("✅ models.py importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import models.py: {e}")
    
    # Test core_logic.py
    try:
        import core_logic
        print("✅ core_logic.py importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import core_logic.py: {e}")
    
    # Test bafoka_integration.py
    try:
        import bafoka_integration
        print("✅ bafoka_integration.py importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import bafoka_integration.py: {e}")
        
except Exception as e:
    print(f"❌ Erreur générale: {e}")

# Test 5: Test de création de l'app Flask
print("\n🚀 Test de création de l'application Flask:")
try:
    from app_corrected import create_app
    app = create_app()
    print("✅ Application Flask créée avec succès")
    
    # Test des routes
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print("✅ Endpoint /health fonctionne")
        else:
            print(f"❌ Endpoint /health retourne {response.status_code}")
            
except Exception as e:
    print(f"❌ Erreur création app Flask: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Diagnostic terminé!")
print("Si des erreurs sont présentes, corrigez-les avant de continuer.")
