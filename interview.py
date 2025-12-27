from flask import Blueprint, request, jsonify, session, redirect, url_for
import os
import base64
import numpy as np
from dotenv import load_dotenv
import json
from typing import List, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

# Interview Blueprint
interview_bp = Blueprint('interview', __name__)

# Constants
MODELS = {
    'LIVE': 'gemini-2.5-flash-native-audio-preview-09-2025',
    'ANALYSIS': 'gemini-3-flash-preview',
}

VOICES = ['Zephyr', 'Puck', 'Charon', 'Kore', 'Fenrir']

def get_system_prompt_interviewer(role: str, level: str, company: str, description: str) -> str:
    """Generate system prompt for interviewer"""
    return f"""
    You are a professional hiring manager interviewing a candidate for a {level} {role} position at {company}.
    Context: {description}
    
    Your goal is to conduct a realistic, engaging, and professional technical and behavioral interview.
    - Start with a warm greeting and a brief introduction.
    - Ask 3-5 relevant questions one by one. 
    - Wait for the candidate's response before asking the next question or providing follow-up.
    - Keep your responses concise and maintain a natural conversational flow.
    - Be professional, polite, but firm in your evaluation.
    - Do NOT provide feedback during the interview. Save it for the end report.
    - If the candidate asks you a question, answer it professionally.
    """

SYSTEM_PROMPT_ANALYZER = """
    You are an expert Interview Performance Analyst. Analyze the following interview transcript and provide a structured feedback report.
    Your response must be valid JSON matching the specified schema.
"""

# Audio processing functions
def decode_base64(base64_string: str) -> bytes:
    """Decodes base64 string to bytes"""
    return base64.b64decode(base64_string)

def encode_base64(data: bytes) -> str:
    """Encodes bytes to base64 string"""
    return base64.b64encode(data).decode('utf-8')

def float32_to_int16(audio_data: np.ndarray) -> np.ndarray:
    """Convert Float32 [-1, 1] to Int16"""
    # Clip values to [-1, 1] range
    clipped = np.clip(audio_data, -1.0, 1.0)
    # Convert to Int16
    int16_data = (clipped * 32767).astype(np.int16)
    return int16_data

def int16_to_float32(audio_data: np.ndarray) -> np.ndarray:
    """Convert Int16 to Float32 [-1, 1]"""
    return audio_data.astype(np.float32) / 32768.0

def create_audio_blob_python(audio_data: np.ndarray) -> Dict[str, str]:
    """
    Creates a blob object with base64 encoded PCM data for sending to Gemini
    audio_data: Float32Array-like numpy array
    Returns: dict with 'data' (base64 string) and 'mimeType'
    """
    # Convert Float32 to Int16
    int16_data = float32_to_int16(audio_data)
    # Convert to bytes
    bytes_data = int16_data.tobytes()
    # Encode to base64
    base64_data = encode_base64(bytes_data)
    
    return {
        'data': base64_data,
        'mimeType': 'audio/pcm;rate=16000'
    }

def decode_audio_data_python(
    data: bytes,
    sample_rate: int = 24000,
    num_channels: int = 1
) -> np.ndarray:
    """
    Decodes raw PCM data from Gemini API into Float32 array for playback
    data: bytes from base64 decoded audio
    sample_rate: sample rate of the audio
    num_channels: number of audio channels
    Returns: Float32 numpy array
    """
    # Convert bytes to Int16 array
    int16_data = np.frombuffer(data, dtype=np.int16)
    # Convert to Float32
    float32_data = int16_to_float32(int16_data)
    return float32_data

def analyze_interview(transcript: List[str]) -> Dict[str, Any]:
    """
    Analyze interview transcript and return feedback
    transcript: List of transcript lines
    Returns: Dictionary with feedback data
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # Configure GenAI
    genai.configure(api_key=api_key)
    
    # Create the model
    model = genai.GenerativeModel(
        model_name=MODELS['ANALYSIS'],
        system_instruction=SYSTEM_PROMPT_ANALYZER
    )
    
    # Prepare transcript text
    transcript_text = '\n'.join(transcript)
    
    # Define the response schema
    response_schema = {
        "type": "object",
        "properties": {
            "overallScore": {"type": "number"},
            "technicalScore": {"type": "number"},
            "communicationScore": {"type": "number"},
            "confidenceScore": {"type": "number"},
            "strengths": {
                "type": "array",
                "items": {"type": "string"}
            },
            "improvements": {
                "type": "array",
                "items": {"type": "string"}
            },
            "summary": {"type": "string"}
        },
        "required": [
            "overallScore",
            "technicalScore",
            "communicationScore",
            "confidenceScore",
            "strengths",
            "improvements",
            "summary"
        ]
    }
    
    # Generate content with structured output
    prompt = f"Analyze this interview transcript:\n\n{transcript_text}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }
        )
        
        # Parse JSON response
        feedback_data = json.loads(response.text)
        return feedback_data
    except Exception as e:
        print(f"Error analyzing interview: {e}")
        # Return default feedback on error
        return {
            "overallScore": 75,
            "technicalScore": 75,
            "communicationScore": 75,
            "confidenceScore": 75,
            "strengths": ["Good participation in the interview"],
            "improvements": ["Could improve with more practice"],
            "summary": "Interview completed. Analysis pending."
        }

# Routes
@interview_bp.route('/api/interview/start', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    role = data.get('role', 'Software Engineer')
    level = data.get('level', 'Senior')
    company = data.get('company', 'Google')
    description = data.get('description', 'General interview')
    
    # Store interview session in session
    session['interview_session'] = {
        'role': role,
        'level': level,
        'company': company,
        'description': description,
        'transcript': []
    }
    
    # Get system prompt
    system_prompt = get_system_prompt_interviewer(role, level, company, description)
    
    return jsonify({
        'success': True,
        'system_prompt': system_prompt,
        'model': MODELS['LIVE'],
        'voices': VOICES
    })

@interview_bp.route('/api/interview/analyze', methods=['POST'])
def analyze_interview_endpoint():
    """Analyze interview transcript and return feedback"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    transcript = data.get('transcript', [])
    
    if not transcript:
        return jsonify({'error': 'No transcript provided'}), 400
    
    try:
        feedback = analyze_interview(transcript)
        return jsonify({
            'success': True,
            'feedback': feedback
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@interview_bp.route('/api/interview/transcript', methods=['POST'])
def add_transcript_line():
    """Add a line to the interview transcript"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    line = data.get('line', '')
    speaker = data.get('speaker', 'Unknown')
    
    if 'interview_session' not in session:
        session['interview_session'] = {'transcript': []}
    
    transcript_line = f"{speaker}: {line}"
    session['interview_session']['transcript'].append(transcript_line)
    
    return jsonify({
        'success': True,
        'transcript': session['interview_session']['transcript']
    })

@interview_bp.route('/api/interview/transcript', methods=['GET'])
def get_transcript():
    """Get the current interview transcript"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'interview_session' not in session:
        return jsonify({
            'success': True,
            'transcript': []
        })
    
    return jsonify({
        'success': True,
        'transcript': session['interview_session'].get('transcript', [])
    })

@interview_bp.route('/api/interview/end', methods=['POST'])
def end_interview():
    """End interview and return transcript"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    transcript = []
    if 'interview_session' in session:
        transcript = session['interview_session'].get('transcript', [])
        # Clear session
        session.pop('interview_session', None)
    
    return jsonify({
        'success': True,
        'transcript': transcript
    })

