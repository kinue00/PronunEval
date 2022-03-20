import MeCab
import jaconv
import re

#記号を削除する関数
#(以下
#http://prpr.hatenablog.jp/entry/2016/11/23/Python%E3%81%A7%E5%85%A8%E8%A7%92%E3%83%BB%E5%8D%8A%E8%A7%92%E8%A8%98%E5%8F%B7%E3%82%92%E3%81%BE%E3%81%A8%E3%82%81%E3%81%A6%E6%B6%88%E3%81%97%E5%8E%BB%E3%82%8B
#よりそのまま引用)
import unicodedata
import string

def format_text(text):
    text = unicodedata.normalize("NFKC", text)  # 全角記号をざっくり半角へ置換（でも不完全）

    # 記号を消し去るための魔法のテーブル作成
    table = str.maketrans("", "", string.punctuation  + "「」、。・")
    text = text.translate(table)

    return text
#(引用ここまで)


class PhonemeUtil:
    _NUMBER_ZEN2HAN_TABLE = str.maketrans(
        '０１２３４５６７８９．。，、／',
        '0123456789..,,/')

    _KANA2CHAR1 = {
        'ア': 'a',    'イ': 'i',    'ウ': 'u',    'エ': 'e',    'オ': 'o',
        'ァ': 'a',    'ィ': 'i',    'ゥ': 'u',    'ェ': 'e',    'ォ': 'o',
        'カ': 'k a',  'キ': 'k i',  'ク': 'k u',  'ケ': 'k e',  'コ': 'k o',
        'ガ': 'g a',  'ギ': 'g i',  'グ': 'g u',  'ゲ': 'g e',  'ゴ': 'g o',
        'サ': 's a',  'シ': 'sh i', 'ス': 's u',  'セ': 's e',  'ソ': 's o',
        'ザ': 'z a',  'ジ': 'j i',  'ズ': 'z u',  'ゼ': 'z e',  'ゾ': 'z o',
        'タ': 't a',  'チ': 'ch i', 'ツ': 'ts u', 'テ': 't e',  'ト': 't o',
        'ダ': 'd a',  'ヂ': 'j i',  'ヅ': 'd u',  'デ': 'd e',  'ド': 'd o',
        'ナ': 'n a',  'ニ': 'n i',  'ヌ': 'n u',  'ネ': 'n e',  'ノ': 'n o',
        'ハ': 'h a',  'ヒ': 'h i',  'フ': 'f u',  'ヘ': 'h e',  'ホ': 'h o',
        'バ': 'b a',  'ビ': 'b i',  'ブ': 'b u',  'ベ': 'b e',  'ボ': 'b o',
        'パ': 'p a',  'ピ': 'p i',  'プ': 'p u',  'ペ': 'p e',  'ポ': 'p o',
        'マ': 'm a',  'ミ': 'm i',  'ム': 'm u',  'メ': 'm e',  'モ': 'm o',
        'ヤ': 'y a',                'ユ': 'y u',                'ヨ': 'y o',
        'ャ': 'y a',                'ュ': 'y u',                'ョ': 'y o',
        'ラ': 'r a',  'リ': 'r i',  'ル': 'r u',  'レ': 'r e',  'ロ': 'r o',
        'ワ': 'w a',  'ヰ': 'i'  ,                'ヱ': 'e',    'ヲ': 'o',
        'ヴ': 'b u',
        'ン': 'N',  'ッ': 'cl',
        'ー': ':',   '―': ':', '‐': ':', '-': ':', '～': ':',
        '・': '', '「': '', '」': '', '”': '', '’': '', '。': 'sp', '、': 'sp', '，': 'sp',
        '＆': 'a N d o'
    }
    _KANA2CHAR2 = {
        'キャ': 'ky a',             'キュ': 'ky u',            'キョ': 'ky o',
        'ギャ': 'gy a',             'ギュ': 'gy u',            'ギョ': 'gy o',
        'クゥ': 'k u',
        'シャ': 'sh a',             'シュ': 'sh u',            'ショ': 'sh o',
        'ジャ': 'j a',              'ジュ': 'j u',             'ジョ': 'j o',
        'チャ': 'ch a',             'チュ': 'ch u', 'チェ': 'ch e', 'チョ': 'ch o',
        'ティ': 't i', 'トゥ': 't u',
        'ディ': 'd i', 'デュ': 'dy u', 'ドゥ': 'd u',
        'ニャ': 'ny a', 'ニュ': 'ny u', 'ニョ': 'ny o',
        'ファ': 'f a', 'フィ': 'f i', 'フェ': 'f e', 'フォ': 'f o',
                                    'フュ': 'hy u',            'フョ': 'hy o',
        'ヒャ': 'hy a',             'ヒュ': 'hy u',            'ヒョ': 'hy o',
        'ビャ': 'by a',             'ビュ': 'by u',            'ビョ': 'by o',
        'ピャ': 'py a',             'ピュ': 'py u',            'ピョ': 'py o',
        'ミャ': 'my a',             'ミュ': 'my u',            'ミョ': 'my o',
        'リャ': 'ry a',             'リュ': 'ry u',            'リョ': 'ry o',
                        'ウィ': 'w i',  'ウェ': 'w e',  'ウォ': 'wh o',
        'ヴァ': 'b a',  'ヴィ': 'b i',  'ヴェ': 'b e',  'ヴォ': 'b o',
        'ウ゛ァ': 'b a', 'ウ゛ィ': 'b i', 'ウ゛ェ': 'b e', 'ウ゛ォ': 'b o'
    }

    _RE_HIRAGANA = re.compile(r'[ぁ-ゔ]')
    _RE_NUMBER   = re.compile(r'[0-9]')

    @classmethod
    def kana2phone(cls, text):
        # convert from Hiragana to Katakana
        str_kana = cls._RE_HIRAGANA.sub(lambda x: chr(ord(x.group(0)) + 0x60), text)

        # convert from Katakana to Keyboard numbers
        for k, v in cls._KANA2CHAR2.items():
            str_kana = str_kana.replace(k, v+" ")
        for k, v in cls._KANA2CHAR1.items():
            str_kana = str_kana.replace(k, v+" ")

        # sokuon
        #str_kana = re.sub(r'Q([a-z])', r'\1\1', str_kana)
        #str_kana = re.sub(r'Q$', r'ltu', str_kana)

        # concatenate long-vowel
        str_kana = re.sub(r'([aiueo]) :', r'\1:', str_kana)
        
        # remove punctuations
        str_kana = re.sub(r',', r'', str_kana)

        # remove numbers
        str_kana = str_kana.translate(cls._NUMBER_ZEN2HAN_TABLE)
        str_kana = cls._RE_NUMBER.sub(r'', str_kana)
        
        # remove double spaces
        str_kana = re.sub(r' +', r' ', str_kana)

        #長音記号を書き換える
        str_kana = str_kana.replace('a:', 'a a')
        str_kana = str_kana.replace('i:', 'i i')
        str_kana = str_kana.replace('u:', 'u u')
        str_kana = str_kana.replace('e:', 'e e')
        str_kana = str_kana.replace('o:', 'o o')
        return str_kana


