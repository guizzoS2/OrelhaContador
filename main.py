import os
import re
import json
from colorama import Fore, Style, init
import msvcrt

init(autoreset=True)

KEYWORDS_FILE = 'categorias.json'

def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_keywords(keywords_to_categories):
    with open(KEYWORDS_FILE, 'w', encoding='utf-8') as file:
        json.dump(keywords_to_categories, file, indent=4, ensure_ascii=False)

def read_transactions_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_monetary_value(value_str):
    value_str = value_str.strip()
    
    # Remove todos os pontos (separadores de milhares)
    value_str = value_str.replace('.', '')
    
    # Substitui a vírgula (separador decimal) por ponto
    value_str = value_str.replace(',', '.')
    
    try:
        return float(value_str)
    except ValueError:
        return None

def process_transactions(input_text):
    lines = input_text.strip().split("\n")
    transactions = []
    current_transaction = []
    date_pattern = re.compile(r'^\d{1,2}/\d{1,2}')  # Padrão para datas no formato MM/DD

    for line in lines:
        if date_pattern.match(line.strip()):  # Verifica se a linha começa com uma data
            if current_transaction:  # Se já há uma transação em andamento, finaliza ela
                transactions.append(" ".join(current_transaction).strip())
                current_transaction = []  # Começa uma nova transação
            current_transaction.append(line.strip())  # Adiciona a linha atual à nova transação
        else:
            current_transaction.append(line.strip())  # Adiciona a linha à transação atual

    if current_transaction:  # Adiciona a última transação, se houver
        transactions.append(" ".join(current_transaction).strip())

    return transactions

def categorize_transactions(transactions, keywords_to_categories, account_owners):
    categories = {}
    categorized_transactions = {}
    debit_values = []
    credit_values = []
    transacoes_internas = []

    # Dicionários para armazenar débitos e créditos por categoria
    debitos_por_categoria = {}
    creditos_por_categoria = {}

    for transaction in transactions:
        print(Fore.WHITE + "=" * 60)
        print(f"{Fore.GREEN}Transação: {transaction}{Style.RESET_ALL}")

        if "Zelle" in transaction:
            has_owner = any(owner.lower() in transaction.lower() for owner in account_owners)
            if has_owner:
                print(f"{Fore.MAGENTA}Transação ignorada (contém 'Zelle' e nome do dono da conta): {transaction}{Style.RESET_ALL}")
                continue

        category = None
        if "Reversal" in transaction:
            category = "Reembolso"
        else:
            for keyword, cat in keywords_to_categories.items():
                if keyword.lower() in transaction.lower():
                    category = cat
                    break

            if not category:
                category = input("Qual a categoria desta transação? ").strip().capitalize()
                keyword = input("Sugira uma palavra-chave para associar a esta categoria (ou pressione Enter para pular):").strip()
                if keyword:
                    keywords_to_categories[keyword] = category

        print(f"{Fore.YELLOW}Categoria detectada automaticamente: {category}{Style.RESET_ALL}")

        # Expressão regular ajustada para aceitar 1 ou 2 dígitos após o separador decimal
        amount_match = re.search(r'-?\d+(?:[\.,]\d{1,2})?$', transaction)
        if amount_match:
            amount_str = amount_match.group(0)
            amount = parse_monetary_value(amount_str)
            if amount is not None:
                if amount < 0:
                    credit_values.append(amount)
                    # Atualiza o total de créditos para a categoria
                    creditos_por_categoria[category] = creditos_por_categoria.get(category, 0) + amount
                    print(f"{Fore.WHITE}Crédito registrado: {amount}{Style.RESET_ALL}")
                else:
                    debit_values.append(amount)
                    # Atualiza o total de débitos para a categoria
                    debitos_por_categoria[category] = debitos_por_categoria.get(category, 0) + amount
                    print(f"{Fore.WHITE}Débito registrado: {amount}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Nenhum valor monetário encontrado na transação: {transaction}{Style.RESET_ALL}")

        categorized_transactions.setdefault(category, []).append(transaction)

    return categorized_transactions, debit_values, credit_values, transacoes_internas, debitos_por_categoria, creditos_por_categoria

def main():
    owners_input = input("Digite os nomes dos donos da conta, separados por vírgula: ").strip()
    account_owners = [owner.strip().lower() for owner in owners_input.split(',')]

    keywords_to_categories = load_keywords()
    input_text = read_transactions_file('transacoes.txt')
    transactions = process_transactions(input_text)

    categorized_transactions, debit_values, credit_values, transacoes_internas, debitos_por_categoria, creditos_por_categoria = categorize_transactions(
        transactions, keywords_to_categories, account_owners
    )

    save_keywords(keywords_to_categories)

    print("\nRelatório Final:")
    for category, transactions in sorted(categorized_transactions.items()):
        print(f"\n{category}")
        print("-" * len(category))
        for transaction in transactions:
            print(transaction)

    print("\nResumo de Valores:")
    print("=" * 20)
    print(f"Total Débito (positivos): {sum(debit_values):.2f}")
    for categoria, debito in debitos_por_categoria.items():
        print(f"Débito de {categoria}: {debito:.2f}")

    print("\n" + "=" * 20)
    print(f"Total Crédito (negativos): {sum(credit_values):.2f}")
    for categoria, credito in creditos_por_categoria.items():
        print(f"Crédito de {categoria}: {credito:.2f}")

    if transacoes_internas:
        print("\nTransações Internas:")
        for internal_transaction in transacoes_internas:
            print(internal_transaction)
    else:
        print("\nNenhuma transação interna detectada.")

    print("\nAperte qualquer tecla para sair...")
    msvcrt.getch()

if __name__ == "__main__":
    main()