import requests
from bs4 import BeautifulSoup
import re
import time
import random
from typing import Dict, List, Optional


class CambridgeTranslator:
    """
    基于剑桥词典网页的翻译类

    提供英文到中文的翻译功能，支持单词和短语翻译，包含音标和发音视频支持
    """

    def __init__(self, user_agent: str = None, delay: float = 1.0):
        """
        初始化翻译器

        Args:
            user_agent: 自定义User-Agent，默认为常见浏览器UA
            delay: 请求之间的延迟时间(秒)，避免请求过快
        """
        self.base_url = "https://dictionary.cambridge.org/dictionary/english-chinese-simplified/"
        self.pronunciation_url = "https://dictionary.cambridge.org/pronunciation/english/"
        self.session = requests.Session()

        # 设置默认User-Agent
        if user_agent is None:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        self.delay = delay

        # 音标发音资源映射
        self.pronunciation_resources = {
            'youtube': {
                'british': 'https://www.youtube.com/results?search_query=how+to+pronounce+{word}+british+english',
                'american': 'https://www.youtube.com/results?search_query=how+to+pronounce+{word}+american+english'
            },
            'forvo': 'https://forvo.com/word/{word}/',
            'youglish': 'https://youglish.com/pronounce/{word}/english'
        }

    def _clean_text(self, text: str) -> str:
        """清理文本中的多余空格和特殊字符"""
        if not text:
            return ""
        # 替换各种空格和换行符
        text = re.sub(r'\s+', ' ', text)
        # 移除首尾空格
        return text.strip()

    def _extract_pronunciation(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """
        从HTML中提取音标信息

        Args:
            soup: BeautifulSoup对象

        Returns:
            包含英式和美式音标的字典
        """
        pronunciation = {'uk': [], 'us': []}

        try:
            # 查找英式音标
            uk_blocks = soup.find_all('span', class_=['uk dpron-i'])
            for block in uk_blocks:
                ipa = block.find('span', class_=['ipa', 'dipa'])
                if len(pronunciation['uk'])==1:
                    break
                if ipa and ipa.text.strip():
                    pronunciation['uk'].append(self._clean_text(ipa.text))



            # 查找美式音标
            us_blocks = soup.find_all('span', class_=['us dpron-i'])
            for block in us_blocks:
                ipa = block.find('span', class_=['ipa', 'dipa'])
                if len(pronunciation['us'])==1:
                    break
                if ipa and ipa.text.strip():
                    pronunciation['us'].append(self._clean_text(ipa.text))

        except Exception as e:
            print(f"提取音标时出错: {e}")

        return pronunciation

    def _extract_audio_links(self, soup: BeautifulSoup, word: str) -> Dict[str, str]:
        """
        提取发音音频链接

        Args:
            soup: BeautifulSoup对象
            word: 查询的单词

        Returns:
            包含音频链接的字典
        """
        audio_links = {'uk_audio': '', 'us_audio': ''}

        try:
            # 查找音频按钮
            audio_buttons = soup.find_all('button', class_=['hdn', 'hdb', 'ts', 'sound'])
            for button in audio_buttons:
                audio_source = button.get('data-src-mp3') or button.get('data-src-ogg')
                if audio_source:
                    # 确保链接是完整的URL
                    if not audio_source.startswith('http'):
                        audio_source = f"https://dictionary.cambridge.org{audio_source}"

                    if 'uk' in button.get('class', []) or 'UK' in str(audio_source).upper():
                        audio_links['uk_audio'] = audio_source
                    elif 'us' in button.get('class', []) or 'US' in str(audio_source).upper():
                        audio_links['us_audio'] = audio_source

            # 备用方法：查找音频源标签
            if not audio_links['uk_audio'] and not audio_links['us_audio']:
                audio_sources = soup.find_all('source', type='audio/mpeg')
                for source in audio_sources:
                    audio_src = source.get('src')
                    if audio_src:
                        if not audio_src.startswith('http'):
                            audio_src = f"https://dictionary.cambridge.org{audio_src}"

                        if 'uk' in audio_src or 'UK' in audio_src.upper():
                            audio_links['uk_audio'] = audio_src
                        elif 'us' in audio_src or 'US' in audio_src.upper():
                            audio_links['us_audio'] = audio_src
                    if audio_links['uk_audio'] != '' and audio_links['us_audio'] != '':
                        break

        except Exception as e:
            print(f"提取音频链接时出错: {e}")

        return audio_links

    # def _extract_definitions(self, soup: BeautifulSoup) -> List[Dict]:
    #     """
    #     从HTML中提取单词定义和翻译
    #
    #     Args:
    #         soup: BeautifulSoup对象
    #
    #     Returns:
    #         包含定义和翻译的字典列表
    #     """
    #     definitions = []
    #
    #     # 查找所有的词条区域
    #     entries = soup.find_all('div', class_=['entry', 'pr', 'entry-body__el'])
    #
    #     for entry in entries:
    #         # 提取词性
    #         pos_block = entry.find('span', class_='pos')
    #         pos = pos_block.text.strip() if pos_block else ""
    #
    #         # 提取定义和翻译
    #         def_blocks = entry.find_all('div', class_=['def-block', 'ddef_block'])
    #
    #         for def_block in def_blocks:
    #             # 英文定义
    #             eng_def = def_block.find('div', class_=['def', 'ddef_d', 'db'])
    #             eng_text = eng_def.text.strip() if eng_def else ""
    #
    #             # 中文翻译
    #             trans_block = def_block.find('span', class_=['trans', 'dtrans', 'dtrans-se'])
    #             trans_text = trans_block.text.strip() if trans_block else ""
    #
    #             # 例句
    #             examples = []
    #             example_blocks = def_block.find_all('div', class_=['examp', 'dexamp'])
    #             for ex in example_blocks:
    #                 eng_ex = ex.find('span', class_=['eg', 'deg'])
    #                 trans_ex = ex.find('span', class_=['trans', 'dtrans', 'dtrans-se'])
    #
    #                 if eng_ex and trans_ex:
    #                     examples.append({
    #                         'english': self._clean_text(eng_ex.text),
    #                         'chinese': self._clean_text(trans_ex.text)
    #                     })
    #
    #             if eng_text or trans_text:
    #                 for i, definition in enumerate(definitions, 1):
    #                     if pos != definition['pos'] and self._clean_text(eng_text) !=  definition['english']:
    #                         definitions.append({
    #                             'pos': pos,
    #                             'english': self._clean_text(eng_text),
    #                             'chinese': self._clean_text(trans_text),
    #                             'examples': examples
    #                         })
    #
    #     return definitions

    def _extract_definitions(self, soup: BeautifulSoup) -> List[Dict]:
        """
        提取英中释义 + 中英文例句
        """
        definitions = []

        # 找到所有词条块
        entries = soup.find_all("div", class_="entry-body__el")
        for entry in entries:
            pos_tag = entry.find("span", class_="pos")
            pos = pos_tag.text.strip() if pos_tag else ""

            # 每个 def-block
            def_blocks = entry.find_all("div", class_="def-block")
            for block in def_blocks:
                eng_def_tag = block.find("div", class_="def")
                eng_text = eng_def_tag.text.strip() if eng_def_tag else ""

                cn_def_tag = block.find("span", class_="trans")
                cn_text = cn_def_tag.text.strip() if cn_def_tag else ""

                examples = []
                ex_blocks = block.find_all("div", class_="examp")
                for ex in ex_blocks:
                    eng_ex = ex.find("span", class_="eg")
                    cn_ex = ex.find("span", class_="trans")
                    examples.append({
                        "english": eng_ex.text.strip() if eng_ex else "",
                        "chinese": cn_ex.text.strip() if cn_ex else ""
                    })

                # 直接 append
                if eng_text or cn_text:
                    definitions.append({
                        "pos": pos,
                        "english": eng_text,
                        "chinese": cn_text,
                        "examples": examples
                    })

        return definitions

    def get_pronunciation_resources(self, word: str) -> Dict[str, str]:
        """
        获取发音学习资源链接

        Args:
            word: 要查询的单词

        Returns:
            包含各种发音资源链接的字典
        """
        resources = {}
        word_encoded = word.lower().replace(' ', '+')

        # YouTube资源
        resources['youtube_british'] = self.pronunciation_resources['youtube']['british'].format(word=word_encoded)
        resources['youtube_american'] = self.pronunciation_resources['youtube']['american'].format(word=word_encoded)

        # 其他发音资源
        resources['forvo'] = self.pronunciation_resources['forvo'].format(word=word_encoded)
        resources['youglish'] = self.pronunciation_resources['youglish'].format(word=word_encoded)

        # 剑桥词典发音页面
        resources['cambridge_pronunciation'] = f"https://dictionary.cambridge.org/pronunciation/english/{word.lower()}"

        return {}

    def translate_sentence(self, text: str, include_audio: bool = True) -> Dict:
        """
        翻译英文短句/句子（优先尝试 Cambridge Translate 页面，失败时回落到 MyMemory 翻译）。
        返回结构：
        {
          "text": <原句>,
          "chinese": <中文翻译>,
          "pronunciation": {"uk": "", "us": ""},    # 句子通常无 IPA，保留字段
          "audio_links": {"uk_audio": <url>, "us_audio": <url>},
          "url": <查询页面或参考 url>
        }
        """
        import urllib.parse
        import requests
        from bs4 import BeautifulSoup
        import time

        # prepare
        encoded = urllib.parse.quote(text)
        cambridge_url = f"https://dictionary.cambridge.org/zhs/translate/english-chinese-simplified/?q={encoded}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://dictionary.cambridge.org/"
        }

        # default result
        result = {
            "text": text,
            "chinese": "",
            "pronunciation": {"uk": "", "us": ""},
            "audio_links": {"uk_audio": None, "us_audio": None},
            "url": cambridge_url
        }

        try:
            # try Cambridge translate page first
            resp = requests.get(cambridge_url, headers=headers, timeout=8)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 1) try multiple selectors for the Chinese translation (robust fallback)
            chinese = ""
            # common candidate selectors used historically
            candidates = [
                ("span", {"class": "trans dtrans"}),  # direct trans span
                ("span", {"class": "translate"}),  # some variants
                ("div", {"class": "result-body"}),  # container
                ("div", {"class": "cdi-body"}),  # other containers
                ("div", {"class": "trans"}),  # generic
            ]
            for tag, attrs in candidates:
                node = soup.find(tag, attrs=attrs)
                if node and node.get_text(strip=True):
                    chinese = node.get_text(" ", strip=True)
                    break

            # 2) try more generic heuristics if still empty
            if not chinese:
                # some pages_list render JSON inside a <script> or data attribute — try to find any visible translated text
                text_nodes = soup.select("div, span, p")
                for n in text_nodes:
                    txt = n.get_text(" ", strip=True)
                    if txt and len(txt) > 0 and any(ch in txt for ch in ["。", "的", "是", "了"]):
                        # heuristic: contains CJK punctuation/characters -> likely chinese
                        chinese = txt
                        break

            # 3) extract audio from Cambridge if available (buttons with data-src-mp3)
            uk_audio = None
            us_audio = None
            if include_audio:
                # look for button elements that commonly contain data-src-mp3/ogg
                for btn in soup.find_all("button"):
                    src = btn.get("data-src-mp3") or btn.get("data-src-ogg") or btn.get("data-src")
                    if not src:
                        continue
                    src_str = src if src.startswith("http") else ("https://dictionary.cambridge.org" + src)
                    src_low = src.lower()
                    if "uk" in src_low or "gb" in src_low:
                        if not uk_audio:
                            uk_audio = src_str
                    elif "us" in src_low or "am" in src_low:
                        if not us_audio:
                            us_audio = src_str
                    else:
                        # if ambiguous, fill first available for both as fallback
                        if not uk_audio:
                            uk_audio = src_str
                        elif not us_audio:
                            us_audio = src_str

                # also look for <source> tags
                if (not uk_audio or not us_audio):
                    for source in soup.select("source[type='audio/mpeg'], source[type='audio/ogg']"):
                        s = source.get("src", "")
                        if not s:
                            continue
                        full = s if s.startswith("http") else ("https://dictionary.cambridge.org" + s)
                        sl = s.lower()
                        if "uk" in sl and not uk_audio:
                            uk_audio = full
                        elif "us" in sl and not us_audio:
                            us_audio = full
                        elif not uk_audio:
                            uk_audio = full
                        elif not us_audio:
                            us_audio = full

            # set found chinese/audio
            if chinese:
                result["chinese"] = chinese

            if uk_audio:
                result["audio_links"]["uk_audio"] = uk_audio
            if us_audio:
                result["audio_links"]["us_audio"] = us_audio

            # If we already found a Chinese translation, return (but keep trying to add audio fallbacks below)
            if result["chinese"]:
                # keep going to ensure we have audio links (fall back to TTS if needed)
                pass

        except Exception:
            # ignore Cambridge errors; we'll fall back to external translate
            pass

        # FALLBACK: if no chinese found from Cambridge, call MyMemory free API
        if not result["chinese"]:
            try:
                # MyMemory endpoint (free, limited) - safe fallback
                mem_url = "https://api.mymemory.translated.net/get"
                params = {"q": text, "langpair": "en|zh-CN"}
                r2 = requests.get(mem_url, params=params, timeout=6)
                r2.raise_for_status()
                data = r2.json()
                # MyMemory stores translation at responseData.translatedText
                if data and "responseData" in data and data["responseData"].get("translatedText"):
                    result["chinese"] = data["responseData"]["translatedText"]
            except Exception:
                # last resort: empty string remains
                result["chinese"] = result.get("chinese", "") or ""

        # AUDIO FALLBACK: if Cambridge provided no audio and include_audio=True, create TTS links (client-side)
        if include_audio and (not result["audio_links"].get("uk_audio") or not result["audio_links"].get("us_audio")):
            # Use Google TTS style endpoints as direct audio URLs. These are simple GET endpoints that browsers can play.
            # Note: these are not guaranteed official API; but they work as audio-sources in many clients.
            safe_text = urllib.parse.quote(text)
            # en-GB for UK, en for US (approx)
            if not result["audio_links"].get("uk_audio"):
                result["audio_links"][
                    "uk_audio"] = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={safe_text}&tl=en-GB"
            if not result["audio_links"].get("us_audio"):
                result["audio_links"][
                    "us_audio"] = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={safe_text}&tl=en"

        # pronunciation for sentences: usually not available as IPA; leave empty strings but keep keys
        if "pronunciation" not in result:
            result["pronunciation"] = {"uk": "", "us": ""}

        result["url"] = cambridge_url
        return result

    def translate(self, word: str, max_definitions: int = 50, include_audio: bool = True) -> Dict:
        """
        翻译英文单词或短语

        Args:
            word: 要翻译的英文单词或短语
            max_definitions: 返回的最大定义数量
            include_audio: 是否包含音频链接

        Returns:
            包含翻译结果的字典
        """
        # 添加随机延迟，避免请求过快
        time.sleep(self.delay + random.uniform(0, 0.5))

        # 构建URL
        url = self.base_url + word.lower().replace(' ', '-')

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # 检查是否重定向到搜索页面（表示单词不存在）
            if 'search' in response.url:
                return {
                    'word': word,
                    'error': 'Word not found in Cambridge Dictionary',
                    'definitions': [],
                    'pronunciation': {'uk': [], 'us': []},
                    'audio_links': {},
                    'pronunciation_resources': self.get_pronunciation_resources(word)
                }

            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取定义
            definitions = self._extract_definitions(soup)

            # 提取音标
            pronunciation = self._extract_pronunciation(soup)

            # 提取音频链接
            audio_links = {}
            if include_audio:
                audio_links = self._extract_audio_links(soup, word)

            # 限制返回的定义数量
            if max_definitions and len(definitions) > max_definitions:
                definitions = definitions[:max_definitions]

            return {
                'word': word,
                'pronunciation': pronunciation,
                'audio_links': audio_links,
                'definitions': definitions,
                'pronunciation_resources': self.get_pronunciation_resources(word),
                'url': url
            }

        except requests.exceptions.RequestException as e:
            return {
                'word': word,
                'error': f'Request failed: {str(e)}',
                'definitions': [],
                'pronunciation': {'uk': [], 'us': []},
                'audio_links': {},
                'pronunciation_resources': self.get_pronunciation_resources(word)
            }
        except Exception as e:
            return {
                'word': word,
                'error': f'Unexpected error: {str(e)}',
                'definitions': [],
                'pronunciation': {'uk': [], 'us': []},
                'audio_links': {},
                'pronunciation_resources': self.get_pronunciation_resources(word)
            }


if __name__ == '__main__':
    print(CambridgeTranslator('5').translate_sentence('modest indulgence'))

