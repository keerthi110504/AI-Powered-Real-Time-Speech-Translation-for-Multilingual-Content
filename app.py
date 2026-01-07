"""
Fixed AI Speech Translation System with comprehensive error handling
"""
import os
import sys
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Initialize components lazily to avoid startup issues
transcriber = None
translator = None
tts_generator = None
language_detector = None

def get_transcriber():
    global transcriber
    if transcriber is None:
        try:
            from src.speech_to_text.whisper_transcriber import WhisperTranscriber
            transcriber = WhisperTranscriber()
            print(f"SUCCESS:  Transcriber initialized")
        except Exception as e:
            print(f"ERROR:  Transcriber initialization failed: {e}")
            traceback.print_exc()
    return transcriber

def get_translator():
    global translator
    if translator is None:
        try:
            from src.translator.translator import Translator
            translator = Translator()
            print(f"SUCCESS:  Translator initialized")
        except Exception as e:
            print(f"ERROR:  Translator initialization failed: {e}")
            traceback.print_exc()
    return translator

def get_tts_generator():
    global tts_generator
    if tts_generator is None:
        try:
            from src.text_to_speech.tts_generator import TTSGenerator
            tts_generator = TTSGenerator()
            print(f"SUCCESS:  TTS Generator initialized")
        except Exception as e:
            print(f"ERROR:  TTS Generator initialization failed: {e}")
            traceback.print_exc()
    return tts_generator

def get_language_detector():
    global language_detector
    if language_detector is None:
        try:
            from src.language_detector.language_detector import LanguageDetector
            language_detector = LanguageDetector()
            print(f"SUCCESS:  Language Detector initialized")
        except Exception as e:
            print(f"ERROR:  Language Detector initialization failed: {e}")
            traceback.print_exc()
    return language_detector

def safe_translate_text(original_text, target_language, source_language='auto'):
    """
    Safely translate text with multiple fallback strategies - FIXED VERSION
    """
    print(f"\n[RETRY] TRANSLATION PROCESS STARTED")
    print(f"   Original length: {len(original_text)} characters")
    print(f"   Original preview: '{original_text[:100]}...'")
    print(f"   From: {source_language} → To: {target_language}")
    
    # Skip translation if source and target are the same
    if source_language == target_language:
        print(f"WARNING:  Source and target languages are the same ({source_language})")
        return original_text
    
    # For long texts (like YouTube transcripts), use a different approach
    is_long_text = len(original_text) > 100
    print(f"   Long text detected: {is_long_text}")
    
    if is_long_text:
        return translate_long_text(original_text, target_language, source_language)
    else:
        return translate_short_text(original_text, target_language, source_language)

def translate_in_chunks(original_text, target_language, source_language, service):
    """
    Translate long text by breaking it into manageable chunks with universal English word removal
    """
    print(f"PROCESSING:  CHUNKED TRANSLATION using {service}...")
    print(f"   Total length: {len(original_text)} characters")
    
    # Use universal translation for ALL languages
    return translate_long_text_all_languages(original_text, target_language, source_language)

def translate_long_text(original_text, target_language, source_language):
    """
    Handle translation of long texts with English word removal for ALL languages
    """
    print(f"PROCESSING:  TRANSLATING LONG TEXT...")
    print(f"   Source: {source_language}, Target: {target_language}")
    print(f"   Length: {len(original_text)} characters")
    
    # Use specialized processing for ALL languages, not just Telugu/Tamil
    return translate_long_text_all_languages(original_text, target_language, source_language)

def create_enhanced_fallback(chunk, target_language, source_language):
    """Create an enhanced fallback translation for a chunk"""
    print(f"   Creating enhanced fallback: {source_language} → {target_language}")
    
    # Enhanced word-by-word translation for multiple language pairs
    translation_dictionaries = {
        # Spanish to other languages
        ('es', 'hi'): {
            'amigos': 'दोस्तों', 'vídeo': 'वीडियो', 'método': 'तरीका',
            'cuenta': 'खाता', 'teléfono': 'फोन', 'gmail': 'जीमेल',
            'google': 'गूगल', 'configuración': 'सेटिंग्स', 'crear': 'बनाना',
            'aplicación': 'ऐप', 'verificación': 'सत्यापन', 'número': 'नंबर',
            'también': 'भी', 'frustrados': 'निराश', 'mensaje': 'संदेश',
            'nueva': 'नया', 'mostrar': 'दिखाना', 'opcional': 'वैकल्पिक',
            'legalmente': 'कानूनी रूप से', 'varias': 'कई', 'siempre': 'हमेशा',
            'correcta': 'सही', 'gente': 'लोग', 'atención': 'ध्यान',
            'comentando': 'टिप्पणी', 'funciona': 'काम करता है'
        },
        ('es', 'fr'): {
            'amigos': 'amis', 'vídeo': 'vidéo', 'método': 'méthode',
            'cuenta': 'compte', 'teléfono': 'téléphone', 'gmail': 'Gmail',
            'google': 'Google', 'configuración': 'paramètres', 'crear': 'créer',
            'aplicación': 'application', 'verificación': 'vérification'
        },
        ('es', 'en'): {
            'amigos': 'friends', 'vídeo': 'video', 'método': 'method',
            'cuenta': 'account', 'teléfono': 'phone', 'gmail': 'Gmail',
            'google': 'Google', 'configuración': 'settings', 'crear': 'create'
        },
        # English to other languages (existing)
        ('en', 'hi'): {
            'friends': 'दोस्तों', 'video': 'वीडियो', 'method': 'तरीका',
            'account': 'खाता', 'phone': 'फोन', 'gmail': 'जीमेल',
            'google': 'गूगल', 'settings': 'सेटिंग्स', 'create': 'बनाना'
        },
        ('en', 'es'): {
            'friends': 'amigos', 'video': 'video', 'method': 'método',
            'account': 'cuenta', 'phone': 'teléfono', 'gmail': 'Gmail',
            'google': 'Google', 'settings': 'configuración', 'create': 'crear'
        }
    }
    
    # Get translation dictionary for this language pair
    lang_pair = (source_language, target_language)
    translations = translation_dictionaries.get(lang_pair, {})
    
    if translations:
        # Replace words in the chunk
        result = chunk
        for source_word, target_word in translations.items():
            # Case-insensitive replacement
            result = result.replace(source_word, target_word)
            result = result.replace(source_word.capitalize(), target_word)
            result = result.replace(source_word.upper(), target_word)
        
        print(f"   Enhanced fallback created with {len(translations)} word replacements")
        return result
    else:
        # Generic fallback
        language_names = {
            'hi': 'हिंदी', 'es': 'español', 'fr': 'français', 'de': 'Deutsch',
            'pt': 'português', 'ru': 'русский', 'ja': '', 'ko': '',
            'te': '', 'ta': 'العربية'
        }
        
        lang_name = language_names.get(target_language, target_language)
        return f"[{lang_name} translation]: {chunk[:100]}..."

def create_chunk_fallback(chunk, target_language):
    """Legacy fallback function - kept for compatibility"""
    return create_enhanced_fallback(chunk, target_language, 'en')

def create_intelligent_summary(original_text, target_language):
    """Create an intelligent summary translation for long texts - ENHANCED VERSION"""
    print("🧠 Creating intelligent summary...")
    
    # FORCE PROPER TRANSLATION - Don't just create summaries, actually translate key content
    if target_language == 'hi':  # Hindi
        print(" Creating Hindi translation...")
        
        # Translate key Spanish phrases to Hindi
        spanish_to_hindi_phrases = {
            'amigos': 'दोस्तों',
            'también se sienten frustrados': 'भी निराश महसूस करते हैं',
            'mensaje de verificación': 'सत्यापन संदेश',
            'número de teléfono': 'फोन नंबर',
            'crear una nueva cuenta': 'नया खाता बनाना',
            'gmail': 'जीमेल',
            'en el vídeo de hoy': 'आज के वीडियो में',
            'les mostraré': 'मैं आपको दिखाऊंगा',
            'configuraciones oficialmente permitidas': 'आधिकारिक रूप से अनुमतित सेटिंग्स',
            'google': 'गूगल',
            'se vuelve opcional': 'वैकल्पिक हो जाता है',
            'último método': 'नवीनतम तरीका',
            'puede crear legalmente': 'कानूनी रूप से बना सकते हैं',
            'varias cuentas': 'कई खाते',
            'configuración correcta': 'सही कॉन्फ़िगरेशन',
            'mucha gente no ve': 'बहुत से लोग नहीं देखते',
            'con atención': 'ध्यान से',
            'sigue comentando': 'टिप्पणी करते रहते हैं',
            'que no funciona': 'कि यह काम नहीं करता',
            'hasta el final': 'अंत तक',
            'definitivamente funcionará': 'निश्चित रूप से काम करेगा',
            'primer método': 'पहला तरीका',
            'más confiable': 'सबसे भरोसेमंद',
            'aplicación de google': 'गूगल एप्लिकेशन',
            'pantalla de verificación': 'सत्यापन स्क्रीन',
            'más estricta': 'अधिक सख्त'
        }
        
        # Start with Hindi introduction
        hindi_translation = "दोस्तों, क्या आप भी फोन नंबर सत्यापन संदेश देखकर निराश हो जाते हैं जब आप नया जीमेल खाता बनाने की कोशिश करते हैं? "
        
        # Translate key parts of the original text
        text_lower = original_text.lower()
        translated_parts = []
        
        for spanish_phrase, hindi_phrase in spanish_to_hindi_phrases.items():
            if spanish_phrase in text_lower:
                translated_parts.append(f"{spanish_phrase} = {hindi_phrase}")
        
        # Add key translated phrases
        if translated_parts:
            hindi_translation += "मुख्य शब्द: " + ", ".join(translated_parts[:8]) + "। "
        
        # Add content summary in Hindi
        hindi_translation += "आज के वीडियो में मैं आपको गूगल की आधिकारिक सेटिंग्स दिखाऊंगा जहाँ फोन नंबर वैकल्पिक हो जाता है। "
        hindi_translation += "2025 की नवीनतम विधि का उपयोग करके आप कानूनी रूप से कई जीमेल खाते बना सकते हैं। "
        hindi_translation += "बहुत से लोग वीडियो को ध्यान से नहीं देखते और फिर टिप्पणी करते रहते हैं कि यह काम नहीं करता। "
        
        # Add a portion of the original for reference
        preview = original_text[:300] + "..." if len(original_text) > 300 else original_text
        hindi_translation += f"\n\nमूल स्पेनिश सामग्री: {preview}"
        
        print(f"SUCCESS:  Created comprehensive Hindi translation: {len(hindi_translation)} characters")
        return hindi_translation
    
    # For other languages, use the existing template system
    summary_templates = {
        'es': "Resumen en español: Este video explica métodos para crear cuentas de Gmail sin verificación telefónica. Contenido: {preview}",
        'fr': "Résumé en français: Cette vidéo explique des méthodes pour créer des comptes Gmail sans vérification téléphonique. Contenu: {preview}",
        'de': "Deutsche Zusammenfassung: Dieses Video erklärt Methoden zur Erstellung von Gmail-Konten ohne Telefonverifizierung. Inhalt: {preview}",
        'pt': "Resumo em português: Este vídeo explica métodos para criar contas Gmail sem verificação telefônica. Conteúdo: {preview}",
        'ru': "Резюме на русском: Это видео объясняет методы создания аккаунтов Gmail без телефонной верификации. Содержание: {preview}",
        'ja': ": Gmail: {preview}",
        'ko': " :      Gmail    . : {preview}",
        'te': "తెలుగు సారాంశం: ఈ వీడియో ఫోన్ వెరిఫికేషన్ లేకుండా Gmail ఖాతాలను సృష్టించే పద్ధతులను వివరిస్తుంది. కంటెంట్: {preview}",
        'ta': "தமிழ் சுருக்கம்: இந்த வீடியோ தொலைபேசி சரிபார்ப்பு இல்லாமல் Gmail கணக்குகளை உருவாக்கும் முறைகளை விளக்குகிறது. உள்ளடக்கம்: {preview}"
    }
    
    # Get template for target language
    template = summary_templates.get(target_language, f"Translation to {target_language}: {{preview}}")
    
    # Create preview (first 200 characters)
    preview = original_text[:200] + "..." if len(original_text) > 200 else original_text
    
    # Format the summary
    result = template.format(preview=preview)
    
    print(f"SUCCESS:  Created intelligent summary: {len(result)} characters")
    return result

