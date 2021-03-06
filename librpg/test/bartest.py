import pygame
import librpg
from librpg.config import graphics_config
from librpg.menu import (Menu, Cursor, Bar, Grid, Panel, AlignTop,
                         AlignCenter, TabGroup, AnimatedImageWidget)
from librpg.context import get_context_stack
from librpg.animation import AnimatedImage
from librpg.collection.theme import ClassicMenuTheme


class CrazyBar(Bar):

    def __init__(self, width, height, filled=1.0, focusable=True,
                 theme=None):
        Bar.__init__(self, width, height, filled, focusable, theme)
        self.ascending = True

    def update(self):
        if self.ascending:
            self.filled += 0.02
        else:
            self.filled -= 0.02

        if self.filled == 1.0:
            self.ascending = False
        elif self.filled == 0.0:
            self.ascending = True


class BarMenu(Menu):

    TABS = 5

    def __init__(self):
        Menu.__init__(self, 480, 320)
        tab_group = TabGroup(['Bars%d' % (i + 1) for i in xrange(self.TABS)],
                             480, 320, tab_height=30)
        self.add_widget(tab_group, AlignCenter())

        # Bar tabs
        for k in xrange(4):
            grid = Grid(480, 290, 4, 10)
            for i in xrange(4):
                for j in xrange(10):
                    grid[i, j].add_widget(Panel(120, 29), AlignCenter())
                    width = 10 + 10 * (i + 1)
                    height = 1 + j
                    bar = CrazyBar(width, height)
                    grid[i, j].add_widget(bar, AlignCenter())
            tab_group[k].add_widget(grid, AlignCenter())

        # Animated image tab
        surfaces = []
        for k in xrange(25):
            s = pygame.Surface((100, 100))
            s.fill(((25 - k) * 10, 0, k * 10))
            surfaces.append(s)
        for k in xrange(25):
            s = pygame.Surface((100, 100))
            s.fill((0, k * 10, (25 - k) * 10))
            surfaces.append(s)
        for k in xrange(25):
            s = pygame.Surface((100, 100))
            s.fill((k * 10, (25 - k) * 10, 0))
            surfaces.append(s)
        animation = AnimatedImage(surfaces, 1)
        a = AnimatedImageWidget(animation, False)
        tab_group[4].add_widget(a, AlignTop())

        # Add cursor
        cursor = Cursor()
        cursor.bind(self)


def main():
    librpg.init()
    graphics_config.config(screen_width=480, screen_height=320)
    librpg.config.menu_config.config(theme=ClassicMenuTheme())

    get_context_stack().stack_model(BarMenu())
    get_context_stack().gameloop()

if __name__ == '__main__':
    main()
