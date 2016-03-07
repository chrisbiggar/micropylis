'''
Custom Widgets for map editor

'''

from kytten.layout import ANCHOR_CENTER
from kytten.layout import GetRelativePoint, VerticalLayout
from kytten.layout import GridLayout
from kytten.layout import HALIGN_CENTER
from kytten.layout import VALIGN_CENTER
from kytten.menu import *

'''
    Image Widget
'''


class Image(Widget):
    def __init__(self, image, anchor=ANCHOR_CENTER, maxWidth=0, maxHeight=0, padding=2):
        Widget.__init__(self)
        self.image = image
        self.sprite = None
        self.padding = padding
        self.anchor = anchor
        self.maxW = maxWidth
        self.maxH = maxHeight

    def delete(self):
        if self.sprite is not None:
            self.sprite.delete()
            self.sprite = None

    def layout(self, x, y):
        self.x, self.y = x, y
        if self.sprite is not None:
            w, h = self.sprite.width, self.sprite.height
            x, y = GetRelativePoint(self, self.anchor,
                                    Widget(w, h),
                                    self.anchor, (0, 0))
            self.sprite.x = x
            self.sprite.y = y

    def setImage(self, image):
        self.image = image
        self.delete()
        if self.saved_dialog is not None:
            self.saved_dialog.set_needs_layout()

    def size(self, dialog):
        if dialog is None:
            return
        Widget.size(self, dialog)
        if self.sprite is None and self.image is not None:
            self.sprite = pyglet.sprite.Sprite(
                self.image, batch=dialog.batch, group=dialog.fg_group)

            ''' scales the image to smallest out of max width or max height
            '''
            ratioW, ratioH = 1, 1
            if self.sprite.width > self.maxW:
                ratioW = float(self.maxW) / float(self.sprite.width)
            if self.sprite.height > self.maxH:
                ratioH = float(self.maxH) / float(self.sprite.height)
            self.sprite.scale = min(ratioH, ratioW)

            self.width = self.sprite.width + self.padding * 2
            self.height = self.sprite.height + self.padding * 2


'''
    class Item
'''


class Item(Control):
    """
    MenuOption is a choice within a menu.  When selected, it inverts
    (inverted color against text-color background) to indicate that it
    has been chosen.
    """

    def __init__(self, text="", image=None, anchor=ANCHOR_CENTER, menu=None,
                 disabled=False):
        Control.__init__(self, disabled=disabled)
        self.text = text
        self.image = image
        self.sprite = None
        self.anchor = anchor
        self.menu = menu
        self.label = None
        self.background = None
        self.highlight = None
        self.is_selected = False

    def delete(self):
        if self.label is not None:
            self.label.delete()
            self.label = None
        if self.background is not None:
            self.background.delete()
            self.background = None
        if self.highlight is not None:
            self.highlight.delete()
            self.highlight = None
        if self.sprite is not None:
            self.sprite.delete()
            self.sprite = None

    def expand(self, width, height):
        self.width = width
        self.height = height

    def is_expandable(self):
        return True

    def layout(self, x, y):
        self.x, self.y = x, y
        if self.background is not None:
            self.background.update(x, y, self.width, self.height)
        if self.highlight is not None:
            self.highlight.update(x, y, self.width, self.height)

        font = self.label.document.get_font()
        height = font.ascent - font.descent
        '''labelX, labelY = GetRelativePoint(self, self.anchor,
                                Widget(self.label.content_width, height),
                                self.anchor, (0, 0))'''
        self.label.x = x + 100
        self.label.y = y + height + 60

        # gen sprite pos
        '''spriteX, spriteY = GetRelativePoint(self, self.anchor,
                                Widget(self.image.width, self.image.height),
                                self.anchor, (self.label.content_width, 0))'''
        self.sprite.x = self.label.x + self.label.content_width + 150
        self.sprite.y = y + 25

    def on_gain_highlight(self):
        Control.on_gain_highlight(self)
        self.size(self.saved_dialog)  # to set up the highlight
        if self.highlight is not None:
            self.highlight.update(self.x, self.y,
                                  self.menu.width, self.height)

    def on_lose_highlight(self):
        Control.on_lose_highlight(self)
        if self.highlight is not None:
            self.highlight.delete()
            self.highlight = None

    def on_mouse_release(self, x, y, button, modifiers):
        self.menu.select(self.text)

    def select(self):
        if self.is_disabled():
            return  # disabled options can't be selected

        self.is_selected = True
        if self.label is not None:
            self.label.delete()
            self.label = None
        self.saved_dialog.set_needs_layout()

    def size(self, dialog):
        if dialog is None:
            return
        Control.size(self, dialog)
        if self.is_selected:
            path = ['menuoption', 'selection']
        else:
            path = ['menuoption']
        if self.label is None:
            if self.is_disabled():
                color = dialog.theme[path]['disabled_color']
            else:
                color = dialog.theme[path]['text_color']
            self.label = KyttenLabel(self.text,
                                     color=color,
                                     font_name=dialog.theme[path]['font'],
                                     font_size=dialog.theme[path]['font_size'],
                                     batch=dialog.batch,
                                     group=dialog.fg_group)
            font = self.label.document.get_font()

            if self.is_disabled():
                opacity = 50
                color = dialog.theme[path]['disabled_color']
            else:
                opacity = 255
                color = dialog.theme[path]['text_color']
            self.sprite = pyglet.sprite.Sprite(
                self.image, batch=dialog.batch, group=dialog.fg_group)
            self.sprite.opacity = opacity
            self.sprite.scale = 0.5

            self.width = self.label.content_width + self.sprite.width + 250 + 60
            # self.height = max(font.ascent - font.descent, self.sprite.height)
            # self.width = 1000
            self.height = 200

        if self.background is None:
            if self.is_selected:
                self.background = \
                    dialog.theme[path]['highlight']['image'].generate(
                        dialog.theme[path]['gui_color'],
                        dialog.batch,
                        dialog.bg_group)
        if self.highlight is None:
            if self.is_highlight():
                self.highlight = \
                    dialog.theme[path]['highlight']['image'].generate(
                        dialog.theme[path]['highlight_color'],
                        dialog.batch,
                        dialog.highlight_group)

    def unselect(self):
        self.is_selected = False
        if self.label is not None:
            self.label.delete()
            self.label = None
        if self.background is not None:
            self.background.delete()
            self.background = None
        self.saved_dialog.set_needs_layout()

    def teardown(self):
        self.menu = None
        Control.teardown(self)


