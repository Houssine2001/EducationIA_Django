"""
Extracteur de texte à partir de fichiers PDF
"""
import re


class PDFTextExtractor:
    """
    Extracteur de texte à partir de fichiers PDF
    Utilise PyPDF2 pour l'extraction basique
    """
    
    def __init__(self):
        self.min_text_length = 50  # Longueur minimale de texte valide
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """
        Extrait le texte d'un fichier PDF
        
        Args:
            pdf_file_path: Chemin vers le fichier PDF
            
        Returns:
            Texte extrait du PDF
        """
        try:
            import PyPDF2
            
            text = ""
            
            # Ouverture du fichier PDF
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extraction du texte de chaque page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        text += page_text + "\n\n"
            
            # Nettoyage du texte
            text = self._clean_extracted_text(text)
            
            return text
            
        except ImportError:
            # Si PyPDF2 n'est pas installé, retourner un message d'erreur
            return "Erreur : PyPDF2 n'est pas installé. Installez-le avec : pip install PyPDF2"
        
        except Exception as e:
            return f"Erreur lors de l'extraction du PDF : {str(e)}"
    
    def extract_text_from_file(self, file_obj) -> str:
        """
        Extrait le texte d'un objet fichier Django (UploadedFile)
        
        Args:
            file_obj: Objet fichier Django uploadé
            
        Returns:
            Texte extrait
        """
        try:
            import PyPDF2
            from io import BytesIO
            
            text = ""
            
            # Lecture du contenu du fichier
            file_content = file_obj.read()
            pdf_file = BytesIO(file_content)
            
            # Extraction avec PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    text += page_text + "\n\n"
            
            # Nettoyage
            text = self._clean_extracted_text(text)
            
            return text
            
        except ImportError:
            return "Erreur : PyPDF2 n'est pas installé. Installez-le avec : pip install PyPDF2"
        
        except Exception as e:
            return f"Erreur lors de l'extraction du PDF : {str(e)}"
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Nettoie le texte extrait d'un PDF
        """
        if not text:
            return ""
        
        # Suppression des caractères spéciaux excessifs
        text = re.sub(r'\x00', '', text)  # Caractères null
        
        # Normalisation des espaces
        text = re.sub(r' +', ' ', text)
        
        # Normalisation des sauts de ligne
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Suppression des lignes trop courtes (probablement des artefacts)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 3 or stripped == '':
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        return text.strip()
    
    def validate_extracted_text(self, text: str) -> bool:
        """
        Valide que le texte extrait est suffisant pour l'analyse
        """
        if not text or len(text.strip()) < self.min_text_length:
            return False
        
        # Vérification qu'il y a des mots significatifs
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{3,}\b', text.lower())
        
        return len(words) >= 10  # Au moins 10 mots significatifs


# Fonction utilitaire pour tester l'extracteur
def test_pdf_extraction(pdf_path: str):
    """
    Fonction de test pour l'extraction PDF
    """
    extractor = PDFTextExtractor()
    
    print(f"Extraction du PDF : {pdf_path}")
    text = extractor.extract_text_from_pdf(pdf_path)
    
    print(f"\nTexte extrait ({len(text)} caractères) :")
    print("=" * 50)
    print(text[:500])  # Premiers 500 caractères
    print("...")
    
    is_valid = extractor.validate_extracted_text(text)
    print(f"\nTexte valide : {is_valid}")
    
    return text
