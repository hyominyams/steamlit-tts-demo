import streamlit as st
import io
from google.cloud import texttospeech
from google.oauth2 import service_account

# 인증
gcp_info = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(gcp_info)
client = texttospeech.TextToSpeechClient(credentials=credentials)

st.title("🗣️ Google Cloud Text-to-Speech")

@st.cache_data
def get_voices():
    response = client.list_voices()
    return [
        {
            "name": voice.name,
            "language_codes": list(voice.language_codes),
            "ssml_gender": voice.ssml_gender.name,
            "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
        }
        for voice in response.voices
    ]

voices = get_voices()
languages = sorted(set(lang for v in voices for lang in v["language_codes"]))
language = st.selectbox("🌐 언어 선택", languages)

filtered_voices = [v for v in voices if language in v["language_codes"]]
voice_names = [f"{v['name']} ({v['ssml_gender']})" for v in filtered_voices]
selected_voice = st.selectbox("🗣️ 보이스 선택", voice_names)

text = st.text_area("💬 변환할 텍스트를 입력하세요", "Hello world!")

# ✅ 세션 상태에 음성 데이터 저장
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if st.button("🎧 음성 생성"):
    idx = voice_names.index(selected_voice)
    voice_info = filtered_voices[idx]

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice_info["name"],
        ssml_gender=texttospeech.SsmlVoiceGender[voice_info["ssml_gender"]],
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    st.session_state.audio_data = response.audio_content
    st.success("✅ 음성 생성 완료!")

# ✅ 음성 생성 후에는 항상 재생/다운로드 표시
if st.session_state.audio_data:
    st.audio(st.session_state.audio_data, format="audio/mp3")
    st.download_button(
        label="📥 MP3 다운로드",
        data=st.session_state.audio_data,
        file_name="output.mp3",
        mime="audio/mpeg"
    )
