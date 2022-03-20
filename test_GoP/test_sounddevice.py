import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def recording():

    sd.default.device[0] = 1
    fs = 16000  # Sample rate
    seconds = 2.5  # Duration of recording
    sd.default.dtype='int32'

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write('output.wav', fs, myrecording)  # Save as WAV file .astype(np.int16)
    print('recording finished\n')

    return 0









# # import sounddevice as sd
# # print(sd.query_devices())
# import matplotlib.pyplot as plt
# sd.default.device[0] = 1
# fs = 16000  # 指定采样频率
# duration = 5  # 指定持续时间
# #方法会立即返回, 但是会在后台继续的录音
# myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
# # 调用wait(), wait()会在播放完成后才返回
# sd.wait()
# write('output2.wav', fs, myrecording.astype(np.int16)) 
# print('语音信号采集结束\nVoice signal picked finished')
# print('开始播放:\n Start to play:')
# print(myrecording[:,1])
# plt.plot(myrecording[:,1])
# plt.show()
# #方法会立即返回, 但是会在后台继续播放
# sd.play(myrecording, fs)
# # 调用wait(), wait()会在播放完成后才返回
# sd.wait()

