# Dashboard – Precificação de Carbono

Este repositório contém todos os códigos, dados e instruções necessários para rodar o dashboard interativo de **Precificação de Carbono**. Além das páginas do dashboard, também estão incluídos os dados brutos, processados e os scripts de tratamento.

---

## Como rodar o dashboard

1. Certifique-se de que tem o **Streamlit** instalado:

   ```bash
   pip install streamlit
   ```

2. Execute a página inicial do dashboard:

   ```bash
   streamlit run "1 Mecanismos _de_Compliance .py"
   ```

---

## Estrutura do Repositório

```
data/
│
├── raw/                # Dados brutos (download direto dos sites)
├── processed/          # Dados tratados, prontos para uso no dashboard
│   └── DADOS_MANUAIS.xlsx  # Única planilha que requer atualização manual
│
pages/                  # Páginas adicionais do dashboard (exceto a principal)
treat_data/             # Scripts de tratamento e atualização de dados
utils/                  # Funções auxiliares utilizadas no dashboard
```

> ⚠️ Apenas o arquivo `DADOS_MANUAIS.xlsx` (em `data/processed/`) deve ser atualizado manualmente. Os demais dados são atualizados por meio dos scripts em `treat_data/`.

---

## Como atualizar os dados

### Word Bank

1. Baixe a base no site: [World Bank Dashboard](https://carbonpricingdashboard.worldbank.org/about#download-data)
2. Substitua o arquivo em: `data/raw/dados_wb.xlsx`
3. Execute:

   ```bash
   python treat_data/treat_wb.py
   ```
4. (Caso não vá atualizar o MCV) Rode também:

   ```bash
   python treat_data/get_lat_long.py
   ```

   Isso atualiza os dados de latitude e longitude para visualização no mapa.

---

### Mecanismo de Compensação Voluntária (MCV)

1. Baixe a base no site da [Berkeley](https://gspp.berkeley.edu/berkeley-carbon-trading-project/offsets-database)
2. Substitua o arquivo em: `data/raw/dados_mvc.xlsx`
3. Execute:

   ```bash
   python treat_data/treattreat_mvc_wb.py
   ```
4. Rode:

   ```bash
   python treat_data/get_lat_long.py
   ```

---

### CBIO (Créditos de Descarbonização)

1. Baixe os arquivos **Aposentadoria**, **Negociações** e **Estoque** no site da [B3](https://www.b3.com.br/pt_br/b3/sustentabilidade/produtos-e-servicos-esg/credito-de-descarbonizacao-cbio/cbio-consultas/)
2. Copie os dados para os arquivos `.csv` correspondentes em `data/raw/cbio/`

   > ⚠️ Se colar entradas duplicadas por data, o script manterá apenas a **primeira** ocorrência.
3. Execute:

   ```bash
   python treat_data/treat_cbio.py
   ```

---

### Demais bases

* Edite manualmente a planilha:
  `data/processed/DADOS_MANUAIS.xlsx`