'''
    class ItemMenu
'''


class ItemMenu(VerticalLayout):
    """
    Menu is a VerticalLayout of MenuOptions.  Moving the mouse across
    MenuOptions highlights them; clicking one selects it and causes Menu
    to send an on_click event.
    """

    def __init__(self, options=[], align=HALIGN_CENTER, padding=4,
                 on_select=None):
        names = list()
        for option in options:
            names.append(option[0])
        self.align = align
        menu_options = self._make_options(options)
        self.options = dict(list(zip(names, menu_options)))
        self.on_select = on_select
        self.selected = None
        VerticalLayout.__init__(self, menu_options,
                                align=align, padding=padding)

    def _make_options(self, options):
        menu_options = []
        for option in options:
            if option[0].startswith('-'):
                disabled = True
                option = option[1:]
            else:
                disabled = False
            menu_options.append(Item(option[0], image=option[1],
                                     anchor=(VALIGN_CENTER, self.align),
                                     menu=self,
                                     disabled=disabled))
        return menu_options

    def get_value(self):
        return self.selected

    def is_input(self):
        return True

    def select(self, text):
        if not text in self.options:
            return

        if self.selected is not None:
            self.options[self.selected].unselect()
        self.selected = text
        menu_option = self.options[text]
        menu_option.select()

        if self.on_select is not None:
            self.on_select(text)

    def set_options(self, options):
        self.delete()
        self.selected = None
        menu_options = self._make_options(options)
        self.options = dict(list(zip(options, menu_options)))
        self.set(menu_options)
        self.saved_dialog.set_needs_layout()

    def teardown(self):
        self.on_select = None
        VerticalLayout.teardown(self)


'''
    class PaletteOption
'''


