import sqlite3

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.core.window import Window
from receita import Receita


# Cria a janela do menu principal
class Ingredientes(Screen):
    lista_receitas = list()

    def carregar_itens(self):
        # Primeiro, ter certeza que estamos zerando a lista de receitas
        self.lista_receitas = list()

        # Inicializar a conexao
        conn = sqlite3.connect('receitas.sqlite')

        # Carregar a joint na memoria para analisar quais receitas tem quais ingredientes
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM joint')
        joint = cursor.fetchall()

        # Juntar cada receita num unico id com todos os ingredientes
        receitas_ids = {}
        for item in joint:
            if item[0] not in receitas_ids.keys():
                # true se existir na busca false se nao
                receitas_ids[item[0]] = [item[1]]

            else:
                temp_list = receitas_ids[item[0]]
                temp_list.append(item[1])
                receitas_ids[item[0]] = temp_list

        # Carregar receitas do banco e montar uma lista
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM receitas')
        receitas_nomes = cursor.fetchall()
        for receita in receitas_nomes:
            self.lista_receitas.append(
                Receita(receita[0],
                        receita[1],
                        tuple(receitas_ids[receita[0]])
                        )
            )

        print("completo")

    def buscar(self):
        # Checar o tamanho da lista
        if len(self.lista_receitas) == 0:
            return

        ingredientes = self.ids.ingredientes.text
        ingredientes_lista = ingredientes.lower().split('\n')
        ingredientes_ids = []

        # Pegar o id de cada ingrediente na lista dada pelo usuario
        # Montar um tuple com a sequencia dos ingredientes dados
        conn = sqlite3.connect('receitas.sqlite')

        for ingrediente in ingredientes_lista:
            if ingrediente is '':
                ingredientes_lista.remove(ingrediente)
                continue

            cursor = conn.cursor()
            cursor.execute("SELECT id FROM ingredientes WHERE ingrediente = ?", (ingrediente,))
            ingredientes_ids.append(cursor.fetchall()[0][0])

        # Agora comparar e rankear as receitas com o maior numero de ingredientes presentes
        # Salvar resultados num mapa chamado rank
        rank = dict()

        for receita in self.lista_receitas:
            resultado = receita.presenca_ingredientes(tuple(ingredientes_ids))
            rank[receita.nome] = float(resultado[2] / resultado[0])

        return sorted(rank.items(), key=lambda x: x[1], reverse=True)

    def buscar_todos(self):
        rank = self.buscar()
        itens_possiveis = []

        for item in rank:
            if item[1] >= float(1.0):
                itens_possiveis.append(item)

        # Mudar tela para os resultados da pesquisa
        self.mudar_tela(itens_possiveis)

    def buscar_alguns(self):
        rank = self.buscar()
        itens_possiveis = []

        for item in rank:
            if item[1] > 0:
                itens_possiveis.append(item)

        # Mudar tela para os resultados da pesquisa
        self.mudar_tela(itens_possiveis)

    def on_pre_enter(self, *args):
        self.carregar_itens()

    def mudar_tela(self, list_receitas):
        App.get_running_app().temp = list_receitas

        self.manager.transition.direction = 'left'
        self.manager.current = 'lista'




        # TODO Iterar para cada receita quais sao os ingredientes presentes


# Classe para definir cada item da lista de receitas encontradas
class LabelReceita(Label):
    def on_touch_up(self, touch):
        print(touch)


# Cria a janela das receitas encontradas
class ListaReceitas(Screen):
    def on_pre_enter(self, *args):
        lista_receitas = App.get_running_app().temp

        for receita in lista_receitas:
            self.ids.box.add_widget(LabelReceita(text=receita[0]))


# Classe do aplicativo
class ReceitasLegaisApp(App):
    def build(self):
        Window.size = (300, 400)

        sm = ScreenManager()

        buscar_ingredientes = Ingredientes(name='buscar')
        lista_receitas = ListaReceitas(name='lista')

        sm.add_widget(buscar_ingredientes)
        sm.add_widget(lista_receitas)

        # variavel que servira para auxiliar na manipulacao de
        # conteudo entre diferentes janelas
        self.temp = None

        # retorna a instancia do ScreenManager
        # como widget principal da aplicacao
        return sm


aplicativo = ReceitasLegaisApp()
aplicativo.run()
