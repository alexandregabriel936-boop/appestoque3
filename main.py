from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import sqlite3
from datetime import datetime

BANCO = "estoque.db"


# ==========================
# BANCO
# ==========================
def conectar():
    return sqlite3.connect(BANCO)


# ==========================
# POPUP INPUT
# ==========================
def popup_input(titulo, callback):
    layout = BoxLayout(
        orientation="vertical",
        spacing=10,
        padding=10
    )

    entrada = TextInput(
        multiline=False
    )

    btn = Button(
        text="Confirmar",
        size_hint_y=None,
        height=50
    )

    layout.add_widget(Label(text=titulo))
    layout.add_widget(entrada)
    layout.add_widget(btn)

    popup = Popup(
        title=titulo,
        content=layout,
        size_hint=(0.8, 0.4)
    )

    btn.bind(
        on_press=lambda x: (
            callback(entrada.text),
            popup.dismiss()
        )
    )

    popup.open()


# ==========================
# APP
# ==========================
class EstoqueApp(App):

    def build(self):
        self.layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )

        titulo = Label(
            text="Controle de Almoxarifado",
            size_hint_y=None,
            height=60
        )

        self.layout.add_widget(titulo)

        botoes = [
            ("Cadastrar Material", self.cadastrar_material),
            ("Entrada", self.entrada_material),
            ("Saída", self.saida_material),
            ("Ver Estoque", self.ver_estoque)
        ]

        for texto, funcao in botoes:
            btn = Button(
                text=texto,
                size_hint_y=None,
                height=60
            )
            btn.bind(on_press=funcao)
            self.layout.add_widget(btn)

        return self.layout

    # ==========================
    # CADASTRAR
    # ==========================
    def cadastrar_material(self, instance):

        def salvar_nome(nome):

            def salvar_unidade(unidade):

                def salvar_quantidade(qtd):

                    def salvar_minimo(minimo):

                        def salvar_local(local):
                            conn = conectar()
                            cursor = conn.cursor()

                            cursor.execute("""
                                INSERT INTO estoque
                                (
                                    Material,
                                    Unidade,
                                    Quantidade,
                                    Estoque_Minimo,
                                    Localizacao
                                )
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                nome,
                                unidade,
                                int(qtd),
                                int(minimo),
                                local
                            ))

                            conn.commit()
                            conn.close()

                        popup_input(
                            "Localização",
                            salvar_local
                        )

                    popup_input(
                        "Estoque mínimo",
                        salvar_minimo
                    )

                popup_input(
                    "Quantidade inicial",
                    salvar_quantidade
                )

            popup_input(
                "Unidade",
                salvar_unidade
            )

        popup_input(
            "Nome do material",
            salvar_nome
        )

    # ==========================
    # ENTRADA
    # ==========================
    def entrada_material(self, instance):

        def pegar_nome(nome):

            def pegar_qtd(qtd):
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE estoque
                    SET Quantidade = Quantidade + ?
                    WHERE Material = ?
                """, (
                    int(qtd),
                    nome
                ))

                cursor.execute("""
                    INSERT INTO movimentacoes
                    (
                        data,
                        tipo,
                        material,
                        quantidade,
                        destino,
                        observacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().strftime("%d/%m/%Y"),
                    "Entrada",
                    nome,
                    int(qtd),
                    "",
                    ""
                ))

                conn.commit()
                conn.close()

            popup_input(
                "Quantidade",
                pegar_qtd
            )

        popup_input(
            "Material",
            pegar_nome
        )

    # ==========================
    # SAÍDA
    # ==========================
    def saida_material(self, instance):

        def pegar_nome(nome):

            def pegar_qtd(qtd):
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT Quantidade
                    FROM estoque
                    WHERE Material = ?
                """, (nome,))

                resultado = cursor.fetchone()

                if not resultado:
                    conn.close()
                    return

                qtd_atual = resultado[0]

                if int(qtd) > qtd_atual:
                    conn.close()
                    return

                cursor.execute("""
                    UPDATE estoque
                    SET Quantidade = Quantidade - ?
                    WHERE Material = ?
                """, (
                    int(qtd),
                    nome
                ))

                cursor.execute("""
                    INSERT INTO movimentacoes
                    (
                        data,
                        tipo,
                        material,
                        quantidade,
                        destino,
                        observacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().strftime("%d/%m/%Y"),
                    "Saída",
                    nome,
                    int(qtd),
                    "",
                    ""
                ))

                conn.commit()
                conn.close()

            popup_input(
                "Quantidade",
                pegar_qtd
            )

        popup_input(
            "Material",
            pegar_nome
        )

    # ==========================
    # VER ESTOQUE
    # ==========================
    def ver_estoque(self, instance):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                Material,
                Unidade,
                Quantidade,
                Estoque_Minimo,
                Localizacao
            FROM estoque
        """)

        dados = cursor.fetchall()

        conn.close()

        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
            size_hint_y=None
        )

        layout.bind(
            minimum_height=layout.setter("height")
        )

        for item in dados:
            texto = (
                f"Material: {item[0]}\n"
                f"Unidade: {item[1]}\n"
                f"Quantidade: {item[2]}\n"
                f"Mínimo: {item[3]}\n"
                f"Local: {item[4]}"
            )

            layout.add_widget(
                Label(
                    text=texto,
                    size_hint_y=None,
                    height=150
                )
            )

        scroll = ScrollView()
        scroll.add_widget(layout)

        popup = Popup(
            title="Estoque",
            content=scroll,
            size_hint=(0.9, 0.9)
        )

        popup.open()


if __name__ == "__main__":
    EstoqueApp().run()