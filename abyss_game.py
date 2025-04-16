import pygame as pg
from config import Config
from abyss_manager import GameManager

def main():
    pg.init()
    pg.font.init()
    font = pg.font.SysFont("arial", 20)

    screen = pg.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pg.display.set_caption("Abyss Slayer")
    clock = pg.time.Clock()

    gm = GameManager(screen)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        gm.update()
        screen.fill((0, 0, 0))
        gm.draw()
        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main()