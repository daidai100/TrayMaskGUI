# https://qiita.com/sunameri22/items/da002d628d7a28cd6e97 を参考に作成

import PySimpleGUI as sg
import tkinter as tk
import glob
import cv2
import numpy as np


# 画像読込
# cv2.imread()は日本語パスに対応していないのでその対策
def imread(filename, flags=cv2.IMREAD_UNCHANGED, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


# 画像を表示（sg.Graph インスタンスメソッド）
def draw_image_plus(self, img, location=(0,0)):
    if type(img) == np.ndarray:
        img = cv2.imencode('.png', img)[1].tobytes()
    id_ = self.draw_image(data=img, location=location)
    return id_
sg.Graph.draw_image_plus = draw_image_plus


# 1. レイアウト
# 描画エリア
canvas = sg.Graph(
    (1920, 1920), # 大きめに作って画面外にはみ出させる
    (0, 1920), # 表示サイズに合わせる
    (1920, 0), 
    background_color='#000000',
    pad=(0, 0), 
    key='CANVAS', 
)
# 画像リスト表示
table_source = sg.Table(
    [[]], ['Images'], 
    col_widths=[30], 
    auto_size_columns=False, 
    num_rows=100, # 長めに作ってはみ出させる
    justification='left', 
    select_mode=sg.TABLE_SELECT_MODE_BROWSE, 
    background_color='#000000', 
    pad=(0, 0), 
    enable_events=True, 
    key='TABLE_SOURCE', 
    font=('Arial', 12),
)

# レイアウト
layout = [
    [
        sg.Menu(
            [
                [
                    'Files(&F)', 
                    [
                        'Open (&O)::MENU_OPEN_FOLDER::', 
                        'Close (&X)::MENU_EXIT::', 
                    ], 
                ], 
                [
                    'Edit(&E)', 
                    [
                        'Undo (&Z)::MENU_UNDO::', 
                        'Redo (&Y)::MENU_REDO::', 
                    ], 
                ], 
                [
                    'Mask(&M)',
                    [
                        'Create Mask (&M)::CREATE_MASK::',
                        'Triming (&T)::MENU_TRIMING::',
                    ]
                ]
            ], 
            font=('Arial', 15)
        ),
    ], 
    [
        sg.Checkbox('縦横比固定', True, pad=(0, 0), key='ENABLE_ASPECT', font=('Arial', 12)), 
        sg.Combo(['画面サイズ', '1:1', '3:2', '4:3 <--基本これ', '16:9', '2:3', '3:4', '9:16', '指定比率'], '画面サイズ', size=(15, 1), readonly=True, enable_events=True, key='ASPECT_MODE', font=('Arial', 12)), 
        sg.Text('', size=(2, 1), pad=(0, 0)), 
        sg.Column(
            [
                [
                    sg.Input('', size=(5, 1), pad=(0, 0), key='ASPECT_X'), 
                    sg.Text(' : ', pad=(0, 0)), 
                    sg.Input('', size=(5, 1), pad=(0, 0), key='ASPECT_Y'), 
                ]
            ], 
            visible=False, 
            key='COLUMN_ASPECT', 
        ),
    ], 
    # [
    #     sg.Text("angle"),
    #     sg.Slider(key='angle', range=(0, 359), resolution=1, default_value=45, orientation='horizontal', expand_x=True)
    # ],
    # [
    #     sg.Text("scale"),
    #     sg.Slider(key='scale', range=(0, 200), resolution=1, default_value=120, orientation='horizontal', expand_x=True)
    # ],
    [
        table_source, 
        canvas, 
    ]
]


# 2. ウィンドウの生成
window = sg.Window(
    title='TrayMask',
    layout=layout, 
    resizable=True, 
    size=(1200, 900), 
    margins=(0, 0), 
    icon='daidai.png' # アイコン。なくてもいい
)
window.finalize()

table_source.bind('<ButtonPress-1>', '__LEFT_PRESS') # テーブル選択
canvas.bind('<MouseWheel>', '__SCROLL') # 表示画像のスクロール変更
canvas.bind('<ButtonPress-1>', '__LEFT_PRESS') # 範囲選択開始
canvas.bind('<Button1-Motion>', '__DRAG') # ドラッグで範囲選択
canvas.bind('<Button1-ButtonPress-3>', '__DRAG_CANCEL') # ドラッグ中止（ドラッグ中に右クリック）
canvas.bind('<ButtonRelease-1>', '__LEFT_RELEASE') # ドラッグ範囲確定
canvas.bind('<Double-ButtonPress-1>', '__DOUBLE_LEFT') # 選択範囲解除

canvas.drag_from = None # ドラッグ開始位置
canvas.current = None # カーソル現在位置
canvas.selection = None # 選択範囲
canvas.selection_figure = None # 選択範囲の描画ID
trim_areas = {} # 選択範囲記憶用 key=ファイルパス, value=選択範囲
img_update = False # 画像の更新要否
previous_canvas_size = None # 前フレームのキャンバスサイズ（ウィンドウサイズ変更検出用）


# 3. GUI処理
while True:
    event, values = window.read(timeout=100, timeout_key='TIMEOUT')
# 終了
    if event is None or '::MENU_EXIT::' in event:
        break
# ウィンドウサイズ変更の検出
    if event == 'TIMEOUT':
        if previous_canvas_size != canvas.get_size():
            event = 'CANVAS_RESIZE'
        previous_canvas_size = canvas.get_size()
        if event == 'TIMEOUT':
            continue
# フォルダを開く
    if '::MENU_OPEN_FOLDER::' in event:
        source_dir = tk.filedialog.askdirectory().replace('[', '[[]').replace(']', '[]]').replace('[[[]]', '[[]')
        if source_dir:
            trim_areas = {}
        # ファイル一覧を取得
            fullpath_list = glob.glob('{}/*.png'.format(source_dir)) \
                + glob.glob('{}/*.jpg'.format(source_dir)) \
                + glob.glob('{}/*.jpeg'.format(source_dir)) \
                + glob.glob('{}/*.bmp'.format(source_dir)) \
                + glob.glob('{}/*.gif'.format(source_dir)) 
            fullpath_list.sort()
            fullpath_list = [s.replace('\\', '/') for s in fullpath_list]
            if fullpath_list:
                select_rows=[0]
            else:
                select_rows=[]
        # ファイル一覧更新
            window['TABLE_SOURCE'].update([[s.split('/')[-1]] for s in fullpath_list], select_rows=select_rows)

# スライダー回転拡大縮小
'''filename = fullpath_list[values['TABLE_SOURCE'][0]]
img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

rv, frame = cv2.imencode(filename, img)
if rv is True:
    height, width = img.shape[:2]
    angle = values['angle']
    scale = values['scale']

    rm = cv2.getRotationMatrix2D((int(width/2), int(height/2)), angle, scale/100)
    resized = cv2.resize(frame, (width, height))

    ati = cv2.warpAffine(resized, rm, (width, height))

    img = cv2.imencode(filename, resized)[1].tobytes()
    window.update('CANVAS', data=img)
'''
# 縦横比選択
if event == 'ASPECT_MODE':
    if values['ASPECT_MODE'] == '指定比率':
        aspect_visible = True
    else:
        aspect_visible = False
    window['COLUMN_ASPECT'].update(aspect_visible)
# 選択スクロール
    if event == 'CANVAS__SCROLL' and values['TABLE_SOURCE']:
        row = values['TABLE_SOURCE'][0]
        item_len = len(fullpath_list)
        if canvas.user_bind_event.delta > 0 and row > 0:
            row -= 1
        elif canvas.user_bind_event.delta < 0 and row < item_len - 1:
            row += 1
        window['TABLE_SOURCE'].update(
            [[s.split('/')[-1]] for s in fullpath_list], 
            select_rows=[row], 
        )
    # スクロール外の要素を選択しても融通はきかないので自分で動かす必要あり
    # スクロール位置を0~1で指定
        window['TABLE_SOURCE'].set_vscroll_position(row/item_len)
# 選択中の画像があれば処理
    if values['TABLE_SOURCE']:
        current_fullpath = fullpath_list[values['TABLE_SOURCE'][0]]
    # アス比取得
        if values['ENABLE_ASPECT']:
            if ':' in values['ASPECT_MODE']:
                (x, y) = values['ASPECT_MODE'].split(':')
                aspect = np.array((
                    int(x), 
                    int(y), 
                ))
            elif values['ASPECT_MODE'] == '指定比率':
                try:
                    aspect = np.array((int(values['ASPECT_X']), int(values['ASPECT_Y'])))
                except ValueError:
                    aspect = None
        # get_size()で表示エリアサイズを測定
            elif values['ASPECT_MODE'] == '画面サイズ':
                aspect = np.array(canvas.get_size())
        else:
            aspect = None
    # 矩形選択開始
        if event == 'CANVAS__LEFT_PRESS':
            canvas.drag_from = np.array((canvas.user_bind_event.x, canvas.user_bind_event.y))
            canvas.current = np.array((canvas.user_bind_event.x, canvas.user_bind_event.y))
    # ドラッグ処理
        if event == 'CANVAS__DRAG' and canvas.drag_from is not None:
            canvas.current = np.array((canvas.user_bind_event.x, canvas.user_bind_event.y))
            canvas.selection = np.array((canvas.drag_from, canvas.current))
            canvas.selection = np.array((canvas.selection.min(axis=0), canvas.selection.max(axis=0))) # ((左上), (右下))の順に並び替える
        # アスペクト比の適用
            if aspect is not None:
                selection_size = (canvas.selection[1] - canvas.selection[0])
                aspected = (aspect[0]/aspect[1]*selection_size[1], aspect[1]/aspect[0]*selection_size[0]) + canvas.selection[0]
                canvas.selection = np.vstack([canvas.selection, [aspected]]) # アス比適応時と合体させる
            canvas.selection = np.array((canvas.selection.min(axis=0), canvas.selection.max(axis=0))).clip((0, 0), img_area_limit) # アス比適応、上下限適応
    # 矩形選択キャンセル
        if event == 'CANVAS__DRAG_CANCEL':
            canvas.selection = None
            canvas.drag_from = None
    # 矩形選択完了
        current_is_key = current_fullpath in list(trim_areas.keys()) # 記録済みの選択範囲があるか
        if event == 'CANVAS__LEFT_RELEASE' and canvas.selection is not None:
        # 面積0の選択範囲はスキップ
            if (canvas.selection[1] - canvas.selection[0]).min() >= 1:
                canvas.selection = (canvas.selection.astype(float)*image_scale).astype(int)
            # すでに選択範囲がある場合はオフセットする
                if current_is_key:
                    canvas.selection += trim_areas[current_fullpath][0]
            # 選択範囲の記録
                trim_areas[current_fullpath] = canvas.selection
        # 範囲を記録したらリセット
            canvas.selection = None
            canvas.drag_from = None
        current_is_key = current_fullpath in list(trim_areas.keys())
    # 選択範囲の登録解除
        if event == 'CANVAS__DOUBLE_LEFT' and current_is_key:
            trim_areas.pop(current_fullpath)
            current_is_key = False
    # 画像更新
        if event in ('TABLE_SOURCE', 'CANVAS__LEFT_RELEASE', 'CANVAS__DOUBLE_LEFT'):
            filename = fullpath_list[values['TABLE_SOURCE'][0]]
            img = imread(filename)
        # 登録済みの選択範囲があればトリミングする
            if current_is_key:
                rect = trim_areas[current_fullpath]
                img_trim = img[rect[0, 1]:rect[1, 1], rect[0, 0]:rect[1, 0]]
            else:
                img_trim = img.copy()
            img_update = True
# 画像表示（画像が更新された場合か、ウィンドウがリサイズされた場合）
    if img_update or (event == 'CANVAS_RESIZE' and values['TABLE_SOURCE']):
        img_size = np.array(img_trim.shape[1::-1], dtype=int) # shapeは縦、横の順なのでスライスは反転させる
        canvas_size = np.array(canvas.get_size())
    # キャンバス比で長い方の割合をsceleとする
        image_scale = (img_size / canvas_size).max()
    # キャンバスに対して長い方を基準に縮小するので、画像が画面外にはみ出ない
        img_resize = cv2.resize(img_trim, tuple((img_size/image_scale).astype(int)))
    # 画像端座標を取得
        img_area_limit = ((np.array(img_resize.shape[1::-1])-1))
    # キャンバスリセット→画像表示
        canvas.erase()
        canvas.draw_image_plus(img_resize)
        img_update = False
# 選択範囲表示
    if canvas.selection_figure is not None:
        canvas.delete_figure(canvas.selection_figure)
    if canvas.selection is not None:
        canvas.selection_figure = canvas.draw_rectangle(
            list(canvas.selection[0]), 
            list(canvas.selection[1]), 
            line_color='#FF0000', 
            line_width=1
        )
# マスク作成
    if event == 'CREATE_MASK':
        if trim_areas:
            mask = np.zeros(img_trim.shape[:2], dtype=np.uint8)
            for rect in trim_areas.values():
                mask[rect[0, 1]:rect[1, 1], rect[0, 0]:rect[1, 0]] = 255
            cv2.imwrite('mask.png', mask)
        else:
            sg.popup('選択範囲がありません')
window.close()
