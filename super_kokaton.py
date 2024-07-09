import math
import os
import random
import sys
import time
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 1
        self.life = 1  # ライフを追加
        self.life_image = pg.transform.rotozoom(pg.image.load(f"fig/4.png"), 0, 0.5)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_UP]:
            i = 0
            j = -1
        elif key_lst[pg.K_DOWN]:
            i = 0
            j = 1
        elif key_lst[pg.K_LEFT]:
            i = -1
            j = 0
        elif key_lst[pg.K_RIGHT]:
            i = 2
            j = 0
        else:
            i = -1
            j = 0
        self.rect.move_ip((i, j))
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*i, -self.speed*j)
        screen.blit(self.image, self.rect)

        # ライフを画像で表示する
        life_text = "Life:"
        font = pg.font.Font(None, 36)
        text = font.render(life_text, True, (255, 255, 255))
        screen.blit(text, (20, HEIGHT - 40))

        x_offset = 20 + text.get_width() + 10  # テキストの右側に10ピクセルの間隔を空ける
        y = HEIGHT - 40
        for _ in range(self.life):
            screen.blit(self.life_image, (x_offset, y))
            x_offset += self.life_image.get_width() + 10
            
        # ライフが2になったらこうかとんを一回り大きくする
        if self.life == 2:
            self.image = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.5)
            self.image = pg.transform.flip(self.image, True, False)
        # ライフが3になったらさらに大きくする
        elif self.life == 3:
            self.image = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 3.0)
            self.image = pg.transform.flip(self.image, True, False)


class Score:
    """
    打ち落とした敵機の数をスコアとして表示するクラス
    敵機：1点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class Time:
    """
    タイムを表示
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Time: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-100
        self.tmr = 0

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Time: {self.tmr/200}", 0, self.color)
        screen.blit(self.image, self.rect)


class Chicken(pg.sprite.Sprite):
    """
    チキンを食べてライフを１つ増やす機能
    """
    
    def __init__(self):
        super().__init__()
        image = pg.image.load(f"fig/chicken.png")
        self.image = pg.transform.scale(image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(500, WIDTH), 0
        self.vy, self.vx = 1,-1  # チキンの降下速度を設定する

    def update(self):
        """
        チキンを画面内を降下させる
        """
        self.rect.move_ip(self.vx, self.vy)  # チキンを降下させる
        if self.rect.top > HEIGHT:  # チキンが画面外に出たら
            self.kill()  # チキンを削除する


def main():
    pg.display.set_caption("スーパーこうかとんブラザーズ")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    bird = Bird(3, (900, 400))
    score = Score()
    time = Time()
    chickens = pg.sprite.Group()  # チキンの機能

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

        x = time.tmr % 3200
        screen.blit(bg_img, [-x, 0])
        screen.blit(bg_img2, [-x+1600, 0])
        screen.blit(bg_img, [-x+3200, 0])
        screen.blit(bg_img2, [-x+4800, 0])
        
        if x % 1000 == 0 and bird.life < 3 :  # 1000フレームに1回，チキンを出現させる
            chickens.add(Chicken())
        
        if pg.sprite.spritecollide(bird, chickens, True):  # チキンを食べた時の処理
            bird.life += 1  # ライフを増やす
            #bird.change_img(6, screen)  # こうかとん喜びエフェクト
        
        bird.update(key_lst, screen)
        score.update(screen)
        time.update(screen)
        chickens.update()
        chickens.draw(screen)
        pg.display.update()
        time.tmr += 1
        clock.tick(200)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()