import os
import streamlit as st
from google.cloud import texttospeech
from google.oauth2 import service_account

# 인증 정보 가져오기 (Streamlit secrets 사용)
gcp_info = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(gcp_info)
client = texttospeech.TextToSpeechClient(credentials=credentials)

st.title("🗣️ Google Cloud Text-to-Speech")

@st.cache_data
def get_voices():
    response = client.list_voices()
    return response.voices

voices = get_voices()
languages = sorted(set(lang for voice in voices for lang in voice.language_codes))
language = st.selectbox("언어 선택", languages)

filtered_voices = [v for v in voices if language in v.language_codes]
voice_names = [f"{v.name} ({texttospeech.SsmlVoiceGender(v.ssml_gender).name})" for v in filtered_voices]
selected_voice = st.selectbox("보이스 선택", voice_names)
text = st.text_area("텍스트 입력", "Hello world!")

if st.button("음성 생성"):
    voice_idx = voice_names.index(selected_voice)
    voice_param = filtered_voices[voice_idx]

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice_param.name,
        ssml_gender=voice_param.ssml_gender,
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    st.audio("output.mp3", format="audio/mp3")