class PaletteOption(Control):
    def __init__(self, name, image, scale_size=None, anchor=ANCHOR_CENTER,
                 palette=None, disabled=False, padding=0):
        Control.__init__(self, disabled=disabled)
        self.id = name
        self.image = image
        self.scale_size = scale_size
        self.anchor = anchor
        self.palette = palette
        self.sprite = None
        self.background = None
        self.highlight = None
        self.is_selected = False
        self.padding = padding

    def delete(self):
        if self.sprite is not None:
            self.sprite.delete()
            self.sprite = None
        if self.background is not None:
            self.background.delete()
            self.background = None
        if self.highlight is not None:
            self.highlight.delete()
            self.highlight = None

            # ~ def expand(self, width, height):
            # ~ self.width = width
            # ~ self.height = height

            # ~ def is_expandable(self):
            # ~ return False

    def layout(self, x, y):
        self.x, self.y = x, y
        if self.background is not None:
            self.background.update(x, y, self.width, self.height)
        if self.highlight is not None:
            self.highlight.update(x, y, self.width, self.height)
        # height = 32 #self.tile_height
        w, h = self.sprite.width, self.sprite.height
        x, y = GetRelativePoint(self, self.anchor,
                                Widget(w, h),
                                self.anchor, (0, 0))
        self.sprite.x = x  # + self.padding / 2
        self.sprite.y = y  # + self.padding / 2

        # ~ def on_gain_highlight(self):
        # ~ Control.on_gain_highlight(self)

        # ~ def on_lose_highlight(self):
        # ~ Control.on_lose_highlight(self)

    def on_mouse_release(self, x, y, button, modifiers):
        self.palette.select(self.id)  # (self.text)

    def select(self):
        if self.is_disabled():
            return  # disabled options can't be selected
        self.is_selected = True
        self.size(self.saved_dialog)  # to set up the highlight
        if self.highlight is not None:
            self.highlight.update(self.x, self.y,
                                  self.width, self.height)
        if self.saved_dialog is not None:
            self.saved_dialog.set_needs_layout()

    def size(self, dialog):
        if dialog is None:
            return
        Control.size(self, dialog)
        if self.is_selected:
            path = ['menuoption', 'selection']
        else:
            path = ['menuoption']
        if self.sprite is None:
            if self.is_disabled():
                opacity = 50
                color = dialog.theme[path]['disabled_color']
            else:
                opacity = 255
                color = dialog.theme[path]['text_color']
            self.sprite = pyglet.sprite.Sprite(
                self.image, batch=dialog.batch, group=dialog.fg_group)  # , y=y, x=x, batch=self.tiles_batch)
            self.sprite.opacity = opacity
            if self.scale_size is not None:
                self.sprite.scale = self.scale_size / float(self.sprite.width)
            self.width = self.sprite.width + self.padding * 2
            self.height = self.sprite.height + self.padding * 2

            # ~ if self.background is None:
            # ~ if self.is_selected:
            # ~ self.background = \
            # ~ dialog.theme[path]['highlight']['image'].generate(
            # ~ dialog.theme[path]['gui_color'],
            # ~ dialog.batch,
            # ~ dialog.bg_group)

        if self.highlight is None:
            if self.is_selected:
                self.highlight = \
                    dialog.theme[path]['palette']['image'].generate(
                        dialog.theme[path]['input']['gui_color'],
                        dialog.batch,
                        dialog.highlight_group)

    def unselect(self):
        self.is_selected = False
        if self.highlight is not None:
            self.highlight.delete()
            self.highlight = None
        if self.background is not None:
            self.background.delete()
            self.background = None
        if self.saved_dialog is not None:
            self.saved_dialog.set_needs_layout()

    def teardown(self):
        self.palette = None
        self.image = None
        Control.teardown(self)


'''
    class PaletteMenu
    Palette is a GridLayout of PaletteOptions.  Clicking a PaletteOption
    selects it and causes Palette to send an on_click event.
'''


class PaletteMenu(GridLayout):

    def __init__(self, options=[[]], padding=2, on_select=None, initialSelection=None):
        # ~ menu_options = self._make_options(options)

        GridLayout.__init__(self, options, padding=padding)
        self.on_select = on_select
        self.selected = None
        self.options = {}
        for row in options:
            for option in row:
                self.options[option.id] = option
                if option is not None:
                    option.palette = self
        if initialSelection:
            self.selected = self.options[initialSelection]
            self.selected.select()

    '''
    #~ def _make_options(self, options):
        #~ menu_options = []
        #~ for option in options:
            #~ if option.startswith('-'):
                #~ disabled = True
                #~ option = option[1:]
            #~ else:
                #~ disabled = False
            #~ menu_options.append(MenuOption(option,
                                           #~ anchor=(VALIGN_CENTER, self.align),
                                           #~ menu=self,
                                           #~ disabled=disabled))
        #~ return menu_options'''

    def get_value(self):
        return self.selected

    def is_input(self):
        return True

    def select(self, id):
        if self.selected is not None:
            self.selected.unselect()
        self.selected = self.options[id]
        self.selected.select()
        if self.on_select is not None:
            self.on_select(id)
            # print self.selected

    def set_options(self, options):
        self.delete()
        self.selected = None
        # menu_options = self._make_options(options)
        # self.options = dict(zip(options, menu_options))

        # ~ i = 0
        # ~ for row in option:
        # ~ j = 0
        # ~ for cell in row:
        # ~ self.set(cell)
        # ~ j++
        # ~ i++
        # ~ self.set(menu_options)
        self.saved_dialog.set_needs_layout()

    def teardown(self):
        self.on_select = None
        GridLayout.teardown(self)


'''
    class ClickMenu
    A menu that does not stay selected.
'''


class ClickMenu(Menu):
    def __init__(self, options=[], align=HALIGN_CENTER, padding=4,
                 on_select=None, option_padding_x=0, option_padding_y=0):
        Menu.__init__(self, options=options, align=align,
                      padding=padding, on_select=on_select,
                      option_padding_x=option_padding_x,
                      option_padding_y=option_padding_y)

    def select(self, text):
        if not text in self.options:
            return

        if self.selected is not None:
            self.options[self.selected].unselect()
        self.selected = text
        menu_option = self.options[text]
        # menu_option.select()

        if self.on_select is not None:
            self.on_select(text)
