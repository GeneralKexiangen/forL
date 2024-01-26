import streamlit as st
import translator as tr
import json
from streamlit.components.v1 import html

# js_code = '''
# $(document).ready(function(){
#     $("button[kind=header]", window.parent.document).remove()
# });
# '''
# html(f'''<script src="https://cdn.bootcdn.net/ajax/libs/jquery/2.2.4/jquery.min.js"></script>
#     <script>{js_code}</script>''',
#      width=0,
#      height=0)


st.title(':orange[_ForMing_] :sunglasses:')
if 'words' not in st.session_state:
    st.session_state.words = []

word = st.text_input('anything', label_visibility='collapsed')

if word:
    to_word = json.loads(tr.main(word))
    if len(to_word) == 0:
        st.error(':cry:')
    else:
        if word not in st.session_state.words:
            st.session_state.words.append(word)
        left, right = st.columns([7, 3])
        with left:
            if len(to_word.keys()) == 2:
                title = to_word.get('title')
                st.header(':green[' + title + ']')
            else:
                title = to_word.get('title')
                st.header(':green[' + title + ']')
                uk_pron = to_word.get('uk_pron')
                us_pron = to_word.get('us_pron')
                if uk_pron and us_pron:
                    with st.expander("See pronunciation:"):
                        c1, c2, c3 = st.columns([5, 1, 5])
                        with c1:
                            st.text('英:' + uk_pron)
                            st.audio('pron/{uk}_uk.mp3'.format(uk=title))
                        with c3:
                            st.text('美:' + us_pron)
                            st.audio('pron/{us}_us.mp3'.format(us=title))

                wfs = to_word.get('wfk').keys()
                n = 0
                if len(wfs) > 0:
                    for wf in st.tabs(list(wfs)):
                        while n > len(list(wfs)) - 1:
                            break
                        with wf:
                            wf = list(wfs)[n]
                            # st.write(':blue['+wf+'].')
                            ewf = list(to_word.get('wfk').get(wf).keys())
                            i = 1
                            for e in ewf:
                                st.write(str(i) + '.' + e)
                                with st.expander("See example:"):
                                    exams = to_word.get('wfk').get(wf).get(e)
                                    for exam in exams:
                                        st.write(exam.replace(word, ':blue[' + word + ']'))
                                i += 1
                            n += 1
            st.balloons()
        with right:
            clear = st.button('Clear')
            if clear:
                st.session_state.words = []
            for w in st.session_state.words:
                st.write(':red[' + w + ']')

else:
    st.warning('try to input something.')