m = MeCab.Tagger() #形態素解析用objectの宣言

def getPronunciation(text):
    m_result = m.parse(text).splitlines() #mecabの解析結果の取得
    m_result = m_result[:-1] #最後の1行は不要な行なので除く

    pro = '' #発音文字列全体を格納する変数
    for v in m_result:
        if '\t' not in v: continue
        surface = v.split('\t')[0] #表層形
        p = v.split('\t')[1].split(',')[-1] #発音を取得したいとき
        #p = v.split('\t')[1].split(',')[-2] #ルビを取得したいとき
        #発音が取得できていないときsurfaceで代用
        if p == '*': p = surface
        pro += p

    pro = jaconv.hira2kata(pro) #ひらがなをカタカナに変換
    pro = format_text(pro) #余計な記号を削除

    return pro

#txtファイルを読み込み

testDic = {}
with open("./smallToken.txt",'r',encoding='utf-8') as f:
    for line in f:
        line = line.replace('、', '')
        line = line.replace('。', '')
        line = line.replace('「', '')
        line = line.replace('」', '')
        words = line.split()
#print(words)
for word in words:
    testDic[word] = PhonemeUtil.kana2phone((getPronunciation(word)).rstrip())
print(testDic)

#辞書をtxtファイルに書き込む
with open('testLexicon.txt', 'w', encoding='utf-8') as f:
    for item in testDic.items():
        key = item[0]
        value = item[1]
        tmp = key + ' ' + value + '\n'
        f.write(tmp)



'''
#出力確認
text = '今日はよく寝ました'
print(text)
print(getPronunciation(text))
'''