import sqlite3

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.popup import Popup
from receita import Receita, ReceitaListaItem
from datagrid import *


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

        # Selecionar a tabela 'joint'
        cursor.execute('SELECT * FROM joint_new')
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

        # Selecionar a tabela 'receitas' para carregar todas as receitas
        cursor.execute('SELECT * FROM receitas_new')
        receitas_nomes = cursor.fetchall()
        for receita in receitas_nomes:
            self.lista_receitas.append(
                Receita(receita[0],
                        receita[1],
                        tuple(receitas_ids[receita[0]]),
                        receita[2]
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

            # Selecionar os ingredientes da tabela 'ingredientes'
            cursor.execute("SELECT id FROM ingredientes_new WHERE ingrediente = ?", (ingrediente,))
            data = cursor.fetchall()

            if len(data) > 0:
                ingredientes_ids.append(data[0][0])

        if len(ingredientes_ids) == 0:
            return []

        # Agora comparar e rankear as receitas com o maior numero de ingredientes presentes
        # Salvar resultados numa lista chamado rank, que contem o ID da receita e a porcentagem de itens existentes
        rank = []
        entregar = []

        for x in range(0, len(self.lista_receitas)):
            resultado = self.lista_receitas[x].presenca_ingredientes(tuple(ingredientes_ids))

            rank.append((x, float(resultado[2]/resultado[0]), resultado[0], resultado[2]))

        sorted_rank = sorted(rank, key=lambda y: y[1], reverse=True)

        for sorted_item in sorted_rank:
            # Essa é a lista que entregamos no return
            entregar.append((self.lista_receitas[sorted_item[0]],
                             sorted_item[1],
                             sorted_item[2],
                             sorted_item[3]))

        return entregar

    def buscar_todos(self):
        rank = self.buscar()
        itens_possiveis = []

        if len(rank) == 0:
            popup = Popup(
                content=Label(
                    text='Desculpe. Não foi encontrada nenhuma receita com esses ingredientes, tente com outros.',
                    halign='center',
                    valign='middle',
                    text_size=(180, 100)),
                title='Ops!',
                size_hint=(None, None),
                size=(200, 200))
            popup.open()

            return

        for item in rank:
            if item[1] >= float(1.0):
                itens_possiveis.append(item)

        # Mudar tela para os resultados da pesquisa
        self.mudar_tela(itens_possiveis)

    def buscar_alguns(self):
        rank = self.buscar()
        itens_possiveis = []

        if len(rank) == 0:
            popup = Popup(
                content=Label(text='Desculpe. Não foi encontrada nenhuma receita com esses ingredientes, tente com outros.',
                                halign='center',
                              valign='middle',
                              text_size=(180, 100)),
            title='Ops!',
            size_hint=(None, None),
            size=(200, 200))
            popup.open()

            return

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


# Cria a janela das receitas encontradas
class ListaReceitas(Screen):
    def on_pre_enter(self, *args):
        lista_receitas = App.get_running_app().temp

        self.ids.listaReceitas.set_header('Receita', 'Ingredientes')

        for receita in lista_receitas:
            self.ids.listaReceitas.add_row(ReceitaListaItem(receita[0].nome, receita[2], receita[3]))

    def mudar_para_detalhe(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'detalhe'


# Aqui é onde montamos do detalhe da receita selecionada
class DetalheReceita(Screen):
    def on_enter(self, *args):
        # Carregar a lista de receitas para identificar a receita selecionada
        # E também cerregar o index do item clicado na lista
        # Dessa forma, conseguimos saber qual foi a receita clicada

        lista_receitas = App.get_running_app().temp
        selecionado = App.get_running_app().selecionado

        item_selecionado = lista_receitas[int(selecionado)]
        self.ids.idreceita.text = item_selecionado[0].descricao

        # TODO colocar bonito os ingredientes necessarios pra cada receita e quais ingredientes têm na tela anterior


# Classe do aplicativo
class ReceitasLegaisApp(App):
    def build(self):
        Window.size = (300, 400)

        sm = ScreenManager()

        buscar_ingredientes = Ingredientes(name='buscar')
        lista_receitas = ListaReceitas(name='lista')
        detalhe_receita = DetalheReceita(name='detalhe')

        sm.add_widget(buscar_ingredientes)
        sm.add_widget(lista_receitas)
        sm.add_widget(detalhe_receita)

        # variavel que servira para auxiliar na manipulacao de
        # conteudo entre diferentes janelas
        self.temp = None
        self.selecionado = None

        # retorna a instancia do ScreenManager
        # como widget principal da aplicacao
        return sm


aplicativo = ReceitasLegaisApp()
aplicativo.run()
