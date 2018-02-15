import pygame
pygame.init()


class GUI:
    def __init__(self, *elemets):
        self.element = elemets
        self.active_tb = len(self.textbox_list)-1
        self.check = True

    @property
    def textbox_list(self):
        return list(filter(lambda x: type(x) is TextBox, self.element))

    def add_element(self, *element):
        self.element += element
        return self

    def render(self, surface):
        for i in self.element:
            render = getattr(i, "render", None)
            if callable(render):
                i.render(surface)

    def update(self):
        for i in self.element:
            render = getattr(i, "update", None)
            if callable(render):
                i.update()

        if all(map(lambda x: not x.focus, self.textbox_list)):
            self.active_tb = 0
        elif not self.check:
            for i in self.textbox_list:
                if i.focus:
                    self.active_tb = self.textbox_list.index(i)

        if self.check and self.textbox_list:
            for i in self.textbox_list:
                i.focus = False
            self.textbox_list[self.active_tb].focus = True
            self.check = False

        # print('\r%d' % self.active_tb, end='', flush=True)

    def get_event(self, event):
        for i in self.element:
            get_event = getattr(i, "get_event", None)
            if callable(get_event):
                i.get_event(event)
        if event.type == pygame.KEYDOWN and event.key == 9 and self.textbox_list:
            self.active_tb += 1
            self.active_tb = self.active_tb % len(self.textbox_list)
            self.check = True


class Label:
    def __init__(self, rect, text, text_color='gray', bg_color=-1):
        self.Rect = pygame.Rect(rect)
        self.text = text
        self.font_color = pygame.Color(text_color)
        self.bg_color = None if bg_color == -1 else \
            (bg_color if type(bg_color) is pygame.Color else pygame.Color(bg_color))
        self.font = pygame.font.Font(None, self.Rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface: pygame.Surface):
        if self.bg_color is not None:
            surface.fill(self.bg_color, self.Rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.Rect.x + 2, centery=self.Rect.centery)
        surface.blit(self.rendered_text, self.rendered_rect)


class TextBox(Label):
    def __init__(self, rect, text, max_len=None, execute=(lambda self: self.set_focus())):
        super().__init__(rect, text, bg_color='white')
        self.focus = False
        self.blink = True
        self.blink_timer = 0
        self.shift = 0
        self.max_len = max_len
        self.execute = execute

    def can_write(self, text=None):
        if text is None:
            text = self.text
        return self.font.size(text)[0] < self.Rect.width if self.max_len is None else len(text) <= self.max_len

    @property
    def get_text(self):
        return [self.text[:len(self.text)-self.shift] if self.shift else self.text,
                self.text[len(self.text)-self.shift:]]

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.focus:
            text = self.get_text
            if event.key in (pygame.K_KP_ENTER, pygame.K_RETURN, 27):
                self.execute(self)
            elif event.key == pygame.K_BACKSPACE:
                self.text = text[0][:-1] + text[1]

            elif event.key == pygame.K_DELETE:
                self.text = text[0] + text[1][1:]
                self.shift -= int(bool(self.shift))

            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                if event.key % 2:
                    self.shift -= int(self.shift > 0)
                else:
                    self.shift += int(self.shift < len(self.text))
            else:
                text[0] += event.unicode if (event.unicode.isprintable() or event.unicode == ' ') else ''
                if self.can_write(''.join(text)):
                    self.text = ''.join(text)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focus = self.Rect.collidepoint(*event.pos)
            if self.focus:
                t = ''
                in_text = False
                for i in self.text+' ':
                    rect = self.font.render(t, 1, self.font_color).get_rect(x=self.Rect.x + 2,
                                                                            centery=self.Rect.centery)
                    if rect.collidepoint(*event.pos):
                        self.shift = len(self.text) - len(t)
                        in_text = True
                        break
                    t += i
                self.shift = 0 if not in_text else self.shift

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super().render(surface)
        if self.focus and self.blink:
            self.rendered_text = self.font.render(self.get_text[0], 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(x=self.Rect.x + 2, centery=self.Rect.centery)

            is_shift = (2 if not self.shift else 0)
            pygame.draw.line(surface, (0, 0, 0), (self.rendered_rect.right + is_shift, self.rendered_rect.top + 2),
                             (self.rendered_rect.right + is_shift, self.rendered_rect.bottom - 2))


class Button(Label):
    def __init__(self, rect, text, text_color='gray', bg_color=pygame.Color('blue'),
                 active_color=pygame.Color("lightblue")):
        super().__init__(rect, text, text_color, bg_color)
        self.active_color = active_color
        self.color = self.bg_color
        self.pressed = False

    def __bool__(self):
        return bool(self.pressed)

    def render(self, surface):
        surface.fill(self.color, self.Rect)
        text = ''
        for t in self.text:
            text += t
            if self.font.size(text+'...')[0] > self.Rect.width - 7 or self.font.size(text)[0] > self.Rect.width:
                text = text+('...' if not text.startswith(self.text) else '')
                break
        self.rendered_text = self.font.render(text, 1, self.font_color)

        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(centerx=self.Rect.centerx + 3, centery=self.Rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(centerx=self.Rect.centerx + 4, centery=self.Rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.Rect, 2)
        pygame.draw.line(surface, color2, (self.Rect.right - 1, self.Rect.top),
                         (self.Rect.right - 1, self.Rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.Rect.left, self.Rect.bottom - 1),
                         (self.Rect.right, self.Rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.Rect.collidepoint(*event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False
        if event.type == pygame.MOUSEMOTION:
            self.color = self.active_color if self.Rect.collidepoint(*event.pos) else self.bg_color


class Checkbox:
    def __init__(self, rect, text, text_color='white'):
        self.Rect = pygame.Rect(rect)
        self.text = text
        self.color = pygame.Color('blue')
        self.font_color = pygame.Color(text_color)
        self.font = pygame.font.Font(None, self.Rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None
        self.pressed = False

    def render(self, surface):
        r = self.Rect
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=r.x + r.width + 5, centery=r.centery)
        surface.blit(self.rendered_text, self.rendered_rect)
        pygame.draw.rect(surface, self.color, r, 1)
        if self.pressed:
            pygame.draw.line(surface, self.color, r.topleft, r.bottomright)
            pygame.draw.line(surface, self.color, r.topright, r.bottomleft)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and \
                (self.Rect.collidepoint(*event.pos) or self.rendered_rect.collidepoint(event.pos)):
            self.pressed = not self.pressed
