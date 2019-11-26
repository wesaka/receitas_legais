# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:19:44 2019

@author: Arnaldo Muller Jr
"""
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout


# classe básica para dados
class DataGridDataClass:
    # sobrescrever esse método para popular as colunas
    def get_lista(self):
        pass


# Adiciona o controle de foco e seleção na view
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):

    def __init__(self, **kwargs):
        self.spacing = dp(2)
        self.orientation = 'vertical'
        self.default_size = (None, dp(35))
        self.default_size_hint = (1, None)
        self.size_hint_y = None

        super().__init__(**kwargs)

    def on_minimum_height(self, instance, value):
        self.height = value


# BoxLayout que representa uma linha de dados
class ListRow(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.orientation = 'horizontal'
        super().__init__(**kwargs)

    def on_selected(self, instance, value):
        with self.canvas.before:
            if self.selected:
                Color(.0, 0.9, .1, .3)
            else:
                Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)

    # chamado quando a recycleview precisa criar uma linha
    def refresh_view_attrs(self, rv, index, data):
        self.index = index

        # obtem a lista de colunas
        vals = data["data"].get_lista()

        # cria todas as colunas
        while len(self.children) < len(vals):
            self.add_widget(Label(text=''))
        while len(self.children) > len(vals):
            self.remove_widget(self.children[-1])

        # aplica os dados aos labels das colunas
        i = len(self.children) - 1
        for w in self.children:
            w.text = str(vals[i])
            i -= 1

        return super().refresh_view_attrs(rv, index, data)

    # Adiciona a seleção por touch_down
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return False
        if self.collide_point(*touch.pos) and self.selectable:
            # Mudar a tela para a receita
            App.get_running_app().selecionado = self.index

            return self.parent.select_with_touch(self.index, touch)

    # resposta à selecão de um iem na vista.
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


# subclasse de RecycleView. Controla o processo inteiro
class DataGridRows(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(SelectableRecycleBoxLayout())
        self.viewclass = 'ListRow'


class DataGrid(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        self._header = BoxLayout()
        self._header.size_hint_y = None
        self._header.height = dp(40)
        self._header.orientation = 'horizontal'
        self.add_widget(self._header)

        self._rows = DataGridRows()
        self.add_widget(self._rows)

    def set_header(self, *headers):
        self._header.clear_widgets()
        for header in headers:
            self._header.add_widget(Label(text=header))

        with self._header.canvas.before:
            Color(0.5, 0.5, 0.5, 1)
            Rectangle(pos=self._header.pos, size=self._header.size)

    def clear_data(self):
        self._rows.data = []

    def add_row(self, *rows):
        if self._rows.data is None:
            self._rows.data = []

        for row in rows:
            self._rows.data.append({"data": row})
