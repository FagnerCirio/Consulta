from database import conn, cursor

def inserir_agendamento(nome, especialidade, data, horario):
    cursor.execute("INSERT INTO agendamentos (nome, especialidade, data, horario) VALUES (?, ?, ?, ?)",
                   (nome, especialidade, data, horario))
    conn.commit()

def inserir_caixa(tipo, descricao, valor):
    cursor.execute("INSERT INTO caixa (tipo, descricao, valor) VALUES (?, ?, ?)",
                   (tipo, descricao, valor))
    conn.commit()

def listar_agendamentos():
    cursor.execute("SELECT * FROM agendamentos ORDER BY data, horario")
    return cursor.fetchall()

def listar_caixa():
    cursor.execute("SELECT * FROM caixa ORDER BY id DESC")
    return cursor.fetchall()
