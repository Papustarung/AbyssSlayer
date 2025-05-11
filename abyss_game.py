import pygame as pg
import time
from config import Config
from abyss_manager import GameManager

def main():
    pg.init()
    pg.font.init()
    font = pg.font.SysFont("arial", 20)

    FPS = 60
    TARGET_FPS = 60

    previous_time = time.time()

    screen = pg.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pg.display.set_caption("Abyss Slayer")
    clock = pg.time.Clock()

    gm = GameManager(screen)


    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if gm.game_over:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r and gm.victory:
                        gm.reset()  # implement to restart
                    elif event.key == pg.K_q:
                        running = False

        now = time.time()
        dt = now - previous_time
        previous_time = now

        # print(round(dt, 4))



        gm.update()
        screen.fill((0, 0, 0))
        gm.draw()
        pg.display.flip()

        # if gm.game_over:

        clock.tick(FPS)

    pg.quit()

if __name__ == "__main__":
    main()