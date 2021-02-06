import requests
from bs4 import BeautifulSoup


def get_grades(ra, senha):
    """
    Função que realiza login no AVA e busca os cursos do aluno
    :param ra: Registro Academico para login
    :param senha: Senha para login
    :return: Nomes dos Cursos, Links Específicos, Sessão, Cookies
    """
    session = requests.Session()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             + "Chrome/47.0.2526.111 Safari/537.36"}

    # Requisição inicial para obter o "logintoken"
    login_url = "https://ava.betim.ifmg.edu.br/moodle/login/index.php"
    req = session.get(login_url, headers=headers, verify=False)
    token = BeautifulSoup(req.content, "html.parser").find("input", {"name": "logintoken"})["value"]

    # Requisição POST para realizar login no AVA, passando os dados de login
    payload = {"username": ra, "password": senha, "logintoken": token}
    req = session.post(login_url, data=payload, headers=headers, verify=False)

    # Requisição para obter lista de cursos e os links para analisar notas
    req = session.get("https://ava.betim.ifmg.edu.br/moodle/grade/report/overview/index.php?id=318",
                      cookies=req.cookies.get_dict(), verify=False)

    # Obter tabela e extrair informações com o "parser" de HTML
    soup = BeautifulSoup(req.content, "html.parser")
    tabela = soup.find("table", {"id": "overview-grade"})

    # Se não encontrar a tabela, provavel erro de login
    if tabela is None:
        return tabela

    cursos = tabela.find_all("td", {"class": "cell c0"})
    cursos = [c.find("a") for c in cursos]
    nomes = [c.contents for c in cursos if c is not None]
    links = [c["href"] for c in cursos if c is not None]

    return nomes, links, session, req.cookies.get_dict()


def get_specific_grades(nomes, links, session, cookies):
    """
    Função que obtém as notas dos cursos no AVA
    :param nomes: Nomes dos cursos
    :param links: Links específicos para consulta das notas
    :param session: Sessão para realizar requisições
    :param cookies: Cookies usados no login inicial
    :return: Dicionário com chave nome do curso e valor tupla (atividade, nota)
    """
    grades = dict()

    for i in range(len(nomes)):
        curso = nomes[i][0]
        grades[curso] = []
        link = links[i]

        # Requisição para o link específico do curso
        req = session.get(link, cookies=cookies, verify=False)

        # Obter tabela de atividades e notas do curso
        soup = BeautifulSoup(req.content, "html.parser")
        tabela = soup.find("table", {"class": "boxaligncenter generaltable user-grade"})
        body = tabela.find("tbody")

        # Selecionar elementos de nome da atividade e valor obtido
        ths = body.select('th')
        tds = body.select('td')

        # Extrair as informações em texto e colocar no dicionário de notas
        for j in range(len(ths)):
            atividade = ths[j].findChild().get_text()
            nota = tds[j].get_text()
            if not atividade or not nota:
                continue
            grades[curso].append((atividade, nota))

    return grades