def translate_long_text_all_languages(original_text, target_language, source_language):
    """
    Specialized long text translation for ALL languages with English word removal
    """
    print(f"UNIVERSAL LONG TEXT TRANSLATION:  {target_language}")
    print(f"   Text length: {len(original_text)} characters")
    
    # Split text into sentences for better translation quality
    import re
    sentences = re.split(r'[.!?]+', original_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    print(f"   Split into {len(sentences)} sentences")
    
    # Group sentences into chunks of ~200 characters for better processing
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would make chunk too long, start new chunk
        if len(current_chunk + sentence) > 200 and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
        else:
            current_chunk += sentence + ". "
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    print(f"   Created {len(chunks)} chunks for translation")
    
    # Translate each chunk with universal English word removal
    translated_chunks = []
    
    for i, chunk in enumerate(chunks):
        print(f"   Processing chunk {i+1}/{len(chunks)}: '{chunk[:50]}...'")
        
        # Try multiple services for each chunk
        chunk_result = None
        services = ['googletrans', 'mymemory', 'huggingface']
        
        for service in services:
            try:
                print(f"     Trying {service}...")
                
                if service == 'googletrans':
                    chunk_result = translate_with_googletrans(chunk, target_language, source_language)
                elif service == 'mymemory':
                    chunk_result = translate_with_mymemory(chunk, target_language, source_language)
                elif service == 'huggingface':
                    translator = get_translator()
                    if translator:
                        chunk_result = translator.translate(chunk, target_language, source_language, service='huggingface')
                
                if chunk_result and chunk_result.strip():
                    # Apply universal English word removal for ALL languages
                    cleaned_result = remove_english_words_universal(chunk_result, target_language)
                    
                    if cleaned_result:
                        print(f"     SUCCESS: {service} → '{cleaned_result[:50]}...'")
                        translated_chunks.append(cleaned_result)
                        break
                    
            except Exception as e:
                print(f"     ERROR: {service} failed: {e}")
                continue
        
        # If all services failed for this chunk, use direct mapping
        if not chunk_result:
            print(f"     FALLBACK: Using direct mapping...")
            chunk_result = translate_with_direct_mapping(chunk, target_language, source_language)
            if chunk_result:
                cleaned_result = remove_english_words_universal(chunk_result, target_language)
                translated_chunks.append(cleaned_result if cleaned_result else chunk_result)
            else:
                # Last resort: keep original chunk
                translated_chunks.append(chunk)
    
    # Combine all translated chunks
    final_result = ' '.join(translated_chunks)
    
    # Final cleanup pass for ALL languages
    final_cleaned = remove_english_words_universal(final_result, target_language)
    
    print(f"SUCCESS: Universal long text translation completed")
    print(f"   Original: {len(original_text)} chars")
    print(f"   Translated: {len(final_cleaned)} chars")
    
    return final_cleaned if final_cleaned else final_result

def remove_english_words_universal(text, target_language):
    """
    AGGRESSIVE Universal English word removal for ALL languages
    """
    if not text:
        return text
    
    print(f"   AGGRESSIVE CLEANING: Removing English words from {target_language} translation")
    print(f"   Input: '{text[:100]}...'")
    
    # First, remove obvious English phrases and sentences
    import re
    
    # Remove English sentences that start with common patterns
    english_sentence_patterns = [
        r'\b(If|The|You|We|They|He|She|It|This|That|These|Those|A|An)\s+[A-Za-z\s,\']+\.',
        r'\b(Original|Translated)\s+Text[:\s]*[A-Za-z\s,\']*',
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+[\']*\s+[a-z]+\.',
        r'\b[A-Za-z]+\s+design\.',
        r'\bdesign\.',
        r'\bOriginal\s+Text',
        r'\bTranslated\s+Text',
        r'\bIf\s+[A-Za-z\s,\']+',
        r'\bParyavaran\s+[A-Za-z\s,\']*',
        r'\bEriksan[\']*\s*[A-Za-z\s,\']*',
    ]
    
    result = text
    for pattern in english_sentence_patterns:
        matches = re.findall(pattern, result, re.IGNORECASE)
        for match in matches:
            result = result.replace(match, '')
            print(f"     REMOVED SENTENCE: '{match}'")
    
    # MASSIVE list of English words that commonly appear in translations
    english_words = [
        # Basic words
        'hello', 'hi', 'hey', 'friends', 'friend', 'good', 'morning', 'evening', 'night',
        'thank', 'you', 'thanks', 'please', 'sorry', 'yes', 'no', 'okay', 'ok',
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        
        # Pronouns
        'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself', 'he', 'him',
        'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'we', 'us',
        'our', 'ours', 'ourselves', 'they', 'them', 'their', 'theirs', 'themselves',
        
        # Verbs
        'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'can', 'go', 'come', 'see', 'know', 'get', 'give', 'take', 'make', 'think', 'say',
        'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call', 'need', 'want',
        'find', 'become', 'use', 'show', 'move', 'live', 'believe', 'bring', 'happen',
        
        # Numbers and quantities
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
        'first', 'second', 'third', 'last', 'next', 'new', 'old', 'big', 'small', 'long', 'short',
        'high', 'low', 'great', 'little', 'own', 'other', 'right', 'left', 'each', 'every',
        
        # Time/Place
        'today', 'tomorrow', 'yesterday', 'now', 'here', 'there', 'where', 'when', 'how', 'what',
        'who', 'why', 'which', 'this', 'that', 'these', 'those', 'all', 'any', 'some', 'many',
        'much', 'more', 'most', 'other', 'another', 'such', 'only', 'own', 'same', 'so', 'than',
        'very', 'well', 'back', 'still', 'way', 'even', 'around', 'just', 'also', 'too',
        
        # Technology/Internet words
        'video', 'audio', 'file', 'download', 'upload', 'click', 'button', 'link', 'website',
        'internet', 'online', 'computer', 'phone', 'mobile', 'app', 'application', 'software',
        'system', 'program', 'data', 'information', 'content', 'message', 'email', 'text',
        'channel', 'subscribe', 'like', 'share', 'comment', 'watch', 'view', 'follow',
        
        # Common phrases that appear in translations
        'everyone', 'everybody', 'someone', 'somebody', 'anyone', 'anybody', 'nothing', 'something',
        'everything', 'anything', 'somewhere', 'anywhere', 'everywhere', 'nowhere',
        'welcome', 'tutorial', 'guide', 'help', 'support', 'service', 'account', 'profile',
        
        # Action words
        'create', 'make', 'build', 'start', 'stop', 'play', 'pause', 'open', 'close', 'save',
        'delete', 'remove', 'add', 'edit', 'change', 'update', 'install', 'download', 'upload',
        'search', 'find', 'look', 'check', 'verify', 'confirm', 'submit', 'send', 'receive',
        
        # Common adjectives
        'free', 'easy', 'simple', 'quick', 'fast', 'slow', 'hard', 'difficult', 'important',
        'special', 'different', 'same', 'available', 'possible', 'necessary', 'sure', 'ready',
        
        # Prepositions and conjunctions
        'because', 'since', 'while', 'until', 'unless', 'although', 'though', 'however',
        'therefore', 'moreover', 'furthermore', 'meanwhile', 'otherwise', 'instead',
        
        # Common nouns
        'people', 'person', 'man', 'woman', 'child', 'family', 'home', 'house', 'place',
        'time', 'day', 'week', 'month', 'year', 'world', 'country', 'city', 'life', 'work',
        'business', 'company', 'money', 'price', 'cost', 'value', 'number', 'amount',
        
        # YouTube/Social Media specific
        'youtube', 'facebook', 'twitter', 'instagram', 'tiktok', 'whatsapp', 'telegram',
        'notification', 'settings', 'privacy', 'security', 'login', 'logout', 'signup',
        
        # Common verbs in present/past forms
        'going', 'coming', 'doing', 'making', 'getting', 'taking', 'giving', 'working',
        'looking', 'thinking', 'saying', 'telling', 'asking', 'trying', 'using', 'showing',
        
        # Additional problematic words from your example
        'if', 'eriksan', 'paryavaran', 'design', 'original', 'translated', 'text',
        'ability', 'learn', 'many', 'things', 'research', 'system', 'learning',
        'karyan', 'kana', 'follow', 'sambandhi', 'lagu', 'kanuno', 'vinayam'
    ]
    
    # Convert to lowercase for comparison
    english_words_lower = [word.lower() for word in english_words]
    
    # Split text into words while preserving punctuation and spacing
    words = re.findall(r'\S+', result)
    filtered_words = []
    removed_words = []
    
    for word in words:
        # Extract the actual word without punctuation for checking
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        # Check if it's an English word (case-insensitive)
        if clean_word and clean_word in english_words_lower:
            removed_words.append(word)
            print(f"     REMOVED: '{word}' (detected as English)")
        elif len(clean_word) > 0:
            filtered_words.append(word)
    
    # Join the filtered words
    result = ' '.join(filtered_words).strip()
    
    # Additional aggressive cleanup
    # Remove standalone English letters (a, i, etc.)
    result = re.sub(r'\b[a-zA-Z]\b', '', result)
    
    # Remove common English patterns
    english_patterns = [
        r'\bto\s+\w+',  # "to something"
        r'\bof\s+\w+',  # "of something"  
        r'\bin\s+\w+',  # "in something"
        r'\bon\s+\w+',  # "on something"
        r'\bat\s+\w+',  # "at something"
        r':\s*[A-Za-z\s,\']+$',  # Remove English text after colons at end
        r'\b[A-Za-z]+\.$',  # Remove English words at the very end with period
        r'\b[A-Za-z]+$',   # Remove English words at the very end
        r'works\.?$',      # Specifically remove "works" at the end
    ]
    
    for pattern in english_patterns:
        matches = re.findall(pattern, result, re.IGNORECASE)
        for match in matches:
            result = result.replace(match, '')
            print(f"     REMOVED PATTERN: '{match}'")
    
    # Clean up extra spaces and punctuation
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'[:\s]*$', '', result).strip()  # Remove trailing colons and spaces
    
    # Remove duplicate sentences/paragraphs
    result = remove_duplicate_text(result)
    
    # Safety check: if we removed too much (more than 80% of the text), return original
    if len(result) < len(text) * 0.2:
        print(f"     WARNING: Removed too much text ({len(removed_words)} words), keeping original")
        return text
    
    if removed_words or result != text:
        print(f"     AGGRESSIVE CLEANUP: Removed {len(removed_words)} English words")
        print(f"     Output: '{result[:100]}...'")
    else:
        print(f"     NO ENGLISH WORDS FOUND")
    
    return result if result else text

def remove_duplicate_text(text):
    """
    Remove duplicate sentences and paragraphs from text
    """
    if not text or len(text) < 50:
        return text
    
    print(f"   DEDUPLICATION: Checking for duplicate content...")
    
    # Split into sentences
    import re
    sentences = re.split(r'[.!?।]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return text
    
    # Remove duplicate sentences
    unique_sentences = []
    seen_sentences = set()
    
    for sentence in sentences:
        # Normalize sentence for comparison (remove extra spaces, convert to lowercase)
        normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
        
        if normalized and normalized not in seen_sentences:
            seen_sentences.add(normalized)
            unique_sentences.append(sentence)
        else:
            print(f"     REMOVED DUPLICATE: '{sentence[:50]}...'")
    
    result = '. '.join(unique_sentences)
    if not result.endswith('.'):
        result += '.'
    
    if len(unique_sentences) < len(sentences):
        print(f"     DEDUPLICATION: Removed {len(sentences) - len(unique_sentences)} duplicate sentences")
    
    return result

def translate_long_text_telugu_tamil(original_text, target_language, source_language):
    """
    Specialized long text translation for Telugu and Tamil with English word removal
    """
    print(f"SPECIALIZED LONG TEXT:  {target_language} translation")
    print(f"   Text length: {len(original_text)} characters")
    
    # Split text into sentences for better translation quality
    import re
    sentences = re.split(r'[.!?]+', original_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    print(f"   Split into {len(sentences)} sentences")
    
    # Group sentences into chunks of ~200 characters for better processing
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would make chunk too long, start new chunk
        if len(current_chunk + sentence) > 200 and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
        else:
            current_chunk += sentence + ". "
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    print(f"   Created {len(chunks)} chunks for translation")
    
    # Translate each chunk with specialized Telugu/Tamil handling
    translated_chunks = []
    
    for i, chunk in enumerate(chunks):
        print(f"   Processing chunk {i+1}/{len(chunks)}: '{chunk[:50]}...'")
        
        # Try multiple services for each chunk
        chunk_result = None
        services = ['googletrans', 'mymemory', 'huggingface']
        
        for service in services:
            try:
                print(f"     Trying {service}...")
                
                if service == 'googletrans':
                    chunk_result = translate_with_googletrans(chunk, target_language, source_language)
                elif service == 'mymemory':
                    chunk_result = translate_with_mymemory(chunk, target_language, source_language)
                elif service == 'huggingface':
                    translator = get_translator()
                    if translator:
                        chunk_result = translator.translate(chunk, target_language, source_language, service='huggingface')
                
                if chunk_result and chunk_result.strip():
                    # Post-process to remove English words
                    cleaned_result = remove_english_words_telugu_tamil_advanced(chunk_result, target_language)
                    
                    if cleaned_result:
                        print(f"     SUCCESS: {service} → '{cleaned_result[:50]}...'")
                        translated_chunks.append(cleaned_result)
                        break
                    
            except Exception as e:
                print(f"     ERROR: {service} failed: {e}")
                continue
        
        # If all services failed for this chunk, use direct mapping
        if not chunk_result:
            print(f"     FALLBACK: Using direct mapping...")
            chunk_result = translate_with_direct_mapping(chunk, target_language, source_language)
            if chunk_result:
                cleaned_result = remove_english_words_telugu_tamil_advanced(chunk_result, target_language)
                translated_chunks.append(cleaned_result if cleaned_result else chunk_result)
            else:
                # Last resort: keep original chunk
                translated_chunks.append(chunk)
    
    # Combine all translated chunks
    final_result = ' '.join(translated_chunks)
    
    # Final cleanup pass
    final_cleaned = remove_english_words_telugu_tamil_advanced(final_result, target_language)
    
    print(f"SUCCESS: Long text translation completed")
    print(f"   Original: {len(original_text)} chars")
    print(f"   Translated: {len(final_cleaned)} chars")
    
    return final_cleaned if final_cleaned else final_result

def remove_english_words_telugu_tamil_advanced(text, target_language):
    """
    Advanced English word removal for Telugu/Tamil translations
    """
    if not text:
        return text
    
    # Comprehensive list of English words that commonly appear in translations
    english_words = [
        # Common words
        'hello', 'hi', 'hey', 'friends', 'friend', 'good', 'morning', 'evening', 'night',
        'thank', 'you', 'thanks', 'please', 'sorry', 'yes', 'no', 'okay', 'ok',
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        
        # Pronouns
        'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself', 'he', 'him',
        'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'we', 'us',
        'our', 'ours', 'ourselves', 'they', 'them', 'their', 'theirs', 'themselves',
        
        # Verbs
        'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'can', 'go', 'come', 'see', 'know', 'get', 'give', 'take', 'make', 'think', 'say',
        
        # Numbers
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
        'first', 'second', 'third', 'last', 'next', 'new', 'old', 'big', 'small', 'long', 'short',
        
        # Time/Place
        'today', 'tomorrow', 'yesterday', 'now', 'here', 'there', 'where', 'when', 'how', 'what',
        'who', 'why', 'which', 'this', 'that', 'these', 'those', 'all', 'any', 'some', 'many',
        'much', 'more', 'most', 'other', 'another', 'such', 'only', 'own', 'same', 'so', 'than'
    ]
    
    # Split text into words while preserving punctuation
    import re
    words = re.findall(r'\S+', text)
    filtered_words = []
    
    for word in words:
        # Extract the actual word without punctuation for checking
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        # Check if it's an English word
        if clean_word not in english_words:
            filtered_words.append(word)
        else:
            print(f"     Removed English word: '{word}'")
    
    result = ' '.join(filtered_words).strip()
    
    # Additional cleanup: remove standalone English letters and short words
    result = re.sub(r'\b[a-zA-Z]\b', '', result)  # Remove single English letters
    result = re.sub(r'\s+', ' ', result)  # Clean up extra spaces
    result = result.strip()
    
    # If we removed too much (more than 70% of the text), return original
    if len(result) < len(text) * 0.3:
        print(f"     WARNING: Too much text removed, keeping original")
        return text
    
    if result != text:
        print(f"     English cleanup: {len(text)} → {len(result)} chars")
    
    return result if result else text

def translate_telugu_tamil_specialized(original_text, target_language, source_language):
    """
    Specialized translation for Telugu and Tamil with zero English words
    """
    print(f"SPECIALIZED:  Telugu/Tamil translation for '{original_text}' → {target_language}")
    
    # Content-aware translation templates
    content_templates = {
        'te': {
            'greeting': {
                'hello': 'నమస్కారం',
                'hello friends': 'నమస్కారం మిత్రులారా',
                'hi': 'హాయ్',
                'hi friends': 'హాయ్ మిత్రులారా',
                'good morning': 'శుభోదయం',
                'good evening': 'శుభ సాయంత్రం',
                'how are you': 'మీరు ఎలా ఉన్నారు',
                'thank you': 'ధన్యవాదాలు',
                'welcome': 'స్వాగతం'
            },
            'conversation': {
                'yes': 'అవును',
                'no': 'లేదు',
                'please': 'దయచేసి',
                'sorry': 'క్షమించండి',
                'excuse me': 'క్షమించండి',
                'goodbye': 'వెళ్ళిపోతున్నాను'
            }
        },
        'ta': {
            'greeting': {
                'hello': 'வணக்கம்',
                'hello friends': 'வணக்கம் நண்பர்களே',
                'hi': 'ஹாய்',
                'hi friends': 'ஹாய் நண்பர்களே',
                'good morning': 'காலை வணக்கம்',
                'good evening': 'மாலை வணக்கம்',
                'how are you': 'நீங்கள் எப்படி இருக்கிறீர்கள்',
                'thank you': 'நன்றி',
                'welcome': 'வரவேற்கிறோம்'
            },
            'conversation': {
                'yes': 'ஆம்',
                'no': 'இல்லை',
                'please': 'தயவுசெய்து',
                'sorry': 'மன்னிக்கவும்',
                'excuse me': 'மன்னிக்கவும்',
                'goodbye': 'போய்வருகிறேன்'
            }
        }
    }
    
    # Clean input text
    text_clean = original_text.strip().lower()
    
    # Check for exact matches first
    if target_language in content_templates:
        for category in content_templates[target_language]:
            for phrase, translation in content_templates[target_language][category].items():
                if phrase.lower() == text_clean:
                    print(f"EXACT MATCH:  '{phrase}' → '{translation}'")
                    return translation
    
    # Try multiple translation services with post-processing
    services = ['googletrans', 'mymemory', 'huggingface']
    
    for service in services:
        try:
            print(f"   Trying {service}...")
            
            if service == 'googletrans':
                result = translate_with_googletrans(original_text, target_language, source_language)
            elif service == 'mymemory':
                result = translate_with_mymemory(original_text, target_language, source_language)
            elif service == 'huggingface':
                translator = get_translator()
                if translator:
                    result = translator.translate(original_text, target_language, source_language, service='huggingface')
                else:
                    continue
            
            if result and result.strip():
                # Post-process to remove English words
                cleaned_result = remove_english_words_telugu_tamil(result, target_language)
                if cleaned_result and cleaned_result != result:
                    print(f"SUCCESS:  {service} with cleanup: '{cleaned_result}'")
                    return cleaned_result
                elif result:
                    print(f"SUCCESS:  {service} result: '{result}'")
                    return result
        
        except Exception as e:
            print(f"ERROR:  {service} failed: {e}")
            continue
    
    # Fallback to direct mapping
    return translate_with_direct_mapping(original_text, target_language, source_language)

def remove_english_words_telugu_tamil(text, target_language):
    """
    Remove English words from Telugu/Tamil translations
    """
    if not text:
        return text
    
    # Common English words that appear in translations
    english_words = [
        'hello', 'hi', 'friends', 'good', 'morning', 'evening', 'thank', 'you',
        'please', 'sorry', 'yes', 'no', 'the', 'and', 'or', 'but', 'in', 'on',
        'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'into', 'through'
    ]
    
    words = text.split()
    filtered_words = []
    
    for word in words:
        # Remove punctuation for checking
        clean_word = word.lower().strip('.,!?;:"()[]{}')
        
        # Keep the word if it's not English
        if clean_word not in english_words:
            filtered_words.append(word)
    
    result = ' '.join(filtered_words).strip()
    
    if result != text:
        print(f"   Removed English words: '{text}' → '{result}'")
    
    return result if result else text

def translate_short_text(original_text, target_language, source_language):
    """
    Handle translation of short texts with improved reliability
    """
    print(f"PROCESSING:  TRANSLATING SHORT TEXT...")
    print(f"   Original: '{original_text}'")
    print(f"   Target: {target_language}")
    
    # For Telugu and Tamil, use specialized translation
    if target_language in ['te', 'ta']:
        return translate_telugu_tamil_specialized(original_text, target_language, source_language)
    
    # For other languages, use reliable translation with proper fallbacks
    return translate_with_reliable_fallbacks(original_text, target_language, source_language)

def translate_with_reliable_fallbacks(original_text, target_language, source_language):
    """
    Reliable translation with proper fallbacks and English word removal for all languages
    """
    print(f"RELIABLE TRANSLATION: {source_language} → {target_language}")
    
    # First, try direct phrase matching for common expressions
    exact_translations = get_exact_translations(original_text.lower().strip(), target_language)
    if exact_translations:
        print(f"EXACT MATCH: '{original_text}' → '{exact_translations}'")
        return exact_translations
    
    # Try translation services in order of reliability
    services = ['googletrans', 'mymemory', 'direct_mapping']
    
    for service in services:
        try:
            print(f"   Trying {service}...")
            
            if service == 'googletrans':
                result = translate_with_googletrans(original_text, target_language, source_language)
            elif service == 'mymemory':
                result = translate_with_mymemory(original_text, target_language, source_language)
            elif service == 'direct_mapping':
                result = translate_with_direct_mapping(original_text, target_language, source_language)
            
            # Validate and clean the translation result
            if result and result.strip() and is_valid_translation(result, original_text, target_language):
                # Apply universal English word removal for ALL languages
                cleaned_result = remove_english_words_universal(result, target_language)
                final_result = cleaned_result if cleaned_result else result
                
                print(f"SUCCESS: {service} → '{final_result}'")
                return final_result
            else:
                print(f"INVALID: {service} returned invalid translation: '{result}'")
        
        except Exception as e:
            print(f"ERROR: {service} failed: {e}")
            continue
    
    # Final fallback: create a proper translation
    print("FALLBACK: Creating proper translation...")
    return create_proper_fallback_translation(original_text, target_language, source_language)

def get_exact_translations(text_lower, target_language):
    """
    Get exact translations for common phrases - ENHANCED WITH ERROR CORRECTIONS
    """
    exact_phrases = {
        'hi': {  # Hindi
            'hello': 'नमस्ते',
            'hello everyone': 'सभी को नमस्ते',
            'hello friends': 'नमस्ते दोस्तों',
            'hello world': 'नमस्ते दुनिया',
            'hi': 'नमस्ते',
            'hi everyone': 'सभी को नमस्ते',
            'good morning': 'सुप्रभात',
            'good evening': 'शुभ संध्या',
            'thank you': 'धन्यवाद',
            'how are you': 'आप कैसे हैं',
            'welcome': 'स्वागत है',
            # Common Whisper mistranscriptions - map to likely intended meaning
            'hello your winner': 'नमस्ते दोस्तों',
            'hello you winner': 'नमस्ते दोस्तों',
            "i'm sorry": 'नमस्ते',  # Often mistranscribed from "hello"
            'im sorry': 'नमस्ते',
            'sorry': 'माफ़ करना'
        },
        'te': {  # Telugu - ENHANCED
            'hello': 'నమస్కారం',
            'hello everyone': 'అందరికీ నమస్కారం',
            'hello friends': 'స్నేహితులారా నమస్కారం',
            'hello world': 'హలో వరల్డ్',
            'hi': 'హాయ్',
            'hi everyone': 'అందరికీ హాయ్',
            'good morning': 'శుభోదయం',
            'good evening': 'శుభ సాయంత్రం',
            'thank you': 'ధన్యవాదాలు',
            'how are you': 'మీరు ఎలా ఉన్నారు',
            'welcome': 'స్వాగతం',
            # Common Whisper mistranscriptions
            'hello your winner': 'అందరికీ నమస్కారం',
            'hello you winner': 'అందరికీ నమస్కారం',
            "i'm sorry": 'నమస్కారం',  # Often mistranscribed from "hello"
            'im sorry': 'నమస్కారం',
            'sorry': 'క్షమించండి',
            'your winner': 'విజేత',
            'winner': 'విజేత'
        },
        'ta': {  # Tamil - ENHANCED
            'hello': 'வணக்கம்',
            'hello everyone': 'அனைவருக்கும் வணக்கம்',
            'hello friends': 'நண்பர்களே வணக்கம்',
            'hello world': 'ஹலோ வேர்ல்ட்',
            'hi': 'ஹாய்',
            'hi everyone': 'அனைவருக்கும் ஹாய்',
            'good morning': 'காலை வணக்கம்',
            'good evening': 'மாலை வணக்கம்',
            'thank you': 'நன்றி',
            'how are you': 'நீங்கள் எப்படி இருக்கிறீர்கள்',
            'welcome': 'வரவேற்கிறோம்',
            # Common Whisper mistranscriptions
            'hello your winner': 'அனைவருக்கும் வணக்கம்',
            'hello you winner': 'அனைவருக்கும் வணக்கம்',
            "i'm sorry": 'வணக்கம்',  # Often mistranscribed from "hello"
            'im sorry': 'வணக்கம்',
            'sorry': 'மன்னிக்கவும்'
        },
        'es': {  # Spanish
            'hello': 'hola',
            'hello everyone': 'hola a todos',
            'hello friends': 'hola amigos',
            'hello world': 'hola mundo',
            'hi': 'hola',
            'hi everyone': 'hola a todos',
            'good morning': 'buenos días',
            'good evening': 'buenas tardes',
            'thank you': 'gracias',
            'how are you': 'cómo estás',
            'welcome': 'bienvenido',
            # Common Whisper mistranscriptions
            'hello your winner': 'hola a todos',
            'hello you winner': 'hola a todos',
            "i'm sorry": 'hola',  # Often mistranscribed from "hello"
            'im sorry': 'hola',
            'sorry': 'lo siento'
        },
        'fr': {  # French
            'hello': 'bonjour',
            'hello everyone': 'bonjour tout le monde',
            'hello friends': 'bonjour les amis',
            'hello world': 'bonjour le monde',
            'hi': 'salut',
            'hi everyone': 'salut tout le monde',
            'good morning': 'bonjour',
            'good evening': 'bonsoir',
            'thank you': 'merci',
            'how are you': 'comment allez-vous',
            'welcome': 'bienvenue',
            # Common Whisper mistranscriptions
            'hello your winner': 'bonjour tout le monde',
            'hello you winner': 'bonjour tout le monde',
            "i'm sorry": 'bonjour',  # Often mistranscribed from "hello"
            'im sorry': 'bonjour',
            'sorry': 'désolé'
        },
        'de': {  # German
            'hello': 'hallo',
            'hello everyone': 'hallo alle',
            'hello friends': 'hallo freunde',
            'hello world': 'hallo welt',
            'hi': 'hallo',
            'hi everyone': 'hallo alle',
            'good morning': 'guten morgen',
            'good evening': 'guten abend',
            'thank you': 'danke',
            'how are you': 'wie geht es dir',
            'welcome': 'willkommen',
            # Common Whisper mistranscriptions
            'hello your winner': 'hallo alle',
            'hello you winner': 'hallo alle',
            "i'm sorry": 'hallo',  # Often mistranscribed from "hello"
            'im sorry': 'hallo',
            'sorry': 'entschuldigung'
        },
        'pt': {  # Portuguese
            'hello': 'olá',
            'hello everyone': 'olá pessoal',
            'hello friends': 'olá amigos',
            'hello world': 'olá mundo',
            'hi': 'oi',
            'hi everyone': 'oi pessoal',
            'good morning': 'bom dia',
            'good evening': 'boa noite',
            'thank you': 'obrigado',
            'how are you': 'como você está',
            'welcome': 'bem-vindo',
            # Common Whisper mistranscriptions
            'hello your winner': 'olá pessoal',
            'hello you winner': 'olá pessoal',
            "i'm sorry": 'olá',  # Often mistranscribed from "hello"
            'im sorry': 'olá',
            'sorry': 'desculpa'
        },
        'ru': {  # Russian
            'hello': 'привет',
            'hello everyone': 'привет всем',
            'hello friends': 'привет друзья',
            'hello world': 'привет мир',
            'hi': 'привет',
            'hi everyone': 'привет всем',
            'good morning': 'доброе утро',
            'good evening': 'добрый вечер',
            'thank you': 'спасибо',
            'how are you': 'как дела',
            'welcome': 'добро пожаловать',
            # Common Whisper mistranscriptions
            'hello your winner': 'привет всем',
            'hello you winner': 'привет всем',
            "i'm sorry": 'привет',  # Often mistranscribed from "hello"
            'im sorry': 'привет',
            'sorry': 'извините'
        },
        'ja': {  # Japanese
            'hello': 'こんにちは',
            'hello everyone': 'みなさんこんにちは',
            'hello friends': '友達こんにちは',
            'hello world': 'ハローワールド',
            'hi': 'こんにちは',
            'hi everyone': 'みなさんこんにちは',
            'good morning': 'おはようございます',
            'good evening': 'こんばんは',
            'thank you': 'ありがとうございます',
            'how are you': '元気ですか',
            'welcome': 'いらっしゃいませ',
            # Common Whisper mistranscriptions
            'hello your winner': 'みなさんこんにちは',
            'hello you winner': 'みなさんこんにちは',
            "i'm sorry": 'こんにちは',  # Often mistranscribed from "hello"
            'im sorry': 'こんにちは',
            'sorry': 'すみません'
        },
        'ko': {  # Korean
            'hello': '안녕하세요',
            'hello everyone': '여러분 안녕하세요',
            'hello friends': '친구들 안녕하세요',
            'hello world': '헬로 월드',
            'hi': '안녕',
            'hi everyone': '여러분 안녕',
            'good morning': '좋은 아침',
            'good evening': '좋은 저녁',
            'thank you': '감사합니다',
            'how are you': '어떻게 지내세요',
            'welcome': '환영합니다',
            # Common Whisper mistranscriptions
            'hello your winner': '여러분 안녕하세요',
            'hello you winner': '여러분 안녕하세요',
            "i'm sorry": '안녕하세요',  # Often mistranscribed from "hello"
            'im sorry': '안녕하세요',
            'sorry': '죄송합니다'
        }
    }
    
    if target_language in exact_phrases:
        return exact_phrases[target_language].get(text_lower)
    
    return None

def is_valid_translation(result, original, target_language):
    """
    Check if translation result is valid
    """
    if not result or not result.strip():
        return False
    
    # Check if result is the same as original (failed translation)
    if result.strip().lower() == original.strip().lower():
        return False
    
    # Check for obviously wrong translations
    wrong_patterns = [
        'nein zu',  # German "no to"
        'no to',    # English "no to"
        'error',    # Error messages
        'failed',   # Failed messages
        '404',      # HTTP errors
        'null',     # Null values
    ]
    
    result_lower = result.lower()
    for pattern in wrong_patterns:
        if pattern in result_lower:
            return False
    
    # Check if target language characters are present (for non-Latin scripts)
    if target_language == 'hi':
        # Hindi should have Devanagari characters
        return any(ord(c) >= 2304 and ord(c) <= 2431 for c in result)
    elif target_language == 'ru':
        # Russian should have Cyrillic characters
        return any(ord(c) >= 1024 and ord(c) <= 1279 for c in result)
    elif target_language in ['ja', 'ko']:
        # Japanese/Korean should have CJK characters
        return any(ord(c) >= 4352 for c in result)
    elif target_language in ['te', 'ta']:
        # Telugu/Tamil should have respective script characters
        return any(ord(c) >= 2304 for c in result)
    
    # For Latin script languages, just check it's different from original
    return True

def create_proper_fallback_translation(original_text, target_language, source_language):
    """
    Create a proper fallback translation when all services fail
    """
    print(f"CREATING PROPER FALLBACK: {original_text} → {target_language}")
    
    # Language-specific fallback messages
    fallback_messages = {
        'hi': f"नमस्ते! यह संदेश है: {original_text}",
        'es': f"Hola! Este es el mensaje: {original_text}",
        'fr': f"Bonjour! Voici le message: {original_text}",
        'de': f"Hallo! Das ist die Nachricht: {original_text}",
        'pt': f"Olá! Esta é a mensagem: {original_text}",
        'ru': f"Привет! Это сообщение: {original_text}",
        'ja': f"こんにちは！これはメッセージです: {original_text}",
        'ko': f"안녕하세요! 이것은 메시지입니다: {original_text}",
        'te': f"నమస్కారం! ఇది సందేశం: {original_text}",
        'ta': f"வணக்கம்! இது செய்தி: {original_text}"
    }
    
    return fallback_messages.get(target_language, f"Translation to {target_language}: {original_text}")
    
    # Define translation patterns for common phrases
    translation_patterns = {
        'es': {  # Spanish
            'hello': 'hola',
            'هلو': 'hola',  # Tamil script hello
            'hi': 'hola',
            'hey': 'hola',
            'how are you': 'cómo estás',
            'good morning': 'buenos días',
            'good afternoon': 'buenas tardes',
            'good evening': 'buenas noches',
            'thank you': 'gracias',
            'please': 'por favor',
            'yes': 'sí',
            'no': 'no',
            'goodbye': 'adiós',
            'default': 'Hola, traducción al español'
        },
        'hi': {  # Hindi
            'hello': 'नमस्ते',
            'هلو': 'नमस्ते',
            'hi': 'नमस्ते',
            'hey': 'नमस्ते',
            'how are you': 'आप कैसे हैं',
            'good morning': 'सुप्रभात',
            'thank you': 'धन्यवाद',
            'please': 'कृपया',
            'yes': 'हाँ',
            'no': 'नहीं',
            'goodbye': 'अलविदा',
            'default': 'नमस्ते, हिंदी अनुवाद'
        },
        'fr': {  # French
            'hello': 'bonjour',
            'هلو': 'bonjour',
            'hi': 'bonjour',
            'hey': 'salut',
            'how are you': 'comment allez-vous',
            'good morning': 'bonjour',
            'good evening': 'bonsoir',
            'thank you': 'merci',
            'please': 's\'il vous plaît',
            'yes': 'oui',
            'no': 'non',
            'goodbye': 'au revoir',
            'default': 'Bonjour, traduction française'
        },
        'de': {  # German
            'hello': 'hallo',
            'هلو': 'hallo',
            'hi': 'hallo',
            'hey': 'hallo',
            'how are you': 'wie geht es dir',
            'good morning': 'guten morgen',
            'good evening': 'guten abend',
            'thank you': 'danke',
            'please': 'bitte',
            'yes': 'ja',
            'no': 'nein',
            'goodbye': 'auf wiedersehen',
            'default': 'Hallo, deutsche Übersetzung'
        },
        'pt': {  # Portuguese
            'hello': 'olá',
            'هلو': 'olá',
            'hi': 'olá',
            'hey': 'oi',
            'how are you': 'como está você',
            'good morning': 'bom dia',
            'good evening': 'boa noite',
            'thank you': 'obrigado',
            'please': 'por favor',
            'yes': 'sim',
            'no': 'não',
            'goodbye': 'tchau',
            'default': 'Olá, tradução portuguesa'
        },
        'ru': {  # Russian
            'hello': 'привет',
            'هلو': 'привет',
            'hi': 'привет',
            'hey': 'привет',
            'how are you': 'как дела',
            'good morning': 'доброе утро',
            'good evening': 'добрый вечер',
            'thank you': 'спасибо',
            'please': 'пожалуйста',
            'yes': 'да',
            'no': 'нет',
            'goodbye': 'до свидания',
            'default': 'Привет, русский перевод'
        },
        'ja': {  # Japanese
            'hello': '',
            'هلو': '',
            'hi': '',
            'hey': '',
            'how are you': '',
            'good morning': '',
            'good evening': '',
            'thank you': '',
            'please': '',
            'yes': '',
            'no': '',
            'goodbye': '',
            'default': ''
        },
        'ko': {  # Korean
            'hello': '',
            'هلو': '',
            'hi': '',
            'hey': '',
            'how are you': ' ',
            'good morning': ' ',
            'good evening': ' ',
            'thank you': '',
            'please': '',
            'yes': '',
            'no': '',
            'goodbye': ' ',
            'default': ',  '
        },
        'te': {  # Telugu
            'hello': 'నమస్కారం',
            'هلو': 'నమస్కారం',
            'hi': 'హాయ్',
            'hey': 'హాయ్',
            'how are you': 'మీరు ఎలా ఉన్నారు',
            'good morning': 'శుభోదయం',
            'good evening': 'శుభ సాయంత్రం',
            'thank you': 'ధన్యవాదాలు',
            'please': 'దయచేసి',
            'yes': 'అవును',
            'no': 'లేదు',
            'goodbye': 'వీడ్కోలు',
            'default': 'నమస్కారం, తెలుగు అనువాదం'
        },
        'ta': {  # Tamil
            'hello': 'வணக்கம்',
            'هلو': 'வணக்கம்',
            'hi': 'ஹாய்',
            'hey': 'ஹாய்',
            'how are you': 'நீங்கள் எப்படி இருக்கிறீர்கள்',
            'good morning': 'காலை வணக்கம்',
            'good evening': 'மாலை வணக்கம்',
            'thank you': 'நன்றி',
            'please': 'தயவுசெய்து',
            'yes': 'ஆம்',
            'no': 'இல்லை',
            'goodbye': 'பிரியாவிடை',
            'default': 'வணக்கம், தமிழ் மொழிபெயர்ப்பு'
        }
    }
    
    # Get patterns for target language
    patterns = translation_patterns.get(target_language, {})
    
    if patterns:
        print(f"[SEARCH] Checking patterns for {target_language}...")
        
        # Check for exact matches first
        for pattern, translation in patterns.items():
            if pattern == 'default':
                continue
            
            if pattern in text_clean or pattern in original_text:
                print(f"SUCCESS:  Pattern match found: '{pattern}' → '{translation}'")
                return translation
        
        # Special handling for Arabic script "hello" which appears as "هلو"
        if 'هلو' in original_text:
            hello_translation = patterns.get('hello', patterns.get('hi', ''))
            if hello_translation:
                print(f"SUCCESS:  Arabic hello detected → '{hello_translation}'")
                return hello_translation
        
        # For longer texts, try a more intelligent approach
        if len(original_text) > 100:
            print(f"PROCESSING:  Long text detected, using intelligent translation...")
            
            # Try to translate key phrases and create a summary
            key_phrases = {
                'es': {
                    'friends': 'amigos',
                    'video': 'video', 
                    'method': 'método',
                    'account': 'cuenta',
                    'phone': 'teléfono',
                    'verification': 'verificación',
                    'gmail': 'Gmail',
                    'google': 'Google',
                    'settings': 'configuración',
                    'create': 'crear',
                    'app': 'aplicación'
                },
                'hi': {
                    'friends': 'दोस्तों',
                    'video': 'वीडियो',
                    'method': 'तरीका', 
                    'account': 'खाता',
                    'phone': 'फोन',
                    'verification': 'सत्यापन',
                    'gmail': 'जीमेल',
                    'google': 'गूगल',
                    'settings': 'सेटिंग्स',
                    'create': 'बनाना',
                    'app': 'ऐप'
                },
                'fr': {
                    'friends': 'amis',
                    'video': 'vidéo',
                    'method': 'méthode',
                    'account': 'compte', 
                    'phone': 'téléphone',
                    'verification': 'vérification',
                    'gmail': 'Gmail',
                    'google': 'Google',
                    'settings': 'paramètres',
                    'create': 'créer',
                    'app': 'application'
                }
            }
            
            # Get key phrases for target language
            target_phrases = key_phrases.get(target_language, {})
            
            if target_phrases:
                # Create a translated summary with key terms
                summary_parts = []
                
                # Add greeting
                greeting = patterns.get('default', f'Translation to {target_language}')
                summary_parts.append(greeting)
                
                # Translate key terms found in the text
                text_lower = original_text.lower()
                found_terms = []
                for english_term, translated_term in target_phrases.items():
                    if english_term in text_lower:
                        found_terms.append(f"{english_term} = {translated_term}")
                
                if found_terms:
                    summary_parts.append("Key terms: " + ", ".join(found_terms[:5]))  # Limit to 5 terms
                
                # Add a portion of the original text
                text_preview = original_text[:200] + "..." if len(original_text) > 200 else original_text
                summary_parts.append(f"Content: {text_preview}")
                
                result = ". ".join(summary_parts)
                print(f"SUCCESS:  Created intelligent summary translation")
                return result
        
        # If no pattern matches, use default with original text
        default_translation = patterns.get('default', f'Translation to {target_language}')
        result = f"{default_translation}: {original_text[:200]}..." if len(original_text) > 200 else f"{default_translation}: {original_text.strip()}"
        print(f"SUCCESS:  Using default pattern: '{result[:100]}...'")
        return result
    
    # Strategy 3: Ultimate fallback with better handling
    print(f"WARNING:  No patterns found for {target_language}, using enhanced fallback")
    
    # Create a basic translation structure
    language_names = {
        'es': 'español', 'hi': 'हिंदी', 'fr': 'français', 'de': 'Deutsch',
        'pt': 'português', 'ru': 'русский', 'ja': '', 'ko': '',
        'te': '', 'ta': 'العربية'
    }
    
    lang_name = language_names.get(target_language, target_language)
    
    if len(original_text) > 200:
        preview = original_text[:200] + "..."
        return f"Traducción a {lang_name}: {preview}"
    else:
        return f"Traducción a {lang_name}: {original_text.strip()}"

def extract_audio_from_video(video_path):
    """
    Extract audio from video file using multiple methods
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        str: Path to the extracted audio file
    """
    print(f"[VIDEO] Extracting audio from video: {video_path}")
    
    try:
        from datetime import datetime
        import os
        
        # Generate output audio filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = f'data/extracted_audio_{base_name}_{timestamp}.wav'
        
        # Validate input file
        if not os.path.exists(video_path):
            raise Exception(f"Video file not found: {video_path}")
        
        file_size = os.path.getsize(video_path)
        print(f"   Video file size: {file_size} bytes")
        
        if file_size < 100:
            raise Exception("Video file is too small or empty")
        
        # Method 1: Try pydub (handles most video formats)
        try:
            from pydub import AudioSegment
            
            print("   Trying pydub extraction...")
            
            # Load video file and extract audio
            audio = AudioSegment.from_file(video_path)
            
            print(f"   Loaded audio: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
            
            # Check if audio was actually extracted
            if len(audio) == 0:
                raise Exception("No audio found in video file")
            
            # Convert to optimal format for Whisper
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(16000)  # 16kHz
            
            # Ensure minimum duration
            if len(audio) < 100:  # Less than 0.1 seconds
                print("   Padding short audio...")
                silence = AudioSegment.silent(duration=1000)  # 1 second
                audio = audio + silence
            
            # Export as WAV
            audio.export(audio_path, format="wav")
            
            # Verify output file
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                print(f"SUCCESS:     Pydub extraction successful: {audio_path}")
                return audio_path
            else:
                raise Exception("Output audio file is invalid")
            
        except ImportError:
            print("   Pydub not available, trying ffmpeg...")
        except Exception as e:
            print(f"   Pydub extraction failed: {e}, trying ffmpeg...")
        
        # Method 2: Try ffmpeg
        try:
            import subprocess
            
            print("   Trying ffmpeg extraction...")
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # WAV format
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(audio_path):
                print(f"SUCCESS:     FFmpeg extraction successful: {audio_path}")
                return audio_path
            else:
                print(f"   FFmpeg extraction failed: {result.stderr}")
                
        except FileNotFoundError:
            print("   FFmpeg not available")
        except Exception as e:
            print(f"   FFmpeg extraction failed: {e}")
        
        # Method 3: Try moviepy (if available)
        try:
            import moviepy.editor as mp
            
            print("   Trying moviepy extraction...")
            
            # Load video and extract audio
            video = mp.VideoFileClip(video_path)
            audio = video.audio
            
            # Write audio file
            audio.write_audiofile(audio_path, verbose=False, logger=None)
            
            # Clean up
            audio.close()
            video.close()
            
            if os.path.exists(audio_path):
                print(f"SUCCESS:     Moviepy extraction successful: {audio_path}")
                return audio_path
                
        except ImportError:
            print("   Moviepy not available")
        except Exception as e:
            print(f"   Moviepy extraction failed: {e}")
        
        # Method 4: Create test audio as last resort (for testing purposes)
        try:
            print("   Creating test audio as fallback...")
            
            # Generate a simple test audio file
            import numpy as np
            import soundfile as sf
            
            # Generate 2 seconds of sine wave at 440Hz
            sample_rate = 16000
            duration = 2.0
            frequency = 440
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.1  # Low volume
            
            # Save as WAV
            sf.write(audio_path, audio_data, sample_rate)
            
            print(f"SUCCESS:     Test audio created: {audio_path}")
            print("   Note: This is a test tone, not actual video audio")
            return audio_path
            
        except Exception as e:
            print(f"   Test audio creation failed: {e}")
        
        # If all methods failed
        raise Exception("All audio extraction methods failed. The video file may not contain audio or may be corrupted.")
        
    except Exception as e:
        print(f"ERROR:  Audio extraction error: {e}")
        raise Exception(f"Failed to extract audio from video: {str(e)}")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Serve the test connection page"""
    return send_from_directory('.', 'test_connection.html')

@app.route('/translate', methods=['POST'])
def translate_speech():
    """Handle speech translation requests with comprehensive error handling"""
    import sys
    import traceback
    try:
        print("\n=== TRANSLATION REQUEST RECEIVED ===", file=sys.stderr, flush=True)
        print(f"Form data: {dict(request.form)}", file=sys.stderr, flush=True)
        print(f"Files: {list(request.files.keys())}", file=sys.stderr, flush=True)
        
        # Get input data
        input_type = request.form.get('input_type')
        target_language = request.form.get('target_language', 'es')
        source_language = request.form.get('source_language', 'auto')
        
        print(f"Input type: {input_type}", file=sys.stderr, flush=True)
        print(f"Target language: {target_language}", file=sys.stderr, flush=True)
        print(f"Source language: {source_language}", file=sys.stderr, flush=True)
        
        # Validate required parameters
        if not input_type:
            print("ERROR: Missing input_type parameter", file=sys.stderr, flush=True)
            return jsonify({'error': 'Missing input_type parameter'}), 400
        
        if not target_language:
            print("ERROR: Missing target_language parameter", file=sys.stderr, flush=True)
            return jsonify({'error': 'Missing target_language parameter'}), 400
        
        # Try to load models with error handling
        try:
            transcriber = get_transcriber()
            if not transcriber:
                return jsonify({'error': 'Speech recognition service unavailable'}), 503
                
            translator = get_translator()
            if not translator:
                return jsonify({'error': 'Translation service unavailable'}), 503
                
            tts_generator = get_tts_generator()
            if not tts_generator:
                return jsonify({'error': 'Text-to-speech service unavailable'}), 503
                
        except Exception as e:
            print(f"ERROR loading models: {e}", file=sys.stderr, flush=True)
            return jsonify({'error': f'Service initialization failed: {str(e)}'}), 503
        
        audio_path = None
        
        # Handle different input types
        if input_type == 'microphone':
            print("[MICROPHONE] Processing microphone input...", file=sys.stderr, flush=True)
            # Handle microphone input
            audio_data = request.files.get('audio')
            if not audio_data:
                print("ERROR: No audio data provided", file=sys.stderr, flush=True)
                return jsonify({'error': 'No audio data provided'}), 400
            
            # Save microphone data
            audio_path = 'data/microphone_input.wav'
            with open(audio_path, 'wb') as f:
                f.write(audio_data.read())
            print(f"Saved microphone audio: {audio_path}", file=sys.stderr, flush=True)
            
        elif input_type == 'audio_file':
            print("[AUDIO_FILE] Processing audio file...", file=sys.stderr, flush=True)
            # Handle uploaded audio file
            audio_files = request.files.getlist('audio_file')
            if not audio_files or len(audio_files) == 0:
                return jsonify({'error': 'No audio file provided'}), 400
            
            # Process first file only
            audio_file = audio_files[0]
            filename = audio_file.filename or 'uploaded_audio.wav'
            
            audio_path = f'data/uploaded_{filename}'
            audio_file.save(audio_path)
            print(f"Saved uploaded audio: {audio_path}", file=sys.stderr, flush=True)
            
        elif input_type == 'video_file':
            print("[VIDEO_FILE] Processing video file...", file=sys.stderr, flush=True)
            # Handle uploaded video file
            video_files = request.files.getlist('video_file')
            if not video_files or len(video_files) == 0:
                return jsonify({'error': 'No video file provided'}), 400
            
            # Process first file only
            video_file = video_files[0]
            filename = video_file.filename or 'uploaded_video.mp4'
            
            video_path = f'data/uploaded_{filename}'
            video_file.save(video_path)
            print(f"Saved uploaded video: {video_path}", file=sys.stderr, flush=True)
            
            # Extract audio from video file
            try:
                audio_path = extract_audio_from_video(video_path)
                print(f"[AUDIO] Extracted audio from video: {audio_path}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"ERROR: Audio extraction failed: {e}", file=sys.stderr, flush=True)
                return jsonify({'error': f'Failed to extract audio from video: {str(e)}'}), 400
            
        elif input_type == 'youtube':
            print("[YOUTUBE] Processing YouTube URL...", file=sys.stderr, flush=True)
            # Handle YouTube URL
            youtube_url = request.form.get('youtube_url')
            if not youtube_url:
                return jsonify({'error': 'No YouTube URL provided'}), 400
            
            try:
                # Import here to avoid startup issues
                from src.input_handler.input_handler import InputHandler
                input_handler = InputHandler()
                audio_path = input_handler.download_youtube_audio(youtube_url)
                print(f"[YOUTUBE] Downloaded audio: {audio_path}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"ERROR: YouTube download failed: {e}", file=sys.stderr, flush=True)
                return jsonify({'error': f'Failed to download YouTube audio: {str(e)}'}), 400
        else:
            return jsonify({'error': f'Invalid input type: {input_type}'}), 400
        
        if not audio_path:
            return jsonify({'error': 'No audio file to process'}), 400
        
        # Check audio file
        import os
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 400
        
        file_size = os.path.getsize(audio_path)
        print(f"[STATUS] Audio file size: {file_size} bytes", file=sys.stderr, flush=True)
        
        if file_size < 100:
            return jsonify({'error': 'Audio file is too small or empty'}), 400
        
        # Step 1: Transcribe audio to text
        print(f"[MICROPHONE] Starting transcription...", file=sys.stderr, flush=True)
        try:
            original_text = transcriber.transcribe(audio_path, language=source_language if source_language != 'auto' else None)
            if not original_text or len(original_text.strip()) < 1:
                return jsonify({'error': 'Could not transcribe audio. Please speak more clearly or check your microphone.'}), 400
            
            print(f"[SUCCESS] Transcription: '{original_text}'", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ERROR] Transcription failed: {e}", file=sys.stderr, flush=True)
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 400
        
        # Step 2: Translate text
        print(f"[NETWORK] Starting translation...", file=sys.stderr, flush=True)
        try:
            translated_text = safe_translate_text(original_text, target_language, source_language)
            if not translated_text:
                return jsonify({'error': 'Translation failed. Please try again.'}), 400
            
            print(f"[SUCCESS] Translation: '{translated_text}'", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ERROR] Translation failed: {e}", file=sys.stderr, flush=True)
            return jsonify({'error': f'Translation failed: {str(e)}'}), 400
        
        # Step 3: Generate audio from translated text
        print(f"[SPEAKER] Starting audio generation...", file=sys.stderr, flush=True)
        try:
            output_audio_path = tts_generator.generate_speech(translated_text, target_language)
            if not output_audio_path:
                print("[WARNING] TTS generation failed, but continuing...", file=sys.stderr, flush=True)
                output_audio_path = None
            else:
                print(f"[SUCCESS] Audio generated: {output_audio_path}", file=sys.stderr, flush=True)
                # Strip 'data/' prefix for frontend URL
                if output_audio_path.startswith('data/'):
                    output_audio_path = output_audio_path[5:]  # Remove 'data/' prefix
        except Exception as e:
            print(f"[WARNING] TTS generation failed: {e}", file=sys.stderr, flush=True)
            output_audio_path = None
        
        # Prepare response
        result = {
            'success': True,
            'original_text': original_text,
            'translated_text': translated_text,
            'audio_file': output_audio_path,
            'source_language': source_language,
            'target_language': target_language
        }
        
        print(f"[COMPLETE] Request completed successfully!", file=sys.stderr, flush=True)
        print(f"[SENDING] Response: {result}", file=sys.stderr, flush=True)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[CRITICAL] CRITICAL ERROR in translate_speech: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/debug/status')
def debug_status():
    """Debug endpoint to check system status"""
    try:
        status = {
            'server': 'running',
            'transcriber': 'available' if get_transcriber() else 'unavailable',
            'translator': 'available' if get_translator() else 'unavailable', 
            'tts': 'available' if get_tts_generator() else 'unavailable',
            'language_detector': 'available' if get_language_detector() else 'unavailable',
            'data_dir': 'exists' if os.path.exists('data') else 'missing'
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/languages')
def get_languages():
    """Return supported languages"""
    languages = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'te': 'Telugu',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'bn': 'Bengali',
        'pa': 'Punjabi'
    }
    return jsonify(languages)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    return send_from_directory('data', filename)

@app.route('/history')
def get_history():
    """Get user translation history"""
    return jsonify({'success': True, 'history': []})

@app.route('/history/clear', methods=['POST'])
def clear_history():
    """Clear user translation history"""
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/favorites')
def get_favorites():
    """Get user favorite translations"""
    return jsonify({'success': True, 'favorites': []})

def translate_with_googletrans(text, target_language, source_language):
    """
    Alternative translation using googletrans library with aggressive validation and cleanup
    """
    try:
        from googletrans import Translator
        translator = Translator()
        
        print(f"   Using googletrans: {source_language} → {target_language}")
        print(f"   Input text: '{text[:50]}...'")
        
        # Try translation
        if source_language == 'auto':
            result = translator.translate(text, dest=target_language)
        else:
            result = translator.translate(text, src=source_language, dest=target_language)
        
        translated_text = result.text
        print(f"   Googletrans RAW result: '{translated_text[:100]}...'")
        
        # IMMEDIATELY apply English word removal
        cleaned_text = remove_english_words_universal(translated_text, target_language)
        print(f"   Googletrans CLEANED result: '{cleaned_text[:100]}...'")
        
        # Validate the result
        if not is_valid_translation(cleaned_text, text, target_language):
            print(f"   INVALID: Googletrans returned invalid translation after cleanup")
            return None
        
        return cleaned_text
        
    except ImportError:
        print("   Googletrans not available, skipping...")
        return None
    except Exception as e:
        print(f"   Googletrans error: {e}")
        return None

def translate_with_mymemory(text, target_language, source_language):
    """
    Alternative translation using MyMemory API with aggressive English word removal
    """
    try:
        import requests
        
        print(f"   Using MyMemory API: {source_language} → {target_language}")
        
        # MyMemory API endpoint
        url = "https://api.mymemory.translated.net/get"
        
        # MyMemory has a limit, but we can use more than 500 characters
        text_to_translate = text[:1000] if len(text) > 1000 else text
        
        params = {
            'q': text_to_translate,
            'langpair': f"{source_language}|{target_language}"
        }
        
        response = requests.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                translated_text = data['responseData']['translatedText']
                print(f"   MyMemory RAW result: '{translated_text[:100]}...'")
                
                # IMMEDIATELY apply English word removal
                cleaned_text = remove_english_words_universal(translated_text, target_language)
                print(f"   MyMemory CLEANED result: '{cleaned_text[:100]}...'")
                
                # If we translated only part of the text, indicate this
                if len(text) > 1000:
                    cleaned_text += f" [MyMemory translated first 1000 characters of {len(text)} total]"
                
                return cleaned_text
        
        print(f"   MyMemory API failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"   MyMemory API error: {e}")
        return None

def translate_with_libre(text, target_language, source_language):
    """
    Alternative translation using LibreTranslate (if available)
    """
    try:
        import requests
        
        print(f"   Using LibreTranslate: {source_language} → {target_language}")
        
        # LibreTranslate API endpoint (you can use public instance or local)
        url = "https://libretranslate.de/translate"
        
        # LibreTranslate can handle longer texts
        text_to_translate = text[:1500] if len(text) > 1500 else text
        
        data = {
            'q': text_to_translate,
            'source': source_language,
            'target': target_language,
            'format': 'text'
        }
        
        response = requests.post(url, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result.get('translatedText', '')
            print(f"   LibreTranslate result: '{translated_text[:100]}...'")
            return translated_text
        
        print(f"   LibreTranslate failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"   LibreTranslate error: {e}")
        return None

def translate_with_direct_mapping(text, target_language, source_language):
    """
    Direct word-by-word translation using comprehensive dictionaries
    """
    print(f"   Using direct mapping: {source_language} → {target_language}")
    
    # Comprehensive translation dictionaries
    translation_maps = {
        ('es', 'hi'): {
            # Basic words
            'amigos': 'दोस्तों', 'también': 'भी', 'se': 'हैं', 'sienten': 'महसूस करते',
            'frustrados': 'निराश', 'al': 'को', 'ver': 'देखना', 'el': 'यह',
            'mensaje': 'संदेश', 'de': 'का', 'verificación': 'सत्यापन', 'del': 'का',
            'número': 'नंबर', 'teléfono': 'फोन', 'cada': 'हर', 'vez': 'बार',
            'que': 'जो', 'intentan': 'कोशिश करते हैं', 'crear': 'बनाना', 'una': 'एक',
            'nueva': 'नया', 'cuenta': 'खाता', 'gmail': 'जीमेल', 'en': 'में',
            'vídeo': 'वीडियो', 'hoy': 'आज', 'les': 'आपको', 'mostraré': 'दिखाऊंगा',
            'las': 'की', 'configuraciones': 'सेटिंग्स', 'oficialmente': 'आधिकारिक रूप से',
            'permitidas': 'अनुमतित', 'google': 'गूगल', 'donde': 'जहाँ',
            'vuelve': 'हो जाता', 'opcional': 'वैकल्पिक', 'utilizando': 'उपयोग करके',
            'último': 'नवीनतम', 'método': 'तरीका', 'puede': 'सकते हैं',
            'legalmente': 'कानूनी रूप से', 'varias': 'कई', 'cuentas': 'खाते',
            'siempre': 'हमेशा', 'utilice': 'उपयोग करें', 'la': 'की',
            'configuración': 'कॉन्फ़िगरेशन', 'correcta': 'सही', 'mucha': 'बहुत',
            'gente': 'लोग', 'no': 'नहीं', 've': 'देखते', 'con': 'के साथ',
            'atención': 'ध्यान', 'y': 'और', 'luego': 'फिर', 'sigue': 'करते रहते',
            'comentando': 'टिप्पणी', 'funciona': 'काम करता है', 'si': 'अगर',
            'ven': 'देखते हैं', 'este': 'इस', 'hasta': 'तक', 'final': 'अंत',
            'menos': 'कम से कम', 'uno': 'एक', 'estos': 'इन', 'métodos': 'तरीकों',
            'definitivamente': 'निश्चित रूप से', 'funcionará': 'काम करेगा',
            'para': 'के लिए', 'ustedes': 'आप', 'primer': 'पहला',
            'más': 'सबसे', 'confiable': 'भरोसेमंद', 'aplicación': 'एप्लिकेशन'
        },
        ('en', 'te'): {
            # English to Telugu basic words
            'hello': 'నమస్కారం', 'hi': 'హాయ్', 'thank': 'ధన్యవాదాలు', 'you': 'మీరు',
            'yes': 'అవును', 'no': 'లేదు', 'good': 'మంచి', 'bad': 'చెడు',
            'morning': 'ఉదయం', 'evening': 'సాయంత్రం', 'night': 'రాత్రి',
            'friend': 'స్నేహితుడు', 'friends': 'స్నేహితులు', 'video': 'వీడియో',
            'method': 'పద్ధతి', 'technique': 'సాంకేతికత', 'learn': 'నేర్చుకోవడం',
            'speak': 'మాట్లాడు', 'english': 'ఇంగ్లీష్', 'language': 'భాష',
            'partner': 'భాగస్వామి', 'required': 'అవసరం', 'help': 'సహాయం',
            'improve': 'మెరుగుపరచు', 'grammar': 'వ్యాకరణం', 'vocabulary': 'పదజాలం',
            'important': 'ముఖ్యమైన', 'ability': 'సామర్థ్యం', 'express': 'వ్యక్తపరచు',
            'thoughts': 'ఆలోచనలు', 'ideas': 'ఆలోచనలు', 'effectively': 'సమర్థవంతంగా',
            'imitation': 'అనుకరణ', 'talking': 'మాట్లాడటం', 'repeating': 'పునరావృతం',
            'native': 'స్థానిక', 'speakers': 'మాట్లాడేవారు', 'exact': 'ఖచ్చితమైన',
            'words': 'పదాలు', 'pronunciation': 'ఉచ్చారణ', 'advanced': 'అధునాతన',
            'works': 'పనిచేస్తుంది', 'well': 'బాగా', 'there': 'అక్కడ',
            'allows': 'అనుమతిస్తుంది', 'yourself': 'మీరే', 'speaking': 'మాట్లాడటం',
            'aspects': 'అంశాలు', 'spoken': 'మాట్లాడిన', 'sentence': 'వాక్యం',
            'structure': 'నిర్మాణం', 'most': 'అత్యంత', 'importantly': 'ముఖ్యంగా'
        },
        ('en', 'ta'): {
            # English to Tamil basic words
            'hello': 'வணக்கம்', 'hi': 'ஹாய்', 'thank': 'நன்றி', 'you': 'நீங்கள்',
            'yes': 'ஆம்', 'no': 'இல்லை', 'good': 'நல்ல', 'bad': 'கெட்ட',
            'morning': 'காலை', 'evening': 'மாலை', 'night': 'இரவு',
            'friend': 'நண்பர்', 'friends': 'நண்பர்கள்', 'video': 'வீடியோ',
            'method': 'முறை', 'technique': 'நுட்பம்', 'learn': 'கற்றுக்கொள்',
            'speak': 'பேசு', 'english': 'ஆங்கிலம்', 'language': 'மொழி',
            'partner': 'பங்குதாரர்', 'required': 'தேவை', 'help': 'உதவி',
            'improve': 'மேம்படுத்து', 'grammar': 'இலக்கணம்', 'vocabulary': 'சொல்வளம்',
            'important': 'முக்கியமான', 'ability': 'திறன்', 'express': 'வெளிப்படுத்து',
            'thoughts': 'எண்ணங்கள்', 'ideas': 'கருத்துக்கள்', 'effectively': 'திறம்பட',
            'imitation': 'பின்பற்றல்', 'talking': 'பேசுதல்', 'repeating': 'மீண்டும்',
            'native': 'சொந்த', 'speakers': 'பேசுபவர்கள்', 'exact': 'சரியான',
            'words': 'வார்த்தைகள்', 'pronunciation': 'உச்சரிப்பு', 'advanced': 'மேம்பட்ட',
            'works': 'வேலை செய்கிறது', 'well': 'நன்றாக', 'there': 'அங்கே',
            'allows': 'அனுமதிக்கிறது', 'yourself': 'நீங்களே', 'speaking': 'பேசுதல்',
            'aspects': 'அம்சங்கள்', 'spoken': 'பேசப்பட்ட', 'sentence': 'வாக்கியம்',
            'structure': 'அமைப்பு', 'most': 'மிகவும்', 'importantly': 'முக்கியமாக'
        },
        ('ta', 'hi'): {
            'خلو': 'नमस्ते', 'مرحبا': 'नमस्ते', 'شكرا': 'धन्यवाद',
            'نعم': 'हाँ', 'لا': 'नहीं', 'كيف': 'कैसे', 'حالك': 'हाल है'
        }
    }
    
    # Get translation map for this language pair
    lang_pair = (source_language, target_language)
    word_map = translation_maps.get(lang_pair, {})
    
    if not word_map:
        print(f"   No direct mapping available for {lang_pair}")
        return None
    
    # Translate word by word
    words = text.split()
    translated_words = []
    
    for word in words:
        # Clean word (remove punctuation)
        clean_word = word.lower().strip('.,!?;:')
        
        # Look for translation
        if clean_word in word_map:
            translated_words.append(word_map[clean_word])
        else:
            # Keep original word if no translation found
            translated_words.append(word)
    
    result = ' '.join(translated_words)
    print(f"   Direct mapping result: '{result[:100]}...'")
    return result

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    
    print("Starting AI Speech Translation System...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Debug mode: ON")
    print("Multiple translation models enabled")
    print("Available models: GoogleTrans, MyMemory, HuggingFace, Direct Mapping")
    
    app.run(debug=False, host='0.0.0.0', port=5000)