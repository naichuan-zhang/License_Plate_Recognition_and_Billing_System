import pygame


class Button(object):

    def __init__(self, screen, centerxy, width, height, bg_color, text_color, msg, text_size):
        self.screen = screen
        self.centerxy = centerxy
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.msg = msg
        self.text_size = text_size
        pygame.font.init()
        self.font = pygame.font.SysFont('SimHei', self.text_size)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = centerxy[0] - self.width / 2 + 2
        self.rect.centery = centerxy[1] - self.height / 2 + 2

        self.__deal_msg(self.msg)

    def __deal_msg(self, msg):
        # draw text on the screen surface
        self.msg_img = self.font.render(msg, True, self.text_color, self.bg_color)
        self.msg_img_rect = self.msg_img.get_rect()
        self.msg_img_rect = (self.rect.center[0] - 20, self.rect.center[1] - 20)

    def draw(self):
        # fill button color
        self.screen.fill(self.bg_color, rect=self.rect)
        # draw button onto the screen
        self.screen.blit(self.msg_img, self.msg_img_rect)

