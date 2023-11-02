import PySimpleGUI as sg
import cv2


sg.theme('SystemDefault')
layout = [
  [
    sg.Text("angle"),
    sg.Slider(key='angle', range=(0, 359), resolution=1, default_value=45, orientation='horizontal', expand_x=True)
  ],
  [
    sg.Text("scale"),
    sg.Slider(key='scale', range=(0, 200), resolution=1, default_value=120, orientation='horizontal', expand_x=True)
  ],
  [sg.Image(key='img1'), sg.Image(key='img2')]
]

# webカメラをキャプチャー
capture = cv2.VideoCapture(0)

# webカメラの解像度を取得
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
window = sg.Window("webカメラ画面", layout=layout, finalize=True)
# イベントループ
while True:
  event, values = window.read(timeout=50)
  if event == sg.WIN_CLOSED:
    break
  rv, frame = capture.read()
  if rv is True:
    # 左右に並べるために縦横のサイズを半分にリサイズ
    resized = cv2.resize(frame, (width, height))
    # Rotation Matrixを取得
    angle = values['angle']
    scale = values['scale']
    rm = cv2.getRotationMatrix2D((int(width/2), int(height/2)), angle, scale/100)
    # アフィン変換
    ati = cv2.warpAffine(resized, rm, (width, height))
    # pngに変換して、Image更新
    img = cv2.imencode('.png', resized)[1].tobytes()
    img2 = cv2.imencode('.png', ati)[1].tobytes()
    window['img1'].update(data=img)
    window['img2'].update(data=img2)


capture.release()
window.close()