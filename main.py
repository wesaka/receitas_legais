from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


# Cria a janela do menu principal
class MenuPrincipal(Screen):

    def muda_janela(self):
        # coloca o numero digitado na variavel temporaria para
        # ser usada entre janelas distintas
        App.get_running_app().temp = self.ids.tx.text

        # janela faz um transicao (movimento) para a esquerda
        self.manager.transition.direction = 'left'

        # seta a janela atual para a secundaria...
        self.manager.current = 'secundaria'


# Cria uma janela secundaria
class OutraJanela(Screen):

    def mostra_mensagem(self):
        # Recupera o texto da variavel e coloca no label da
        # outra janela
        self.ids.mensagem.text = App.get_running_app().temp


# Classe do aplicativo
class MeuApp(App):
    def build(self):
        Window.size = (300, 400)

        sm = ScreenManager()

        menu_principal = MenuPrincipal(name='menu')

        sm.add_widget(menu_principal)
        sm.add_widget(OutraJanela(name='secundaria'))

        # variavel que servira para auxiliar na manipulacao de
        # conteudo entre diferentes janelas
        self.temp = ''

        # retorna a instancia do ScreenManager
        # como widget principal da aplicacao
        return sm


aplicativo = MeuApp()
aplicativo.run()
