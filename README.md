# 💰 OrelhaContador

Um sistema inteligente de categorização automática de transações bancárias desenvolvido em Python, que processa extratos bancários e organiza os gastos por categoria para facilitar o controle financeiro pessoal.

## 📋 Sobre o Projeto

**OrelhaContador** é uma ferramenta que automatiza o processo tedioso de categorizar transações bancárias. O sistema analisa arquivos de extrato, identifica automaticamente as categorias dos gastos baseado em palavras-chave configuráveis, e gera relatórios detalhados com análise de débitos e créditos.

## ✨ Funcionalidades Principais

### 🔍 **Processamento Inteligente de Transações**
- **Leitura automática** do arquivo de transações (`transacoes.txt`)
- **Parser inteligente** que detecta automaticamente datas no formato MM/DD
- **Extração precisa de valores monetários** com suporte a diferentes formatos (pontos e vírgulas)
- **Agrupamento automático** de linhas pertencentes à mesma transação

### 🏷️ **Sistema de Categorização Automática**
- **Base de conhecimento configurável** através do arquivo `categorias.json`
- **Categorização automática** baseada em correspondência de palavras-chave
- **Modo interativo** para categorizar transações não reconhecidas
- **Aprendizado contínuo** - novas palavras-chave são salvas automaticamente
- **Detecção automática de reembolsos** (transações com "Reversal")

### 💳 **Filtros Inteligentes**
- **Filtro Zelle** - ignora automaticamente transações Zelle internas entre donos da conta
- **Detecção de transações internas** para evitar duplicação na contabilização
- **Configuração personalizada** dos nomes dos donos da conta

### 📊 **Análise Financeira Detalhada**
- **Separação automática** entre débitos (saídas) e créditos (entradas)
- **Relatório por categoria** mostrando todas as transações agrupadas
- **Resumo financeiro** com totais de débito e crédito por categoria
- **Interface colorida** no terminal para melhor visualização

## 🚀 Como Usar

### 1. **Preparação dos Dados**
Adicione suas transações no arquivo `transacoes.txt`. O formato deve seguir o padrão:
```
12/15 Walmart Supercenter #1234 Purchase 45.67
12/15 Shell Oil Gas Station 32.50
12/16 Zelle Transfer John Doe -100.00
```

### 2. **Execução do Programa**
Execute o programa principal:
```bash
python main.py
```

### 3. **Configuração Inicial**
- Digite os nomes dos donos da conta (separados por vírgula)
- O sistema utilizará essa informação para filtrar transações Zelle internas

### 4. **Categorização Interativa**
- Transações conhecidas são categorizadas automaticamente
- Para transações não reconhecidas, o sistema pedirá a categoria manualmente
- Você pode sugerir palavras-chave para futuras categorizações automáticas

## 📁 Estrutura do Projeto

```
OrelhaContador/
├── main.py                     # 🐍 Arquivo principal do sistema
├── categorias.json             # 📝 Base de dados de palavras-chave e categorias
├── transacoes.txt              # 📄 Arquivo de entrada (ignorado pelo git)
├── README.md                   # 📖 Documentação do projeto
├── resultados/                 # 📊 Relatórios gerados
│   ├── mes08juliana.txt
│   └── tammy23.txt
├── output/                     # 💾 Executáveis compilados
│   ├── OrelhaContadorV6.2.exe
│   └── outros executáveis...
└── build/                      # 🔧 Arquivos de build
```

## 📊 Exemplo de Saída

```
Relatório Final:

Sup
---
12/15 Walmart Supercenter #1234 Purchase 45.67
12/16 Amazon.com Order #789 67.89

Comida
------
12/15 McDonald's Drive Thru 12.50
12/16 Starbucks Coffee 5.75

Resumo de Valores:
====================
Total Débito (positivos): 131.81
Débito de Sup: 113.56
Débito de Comida: 18.25

====================
Total Crédito (negativos): -50.00
Crédito de Reembolso: -50.00
```

## 🎯 Categorias Pré-configuradas

O sistema vem com mais de 50 categorias pré-configuradas, incluindo:

- **🛒 Supermercados**: Walmart, Costco, Publix, Amazon, Target
- **🍔 Comida**: McDonald's, Starbucks, Chipotle, Jersey Mike's, Five Guys
- **⛽ Gasolina**: Shell Oil, Circle K, Racetrac, Costco Gas
- **🎮 Lazer**: The Lights Fes, Great Clips, Dee The Legacy
- **💊 Farmácia**: Walgreens, CVS Pharmacy
- **🌐 Internet**: Apple.com, Visible, Michaels Stores
- **🚗 Manutenção de Carro**: SETOYOTA, Zips Car Wash
- **🏛️ Serviços**: Pedágio (Sunpass), Estacionamento (Parkmobile)

## 🛠️ Dependências

```python
import os           # Manipulação de arquivos
import re           # Processamento de texto com regex
import json         # Gerenciamento das categorias
import colorama     # Output colorido no terminal
import msvcrt       # Controle de entrada do teclado (Windows)
```

## 💾 Configuração - categorias.json

O arquivo `categorias.json` mapeia palavras-chave para categorias:

```json
{
    "Walmart": "Sup",
    "McDonald's": "Comida",
    "Shell Oil": "Gasolina",
    "Starbucks": "Comida",
    "Amazon": "Sup"
}
```

## 🔒 Segurança e Privacidade

- ✅ O arquivo `transacoes.txt` é ignorado pelo controle de versão
- ✅ Nenhuma informação financeira é enviada para serviços externos
- ✅ Processamento 100% local
- ✅ Dados sensíveis permanecem no seu computador

## 🎯 Casos de Uso

- **📈 Controle financeiro pessoal**
- **📊 Análise de gastos por categoria**
- **📋 Preparação de relatórios financeiros**
- **🔍 Identificação de padrões de consumo**
- **💡 Tomada de decisões financeiras informadas**

## 🚀 Recursos Avançados

### Interface Colorida
- 🟢 Verde: Transações processadas
- 🟡 Amarelo: Categorias detectadas
- 🔴 Vermelho: Erros ou avisos
- 🟣 Roxo: Transações ignoradas
- ⚪ Branco: Informações gerais

### Tratamento de Valores
- Suporte a diferentes formatos de decimal (vírgula e ponto)
- Detecção automática de valores negativos (créditos)
- Parsing robusto que ignora separadores de milhares

### Aprendizado Automático
- Sistema aprende novas categorias durante o uso
- Palavras-chave são salvas automaticamente
- Base de conhecimento cresce com o tempo

## ⚙️ Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd OrelhaContador
```

2. **Instale as dependências:**
```bash
pip install colorama
```

3. **Prepare seus dados:**
- Adicione suas transações no arquivo `transacoes.txt`

4. **Execute:**
```bash
python main.py
```

## 📝 Licença

Este projeto é de uso pessoal. Desenvolvido para automatizar o controle financeiro doméstico.

---

**Desenvolvido para facilitar o controle financeiro pessoal**
