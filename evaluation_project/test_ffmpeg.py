"""
Script de test pour diagnostiquer le problème FFmpeg avec Whisper
"""
import os
import sys

print("=" * 60)
print("DIAGNOSTIC FFMPEG POUR WHISPER")
print("=" * 60)

# 1. Tester imageio-ffmpeg
print("\n1. Test imageio-ffmpeg...")
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg_path = get_ffmpeg_exe()
    print(f"   ✅ FFmpeg trouvé via imageio-ffmpeg")
    print(f"   📁 Chemin: {ffmpeg_path}")
    print(f"   📂 Dossier: {os.path.dirname(ffmpeg_path)}")
    
    # Vérifier si le fichier existe
    if os.path.exists(ffmpeg_path):
        print(f"   ✅ Le fichier existe")
    else:
        print(f"   ❌ Le fichier n'existe PAS")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 2. Tester en ajoutant au PATH
print("\n2. Test ajout au PATH...")
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg_path = get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    
    # Ajouter au PATH
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
    print(f"   ✅ Ajouté au PATH: {ffmpeg_dir}")
    
    # Vérifier
    import subprocess
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"   ✅ FFmpeg fonctionne via PATH!")
        print(f"   Version: {result.stdout.split()[2]}")
    else:
        print(f"   ❌ FFmpeg ne fonctionne pas via PATH")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 3. Tester Whisper avec le PATH configuré
print("\n3. Test Whisper avec FFmpeg...")
try:
    import whisper
    print(f"   ✅ Whisper importé")
    
    # Essayer de charger le modèle (ceci force Whisper à chercher FFmpeg)
    print(f"   🔄 Chargement du modèle Whisper 'tiny'...")
    model = whisper.load_model("tiny")
    print(f"   ✅ Modèle chargé avec succès!")
    
except Exception as e:
    print(f"   ❌ Erreur Whisper: {e}")

# 4. Solution alternative - définir IMAGEIO_FFMPEG_EXE
print("\n4. Test variable d'environnement IMAGEIO_FFMPEG_EXE...")
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg_path = get_ffmpeg_exe()
    os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
    print(f"   ✅ Variable définie: IMAGEIO_FFMPEG_EXE={ffmpeg_path}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DU DIAGNOSTIC")
print("=" * 60)
