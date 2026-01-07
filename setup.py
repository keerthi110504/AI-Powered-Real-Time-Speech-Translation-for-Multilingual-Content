"""
Setup script for the AI Speech Translation System
"""
from setuptools import setup, find_packages

setup(
    name="ai-speech-translator",
    version="1.0.0",
    description="AI-Powered Real-Time Speech Translation for Multilingual Content",
    author="AI Development Team",
    packages=find_packages(),
    install_requires=[
        "openai-whisper>=20231117",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.3",
        "requests>=2.31.0",
        "googletrans>=4.0.0rc1",
        "transformers>=4.35.2",
        "torch>=2.1.1",
        "edge-tts>=6.1.9",
        "gTTS>=2.5.1",
        "pydub>=0.25.1",
        "scipy>=1.10.1",
        "moviepy>=1.0.3",
        "flask>=2.3.2",
        "gunicorn>=21.2.0",
        "pytube>=15.0.0",
        "pytest>=7.4.0",
        "pytest-mock>=3.11.1",
        "tqdm>=4.65.0"
    ],
    entry_points={
        'console_scripts': [
            'speech-translate=app:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)