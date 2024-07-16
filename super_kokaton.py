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


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH, random.randint(0, HEIGHT)
        self.vx, self.vy = -1, 0
        self.speed = 1

    def update(self):
        """
        敵機を移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        # if check_bound(self.rect) != (True, True):
        #     self.kill()


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


class Flag(pg.sprite.Sprite):
    """
    旗に関するクラス
    """
    def __init__(self):
        super().__init__()
        img = pg.image.load("fig/flag.png")
        img = pg.transform.scale(img, (100, 100))
        self.font = pg.font.Font(None, 50)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH, random.randint(0, HEIGHT)
        self.vx, self.vy = -2, 0

    def update(self, screen: pg.Surface):
        self.rect.move_ip(self.vx, self.vy)


def main():
    pg.display.set_caption("こうかとんのスカイフラッグ")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/bg_natural_sky.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    bird = Bird(3, (900, 400))
    score = Score()
    tim = Time()
    emys = pg.sprite.Group()
    flag = pg.sprite.Group()
    count = 0  # 旗用のカウンター

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

        x = tim.tmr % 3200
        screen.blit(bg_img, [-x, 0])
        screen.blit(bg_img2, [-x+1600, 0])
        screen.blit(bg_img, [-x+3200, 0])
        screen.blit(bg_img2, [-x+4800, 0])

        if tim.tmr % 300 == 0:
            emys.add(Enemy())

        # for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
        #     score.value += 1  # 1点アップ
        #     bird.change_img(6, screen)  # こうかとん喜びエフェクト
        # 上記の機能はマージするときに調整する

        if len(pg.sprite.spritecollide(bird, emys, True)) != 0: # GameOver
            bird.change_img(8, screen)  # こうかとん悲しみエフェクト
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("Game Over", True, (0, 0, 0))
            screen.blit(txt, [WIDTH/2-170, HEIGHT/2-50])
            score.update(screen)
            tim.update(screen)
            pg.display.update()
            time.sleep(2)
            return

        if tim.tmr%1000 == 0:  # 1000フレームに1回，旗を出現させる
            flag.add(Flag())
        if count < 5:  # 旗の合計が5本未満だったら
            if len(pg.sprite.spritecollide(bird, flag, True)) != 0:  # 旗に当たったら
                count += 1  # 旗カウント+1
        else:
            # クリア画面
            bird.change_img(6, screen)  #こうかとん喜び画像切り替え
            font_c = pg.font.Font(None, 80)
            txt = font_c.render("Game Clear", True, (255, 0, 0))  # クリア文字表示
            txt_t = font_c.render(f"Clear Time:{tim.tmr/200}", True, (255, 0, 0))  # クリアタイム表示
            screen.blit(txt, [WIDTH/2-150, HEIGHT/2-150])
            screen.blit(txt_t, [WIDTH/2-200, HEIGHT/2-50])
            pg.display.update()
            time.sleep(5)
            pg.display.update()
            time.sleep(1)
            return
        
        font = pg.font.Font(None, 50)  # カウンター用のフォント
        count_text =  font.render(f"Flag: {count}", 0, (0, 0, 255))
        screen.blit(count_text, (45, HEIGHT-160))
        
        bird.update(key_lst, screen)
        emys.update()
        emys.draw(screen)
        score.update(screen)
        tim.update(screen)
        flag.update(screen)
        flag.draw(screen)
        pg.display.update()
        tim.tmr += 1
        clock.tick(200)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
