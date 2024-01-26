from translate import Translator
import requests
from bs4 import BeautifulSoup
import json
import redis
import datetime
import pyttsx3

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, encoding='UTF-8')
r = redis.Redis(connection_pool=pool)


def deleteAllDataFromRedis():
    for key in r.keys():
        print(key)
        r.delete(key)


def getAllKeysFromRedis():
    i=1
    for key in r.keys():
        print(str(i),r.get(key))
        i+=1
    return r.keys()

def dictionaryCambridge(word):
    try:
        url = 'https://dictionary.cambridge.org/zhs'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url=url, headers=headers).text
        soup = BeautifulSoup(response, 'html.parser')
        a = soup.select(
            'body > div.pr.pg-h.fon > div.lpl-15.lpr-15.lmax.lp-xs_t-10.lp-s_t-15.lp-m_l-20.lp-m_r-20.z1 > div > div.hfl-s.lt2b.lp-s_r-20.lmb-10 > div.bpb.lmt-25.lmb--25.lp-10.lp-s_25 > div > div > div.lc.lc1.lc-xs6-12.lp-xs_l-10.lc-s1.lp-s_l-0.lc-l6-12.lp-l_l-10 > div > div.lpl-25.lml-25 > div > ul > li:nth-child(1) > a.hoh.hdb')
        next_url = a[0].get('href')
        next_url = url.replace('/zhs', '') + next_url + word
        print(next_url)
        result = requests.get(url=next_url, headers=headers).text
        res_soup = BeautifulSoup(result, 'html.parser')
        prs = res_soup.find_all(attrs={"class": "pr entry-body__el"})
        title = prs[0].find(attrs={"class": "di-title"}).text
        try:
            uk_pron = prs[0].find(attrs={"class": "uk dpron-i"}).find(attrs={"class": "pron dpron"}).text
        except:
            uk_pron = None
        try:
            uk_pron_mp3 = url.replace('/zhs', '') + \
                          prs[0].find(attrs={"class": "uk dpron-i"}).find(attrs={"class": "hdn"}).find_all('source')[0][
                              'src']
        except:
            uk_pron_mp3 = ''
        try:
            us_pron = prs[0].find(attrs={"class": "us dpron-i"}).find(attrs={"class": "pron dpron"}).text
        except:
            us_pron = None
        try:
            us_pron_mp3 = url.replace('/zhs', '') + \
                          prs[0].find(attrs={"class": "us dpron-i"}).find(attrs={"class": "hdn"}).find_all('source')[0][
                              'src']
        except:
            us_pron_mp3 =''
        try:
            uk_mp3 = requests.get(url=uk_pron_mp3, headers=headers).content
            with open("pron/{uk}.mp3".format(uk=title + '_uk'), "wb") as f:
                f.write(uk_mp3)
        except:
            uk_mp3 = None

        try:
            us_mp3 = requests.get(url=us_pron_mp3, headers=headers).content
            with open("pron/{us}.mp3".format(us=title + '_us'), "wb") as f:
                f.write(us_mp3)
        except:
            us_mp3 = None

        wfk = {}
        for pr in prs:
            if pr.find(attrs={"class": "posgram dpos-g hdib lmr-5"}) is None:
                break
            wf = pr.find(attrs={"class": "posgram dpos-g hdib lmr-5"}).text
            bs = pr.find_all(attrs={"class": "def-body ddef_b"})
            wk = {}
            for b in bs:
                # print(b.text)
                b = b.text.strip()
                es = b.split('\n')
                fw = es[0]
                el = []
                for e in es:
                    if '也请参见' in str(e):
                        break
                    if e != fw:
                        el.append(e.strip() + '\n')
                wk[fw] = el
            wfk[wf] = wk

        result = {
            'title': title
            , 'time': str(datetime.datetime.now())
            , 'uk_pron': uk_pron
            , 'us_pron': us_pron
            , 'wfk': wfk
            , 'uk_pron_mp3': uk_pron_mp3
            , 'us_pron_mp3': us_pron_mp3
            , 'us_mp3': str(us_mp3)
            , 'uk_mp3': str(uk_mp3)
        }
        # print(str(result))
        r.set(title, json.dumps(result, ensure_ascii=False))
        return json.dumps(result, ensure_ascii=False)
    except:
        return "{}"


