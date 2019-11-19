from datagrid import DataGridDataClass

# A classe 'Receita' possui, nesta ordem,
# nome da receita,
# quais os ingredientes nela
# porcentagem de ingredientes presentes
# se e possivel ou nao


class ReceitaListaItem(DataGridDataClass):
    def __init__(self, nome: str, total_ingredientes: int, ingredientes_encontrados: int):
        self.nome = nome
        self.total_ingredientes = total_ingredientes
        self.ingredientes_encontrados = ingredientes_encontrados

    def get_lista(self):
        return [("%s - (%d / %d)" % (str.capitalize(self.nome), self.ingredientes_encontrados, self.total_ingredientes))]


class Receita:
    def __init__(self, r_id: int, nome: str, ingredientes: tuple, descricao: str):
        self.r_id = r_id
        self.nome = nome
        self.ingredientes = ingredientes
        self.descricao = descricao

    # Retorna um tuple com quantos ingredientes a receita tem,
    # quantos eu quero,
    # e quantos estao presentes dos que eu quero
    def presenca_ingredientes(self, ingredientes_consulta: tuple):
        ingredientes_presentes = []
        for ingr in ingredientes_consulta:
            if ingr in self.ingredientes and ingr not in ingredientes_presentes:
                ingredientes_presentes.append(ingr)

        # Calcular quantos ingredientes presentes existem
        return len(self.ingredientes), len(ingredientes_consulta), len(ingredientes_presentes)
