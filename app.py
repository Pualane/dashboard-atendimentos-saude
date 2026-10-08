import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Dashboard de Atendimentos em Saúde', layout='wide')
MESES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho']
AZUL = '#0072B2'

@st.cache_data
def carregar():
    dados = pd.read_csv('atendimentos_saude.csv', encoding='utf-8-sig')
    colunas = {'Mes','Ordem_Mes','Unidade','Tipo_Atendimento','Quantidade'}
    if not colunas.issubset(dados.columns):
        st.error('O CSV não possui todas as colunas necessárias.')
        st.stop()
    return dados

df = carregar()
st.title('Dashboard Interativo de Atendimentos em Saúde')
st.caption('Dados simulados para fins acadêmicos — não representam atendimentos reais.')

if 'mes_selecionado' not in st.session_state:
    st.session_state.mes_selecionado = None
if 'tipo_selecionado' not in st.session_state:
    st.session_state.tipo_selecionado = None

unidades = st.multiselect('Filtrar por unidade de saúde', sorted(df['Unidade'].unique()), default=sorted(df['Unidade'].unique()))
base = df[df['Unidade'].isin(unidades)]

def limpar():
    st.session_state.mes_selecionado = None
    st.session_state.tipo_selecionado = None

st.button('Limpar seleções dos gráficos', on_click=limpar)

# Visões cruzadas: a série temporal respeita a seleção de categoria;
# as barras respeitam a seleção do mês.
base_temporal = base
if st.session_state.tipo_selecionado:
    base_temporal = base_temporal[base_temporal['Tipo_Atendimento'] == st.session_state.tipo_selecionado]

serie = (base_temporal.groupby(['Ordem_Mes','Mes'], as_index=False)['Quantidade'].sum()
         .sort_values('Ordem_Mes'))
fig_tempo = px.line(serie, x='Mes', y='Quantidade', markers=True,
                    title='Evolução mensal dos atendimentos',
                    labels={'Mes':'Mês','Quantidade':'Atendimentos'},
                    custom_data=['Mes'])
fig_tempo.update_traces(line_color=AZUL, marker_size=11)
fig_tempo.update_layout(template='plotly_white', clickmode='event+select',
                        margin=dict(l=15,r=15,t=55,b=15))

base_categorias = base
if st.session_state.mes_selecionado:
    base_categorias = base_categorias[base_categorias['Mes'] == st.session_state.mes_selecionado]
categorias = (base_categorias.groupby('Tipo_Atendimento', as_index=False)['Quantidade'].sum()
              .sort_values('Quantidade'))
fig_tipo = px.bar(categorias, x='Quantidade', y='Tipo_Atendimento', orientation='h',
                  title='Atendimentos por tipo de serviço', text='Quantidade',
                  labels={'Quantidade':'Atendimentos','Tipo_Atendimento':'Serviço'},
                  custom_data=['Tipo_Atendimento'])
fig_tipo.update_traces(marker_color=AZUL, textposition='outside')
fig_tipo.update_layout(template='plotly_white', clickmode='event+select',
                       margin=dict(l=15,r=30,t=55,b=15))

col1,col2 = st.columns(2)
with col1:
    selecao_tempo = st.plotly_chart(fig_tempo, key='grafico_tempo',
                                   on_select='rerun', selection_mode='points',
                                   use_container_width=True)
with col2:
    selecao_tipo = st.plotly_chart(fig_tipo, key='grafico_tipo',
                                  on_select='rerun', selection_mode='points',
                                  use_container_width=True)

# O evento de seleção inclui customdata do ponto selecionado.
pontos_tempo = selecao_tempo.selection.points
pontos_tipo = selecao_tipo.selection.points
mes_novo = pontos_tempo[0].get('customdata', [None])[0] if pontos_tempo else None
tipo_novo = pontos_tipo[0].get('customdata', [None])[0] if pontos_tipo else None
if mes_novo != st.session_state.mes_selecionado or tipo_novo != st.session_state.tipo_selecionado:
    st.session_state.mes_selecionado = mes_novo
    st.session_state.tipo_selecionado = tipo_novo
    st.rerun()

detalhes = base.copy()
if st.session_state.mes_selecionado:
    detalhes = detalhes[detalhes['Mes'] == st.session_state.mes_selecionado]
if st.session_state.tipo_selecionado:
    detalhes = detalhes[detalhes['Tipo_Atendimento'] == st.session_state.tipo_selecionado]

st.subheader('Detalhamento dos atendimentos')
st.write(f"**Total na seleção:** {int(detalhes['Quantidade'].sum()):,} atendimentos | **Registros:** {len(detalhes)}".replace(',', '.'))
st.dataframe(detalhes.sort_values(['Ordem_Mes','Unidade','Tipo_Atendimento'])
             [['Mes','Unidade','Tipo_Atendimento','Quantidade']],
             hide_index=True, use_container_width=True)
st.caption('Clique em um ponto da linha ou em uma barra para coordenar as visualizações. Use o botão para limpar as seleções.')
