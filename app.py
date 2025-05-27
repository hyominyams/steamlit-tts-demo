import os
import streamlit as st
from google.cloud import texttospeech
from google.oauth2 import service_account

# ✅ Streamlit secrets에서 인증 정보 가져오기
gcp_info = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(gcp_info)
client = texttospeech.TextToSpeechClient(credentials=credentials)

st.title("🗣️ Google Cloud Text-to-Speech")

# ✅ 캐시에 직렬화 가능한 값만 반환
@st.cache_data
def get_voices():
    response = client.list_voices()
    return [
        {
            "name": voice.name,
            "language_codes": voice.language_codes,
            "ssml_gender": voice.ssml_gender.name,
            "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
        }
        for voice in response.voices
    ]

voices = get_voices()

# ✅ 언어 코드 목록 생성
languages = sorted(set(lang for voice in voices for lang in voice["language_codes"]))
language = st.selectbox("🌍 언어 선택", languages)

# ✅ 언어 필터링
filtered_voices = [v for v in voices if language in v["language_codes"]]
voice_options = [f"{v['name']} ({v['ssml_gender']})" for v in filtered_voices]
selected_voice = st.selectbox("🗣️ 보이스 선택", voice_options)

# ✅ 텍스트 입력
text = st.text_area("💬 텍스트 입력", "Hello world!")

if st.button("🎧 음성 생성"):
    voice_idx = voice_options.index(selected_voice)
    voice_param = filtered_voices[voice_idx]

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice_param["name"],
        ssml_gender=texttospeech.SsmlVoiceGender[voice_param["ssml_gender"]],
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    st.audio("output.mp3", format="audio/mp3")
