import streamlit as st
from cambridge_translator import CambridgeTranslator
import json
import os

# 页面配置 - 设置默认主题为light并隐藏设置
st.set_page_config(
    page_title="单词王",
    page_icon="📚",
    layout="centered",
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
    position: relative;
    min-height: 100vh;
}
.main-header {
    font-size:2.5rem; 
    color: rgb(40, 100, 245);
    text-align:center; 
    margin-bottom:1rem;
    font-weight: bold;
}
.sub-header {
    font-size:1.8rem; 
    color: rgb(40, 100, 245);
    margin:2rem 0 1rem 0;
    font-weight: 500;
    text-align: left    ;
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
.error-box {
    background:#ffebee; 
    padding:0.8rem; 
    border-radius:8px; 
    border-left:4px solid #f44336;
}

/* 优化输入框样式 - 细边框，无点击背景色 */
.stTextInput {
    width: 100% !important;
}

.stTextInput input {
    # background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 14px;
    font-size: 18px;
    width: 100% !important;
    transition: border-color 0.3s ease;
}

.stTextInput input:focus {
    # border-color: rgb(40, 100, 245);
    box-shadow: 0 0 0 2px rgba(40, 100, 245, 0.1);
    # background-color: #f8f9fa !important;
}

/* 输入框和按钮容器 */
.input-with-button {
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.input-container {
    flex: 1;
}

.history-button-container {
    margin-top: 0;
}

/* 历史按钮样式 - 小图标按钮 */
.history-icon-button {
    background-color: #6c757d !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-size: 18px !important;
    min-width: 50px !important;
    height: 52px !important;
    transition: all 0.3s ease !important;
}

.history-icon-button:hover {
    background-color: #545b62 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}

/* 历史记录页面样式 */
.history-page {
    max-width: 800px;
    margin: 0 auto;
}

.history-item-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid #e9ecef;
    transition: all 0.3s ease;
    cursor: pointer;
}

.history-item-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-color: rgb(40, 100, 245);
}

.history-word {
    font-size: 1.5rem;
    font-weight: bold;
    color: rgb(40, 100, 245);
    margin-bottom: 0.5rem;
}

.history-pronunciation {
    color: #6c757d;
    font-size: 1rem;
    margin-bottom: 0.5rem;
    font-family: 'Courier New', monospace;
}

.history-translation {
    color: #495057;
    font-size: 1.1rem;
    line-height: 1.5;
}

.history-examples {
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px dashed #dee2e6;
}

.history-example {
    font-style: italic;
    color: #6c757d;
    font-size: 0.95rem;
    margin: 0.3rem 0;
}

.history-empty {
    text-align: center;
    padding: 3rem;
    color: #6c757d;
}

.history-empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

/* 调整主内容区域宽度 */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1200px;
}

/* 发音区域样式 */
.pronunciation-text {
    font-size: 1.2rem;
    margin-bottom: 0;
    text-align: left;
    min-width: 180px;
}

/* 固定页脚样式 */
.fixed-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    padding: 1rem 0;
    text-align: center;
    color: #6c757d;
    font-size: 0.9rem;
    border-top: 1px solid #e9ecef;
    z-index: 1000;
    margin-top: 2rem;
}

/* 音频播放器样式 */
.stAudio {
    width: 200px !important;
    min-width: 200px !important;
}

/* 清空历史按钮样式 */
.danger-button {
    background-color: #dc3545 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
}

.danger-button:hover {
    background-color: #c82333 !important;
    transform: translateY(-2px) !important;
}

/* 返回按钮样式 */
.back-button {
    background-color: #6c757d !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    margin-bottom: 2rem !important;
}

