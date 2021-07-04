import json
import cv2
import base64
import numpy as np
import glob

def calc_hue_hist(img):
    # H（色相）S（彩度）V （明度）形式に変換する。
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #hsv = img
    # 成分ごとに分離する。
    h, s, v = cv2.split(hsv)
    # 画像の画素値を計算したもの（ヒストグラム）
    h_hist = calc_hist(h)
    return h_hist

def calc_hist(img):
    # ヒストグラムを計算する。
    hist = cv2.calcHist([img], channels=[0], mask=None, histSize=[256], ranges=[0, 256])
    # ヒストグラムを正規化する。
    hist = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    # (n_bins, 1) -> (n_bins,)
    hist = hist.squeeze(axis=-1)
    return hist

def base64_to_cv2(image_base64):
    # base64 image to cv2
    image_bytes = base64.b64decode(image_base64)
    np_array = np.fromstring(image_bytes, np.uint8)
    image_cv2 = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image_cv2

def cv2_to_base64(image_cv2):
    # cv2 image to base64
    image_bytes = cv2.imencode('.jpg', image_cv2)[1].tostring()
    image_base64 = base64.b64encode(image_bytes).decode()
    return image_base64

# eventでjsonを受け取る { 'img': base64img }
def handler(event, context):
    input_img = event['img'] #画つ目の像を読み出しオブジェクトtrimed_imgに代入
    input_img = base64_to_cv2(input_img)
    height, width, channels = input_img.shape[:3]

    max_ruizido = 0
    tmp_num = 5
    crop_size = 15
    ch_names = {0: 'Hue', 1: 'Saturation', 2: 'Brightness'}
    poke_imgs = glob.glob('pokemons/*.png')
    for i in range(height//crop_size):
        for j in range(width//crop_size):
            # 画像をcrop_size*crop_sizeに分割する
            trimed_img = input_img[crop_size*i : crop_size*(i+1), crop_size*j: crop_size*(j+1)]
            max_ruizido = -1
            tmp_num = 5
            h_hist_2 = calc_hue_hist(trimed_img)
            for poke_name in poke_imgs:
                poke_img = cv2.imread(poke_name) #画つ目の像を読み出しオブジェクトpoke_imgに代入
                # 画像の Hue 成分のヒストグラムを取得する
                h_hist_1 = calc_hue_hist(poke_img)
                h_comp_hist = cv2.compareHist(h_hist_1, h_hist_2, cv2.HISTCMP_CORREL)
                if max_ruizido < h_comp_hist:
                    max_ruizido = h_comp_hist
                    tmp_num = poke_name
            if j == 0:
                # 一番左の画像
                tmp_img = cv2.imread(tmp_num)
            else:
                # 連結したい画像
                tmp_img2 = cv2.imread(tmp_num)
                # 連結された画像
                tmp_img = cv2.hconcat([tmp_img, tmp_img2])
        if i == 0:
            # 最初の１行が完成したので、次の行に移る
            output_img = tmp_img
        else:
            output_img = cv2.vconcat([output_img, tmp_img])
    
    return {'data': cv2_to_base64(output_img)}