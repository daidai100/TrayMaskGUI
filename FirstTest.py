import PySimpleGUI as sg

# 1. レイアウト
layout = [
    [
        sg.Button('押してね', size=(30, 3), key='BUTTON', font ='メイリオ'),
    ],
]

# 2. ウィンドウの生成
window = sg.Window(
    title='Window title',
    layout=layout
)
window.finalize()

# 3. GUI処理
while True:
    event, values = window.read(timeout=None)
    if event is None:
        break
window.close()