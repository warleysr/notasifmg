import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import re


def get_grades(ra, senha):
    """
    Função que realiza login no AVA e busca os cursos do aluno
    :param ra: Registro Academico para login
    :param senha: Senha para login
    :return: Dict (Nome do Aluno, Nomes dos Cursos, Links Específicos), Sessão, Cookies
    """
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
        + "Chrome/47.0.2526.111 Safari/537.36"
    }

    # Requisição inicial para obter o "logintoken"
    login_url = "https://ava.betim.ifmg.edu.br/moodle/login/index.php"
    req = session.get(login_url, headers=headers, verify=False)
    token = BeautifulSoup(req.content, "html.parser").find(
        "input", {"name": "logintoken"}
    )["value"]

    # Requisição POST para realizar login no AVA, passando os dados de login
    payload = {"username": ra, "password": senha, "logintoken": token}
    req = session.post(login_url, data=payload, headers=headers, verify=False)

    aluno = BeautifulSoup(req.content, "html.parser").find(
        "span", {"class": "usertext mr-1"}
    )
    if aluno is None:
        return None
    aluno = aluno.get_text()

    # Requisição para obter lista de cursos e os links para analisar notas
    req = session.get(
        "https://ava.betim.ifmg.edu.br/moodle/grade/report/overview/index.php?id=318",
        cookies=req.cookies.get_dict(),
        verify=False,
    )

    # Obter tabela e extrair informações com o "parser" de HTML
    soup = BeautifulSoup(req.content, "html.parser")
    tabela = soup.find("table", {"id": "overview-grade"})

    # Se não encontrar a tabela, provavel erro de login
    if tabela is None:
        return tabela

    today = datetime.today()
    current_semester = f"{today.year}.{1 if today.month <= 7 else 2}"

    cursos = tabela.find_all("td", {"class": "cell c0"})
    cursos = [c.find("a") for c in cursos]
    nomes = [
        c.text for c in cursos if c is not None and re.match(current_semester, c.text)
    ]
    links = [c["href"] for c in cursos if c is not None and c.text in nomes]

    return dict(aluno=aluno, cursos=nomes, links=links), session, req.cookies.get_dict()


def get_specific_grades(data, session, cookies):
    """
    Função que obtém as notas dos cursos no AVA
    :param data: Dicionário contendo aluno, nomes dos cursos e links específicos
    :param session: Sessão para realizar requisições
    :param cookies: Cookies usados no login inicial
    :return: Dicionário com aluno e cursos dict {chave nome e valor (atividade, nota)}
    """
    grades = dict(aluno=data["aluno"], cursos={})

    for i in range(len(data["cursos"])):
        curso = data["cursos"][i]
        link = data["links"][i]

        # Requisição para o link específico do curso
        req = session.get(link, cookies=cookies, verify=False)

        # Obter tabela de atividades e notas do curso
        soup = BeautifulSoup(req.content, "html.parser")
        tabela = soup.find("table", {"class": "boxaligncenter generaltable user-grade"})
        body = tabela.find("tbody")

        # Extrair atividades
        atividades = []
        for atividade in body.find_all("th"):
            atv = atividade.find("a")
            if atv is not None:
                atividades.append(atv.get_text())

        # Extrair notas
        notas = []
        for nota in body.find_all("td", class_="column-grade"):
            notas.append(nota.get_text())

        # Associar atividades e notas e colocar no dicionario
        grades["cursos"][curso] = list(zip(atividades, notas))

    return grades
