import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página para ocupar a tela inteira
st.set_page_config(layout="wide", page_title="Dashboard Fini")

# Função para carregar os dados
@st.cache_data
def load_data():
    path = './Dados/Fini_analise.xlsx'
    df = pd.read_excel(path, engine='openpyxl')
    
    # Tratamento de datas
    df['Emissão'] = pd.to_datetime(df['Emissão'])
    df['Ano'] = df['Emissão'].dt.year
    df['Mês'] = df['Emissão'].dt.month
    df['Mes_Ano'] = df['Emissão'].dt.to_period('M').astype(str)
    return df

df = load_data()

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("Filtros de Análise")

# Filtros de múltipla escolha
anos = st.sidebar.multiselect("Ano", options=sorted(df['Ano'].unique()), default=sorted(df['Ano'].unique()))
meses = st.sidebar.multiselect("Mês", options=sorted(df['Mês'].unique()), default=sorted(df['Mês'].unique()))
gerentes = st.sidebar.multiselect("Gerente", options=sorted(df['GERENTE'].unique()), default=sorted(df['GERENTE'].unique()))
supervisores = st.sidebar.multiselect("Supervisor", options=sorted(df['SUPERVISOR'].unique()), default=sorted(df['SUPERVISOR'].unique()))
vendedores = st.sidebar.multiselect("Vendedor", options=sorted(df['Nome Vendedor'].unique()), default=sorted(df['Nome Vendedor'].unique()))

# Aplicando os filtros ao DataFrame
df_filt = df[
    (df['Ano'].isin(anos)) & 
    (df['Mês'].isin(meses)) & 
    (df['GERENTE'].isin(gerentes)) & 
    (df['SUPERVISOR'].isin(supervisores)) & 
    (df['Nome Vendedor'].isin(vendedores))
]

# --- CÁLCULOS DOS CARDS (TOP) ---
total_faturamento = df_filt['Vlr. Total'].sum()
media_faturamento = df_filt['Vlr. Total'].mean()
positivacao_total = df_filt['Cnpj_CPF'].nunique()
ticket_medio = total_faturamento / df_filt['NF'].nunique() if df_filt['NF'].nunique() > 0 else 0

# --- LAYOUT DASHBOARD ---

# Linha 1: Cards
st.markdown("### Indicadores Principais")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
c2.metric("Média Faturamento", f"R$ {media_faturamento:,.2f}")
c3.metric("Positivação (Distinta)", f"{positivacao_total}")
c4.metric("Ticket Médio (NF)", f"R$ {ticket_medio:,.2f}")

st.markdown("---")

# Linha 2: Evolução Mensal
st.markdown("### Evolução de Vendas e Positivação (MoM)")
df_evolucao = df_filt.groupby('Mes_Ano').agg({
    'Vlr. Total': 'sum',
    'Cnpj_CPF': 'nunique'
}).reset_index().rename(columns={'Cnpj_CPF': 'Positivação'})

fig_evol = px.line(df_evolucao, x='Mes_Ano', y=['Vlr. Total', 'Positivação'], 
                  markers=True, title="Vendas vs Positivação Mensal",
                  labels={'value': 'Valor / Qtd', 'Mes_Ano': 'Mês/Ano'})
st.plotly_chart(fig_evol, use_container_width=True)

# Linha 3: Tabela Dinâmica de Vendedores
st.markdown("### Detalhamento por Vendedor")

# Agrupamento para a tabela
df_vendedor = df_filt.groupby(['Código', 'Nome Vendedor', 'SUPERVISOR', 'GERENTE']).agg({
    'Vlr. Total': ['sum', 'mean'],
    'Cnpj_CPF': 'nunique',
    'Mês': 'nunique' # Para cálculo da média mensal
}).reset_index()

# Ajustando nomes das colunas
df_vendedor.columns = ['Cod', 'Vendedor', 'Supervisor', 'Gerente', 'Total Venda', 'Média Venda', 'Total Positivação', 'Qtd Meses']

# Cálculo da Média Mensal (MoM)
df_vendedor['Média Mensal Venda'] = df_vendedor['Total Venda'] / df_vendedor['Qtd Meses']
df_vendedor['Média Mensal Posit.'] = df_vendedor['Total Positivação'] / df_vendedor['Qtd Meses']

# Exibindo a tabela formatada
st.dataframe(df_vendedor.drop(columns=['Qtd Meses']).style.format({
    'Total Venda': 'R$ {:,.2f}',
    'Média Venda': 'R$ {:,.2f}',
    'Média Mensal Venda': 'R$ {:,.2f}',
    'Média Mensal Posit.': '{:.2f}'
}), use_container_width=True)