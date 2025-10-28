import os
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service pour l'extraction de texte et génération de résumés IA"""
    
    def __init__(self):
        self.summarizer = None
        self.whisper_model = None
        self._initialized = False
        self._whisper_initialized = False
    
    def _initialize_models(self):
        """Initialisation paresseuse des modèles IA"""
        if self._initialized:
            return
        
        try:
            from transformers import pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            self._initialized = True
        except ImportError:
            print("⚠️ Bibliothèques IA non installées. Les résumés automatiques ne seront pas disponibles.")
            self._initialized = False
    
    def _initialize_whisper(self):
        """Initialisation paresseuse du modèle Whisper"""
        if self._whisper_initialized:
            return
        
        try:
            import whisper
            logger.info("🤖 Chargement du modèle Whisper 'tiny' (rapide et léger)...")
            self.whisper_model = whisper.load_model("tiny")
            self._whisper_initialized = True
            logger.info("✅ Modèle Whisper 'tiny' chargé avec succès")
        except ImportError:
            logger.error("⚠️ Whisper non installé")
            self._whisper_initialized = False
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de Whisper: {e}")
            self._whisper_initialized = False
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text.strip()
        except ImportError:
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text.strip()
            except ImportError:
                return "Erreur: PyPDF2 ou pdfplumber requis pour extraire du PDF"
        except Exception as e:
            return f"Erreur lors de l'extraction du PDF: {str(e)}"
    
    def extract_text_from_video(self, file_path: str) -> str:
        """Extrait l'audio d'une vidéo et le transcrit avec Whisper (limité à 3 minutes)"""
        import tempfile
        temp_audio_path = None
        
        try:
            import whisper
            import os
            import subprocess
            
            # Initialiser le modèle Whisper (une seule fois)
            self._initialize_whisper()
            
            if not self._whisper_initialized or not self.whisper_model:
                return "⚠️ Modèle Whisper non disponible.\n\nLa vidéo a été uploadée mais la transcription automatique a échoué. Vous pouvez ajouter manuellement une description."
            
            # Configurer FFmpeg depuis imageio-ffmpeg
            try:
                from imageio_ffmpeg import get_ffmpeg_exe
                ffmpeg_path = get_ffmpeg_exe()
                
                # Définir les variables d'environnement pour que Whisper trouve FFmpeg
                os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
                os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get('PATH', '')
                
                # Créer un lien symbolique si besoin (pour que 'ffmpeg' pointe vers le binaire)
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                simple_ffmpeg = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
                if not os.path.exists(simple_ffmpeg):
                    try:
                        import shutil
                        shutil.copy2(ffmpeg_path, simple_ffmpeg)
                        logger.info(f"✅ Copie FFmpeg créée: {simple_ffmpeg}")
                    except Exception as copy_error:
                        logger.warning(f"⚠️ Impossible de copier ffmpeg.exe: {copy_error}")
                
                logger.info(f"✅ FFmpeg configuré: {ffmpeg_path}")
                
                # Extraire seulement les 3 premières minutes (180 secondes) de l'audio
                logger.info("⏱️ Extraction des 3 premières minutes de l'audio...")
                temp_audio_path = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False).name
                
                # Commande ffmpeg pour extraire 3 minutes d'audio
                cmd = [
                    ffmpeg_path,
                    '-i', file_path,           # Fichier d'entrée
                    '-t', '180',               # Durée: 180 secondes (3 minutes)
                    '-vn',                     # Pas de vidéo
                    '-acodec', 'libmp3lame',   # Codec audio MP3
                    '-ar', '16000',            # Sample rate 16kHz (optimal pour Whisper)
                    '-ac', '1',                # Mono
                    '-y',                      # Overwrite si existe
                    temp_audio_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"✅ Audio extrait: {temp_audio_path}")
                
            except ImportError:
                logger.warning("⚠️ imageio-ffmpeg non disponible, transcription complète de la vidéo")
                temp_audio_path = file_path  # Utiliser la vidéo complète si ffmpeg n'est pas disponible
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Erreur ffmpeg: {e.stderr.decode() if e.stderr else str(e)}")
                temp_audio_path = file_path  # Fallback sur la vidéo complète
            
            logger.info(f"📹 Chargement de la vidéo: {file_path}...")
            
            # Utiliser le modèle Whisper déjà chargé
            logger.info("📝 Transcription en cours des 3 premières minutes...")
            result = self.whisper_model.transcribe(
                temp_audio_path,
                language='fr',  # Français pour meilleure précision
                fp16=False,     # Désactiver fp16 pour compatibilité CPU
                condition_on_previous_text=False,  # Plus rapide
                verbose=False   # Moins de logs
            )
            
            logger.info(f"✅ Transcription réussie: {len(result['text'])} caractères")
            return result['text']
            
        except ImportError as e:
            missing = "whisper"
            return f"⚠️ Bibliothèque manquante: {missing}\n\nInstallez avec: pip install openai-whisper"
        except Exception as e:
            logger.error(f"❌ Erreur lors de la transcription vidéo: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"⚠️ Erreur lors de la transcription: {str(e)}\n\nLa vidéo a été uploadée mais la transcription automatique a échoué. Vous pouvez ajouter manuellement une description."
        finally:
            # Nettoyer le fichier audio temporaire
            if temp_audio_path and temp_audio_path != file_path:
                try:
                    import os
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                        logger.info(f"🗑️ Fichier audio temporaire supprimé")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Erreur lors du nettoyage: {cleanup_error}")
    
    def extract_text_from_text_file(self, file_path: str) -> str:
        """Extrait le texte d'un fichier texte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                return f"Erreur lors de la lecture du fichier: {str(e)}"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extrait le texte d'un fichier DOCX"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except ImportError:
            return "Erreur: python-docx requis pour extraire du DOCX"
        except Exception as e:
            return f"Erreur lors de l'extraction du DOCX: {str(e)}"
    
    def generate_summary(self, text: str, max_length: int = 300, min_length: int = 100, do_sample: bool = True, temperature: float = 0.8) -> str:
        """Génère un résumé du texte avec IA"""
        if not text or len(text.strip()) < 100:
            return "Texte trop court pour générer un résumé."
        
        self._initialize_models()
        
        if not self._initialized or not self.summarizer:
            return self._generate_simple_summary(text, num_sentences=10)
        
        try:
            # Limiter le texte à une longueur raisonnable pour le modèle
            # BART peut gérer jusqu'à 1024 tokens (environ 4000 caractères)
            max_input_length = 8000  # Augmenté pour traiter plus de texte
            if len(text) > max_input_length:
                text = text[:max_input_length]
            
            # Générer le résumé avec variabilité
            summary = self.summarizer(
                text, 
                max_length=max_length,  # Résumé plus long (300 mots au lieu de 150)
                min_length=min_length,  # Minimum 100 mots
                do_sample=do_sample,
                temperature=temperature,
                top_k=50,
                top_p=0.95,
                num_beams=4  # Améliore la qualité du résumé
            )
            return summary[0]['summary_text']
        
        except Exception as e:
            print(f"Erreur lors de la génération du résumé IA: {str(e)}")
            return self._generate_simple_summary(text, num_sentences=10)
    
    def _generate_simple_summary(self, text: str, num_sentences: int = 10) -> str:
        """Génère un résumé simple en prenant les phrases les plus importantes"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Prendre un mélange de phrases du début, milieu et fin
        if len(sentences) <= num_sentences:
            summary_sentences = sentences
        else:
            # Prendre des phrases distribuées dans tout le texte
            step = len(sentences) // num_sentences
            summary_sentences = [sentences[i * step] for i in range(num_sentences)]
        
        return '. '.join(summary_sentences) + '.'
    
    def process_resource(self, resource) -> dict:
        """
        Traite une ressource : extraction de texte et génération de résumé
        
        Args:
            resource: Instance du modèle Resource
        
        Returns:
            dict: Résultat du traitement avec 'success', 'summary', 'error'
        """
        try:
            file_path = resource.file.path
            text = ""
            
            # Extraction du texte selon le type
            if resource.type == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif resource.type == 'video':
                text = self.extract_text_from_video(file_path)
            elif resource.type == 'text':
                if file_path.endswith('.docx'):
                    text = self.extract_text_from_docx(file_path)
                else:
                    text = self.extract_text_from_text_file(file_path)
            else:
                return {
                    'success': False,
                    'error': 'Type de fichier non supporté pour l\'extraction'
                }
            
            # Vérification du texte extrait
            if text.startswith('Erreur'):
                return {
                    'success': False,
                    'error': text
                }
            
            # Si le texte commence par un avertissement (⚠️), c'est un message informatif
            if text.startswith('⚠️'):
                return {
                    'success': True,
                    'summary': text,
                    'error': None
                }
            
            if not text or len(text.strip()) < 100:
                # Pour les vidéos, accepter même sans transcription
                if resource.type == 'video':
                    return {
                        'success': True,
                        'summary': '📹 Vidéo uploadée avec succès.\n\nℹ️ La transcription automatique nécessite FFmpeg. Vous pouvez ajouter une description manuellement.',
                        'error': None
                    }
                return {
                    'success': False,
                    'error': 'Texte extrait trop court ou vide'
                }
            
            # Génération du résumé
            summary = self.generate_summary(text)
            
            return {
                'success': True,
                'summary': summary,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors du traitement: {str(e)}'
            }


# Instance globale du service IA
ai_service = AIService()
