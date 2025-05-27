import streamlit as st
from google.cloud import texttospeech
from google.oauth2 import service_account

# ✅ 인증 정보 (Streamlit Secrets 사용)
gcp_info = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(gcp_info)
client = texttospeech.TextToSpeechClient(credentials=credentials)

st.title("🗣️ Google Cloud Text-to-Speech")

# ✅ 직렬화 가능한 형식으로 캐시
@st.cache_data
def get_voices():
    response = client.list_voices()
    voice_list = []
    for voice in response.voices:
        voice_list.append({
            "name": voice.name,
            "language_codes": list(voice.language_codes),
            "ssml_gender": voice.ssml_gender.name,
            "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
        })
    return voice_list

# ✅ 보이스 목록 불러오기
voices = get_voices()

# ✅ 언어 선택
languages = sorted(set(lang for voice in voices for lang in voice["language_codes"]))
language = st.selectbox("🌐 언어 선택", languages)

# ✅ 보이스 필터링
filtered_voices = [v for v in voices if language in v["language_codes"]]
voice_names = [f"{v['name']} ({v['ssml_gender']})" for v in filtered_voices]
selected_voice = st.selectbox("🗣️ 보이스 선택", voice_names)

# ✅ 텍스트 입력
text = st.text_area("💬 변환할 텍스트를 입력하세요", "Hello world!")

# ✅ 음성 생성 버튼
if st.button("🎧 음성 생성"):
    voice_index = voice_names.index(selected_voice)
    voice_info = filtered_voices[voice_index]

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

    # ✅ 오디오 파일로 저장하고 재생
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    st.success("✅ 음성 생성 완료!")
    st.audio("output.mp3", format="audio/mp3")
