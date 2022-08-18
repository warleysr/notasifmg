from PySimpleGUI import PySimpleGUI as Sg
from pathlib import Path
import ifmgavascraper as ava
import sys
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Janela de login
def login_window():
    user = ""
    try:
        fl = open(str(Path.home()) + "/.ifmgscraper.cfg", "r")
        user = fl.readline()
        fl.close()
    except IOError:
        pass

    Sg.theme("Reddit")
    font_str = "Helvitica 15 bold"
    layout = [
        [Sg.Image(resource_path("ifmglogo.png"))],
        [Sg.Text("RA:", font=font_str, text_color="green")],
        [
            Sg.Input(
                key="-RA-",
                font=font_str,
                size=(25, 1),
                default_text=user if user else "",
            )
        ],
        [Sg.Text("Senha:", font=font_str, text_color="green")],
        [Sg.Input(key="-PASS-", password_char="•", font=font_str, size=(25, 1))],
        [
            Sg.Checkbox(
                "Salvar login",
                key="-SAVE-",
                font="Helvitica 12",
                default=True if user else False,
            )
        ],
        [Sg.Submit("Buscar notas", font=font_str, button_color=("white", "green"))],
    ]
    return Sg.Window("Notas IFMG - AVA Betim", layout)


# Janela para mostrar os cursos e notas
def grades_window(grades_dict):
    Sg.theme("Reddit")
    tab_group = []

    i = 1
    for curso in grades_dict["cursos"]:
        notas = grades_dict["cursos"][curso]

        if len(notas) == 0:
            notas.append(("", ""))

        tab_lay = [
            [Sg.Text(curso, font="Helvitica 16 bold", text_color="#5534eb")],
            [
                Sg.Table(
                    values=notas,
                    headings=["Atividade", "Nota"],
                    background_color="lightgray",
                    alternating_row_color="lightgreen",
                    font="Helvitica 12 bold",
                    auto_size_columns=True,
                    max_col_width=50,
                )
            ],
        ]
        tab = [Sg.Tab(f"Curso {i}", tab_lay)]
        tab_group.append(tab)
        i += 1

    layout = [[Sg.TabGroup(tab_group)]]

    return Sg.Window(
        f"{grades_dict['aluno']} - Notas IFMG - AVA Betim", layout, resizable=True
    )


# Execução do programa
lw = login_window()
while True:
    event, values = lw.read()
    if event == Sg.WINDOW_CLOSED:
        break
    elif event == "Buscar notas":
        ra = values["-RA-"]
        senha = values["-PASS-"]

        if ra == "" or senha == "":
            Sg.popup_error(
                "Preencha os campos RA e senha!",
                title="Erro de login",
                background_color="gray",
                text_color="white",
                font="Helvitica 12 bold",
            )
            continue

        if not ra.isnumeric():
            Sg.popup_error(
                "O campo RA é numérico!",
                title="Erro de login",
                background_color="gray",
                text_color="white",
                font="Helvitica 12 bold",
            )
            continue

        save = values["-SAVE-"]
        arq = f"{str(Path.home())}/.ifmgscraper.cfg"
        if save:
            try:
                f = open(arq, "w+")
                f.write(ra)
                f.close()
            except IOError:
                pass
        elif os.path.isfile(arq):
            os.remove(arq)

        lw.hide()
        login = ava.get_grades(ra, senha)
        if login is None:
            Sg.popup_error(
                "Não foi possível obter suas informações. Confira o RA e senha e tente novamente.",
                title="Erro de login",
                background_color="gray",
                text_color="white",
                font="Helvitica 12 bold",
            )
            lw.un_hide()
        else:
            grades = ava.get_specific_grades(*login)
            gw = grades_window(grades)
            while True:
                evt, val = gw.read()
                if evt == Sg.WINDOW_CLOSED:
                    lw.un_hide()
                    break
