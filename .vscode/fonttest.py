import pygame
import pygame.freetype

pygame.init()
font = pygame.freetype.Font('E:\\github\\Monopoly\\fonts\\font.ttf', size = 100)
while True:
    char = input('请输入字符：')
    # surf, rect = font.render(char, size = 100)
    print('宽度：{}'.format(font.get_rect(char).w))

