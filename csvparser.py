import csv, sqlite3

lista_receitas = {}
index = 1

with open('receitaslegais.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    for row in reader:
        lista_receitas[index] = row
        index = index + 1

csvFile.close()


# Agora, montar a tabela
conn = sqlite3.connect('receitas.sqlite')
cursor = conn.cursor()

# Apagar tabelas existentes
cursor.execute('drop table if exists receitas_new')
cursor.execute('drop table if exists ingredientes_new')
cursor.execute('drop table if exists joint_new')

# Criar nova tabela
cursor.execute('''create table receitas_new
(
id integer
constraint receitas_new_pk primary key,
receita text,
preparo text
);''')

# Popular a tabela de receitas
for key, value in lista_receitas.items():
    if key != 1:
        cursor.execute('insert into receitas_new (id, receita, preparo) values (?, ?, ?)', (key, value[0], value[1]))

conn.commit()

# Criar tabela de ingredientes
cursor.execute('''create table ingredientes_new
(
id integer
constraint ingredientes_new_pk primary key autoincrement,
ingrediente text
)
''')

# Popular tabela de ingredientes
lista_ingredientes = []
lista_relacoes = []

for key, value in lista_receitas.items():
    if key != 1:
        # Iterar os ingredientes e criar relacoes entre ingredientes e receitas
        for i in range(2, len(value)):
            if value[i] != ' ' and value[i] != '' and i % 2 == 0 and (value[i], value[i+1]) not in lista_ingredientes:
                lista_ingredientes.append((value[i], value[i+1]))

# Agora que carregamos todos os ingredientes numa lista
# Colocamos no banco
for i_ing in range(0, len(lista_ingredientes)):
    cursor.execute('insert into ingredientes_new (id, ingrediente) values (?, ?)', (i_ing + 1, lista_ingredientes[i_ing][0]))

conn.commit()

# Bolar as relacoes entre ingredientes e receitas agora e colocar no banco
cursor.execute('''create table joint_new
(
id_receita integer,
id_ingrediente integer,
quantidade text
)
''')

for key, value in lista_receitas.items():
    if key != 1:
        for i in range(0, len(lista_ingredientes)):
            if lista_ingredientes[i][0] in value:
                cursor.execute('insert into joint_new (id_receita, id_ingrediente, quantidade) values (?, ?, ?)', (key, i+1, lista_ingredientes[i][1]))

conn.commit()

# TODO colocar quantidades de cada ingrediente na joint

conn.close()