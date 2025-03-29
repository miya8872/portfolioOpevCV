import cv2
import datetime
import os

#---------------------------
if not os.path.isdir("./png"):
    os.mkdir("./png")
#---------------------------
path = input("mp4のpathを入力してください")
cap = cv2.VideoCapture(path)
while True:
    nf = int(input("抽出頻度を入力してください(1～10 or 0=Auto)"))
    if nf>=0 and nf<=10:
        break
while True:
    sen = int(input("センシを入力してください(50～200)"))
    if sen>=50 and sen<=200:
        break
while True:
    only = int(input("残像のみの画像を保存しますか？(1=YES, 0=NO)"))
    if only==0 or only==1:
        break
#↓影と本体の割合
fir = 0.5
sha = 0.5
#---------------------------
if nf == 0:#フレーム頻度の自動設定
    frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    nf = round(float(frame/50))
    if nf == 0:
        nf = 1
#-------------------------------------------------

n = 0
x = 0
i = 0
l = 0
prec = 0
pre1 = []
pre2 = []
count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

while(True):
    n += 1
    if n/count <= 1.0:
        print("Working :"+str("{:.2%}".format(n/count))+"\r", end="")
    ret, src = cap.read()
    if not ret:
        break

    if n == 1:#初期設定
        first = src
        if first.ndim == 3:  # RGBならアルファチャンネル追加
            first = cv2.cvtColor(first, cv2.COLOR_RGB2RGBA)
        first2 = first.copy()
        h, w, c = first.shape
        h = h - 1
        w = w - 1

        i = 0
        l = 0#白紙画像の作成
        shad = first.copy()
        while(i<h):
            i += 1
            l = 0
            while(l<w):
                l += 1
                shad[i,l] = [0,0,0,0]

        i = 0
        l = 0#pre作成
        while(i<h):
            i += 1
            l = 0
            while(l<w):
                l += 1
                pre1.append(0)
                pre2.append(0)

 #nfの値で何フレーム毎か指定
    else:#画像処理
        if 0 == n%nf:
            x += 1
            img = src
            if src.ndim == 3:
                img = cv2.cvtColor(src, cv2.COLOR_RGB2RGBA)
            diff = cv2.absdiff(first, img)

            i = 0
            l = 0
            prec = -1
            while(i<h):
                if x == 1:
                    break
                i += 1
                l = 0
                while(l<w):
                    prec += 1
                    l += 1
                    if 0 == x%2:
                        pre2[prec] = 0
                    else:
                        pre1[prec] = 0
                    pixelValue = diff[i,l]
                    b, g, r , a = pixelValue
                    sam = b + g + r

                    if sam >= sen:
                        if 0 == x%2:
                            if pre1[prec] == 0:
                                shad[i,l] = img[i,l]
                                pre2[prec] = 1
                        else:
                            if pre2[prec] == 0:
                                shad[i,l] = img[i,l]
                                pre1[prec] = 1

            first = img.copy()

#混ぜる割合も変更可能にする予定
blended = cv2.addWeighted(src1=first2,alpha=fir,src2=shad,beta=sha,gamma=0)

now = datetime.datetime.now()
timestamp = now.strftime('%Y%m%d_%H%M%S')

file_name = "./png/after_" + timestamp + ".png"
cv2.imwrite(file_name, blended)

if only == 1:
    file_name = "./png/shadow_" + timestamp + ".png"
    cv2.imwrite(file_name, shad)
