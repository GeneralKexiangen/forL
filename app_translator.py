import streamlit as st
from cambridge_translator import CambridgeTranslator
import json
import os

# 页面配置
st.set_page_config(
    page_title="翻译器",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 简洁CSS样式
st.markdown("""
<style>
body { font-family: 'Arial', sans-serif; }
.main-header {font-size:2.5rem; color:#1f77b4; text-align:center; margin-bottom:1rem;}
.sub-header {font-size:1.3rem; color:#2e86ab; margin:1rem 0 0.5rem 0;}
.definition-box {background:#f9f9f9; padding:0.8rem; border-radius:8px; margin-bottom:0.5rem;}
.example-box {background:#f5f5f5; padding:0.4rem 0.8rem; border-radius:5px; margin:0.3rem 0; font-style:italic;}
.pronunciation {font-size:1.1rem; color:#333; margin:0.5rem 0;}
.audio-section {margin:0.5rem 0;}
.history-box {background:#eaf1fb; padding:0.5rem; border-radius:8px; margin-bottom:0.3rem; cursor:pointer;}
.error-box {background:#ffebee; padding:0.8rem; border-radius:8px; border-left:4px solid #f44336;}
.audio-btn {background-color:#4CAF50; color:white; border:none; padding:0.4rem 0.8rem; margin-right:0.3rem; border-radius:5px; cursor:pointer;}
.audio-btn:hover {background-color:#45a049;}
</style>
""", unsafe_allow_html=True)

# 缓存文件路径（项目根目录）
CACHE_FILE = "translation_cache.json"


def load_cache():
    """从本地文件加载缓存数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            # 如果文件损坏，返回空字典，下次查询会重新爬取
            return {}
    return {}


def save_to_cache(word, data):
    """保存数据到缓存文件"""
    try:
        # 加载现有缓存
        cache = load_cache()

        # 更新缓存（使用小写单词作为key确保唯一性）
        cache[word.lower()] = data

        # 保存回文件
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        return True
    except Exception:
        return False


def get_from_cache(word):
    """从缓存中获取数据"""
    cache = load_cache()
    return cache.get(word.lower())


# 翻译器实例
@st.cache_resource
def get_translator():
    return CambridgeTranslator(delay=1.5)


translator = get_translator()

# 初始化历史
if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = ""
if 'auto_translate' not in st.session_state:
    st.session_state.auto_translate = False

# 侧边栏查询历史
with st.sidebar:
    if st.session_state.history:
        # recent_history = st.session_state.history[-20:]
        recent_history = st.session_state.history
        for i, word in enumerate(reversed(recent_history), 1):
            # 从缓存中获取该单词的数据
            cached_result = get_from_cache(word)
            first_translation = ""

            # 如果有缓存数据，获取第一个中文翻译
            if cached_result and 'definitions' in cached_result and cached_result['definitions']:
                first_definition = cached_result['definitions'][0]
                if 'chinese' in first_definition:
                    first_translation = first_definition['chinese']
                    # 如果翻译太长，截取前20个字符
                    if len(first_translation) > 20:
                        first_translation = first_translation[:20] + "..."

            # 显示按钮，包含单词和第一个翻译
            button_text = f"{word}"
            if first_translation:
                button_text += f" - {first_translation}"

            if st.button(button_text, key=f"history_{word}_{i}"):
                st.session_state.selected_word = word
                st.session_state.auto_translate = True
                st.rerun()
    else:
        st.write("")

    if st.button("清空历史"):
        st.session_state.history = []
        st.rerun()

# 主标题
st.markdown('<div class="main-header">📚 翻译器</div>', unsafe_allow_html=True)

# 搜索框
word_input = st.text_input(
    "输入英文单词或短语",
    value=st.session_state.selected_word if st.session_state.selected_word else "",
    placeholder="例如: hello, computer, artificial intelligence",
    label_visibility='hidden'
)

# 查询逻辑
should_translate = False
word_to_translate = ""

if word_input:
    should_translate = True
    word_to_translate = word_input
elif st.session_state.auto_translate and st.session_state.selected_word:
    should_translate = True
    word_to_translate = st.session_state.selected_word
    st.session_state.auto_translate = False

if should_translate and word_to_translate:
    # 首先尝试从缓存获取
    cached_result = get_from_cache(word_to_translate)

    if cached_result:
        # st.success(f"💾 从本地缓存加载: **{word_to_translate}**")
        result = cached_result
        source = "cache"
    else:
        with st.spinner(f"🔍 查询中: '{word_to_translate}'..."):
            result = translator.translate(word_to_translate, max_definitions=5, include_audio=True)
            source = "crawler"

            # 如果查询成功，保存到缓存
            if 'error' not in result:
                save_to_cache(word_to_translate, result)
                # st.success(f"✅ 已保存到本地文件: **{word_to_translate}**")

    # 添加历史
    if word_to_translate not in st.session_state.history:
        st.session_state.history.append(word_to_translate)

    # 错误提示
    if 'error' in result:
        st.markdown(f'<div class="error-box">❌ {result["error"]}</div>', unsafe_allow_html=True)
    else:
        # 单词 + 音标
        st.markdown(f"<div style='font-size:2.5rem; font-weight:bold'>{result['word']}</div>", unsafe_allow_html=True)
        pron = result['pronunciation']
        st.markdown(
            f"<div class='pronunciation'>英式: /{' , /'.join(pron['uk'])}/   |   美式: /{' , /'.join(pron['us'])}/</div>",
            unsafe_allow_html=True)

        # 音频播放按钮（直接播放，无需重新请求）
        # 音频播放（英式+美式一排显示）
        audios = result.get('audio_links', {})
        if audios.get('uk_audio') or audios.get('us_audio'):
            st.markdown('<div class="sub-header">🔊 发音:</div>', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                if audios.get('uk_audio'):
                    st.markdown("🇬🇧 英式")
                    st.audio(audios['uk_audio'], format="audio/mp3")
            with col2:
                if audios.get('us_audio'):
                    st.markdown("🇺🇸 美式")
                    st.audio(audios['us_audio'], format="audio/mp3")

        # 中文释义 + 词性 + 例句
        if result['definitions']:
            st.markdown('<div class="sub-header">📖 释义&例句:</div>', unsafe_allow_html=True)
            for d in result['definitions']:

                with st.container(border=True):
                    if d.get('pos'):
                        st.markdown(f"**词性:** {d['pos']}")
                    if d.get('english'):
                        st.markdown(f"**英释:** ***{d['english']}***")
                    if d.get('chinese'):
                        st.markdown(f"**中释:** {d['chinese']}")
                    if d.get('examples'):
                        st.markdown("**例子:**")
                        for ex in d['examples']:
                            st.markdown(
                                f'<div class="example-box">📝 {ex.get("english", "")}<br>→ {ex.get("chinese", "")}</div>',
                                unsafe_allow_html=True
                            )

        # 原词典链接
        st.markdown(f"[🔗 查看剑桥词典原始页面]({result['url']})")

# 使用示例
if not word_input:
    st.markdown("---")
    st.subheader("使用示例")
    for w in ["hello", "computer", "artificial intelligence"]:
        if st.button(w):
            st.session_state.selected_word = w
            st.session_state.auto_translate = True
            st.rerun()