.back-button:hover {
    background-color: #545b62 !important;
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
            return {}
    return {}


def save_to_cache(word, data):
    """保存数据到缓存文件"""
    try:
        cache = load_cache()
        cache[word.lower()] = data
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

# 初始化状态
if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = ""
if 'auto_translate' not in st.session_state:
    st.session_state.auto_translate = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"  # "main" 或 "history"


def show_history_page():
    """显示历史查询页面"""
    # st.markdown('<div class="history-page">', unsafe_allow_html=True)

    # 按钮布局 - 并排展示
    col1, col2, clo3 = st.columns([2, 6, 2])

    with col1:
        # 返回按钮居左
        if st.button("← 返回", key="back_to_main", use_container_width=True,
                     type="secondary", help="返回翻译页面"):
            st.session_state.current_page = "main"
            st.rerun()

    with clo3:
        # 清空历史按钮居右
        if st.session_state.history and st.button("🗑️ 清空", key="clear_all_history",
                                                  use_container_width=True, type="primary"):
            st.session_state.history = []
            st.rerun()

    if not st.session_state.history:
        st.markdown('''
        <div class="history-empty">
            <div class="history-empty-icon">📖</div>
            <h3>暂无查询历史</h3>
            <p>开始查询单词后，您的查询记录将显示在这里</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # 显示历史记录
        for word in reversed(st.session_state.history):
            cached_result = get_from_cache(word)
            if cached_result and 'error' not in cached_result:
                # 创建历史记录卡片 - 添加点击区域样式
                with st.container():
                    # 显示第一个释义
                    first_chinese = ""
                    if cached_result.get('definitions'):
                        first_def = cached_result['definitions'][0]
                        if first_def.get('chinese'):
                            first_chinese = first_def.get('chinese')

                    # 使用HTML包装按钮文本实现居左
                    button_label = f"{word} : {first_chinese}" if first_chinese else word
                    st.markdown(f"""
                    <style>
                        div[data-testid="stButton"] button {{
                            justify-content: flex-start !important;
                            text-align: left !important;
                            padding-left: 15px !important;
                        }}
                    </style>
                    """, unsafe_allow_html=True)

                    if st.button(button_label, key=f"history_query_{word}",
                                 use_container_width=True,
                                 help=f"查询 {word}"):
                        st.session_state.selected_word = word
                        st.session_state.auto_translate = True
                        st.session_state.current_page = "main"
                        st.rerun()

    # st.markdown('</div>', unsafe_allow_html=True)

def show_main_page():
    """显示主翻译页面"""
    # 主标题
    st.markdown('<div class="main-header">单词王</div>', unsafe_allow_html=True)

    word_input = st.text_input(
        "输入英文单词或短语",
        value=st.session_state.selected_word if st.session_state.selected_word else "",
        placeholder="请默写",
        label_visibility='hidden',
        key="word_input"
    )

    if st.button("📚", key="view_history",
                 help="查看查询历史"):
        st.session_state.current_page = "history"
        st.rerun()

    # 查询逻辑 - 输入后按Enter自动查询
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
                result = translator.translate(word_to_translate, max_definitions=50, include_audio=True)
                source = "crawler"

                # 如果查询成功，保存到缓存
                if 'error' not in result:
                    save_to_cache(word_to_translate, result)

        # 添加历史
        if word_to_translate and word_to_translate not in st.session_state.history:
            st.session_state.history.append(word_to_translate)

        # 错误提示
        if 'error' in result:
            st.markdown(f'<div class="error-box">❌ {result["error"]}</div>', unsafe_allow_html=True)
        else:
            # 音标和发音
            pron = result['pronunciation']
            audios = result.get('audio_links', {})

            # 英式发音行
            if pron.get('uk'):
                with st.container():
                    col1, col2, col3 = st.columns([5, 3, 2])
                    with col1:
                        # st.markdown(f'<div class="pronunciation-text">  🇬🇧 英式: /{" , /".join(pron["uk"])}/</div>',
                        #             unsafe_allow_html=True)
                        # st.subheader(f'🇬🇧 英: /{" , /".join(pron["uk"])}')
                        st.markdown(f'### 🇬🇧 英: /{" , /".join(pron["uk"])}/')

                        # st.markdown(f'<h3>🇬🇧 英: /{" , /".join(pron["uk"])}/</h3>', unsafe_allow_html=True)
                    with col2:
                        if audios.get('uk_audio'):
                            st.audio(audios['uk_audio'], format="audio/mp3")

            # 美式发音行
            if pron.get('us'):
                with st.container():
                    col1, col2, col3 = st.columns([5, 3, 2])
                    with col1:
                        # st.markdown(f'<div class="pronunciation-text">  🇺🇸 美式: /{" , /".join(pron["us"])}/</div>',
                        #             unsafe_allow_html=True)
                        # st.subheader(f'🇺🇸 美: /{" , /".join(pron["us"])}')
                        st.markdown(f'### 🇺🇸 美: /{" , /".join(pron["us"])}/')
                        # st.markdown(f'<h3>🇺🇸 美: /{" , /".join(pron["us"])}/</h3>', unsafe_allow_html=True)

                    with col2:
                        if audios.get('us_audio'):
                            st.audio(audios['us_audio'], format="audio/mp3")

            # 中文释义 + 词性 + 例句
            if result['definitions']:
                st.markdown('<div class="sub-header">📖 释义&例句</div>', unsafe_allow_html=True)
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


# 主程序逻辑
if st.session_state.current_page == "history":
    show_history_page()
else:
    show_main_page()

# 固定页脚
st.markdown(
    '<div class="fixed-footer">'
    '数据来源: dictionary.cambridge.org'
    '</div>',
    unsafe_allow_html=True
)
