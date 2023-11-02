import tkinter as tk
from PIL import Image, ImageTk

def draw_rectangle(event, rectangle, canvas):
    # マウスの座標を取得する
    x1, y1 = event.x, event.y

    # 矩形の座標を更新する
    rectangle.x1 = min(x1, rectangle.x2)
    rectangle.y1 = min(y1, rectangle.y2)
    rectangle.x2 = max(x1, rectangle.x2)
    rectangle.y2 = max(y1, rectangle.y2)

    # 矩形を描画する
    canvas.create_rectangle(rectangle.x1, rectangle.y1, rectangle.x2, rectangle.y2, fill="red")

def main():
    # 画像を読み込む
    image = Image.open("/home/daito_/Desktop/TrayDraw_GUI/ur5e-1_tray_empty.png")
    image = image.resize((500, 500))

    # キャンバスを作成して画像を表示する
    root = tk.Tk()
    canvas = tk.Canvas(root, width=image.width, height=image.height)
    canvas.pack()
    image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=image)

    # マウスドラッグで矩形を描画する
    rectangle = Rectangle()
    canvas.bind("<Button-1>", draw_rectangle)

    # メインループ
    root.mainloop()

class Rectangle:
    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

if __name__ == "__main__":
    main()