def sentenceInput(input_):
    # translator = Translator(from_lang="chinese",to_lang="english")
    translator = Translator(from_lang="english", to_lang="chinese")
    try:
        translation = translator.translate(input_)
        print(translation)
        result = {
            'title': translation
            ,'time': str(datetime.datetime.now())
        }
        r.set(input_, json.dumps(result, ensure_ascii=False))
        return json.dumps(result, ensure_ascii=False)
    except:
        return '{}'


def main(input_text):
    result = '{}'
    if input_text:
        if str(input_text).strip() in r.keys():
            result = r.get(str(input_text))
        else:
            inputs = str(input_text).split(' ')
            if len(inputs) > 1:
                result = sentenceInput(input_text)
            else:
                result = dictionaryCambridge(input_text)
    return result

def speaker(sth):
    engine = pyttsx3.init(driverName='nsss')  # object creation
    """ RATE"""
    # rate = engine.getProperty('rate')  # getting details of current speaking rate
    # print(rate)  # printing current voice rate
    engine.setProperty('rate', 180)  # setting up new voice rate

    """VOLUME"""
    # volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    # print(volume)  # printing current volume level
    # engine.setProperty('volume', 1)  # setting up volume level  between 0 and 1

    """VOICE"""
    # voices = engine.getProperty('voices')  # getting details of current voice
    # for item in voices:
    #     print(item)
    # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    # engine.setProperty('voice', voices[4].id)  # changing index, changes voices. 1 for female

    engine.say(sth)
    # engine.say('My current speaking rate is ' + str(rate))
    engine.runAndWait()
    engine.stop()
def fake():
    from faker import Faker
    # ar_EG - Arabic(Egypt)
    # ar_PS - Arabic(Palestine)
    # ar_SA - Arabic(Saudi Arabia)
    # bg_BG - Bulgarian
    # bs_BA - Bosnian
    # cs_CZ - Czech
    # de_DE - German
    # dk_DK - Danish
    # el_GR - Greek
    # en_AU - English(Australia)
    # en_CA - English(Canada)
    # en_GB - English(Great Britain)
    # en_NZ - English(New Zealand)
    # en_US - English(United States)
    # es_ES - Spanish(Spain)
    # es_MX - Spanish(Mexico)
    # et_EE - Estonian
    # fa_IR - Persian(Iran)
    # fi_FI - Finnish
    # fr_FR - French
    # hi_IN - Hindi
    # hr_HR - Croatian
    # hu_HU - Hungarian
    # hy_AM - Armenian
    # it_IT - Italian
    # ja_JP - Japanese
    # ka_GE - Georgian(Georgia)
    # ko_KR - Korean
    # lt_LT - Lithuanian
    # lv_LV - Latvian
    # ne_NP - Nepali
    # nl_NL - Dutch(Netherlands)
    # no_NO - Norwegian
    # pl_PL - Polish
    # pt_BR - Portuguese(Brazil)
    # pt_PT - Portuguese(Portugal)
    # ro_RO - Romanian
    # ru_RU - Russian
    # sl_SI - Slovene
    # sv_SE - Swedish
    # tr_TR - Turkish
    # uk_UA - Ukrainian
    # zh_CN - Chinese(China Mainland)
    # zh_TW - Chinese(China Taiwan)
    # 创建一个Faker实例
    fake = Faker('zh_CN')

    # 生成虚假姓名
    fake_name = fake.name()

    # 生成虚假电子邮件
    fake_email = fake.email()

    # 生成虚假地址
    fake_address = fake.address()

    # 生成虚假日期
    fake_date = fake.date_of_birth()

    print("姓名:", fake_name)
    print("电子邮件:", fake_email)
    print("地址:", fake_address)
    print("出生日期:", fake_date)
    print("身份证:", fake.ssn())
    print("汽车牌照:", fake.license_plate())
    print("口号:", fake.catch_phrase())


if __name__ == '__main__':
    # print(dictionaryCambridge('refuse'))
    main('b')
    # fake()
    # deleteAllDataFromRedis()
    # print(getAllKeysFromRedis())
    # speaker('hello speaker')

