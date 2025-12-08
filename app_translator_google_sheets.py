#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/8 16:04
# @Author  : Ken
# @Software: PyCharm
import streamlit as st
from cambridge_translator import CambridgeTranslator
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time    
from streamlit import secrets

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
    # background:#f1f3f4; 
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

# Google Sheets 配置
# GOOGLE_SHEET_NAME = "单词王缓存"  # 你的Google Sheet名称
# GOOGLE_CREDENTIALS_FILE = "/Users/kehaigen/PycharmProjects/pythonProject/translation/sustained-spark-276707-166a3ff3144a.json"  # 从Google Cloud下载的服务账号JSON文件


class GoogleSheetsCache:
    """简化的Google Sheets缓存管理器"""
    def __init__(self):
        self.sheet = None
        self.connected = False
        self._connect()

    def _get_credentials_dict(self):
        """获取凭证字典（彻底修复 AttrDict 问题）"""
        try:
            # Try Streamlit secrets
            if hasattr(st, "secrets"):
                secrets_dict = st.secrets.to_dict()

                if "gcp_service_account" in secrets_dict:

                    # ★★ 强制把 AttrDict 转为普通 dict（关键修复）
                    creds_dict = json.loads(json.dumps(secrets_dict["gcp_service_account"]))

                    # 修复 private_key
                    if isinstance(creds_dict.get("private_key"), str):
                        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

                    return creds_dict

            # Try local credentials.json
            if os.path.exists("credentials.json"):
                with open("credentials.json", "r") as f:
                    creds_dict = json.load(f)
                    if isinstance(creds_dict.get("private_key"), str):
                        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                    return creds_dict

            return None

        except Exception as e:
            print("Credential load error:", e)
            return None

    def _connect(self):
        """连接 Google Sheets"""
        try:
            creds_dict = self._get_credentials_dict()
            if not creds_dict:
                print("未找到 Google 凭证，跳过连接。")
                return None

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(credentials)

            # 打开或创建 spreadsheet
            try:
                spreadsheet = client.open("单词王缓存")
            except gspread.SpreadsheetNotFound:
                spreadsheet = client.create("单词王缓存")
                spreadsheet.share('', perm_type='anyone', role='reader')

            self.sheet = spreadsheet.sheet1

            # 初始化表头
            if not self.sheet.get_all_values():
                headers = ['word', 'data', 'timestamp', 'query_count', 'last_accessed']
                self.sheet.append_row(headers)

            self.connected = True

        except Exception as e:
            print("Google Sheets 连接失败:", e)
            self.connected = False

    def save(self, word, data):
        """保存缓存内容"""
        if not self.connected:
            return False

        try:
            word_lower = word.lower()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 压缩 data（兼容 json 缓存结构）
            simplified_data = {
                'word': word,
                'url': data.get('url', ''),
                'pronunciation': data.get('pronunciation', {}),
                'definitions': data.get('definitions', []),
                'audio_links': data.get('audio_links', {})
            }

            data_json = json.dumps(simplified_data, ensure_ascii=False)

            # 查找是否已有记录
            try:
                cell = self.sheet.find(word_lower)
                if cell:
                    row = cell.row
                    self.sheet.update_cell(row, 2, data_json)
                    self.sheet.update_cell(row, 3, timestamp)
                    self.sheet.update_cell(row, 5, timestamp)

                    count = int(self.sheet.cell(row, 4).value or 0) + 1
                    self.sheet.update_cell(row, 4, count)
                    return True
            except:
                pass

            # 新增
            row = [word_lower, data_json, timestamp, 1, timestamp]
            self.sheet.append_row(row)

            return True

        except Exception as e:
            print("save error:", e)
            return False

    def load(self, word):
        """读取缓存"""
        if not self.connected:
            return None

        try:
            word_lower = word.lower()
            cell = self.sheet.find(word_lower)
            if not cell:
                return None

            row = cell.row
            data_json = self.sheet.cell(row, 2).value

            # 更新访问时间 & 次数
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sheet.update_cell(row, 5, timestamp)
            count = int(self.sheet.cell(row, 4).value or 0) + 1
            self.sheet.update_cell(row, 4, count)

            return json.loads(data_json) if data_json else None

        except Exception as e:
            print("load error:", e)
            return None

    def get_all_words(self):
        if not self.connected:
            return []
        try:
            values = self.sheet.col_values(1)
            return values[1:] if len(values) > 1 else []
        except:
            return []


# 创建Google Sheets缓存实例
@st.cache_resource
def get_sheets_cache():
    return GoogleSheetsCache()


cache_manager = get_sheets_cache()


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
    col1, col2, clo3 = st.columns([2, 6, 2])

    with col1:
        if st.button("← 返回", key="back_to_main", use_container_width=True,
                     type="secondary", help="返回翻译页面"):
            st.session_state.current_page = "main"
            st.rerun()

    with clo3:
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
            cached_result = cache_manager.load(word) if cache_manager else None
            if cached_result and 'error' not in cached_result:
                # 创建历史记录卡片
                with st.container():
                    # 显示第一个释义
                    first_chinese = ""
                    if cached_result.get('definitions'):
                        first_def = cached_result['definitions'][0]
                        if first_def.get('chinese'):
                            first_chinese = first_def.get('chinese')

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


def show_main_page():
    """显示主翻译页面"""
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
        # 首先尝试从Google Sheets缓存获取
        cached_result = cache_manager.load(word_to_translate) if cache_manager else None

        if cached_result:
            result = cached_result
            source = "Google Sheets缓存"
        else:
            with st.spinner(f"🔍 查询中: '{word_to_translate}'..."):
                result = translator.translate(word_to_translate, max_definitions=50, include_audio=True)
                source = "剑桥词典"

                # 如果查询成功，保存到Google Sheets
                if 'error' not in result and cache_manager:
                    if cache_manager.save(word_to_translate, result):
                        st.toast(f"✅ 已缓存到Google Sheets", icon="✅")

        # 添加历史
        if word_to_translate and word_to_translate not in st.session_state.history:
            st.session_state.history.append(word_to_translate)

        # 显示缓存来源提示
        if should_translate:
            with st.expander("ℹ️ 数据来源"):
                st.info(f"数据来源: {source}")

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
                        st.markdown(f'### 🇬🇧 英: /{" , /".join(pron["uk"])}/')
                    with col2:
                        if audios.get('uk_audio'):
                            st.audio(audios['uk_audio'], format="audio/mp3")

            # 美式发音行
            if pron.get('us'):
                with st.container():
                    col1, col2, col3 = st.columns([5, 3, 2])
                    with col1:
                        st.markdown(f'### 🇺🇸 美: /{" , /".join(pron["us"])}/')
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
    '数据来源: dictionary.cambridge.org | 缓存存储: Google Sheets'
    '</div>',
    unsafe_allow_html=True
)
