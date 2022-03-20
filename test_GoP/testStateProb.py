import sys
import keyboard
import test_sounddevice as ts
import numpy as np
import wave
from extract_features import FeatureExtractor 
from hmmfunc import MonoPhoneHMM
lexicon_file = './lexicon.txt'
phone_list_file = './phone_list.txt'
hmm_file = './model_3state_1mix/10.hmm'
#log likelihood
threshold = -43000

## 1)
# Trueの場合，文章の先頭と末尾に
# ポーズがあることを前提とする
insert_sil = True
# 音素リストファイルを開き，phone_listに格納
phone_list = []
with open(phone_list_file, mode='r') as f:
    for line in f:
        # 音素リストファイルから音素を取得
        phone = line.split()[0]
        # 音素リストの末尾に加える
        phone_list.append(phone)
# 辞書ファイルを開き，単語と音素列の対応リストを得る
lexicon = []
with open(lexicon_file, mode='r', encoding='UTF-8') as f:
    for line in f:
        # 0列目は単語
        word = line.split()[0]
        # 1列目以降は音素列
        phones = line.split()[1:]
        # insert_silがTrueの場合は両端にポーズを追加
        if insert_sil:
            phones.insert(0, phone_list[0])
            phones.append(phone_list[0])
        # phone_listを使って音素を数値に変換
        ph_int = []
        for ph in phones:
            if ph in phone_list:
                ph_int.append(phone_list.index(ph))
            else:
                sys.stderr.write('invalid phone %s' % (ph))
        # 単語,音素列,数値表記の辞書として
        # lexiconに追加
        lexicon.append({'word': word,
                        'pron': phones,
                        'int': ph_int})

# MonoPhoneHMMクラスを呼び出す
hmm = MonoPhoneHMM()
# HMMを読み込む
hmm.load_hmm(hmm_file)
# 特徴量ファイルを開く
ff = './tmp.bin'
feat = np.fromfile(ff, dtype=np.float32)
# フレーム数 x 次元数の配列に変形
feat = feat.reshape(-1, hmm.num_dims)

## 4),5)
# 音素列の数値表記を得る
number = 0
label = lexicon[number]['int']
 # 各分布の出力確率を求める
hmm.calc_out_prob(feat, label)
# ビタビアルゴリズムを実行
hmm.viterbi_decoding(label)
# バックトラックを実行
viterbi_path = hmm.back_track()
# ビタビパスからフレーム毎の音素列に変換
phone_alignment = []
for vp in viterbi_path:
    # ラベル上の音素インデクスを取得
    l = vp[0]
    # 音素番号を音素リスト上の番号に変換
    p = label[l]
    # 番号から音素記号に変換
    ph = hmm.phones[p]
    # phone_alignmentの末尾に追加
    phone_alignment.append(ph)

score = hmm.viterbi_score

stateProb = hmm.state_prob
(l,s,t) = stateProb.shape

phoneProb = np.arange(l-2)
for i in range(1, l-1):
    for j in range(0,s-1):
        phoneProb[i-1] += np.sum(stateProb[i][j][:])/t
print(phoneProb)
