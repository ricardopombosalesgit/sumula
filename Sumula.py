import streamlit as st
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Súmula de Jogo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo customizado para modo escuro
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stButton>button {
        color: #FFFFFF;
        background-color: #BB86FC;
        border: None;
    }
    input, textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }
    .stDateInput input, .stTimeInput input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Título da Aplicação
st.title("Súmula Completa do Jogo")

# Dividindo a página em duas colunas
col1, col2 = st.columns(2)

with col1:
    st.header("Informações do Time 1")
    t1 = st.text_input('Nome do Time 1')
    escudo1 = st.file_uploader("Upload do Escudo do Time 1", type=['png', 'jpg'])
    g1 = st.number_input('Gols do Time 1', min_value=0, step=1)
    st.subheader("Marcadores do Time 1")
    marcadores_t1 = st.text_area('Digite os nomes dos jogadores que marcaram pelo Time 1, separados por vírgula')

with col2:
    st.header("Informações do Time 2")
    t2 = st.text_input('Nome do Time 2')
    escudo2 = st.file_uploader("Upload do Escudo do Time 2", type=['png', 'jpg'])
    g2 = st.number_input('Gols do Time 2', min_value=0, step=1)
    st.subheader("Marcadores do Time 2")
    marcadores_t2 = st.text_area('Digite os nomes dos jogadores que marcaram pelo Time 2, separados por vírgula')

st.markdown("---")

# Informações adicionais
st.header("Informações Adicionais")
col3, col4 = st.columns(2)

with col3:
    local = st.text_input('Local do Jogo')
    est = st.text_input('Estádio')
    data = st.date_input('Data do Jogo', datetime.today())

with col4:
    camp = st.text_input('Campeonato')
    cat = st.text_input('Categoria')
    horario = st.time_input('Horário do Jogo', datetime.now().time())

# Botão para gerar súmula
if st.button('Gerar Súmula'):
    st.markdown("---")
    st.header("Súmula do Jogo")

    col5, col6, col7 = st.columns([1, 2, 1])

    with col5:
        if escudo1 is not None:
            st.image(escudo1, width=100)
        st.subheader(f"**{t1}**")
        st.write(f"Gols: {g1}")
        st.write("**Marcadores:**")
        marcadores_t1_lista = [jogador.strip() for jogador in marcadores_t1.split(',') if jogador.strip()]
        for jogador in marcadores_t1_lista:
            st.write(f"- {jogador}")

    with col6:
        st.write(f"### {t1} {g1} x {g2} {t2}")
        st.write(f"**Local:** {local} - {est}")
        st.write(f"**Data e Hora:** {data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}")
        st.write(f"**Campeonato:** {camp}")
        st.write(f"**Categoria:** {cat}")

    with col7:
        if escudo2 is not None:
            st.image(escudo2, width=100)
        st.subheader(f"**{t2}**")
        st.write(f"Gols: {g2}")
        st.write("**Marcadores:**")
        marcadores_t2_lista = [jogador.strip() for jogador in marcadores_t2.split(',') if jogador.strip()]
        for jogador in marcadores_t2_lista:
            st.write(f"- {jogador}")

    # Gerar arquivo CSV
    match_data = {
        'Time 1': t1,
        'Gols Time 1': g1,
        'Marcadores Time 1': marcadores_t1,
        'Time 2': t2,
        'Gols Time 2': g2,
        'Marcadores Time 2': marcadores_t2,
        'Local': local,
        'Estádio': est,
        'Data': data.strftime('%d/%m/%Y'),
        'Horário': horario.strftime('%H:%M'),
        'Campeonato': camp,
        'Categoria': cat
    }

    df = pd.DataFrame([match_data])
    csv = df.to_csv(index=False).encode('utf-8')

    # Gerar arquivo PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # Título
    pdf.cell(0, 10, 'Súmula do Jogo', ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    # Informações da Partida
    pdf.cell(0, 10, f"{t1} {g1} x {g2} {t2}", ln=True, align='C')
    pdf.cell(0, 10, f"Local: {local} - {est}", ln=True)
    pdf.cell(0, 10, f"Data e Hora: {data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}", ln=True)
    pdf.cell(0, 10, f"Campeonato: {camp}", ln=True)
    pdf.cell(0, 10, f"Categoria: {cat}", ln=True)
    pdf.ln(10)

    # Detalhes do Time 1
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{t1}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Gols: {g1}", ln=True)
    pdf.cell(0, 10, "Marcadores:", ln=True)
    for jogador in marcadores_t1_lista:
        pdf.cell(0, 10, f"- {jogador}", ln=True)
    pdf.ln(5)

    # Detalhes do Time 2
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{t2}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Gols: {g2}", ln=True)
    pdf.cell(0, 10, "Marcadores:", ln=True)
    for jogador in marcadores_t2_lista:
        pdf.cell(0, 10, f"- {jogador}", ln=True)

    # Obter o conteúdo do PDF em bytes
    pdf_data = pdf.output(dest='S').encode('latin1')

    st.markdown("---")
    st.header("Download dos Arquivos")

    col8, col9 = st.columns(2)

    with col8:
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name='sumula_jogo.csv',
            mime='text/csv'
        )

    with col9:
        st.download_button(
            label="📥 Baixar PDF",
            data=pdf_data,
            file_name='sumula_jogo.pdf',
            mime='application/pdf'
        )