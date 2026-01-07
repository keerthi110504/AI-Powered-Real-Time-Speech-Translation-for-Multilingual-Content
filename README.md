# AI-Powered Real-Time Speech Translation System

An advanced speech translation system that converts speech from one language to another in real-time, supporting multiple input sources including microphone, audio files, video files, and YouTube links.


### Core Functionality
- **Speech Recognition**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **Translation**: Supports multiple translation services (Hugging Face, Azure Translator, Google Translate)
- **Text-to-Speech**: Generates natural-sounding audio using gTTS and Edge TTS
- **Multi-language Support**: Handles numerous languages with automatic language detection

### Features
- **Batch Processing**: Process multiple audio/video files simultaneously
- **Quality Options**: Customize audio sample rate and channel configuration
- **Real-time Streaming**: Stream audio for instant translation

### Input Sources
- **Microphone**: Live speech recording and translation
- **Audio Files**: Support for WAV, MP3, M4A formats
- **Video Files**: Support for MP4, MKV formats
- **YouTube Links**: Direct processing of YouTube videos

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ott-speech-detection
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install additional system dependencies:
   - FFmpeg for audio/video processing
   - Python 3.8 or higher

4. Set up environment variables (for Azure services):
   ```bash
   export AZURE_TRANSLATOR_KEY=your_key
   export AZURE_TRANSLATOR_REGION=your_region
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Select your input method:
   - **Microphone**: Record live speech
   - **Audio File**: Upload audio files
   - **Video File**: Upload video files
   - **YouTube**: Enter YouTube URL

4. Configure translation options:
   - Select source and target languages
   - Adjust audio quality settings
   - Enable advanced translation features

5. Click "Translate Speech" to process

## API Endpoints

- `GET /` - Main application interface
- `POST /translate` - Process translation requests
- `GET /languages` - Get supported languages
- `GET /audio/<filename>` - Serve generated audio files
- `POST /stream/start` - Start streaming processing
- `POST /stream/stop` - Stop streaming processing
- `POST /stream/audio` - Process audio chunks
- `GET /history` - Get translation history
- `POST /history/clear` - Clear translation history
- `GET /favorites` - Get favorite translations
- `POST /favorites/add` - Add to favorites
- `POST /favorites/remove` - Remove from favorites

## Directory Structure

```
ott-speech-detection/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Temporary files and output
├── templates/            # HTML templates
│   └── index.html        # Main interface
└── src/                  # Source modules
    ├── audio_converter/   # Audio conversion utilities
    ├── concurrent/        # Concurrent processing
    ├── input_handler/     # Input handling
    ├── language_detector/ # Language detection
    ├── speech_to_text/    # Speech recognition
    ├── streaming/         # Real-time streaming
    ├── text_to_speech/    # Text-to-speech generation
    ├── translator/        # Translation services
    └── user_history/      # History and favorites
```

## Requirements

- Python 3.8+
- FFmpeg
- OpenAI Whisper models
- Hugging Face transformers
- Various Python packages (see requirements.txt)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI Whisper for speech recognition
- Hugging Face for translation models
- Google Translate API

- Azure Cognitive Services
