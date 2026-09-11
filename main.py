# Sistema de Triagem Hospitalar - Gustavo Victorino
# Enfermagem -> ADS | Python | HealthTech

pacientes = []

def cadastrar_paciente():
    print("\n--- NOVO PACIENTE ---")
    nome = input("Nome: ")
    idade = input("Idade: ")
    print("\nPrioridade:")
    print("1 - VERMELHO - Emergência (dor no peito, falta de ar)")
    print("2 - AMARELO - Urgência (febre alta, vômito)")
    print("3 - VERDE - Pouco urgente (dor leve, check-up)")
    op = input("Escolha 1/2/3: ")

    mapa = {"1": "VERMELHO", "2": "AMARELO", "3": "VERDE"}
    cor = mapa.get(op, "VERDE")

    pacientes.append({"nome": nome, "idade": idade, "prioridade": cor})
    print(f"\n✅ {nome} cadastrado como {cor}!")

def listar_fila():
    if not pacientes:
        print("\nFila vazia.\n")
        return

    ordem = {"VERMELHO": 0, "AMARELO": 1, "VERDE": 2}
    fila = sorted(pacientes, key=lambda x: ordem[x["prioridade"]])

    print("\n=== FILA DE ATENDIMENTO ===")
    for i, p in enumerate(fila, 1):
        emoji = "🔴" if p["prioridade"] == "VERMELHO" else "🟡" if p["prioridade"] == "AMARELO" else "🟢"
        print(f"{i}. {emoji} {p['nome']} ({p['idade']}a) - {p['prioridade']}")
    print("===========================\n")

while True:
    print("\n[1] Cadastrar | [2] Ver Fila | [0] Sair")
    escolha = input("Opção: ")
    if escolha == "1":
        cadastrar_paciente()
    elif escolha == "2":
        listar_fila()
    elif escolha == "0":
        print("Encerrando sistema. Até mais!")
        break
    else:
        print("Opção inválida!")