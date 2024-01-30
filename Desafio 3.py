import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco  = endereco
        self.contas    = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf       = cpf
        self.nome       = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo     = 0
        self._numero    = numero
        self._agencia   = '0001'
        self._cliente   = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    def sacar(self, valor):
        saldo           = self._saldo
        excedeu_saldo   = valor > saldo

        if excedeu_saldo:
            print(f'\n=== Saldo insuficiente ===\nSaldo atual: R${self._saldo}')
        elif valor > 0:
            self._saldo -= valor
            print(f'\n--- Saque realizado com sucesso ---\nSaldo atual: R${self._saldo}')
            return True
        else:
            print(f'\n=== Valor inválido, tente novamente ===')
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f'\n--- Deposito realizado com sucesso ---\nSaldo atual: R${self._saldo}')
        else:
            print(f'\n=== Valor inválido, tente novamente ===')
            return False
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 1000, limite_saques = 3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print(f'\n=== Operação falhou! O valor excede o limite disponível. ===')
        elif excedeu_saques:
            print(f'\n=== Operação falhou! Limite de saques atingido. ===')
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f'''\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        '''

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now(),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """ \n
    ================== MENU ==================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo usuário
    [5]\tNova conta
    [6]\tListar contas
    => """
    return input(textwrap.dedent(menu))

def operacao(clientes, opcao):
    cpf     = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado ===")
        return
    
    if opcao == '1':
        valor   = float(input("Informe o valor do deposito?\n=> R$\t"))
        transacao = Deposito(valor)
    elif opcao == '2':
        valor   = float(input("Informe o valor do saque?\n=> R$\t"))
        transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        print("\n=== Conta não encontrado ===")
        return
    
    cliente.realizar_transacao(conta, transacao)

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n === Cliente não possui conta ===")
        return

    return cliente.contas[0]

def exibir_extrato(clientes):
    cpf     = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado ===")
        return
    
    conta   = recuperar_conta_cliente(cliente)
    if not conta:
        print("\n=== Não foi encontrada conta associada ao cliente ===")
        return
    
    print("\n================== EXTRATO ==================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não há registro de movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f'\nSaldo:\t\tR$ {conta.saldo:.2f}')
    print("\n=============================================")

def criar_cliente(clientes):
    cpf     = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n=== Cliente já cadastrado ===")
        return
    
    nome = input('Informe o nome completo: ')
    data_nascimento = input('Informa a data de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço (logradouro, numero, bairro, cidade/UF): ')

    cliente = PessoaFisica(cpf=cpf,
                           nome=nome,
                           data_nascimento=data_nascimento,
                           endereco=endereco)
    
    clientes.append(cliente)

    print('\n --- Cliente cadastrado com sucesso! ---')

def criar_conta(numero_conta, clientes, contas):
    cpf     = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado ===")
        return
    
    conta   = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('\n --- Conta criada com sucesso! ---')

def listar_contas(contas):
    for conta in contas:
        print('=' * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes    = []
    contas      = []

    while True:
        opcao   = menu()

        if opcao == "1":
            operacao(clientes, '1')
        
        elif opcao == "2":
            operacao(clientes, '2')

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            criar_cliente(clientes)

        elif opcao == "5":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "6":
            listar_contas(contas)

        elif opcao == '7':
            break
        
        else:
            print(f'Operação inválida')

main()