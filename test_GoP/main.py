######################
##孤立単語発音評価実験##
######################
'''
1)辞書を作成し、これから発音評価を行いたい単語を選択
2)マイクロフォンによって音声データを入力し、wavファイルに保存
3)音声特徴量を抽出
4)HMM音響モデルによってGoP点数を算出
5)事前設定した閾値によって発音の正否を判断
'''
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
#辞書から単語を選択
for index in range(len(lexicon)):
    print('%d : %s' % (index, lexicon[index]['word']))
number = input('発音したい単語のの番号を選んでください\n')
number = int(number)
if number <= len(lexicon) and number >= 0:
    choice = lexicon[number]['word']
    print('"' + choice + '"' + 'を選択しました')
else:
    print("エラー\n")

## 2)
print('press key enter to start recording...\n')
keyboard.wait('enter')
print('recodeing started\n')
## recording function
ts.recording()

## 3)
# サンプリング周波数 [Hz]
sample_frequency = 16000
# フレーム長 [ミリ秒]
frame_length = 25
# フレームシフト [ミリ秒]
frame_shift = 10
# 低周波数帯域除去のカットオフ周波数 [Hz]
low_frequency = 20
# 高周波数帯域除去のカットオフ周波数 [Hz]
high_frequency = sample_frequency / 2
# メルフィルタバンクの数
num_mel_bins = 23
# MFCCの次元数
num_ceps = 13
# ディザリングの係数
dither=1.0

# 乱数シードの設定(ディザリング処理結果の再現性を担保)
np.random.seed(seed=0)

# 特徴量抽出クラスを呼び出す
feat_extractor = FeatureExtractor(
                    sample_frequency=sample_frequency, 
                    frame_length=frame_length, 
                    frame_shift=frame_shift, 
                    num_mel_bins=num_mel_bins, 
                    num_ceps=num_ceps,
                    low_frequency=low_frequency, 
                    high_frequency=high_frequency, 
                    dither=dither)

wav_path = './output.wav'
out_file = './tmp.bin'

with wave.open(wav_path) as wav:
    # サンプリング周波数のチェック
    if wav.getframerate() != sample_frequency:
        sys.stderr.write('The expected \
            sampling rate is 16000.\n')
        exit(1)
    # wavファイルが1チャネル(モノラル)
    # データであることをチェック
    if wav.getnchannels() != 1:
        sys.stderr.write('This program \
            supports monaural wav file only.\n')
        exit(1)
    
    # wavデータのサンプル数
    num_samples = wav.getnframes()

    # wavデータを読み込む
    waveform = wav.readframes(num_samples)

    # 読み込んだデータはバイナリ値
    # (16bit integer)なので，数値(整数)に変換する
    waveform = np.frombuffer(waveform, dtype=np.int16)
    
    # MFCCを計算する
    mfcc = feat_extractor.ComputeMFCC(waveform)

    # 特徴量のフレーム数と次元数を取得
    (num_frames, num_dims) = np.shape(mfcc)

    # # 特徴量ファイルの名前(splitextで拡張子を取り除いている)
    # out_file = os.path.splitext(os.path.basename(wav_path))[0]
    # out_file = os.path.join(os.path.abspath(out_dir), 
    #                         out_file + '.bin')

    # データをfloat32形式に変換
    mfcc = mfcc.astype(np.float32)

    # データをファイルに出力
    mfcc.tofile(out_file)
    print('feature extraction finished\n')
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
#音素ごとの事後確率
stateProb = hmm.state_prob
(l,s,t) = stateProb.shape

phoneProb = np.arange(l-2)
for i in range(1, l-1):
    for j in range(0,s-1):
        phoneProb[i-1] += np.sum(stateProb[i][j][:])/t

#Feed back
print('%s : %s\n' % (lexicon[number]['word'],lexicon[number]['pron']))
print('GoP score(log likelihood) = %.2f\n' % score)
print('phone-wise posterior probability:')
print(phoneProb)
if score >= threshold:
    print("\nよくできました。")
else:
    print("まだ改善できるところがあります、頑張りましょう。")

#print(phone_alignment)
#print(hmm.state_prob[][][])

#test
'''
print(len(lexicon))
print(lexicon[0]['word'])
'''