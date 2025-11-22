import streamlit as st
from cambridge_translator import CambridgeTranslator
import json
import os

# 页面配置 - 设置默认主题为light并隐藏设置
st.set_page_config(
    page_title="翻译器",
    page_icon="📚",
    layout="centered",  # 改为wide布局让整体变宽
    initial_sidebar_state="collapsed"
)

# 隐藏右上角的设置菜单和部署按钮
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 简洁CSS样式 - 优化light主题显示
st.markdown("""
<style>
body { 
    font-family: 'Arial', sans-serif;
    background-color: #ffffff;
    color: #262730;
}
.main-header {
    font-size:3.0rem; 
    color: rgb(40, 100, 245);
    text-align:center; 
    margin-bottom:1.5rem;
    font-weight: bold;
}
.sub-header {
    font-size:1.4rem; 
    color: rgb(40, 100, 245);
    margin:1rem 0 0.5rem 0;
    font-weight: 600;
}
.definition-box {
    background:#f8f9fa; 
    padding:0.8rem; 
    border-radius:8px; 
    margin-bottom:0.5rem;
    border: 1px solid #e9ecef;
}
.example-box {
    background:#f1f3f4; 
    padding:0.4rem 0.8rem; 
    border-radius:5px; 
    margin:0.3rem 0; 
    font-style:italic;
    border-left: 3px solid rgb(40, 100, 245);
}
.pronunciation {
    font-size:1.2rem; 
    color:#495057; 
    margin:0.5rem 0;
    font-family: 'Courier New', monospace;
}
.audio-section {
    margin:0.5rem 0;
}
.history-box {
    background:#e3f2fd; 
    padding:0.5rem; 
    border-radius:8px; 
    margin-bottom:0.3rem; 
    cursor:pointer;
    border: 1px solid #bbdefb;
}
.error-box {
    background:#ffebee; 
    padding:0.8rem; 
    border-radius:8px; 
    border-left:4px solid #f44336;
}

/* 优化输入框样式 */
.stTextInput input {
    background-color: #f8f9fa;
    border: 3px solid #dee2e6;
    border-radius: 10px;
    padding: 14px;
    font-size: 18px;
}

.stTextInput input:focus {
    border-color: rgb(40, 100, 245);
    box-shadow: 0 0 0 3px rgba(40, 100, 245, 0.2);
}

/* 优化按钮样式 - 修改点击后的背景颜色 */
.stButton button {
    background-color: #1f77b4;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 16px;
}

.stButton button:hover {
    background-color: rgb(40, 100, 245);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.stButton button:active,
.stButton button:focus {
    background-color: rgb(40, 100, 245) !important;
    border-color: rgb(40, 100, 245) !important;
}

/* 侧边栏样式优化 */
.css-1d391kg {
    background-color: #f8f9fa;
}

/* 隐藏Streamlit的默认装饰元素 */
.stDeployButton {
    display: none;
}

/* 优化标签显示 */
.st-emotion-cache-1q7spjk {
    font-weight: 600;
    color: rgb(40, 100, 245);
}

/* 调整主内容区域宽度 */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1200px;
}

/* 使用示例区域去掉边框 */
div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="column"]) {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* 历史记录按钮样式 */
section[data-testid="stSidebar"] .stButton button {
    background-color: #e3f2fd;
    color: rgb(40, 100, 245);
    border: 1px solid #bbdefb;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background-color: rgb(40, 100, 245);
    color: white;
}

section[data-testid="stSidebar"] .stButton button:active,
section[data-testid="stSidebar"] .stButton button:focus {
    background-color: rgb(40, 100, 245) !important;
    color: white !important;
}

/* 清空历史按钮特殊样式 */
section[data-testid="stSidebar"] .stButton button:contains("清空历史") {
    background-color: #ffebee;
    color: #d32f2f;
    border: 1px solid #ffcdd2;
}

section[data-testid="stSidebar"] .stButton button:contains("清空历史"):hover {
    background-color: #d32f2f;
    color: white;
}

/* 单词显示样式 */
.word-display {
    font-size: 3rem;
    font-weight: bold;
    color: rgb(40, 100, 245);
    text-align: center;
    margin: 1rem 0;
}

/* 链接颜色 */
a {
    color: rgb(40, 100, 245) !important;
}

a:hover {
    color: #1668a3 !important;
}
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
    st.markdown("### 📚 查询历史")

    if st.session_state.history:
        recent_history = st.session_state.history

        # 显示最近查询的单词
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

            if st.button(button_text, key=f"history_{word}_{i}", use_container_width=True):
                st.session_state.selected_word = word
                st.session_state.auto_translate = True
                st.rerun()
    else:
        st.info("暂无查询历史")

    st.markdown("---")
    if st.button("🗑️ 清空历史", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# 使用容器控制主内容宽度
main_container = st.container()

with main_container:
    # 主标题
    st.markdown('<div class="main-header">📚 翻译器</div>', unsafe_allow_html=True)

    # 搜索框
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
            result = cached_result
            source = "cache"
        else:
            with st.spinner(f"🔍 查询中: '{word_to_translate}'..."):
                result = translator.translate(word_to_translate, max_definitions=5, include_audio=True)
                source = "crawler"

                # 如果查询成功，保存到缓存
                if 'error' not in result:
                    save_to_cache(word_to_translate, result)

        # 添加历史
        if word_to_translate not in st.session_state.history:
            st.session_state.history.append(word_to_translate)

        # 错误提示
        if 'error' in result:
            st.markdown(f'<div class="error-box">❌ {result["error"]}</div>', unsafe_allow_html=True)
        else:
            # 单词 + 音标
            st.markdown(f'<div class="word-display">{result["word"]}</div>', unsafe_allow_html=True)
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
        st.markdown("")
        st.markdown("**💡 使用示例**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("hello", use_container_width=True, type="primary"):
                st.session_state.selected_word = "hello"
                st.session_state.auto_translate = True
                st.rerun()
        with col2:
            if st.button("computer", use_container_width=True, type="primary"):
                st.session_state.selected_word = "computer"
                st.session_state.auto_translate = True
                st.rerun()
        with col3:
            if st.button("artificial intelligence", use_container_width=True, type="primary"):
                st.session_state.selected_word = "artificial intelligence"
                st.session_state.auto_translate = True
                st.rerun()

    # 页脚信息
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>"
        "基于剑桥词典的翻译工具 | 数据来源: dictionary.cambridge.org"
        "</div>",
        unsafe_allow_html=True
    )
