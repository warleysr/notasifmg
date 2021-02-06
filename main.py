""""
IFMG Notas - Aplicativo (não muito útil) para verificar as notas no AVA (Moodle)
de cursos do Campus Betim, sem precisar ficar fazendo login
"""
from PySimpleGUI import PySimpleGUI as Sg
from pathlib import Path
import ifmgavascraper as ava


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
        [Sg.Image("ifmglogo.png")],
        [Sg.Text("RA:", font=font_str, text_color="green")],
        [Sg.Input(key="-RA-", font=font_str, size=(25, 1), default_text=user if user else "")],
        [Sg.Text("Senha:", font=font_str, text_color="green")],
        [Sg.Input(key="-PASS-", password_char="•", font=font_str, size=(25, 1))],
        [Sg.Checkbox("Salvar login", key="-SAVE-", font="Helvitica 12", default=True if user else False)],
        [Sg.Submit("Buscar notas", font=font_str, button_color=("white", "green"))]
    ]
    return Sg.Window("Login - AVA IFMG (Betim)", layout)


# Janela para mostrar os cursos e notas
def grades_window(user, grades_dict):
    Sg.theme("Reddit")
    tab_group = []

    i = 1
    for curso in grades_dict:
        notas = grades[curso]
        tab_lay = [[Sg.Text(curso, font="Helvitica 16 bold", text_color="#5534eb")],
                   [Sg.Table(values=notas,
                             headings=["Atividade", "Nota"],
                             background_color="lightgray",
                             alternating_row_color="lightgreen",
                             font="Helvitica 12 bold",
                             auto_size_columns=True,
                             max_col_width=50)]]
        tab = [Sg.Tab(f"Curso {i}", tab_lay)]
        tab_group.append(tab)
        i += 1

    layout = [[Sg.TabGroup(tab_group)]]

    return Sg.Window(f"Suas notas - {user}", layout, resizable=True)


# Execução do programa
lw = login_window()
while True:
    event, values = lw.read()
    if event == Sg.WINDOW_CLOSED:
        break
    elif event == "Buscar notas":
        lw.hide()
        ra = values["-RA-"]
        senha = values["-PASS-"]
        save = values["-SAVE-"]

        if save:
            try:
                f = open(str(Path.home()) + "/.ifmgscraper.cfg", "w+")
                f.write(ra)
                f.close()
            except IOError:
                pass

        login = ava.get_grades(ra, senha)
        if login is None:
            Sg.popup_error("Não foi possível obter suas informações. Confira o RA e a senha e tente novamente.",
                           title="Erro de login", background_color="gray", text_color="white", font="Helvitica 12 bold")
            lw.un_hide()
        else:
            grades = ava.get_specific_grades(*login)
            gw = grades_window(ra, grades)
            while True:
                evt, val = gw.read()
                if evt == Sg.WINDOW_CLOSED:
                    lw.un_hide()
                    break
