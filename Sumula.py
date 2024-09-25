import streamlit as st
from datetime import datetime, time
import pandas as pd
from fpdf import FPDF
from io import BytesIO
from PIL import Image
import tempfile
import os

# Configuração da página
st.set_page_config(
    page_title="Gerador de Súmula de Jogo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo customizado para melhorar o contraste e otimizar o espaço
st.markdown("""
    <style>
    /* Estilos globais */
    body, .stApp {
        background-color: #696969;
        color: #000000;
    }
    /* Estilo para títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #333333;
    }
    /* Estilo para inputs */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* Estilo para botões */
    .stButton>button {
        color: #ffffff !important;
        background-color: #666666 !important;
        border: None;
        border-radius: 5px;
        padding: 5px 10px;
    }
    /* Redução do espaçamento vertical entre campos */
    div.stNumberInput > label, div.stTextInput > label, div.stSelectbox > label {
        font-size: 0;
        height: 0;
        margin: 0;
    }
    /* Ajuste do espaçamento entre linhas */
    div.stNumberInput, div.stTextInput, div.stSelectbox, div.stCheckbox {
        margin-bottom: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Opções para o campo de posição
posicoes_opcoes = [
    'Goleiro(a)',
    'Zagueiro(a)',
    'Lateral',
    'Volante',
    'Meia',
    'Meia-Atacante',
    'Extremo(a)',
    'Atacante'
]

# Função para coletar informações dos jogadores
def coletar_jogadores(time_nome, tipo_jogador):
    jogadores = []
    num_jogadores = 11 if tipo_jogador == "Titulares" else 7
    st.markdown(f"### {tipo_jogador} do {time_nome}")
    for i in range(1, num_jogadores + 1):
        with st.container():
            cols = st.columns([1, 3, 2, 1, 1, 2])  # Ajuste nas proporções das colunas
            with cols[0]:
                numero = st.number_input(
                    'Número',
                    min_value=1,
                    max_value=99,
                    key=f'{time_nome}_{tipo_jogador}_num_{i}',
                    label_visibility="collapsed"
                )
            with cols[1]:
                nome = st.text_input(
                    'Nome',
                    key=f'{time_nome}_{tipo_jogador}_nome_{i}',
                    label_visibility="collapsed"
                )
            with cols[2]:
                posicao = st.selectbox(
                    'Posição',
                    posicoes_opcoes,
                    key=f'{time_nome}_{tipo_jogador}_posicao_{i}',
                    label_visibility="collapsed"
                )
            with cols[3]:
                cartao_amarelo = st.checkbox(
                    '🟨',
                    key=f'{time_nome}_{tipo_jogador}_amarelo_{i}'
                )
            with cols[4]:
                cartao_vermelho = st.checkbox(
                    '🟥',
                    key=f'{time_nome}_{tipo_jogador}_vermelho_{i}'
                )
            with cols[5]:
                if tipo_jogador == "Titulares":
                    tempo_saida = st.number_input(
                        'Substituído (min.)',
                        min_value=0,
                        max_value=120,
                        step=1,
                        key=f'{time_nome}_{tipo_jogador}_tempo_saida_{i}',
                        label_visibility="collapsed"
                    )
                else:
                    tempo_entrada = st.number_input(
                        'Entrada (min.)',
                        min_value=0,
                        max_value=120,
                        step=1,
                        key=f'{time_nome}_{tipo_jogador}_tempo_entrada_{i}',
                        label_visibility="collapsed"
                    )
            # Adiciona o jogador mesmo se o nome estiver vazio
            jogador_info = {
                'Número': numero,
                'Nome': nome,
                'Posição': posicao,
                'Amarelo': cartao_amarelo,
                'Vermelho': cartao_vermelho
            }
            if tipo_jogador == "Titulares":
                jogador_info['Tempo de Saída'] = tempo_saida
            else:
                jogador_info['Tempo de Entrada'] = tempo_entrada
            jogadores.append(jogador_info)
    return jogadores

# Função para coletar informações do time
def coletar_info_time(numero_time):
    time_info = {}
    time_nome = st.text_input(
        f'Nome do Time {numero_time}',
        key=f'time{numero_time}_nome'
    )
    time_escudo = st.file_uploader(
        f"Escudo do Time {numero_time}",
        type=['png', 'jpg', 'jpeg'],
        key=f'time{numero_time}_escudo'
    )
    gols = st.number_input(
        f'Gols do Time {numero_time}',
        min_value=0,
        step=1,
        key=f'time{numero_time}_gols'
    )
    marcadores = st.text_area(
        f'Marcadores do Time {numero_time} (separados por vírgula)',
        key=f'time{numero_time}_marcadores'
    )

    # Coleta de jogadores
    titulares = coletar_jogadores(
        time_nome if time_nome else f"Time {numero_time}",
        "Titulares"
    )
    suplentes = coletar_jogadores(
        time_nome if time_nome else f"Time {numero_time}",
        "Suplentes"
    )

    time_info = {
        'Nome': time_nome,
        'Escudo': time_escudo,
        'Gols': gols,
        'Marcadores': marcadores,
        'Titulares': titulares,
        'Suplentes': suplentes
    }
    return time_info

# Função para gerar o PDF
def gerar_pdf(match_data):
    pdf = FPDF()
    pdf.add_page()

    # Título
    pdf.set_font("Helvetica", 'B', 20)
    pdf.cell(0, 10, 'Súmula do Jogo', ln=True, align='C')

    pdf.ln(10)

    # Informações da partida
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Estádio: {match_data['Estádio']}", ln=True)
    pdf.cell(0, 10, f"Data e Hora: {match_data['Data'].strftime('%d/%m/%Y')} às {match_data['Horário'].strftime('%H:%M')}", ln=True)
    pdf.cell(0, 10, f"Campeonato: {match_data['Campeonato']}", ln=True)

    pdf.ln(10)

    # Placar
    pdf.set_font("Helvetica", 'B', 16)
    placar = f"{match_data['Team1']['Nome'] or 'Time 1'} {match_data['Team1']['Gols']} x {match_data['Team2']['Gols']} {match_data['Team2']['Nome'] or 'Time 2'}"
    pdf.cell(0, 10, placar, ln=True, align='C')

    # Escudos dos times
    y_position = pdf.get_y()
    escudos_temp_files = []  # Lista para armazenar caminhos dos arquivos temporários

    # Processa escudo do Time 1
    if match_data['Team1']['Escudo'] is not None:
        try:
            team1_logo = Image.open(match_data['Team1']['Escudo'])
            team1_logo = team1_logo.convert("RGB")  # Garante que a imagem esteja em RGB
            team1_logo = team1_logo.resize((30, 30))
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp1:
                team1_logo.save(tmp1, format='PNG')
                tmp1_path = tmp1.name
                escudos_temp_files.append(tmp1_path)
            pdf.image(tmp1_path, x=30, y=y_position + 10, w=30)
        except Exception as e:
            st.error(f"Erro ao processar o escudo do Time 1: {e}")

    # Processa escudo do Time 2
    if match_data['Team2']['Escudo'] is not None:
        try:
            team2_logo = Image.open(match_data['Team2']['Escudo'])
            team2_logo = team2_logo.convert("RGB")  # Garante que a imagem esteja em RGB
            team2_logo = team2_logo.resize((30, 30))
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp2:
                team2_logo.save(tmp2, format='PNG')
                tmp2_path = tmp2.name
                escudos_temp_files.append(tmp2_path)
            pdf.image(tmp2_path, x=pdf.w - 60, y=y_position + 10, w=30)
        except Exception as e:
            st.error(f"Erro ao processar o escudo do Time 2: {e}")

    pdf.ln(40)

    # Detalhes dos times
    for team in ['Team1', 'Team2']:
        team_data = match_data[team]
        # Nome do time
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, team_data['Nome'] or f"Time {team[-1]}", ln=True)

        # Gols e marcadores
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Gols: {team_data.get('Gols', 0)}", ln=True)
        pdf.cell(0, 10, "Marcadores:", ln=True)
        marcadores_lista = [jogador.strip() for jogador in team_data.get('Marcadores', '').split(',') if jogador.strip()]
        for marcador in marcadores_lista:
            pdf.cell(0, 10, f"- {marcador}", ln=True)

        pdf.ln(5)

        # Titulares
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, "Titulares:", ln=True)
        pdf.set_font("Helvetica", size=12)
        # Cabeçalho da tabela
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(12, 8, 'Nº', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Nome', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Posição', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Amarelo', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Vermelho', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Saída (min.)', 1, 1, 'C', fill=True)

        # Dados dos titulares
        for jogador in team_data['Titulares']:
            pdf.cell(12, 6, str(jogador.get('Número', '')), 1, 0, 'C')
            pdf.cell(30, 6, jogador.get('Nome', ''), 1, 0, 'C')
            pdf.cell(30, 6, jogador.get('Posição', ''), 1, 0, 'C')
            pdf.cell(30, 6, 'Sim' if jogador.get('Amarelo') else '', 1, 0, 'C')
            pdf.cell(30, 6, 'Sim' if jogador.get('Vermelho') else '', 1, 0, 'C')
            pdf.cell(30, 6, str(jogador.get('Tempo de Saída', '')), 1, 1, 'C')

        pdf.ln(5)

        # Suplentes
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, "Suplentes:", ln=True)
        pdf.set_font("Helvetica", size=12)
        # Cabeçalho da tabela
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(12, 8, 'Nº', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Nome', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Posição', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Amarelo', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Vermelho', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Entrada (min.)', 1, 1, 'C', fill=True)

        # Dados dos suplentes
        for jogador in team_data['Suplentes']:
            pdf.cell(12, 6, str(jogador.get('Número', '')), 1, 0, 'C')
            pdf.cell(30, 6, jogador.get('Nome', ''), 1, 0, 'C')
            pdf.cell(30, 6, jogador.get('Posição', ''), 1, 0, 'C')
            pdf.cell(30, 6, 'Sim' if jogador.get('Amarelo') else '', 1, 0, 'C')
            pdf.cell(30, 6, 'Sim' if jogador.get('Vermelho') else '', 1, 0, 'C')
            pdf.cell(30, 6, str(jogador.get('Tempo de Entrada', '')), 1, 1, 'C')

        pdf.ln(5)

    # Descrição das substituições
    if match_data['Substituições']:
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, "Substituições:", ln=True)
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, match_data['Substituições'])
        pdf.ln(5)

    # Gerar o PDF e retornar os dados
    try:
        pdf_data = pdf.output(dest='S').encode('latin1', 'ignore')
    except Exception as e:
        st.error(f"Erro ao gerar o PDF: {e}")
        pdf_data = None

    # Remover arquivos temporários
    for tmp_file in escudos_temp_files:
        try:
            os.remove(tmp_file)
        except Exception as e:
            st.error(f"Erro ao remover arquivo temporário {tmp_file}: {e}")

    return pdf_data

# Função para gerar o CSV
def gerar_csv(data):
    csv_data = {
        'Time': [],
        'Número': [],
        'Nome': [],
        'Posição': [],
        'Titular/Suplente': [],
        'Amarelo': [],
        'Vermelho': [],
        'Tempo de Saída/Entrada': [],
        'Gols': [],
        'Marcadores': []
    }
    for team in ['Team1', 'Team2']:
        team_data = data[team]
        for jogador in team_data['Titulares']:
            csv_data['Time'].append(team_data['Nome'] or f"Time {team[-1]}")
            csv_data['Número'].append(jogador.get('Número', ''))
            csv_data['Nome'].append(jogador.get('Nome', ''))
            csv_data['Posição'].append(jogador.get('Posição', ''))
            csv_data['Titular/Suplente'].append('Titular')
            csv_data['Amarelo'].append('Sim' if jogador.get('Amarelo') else 'Não')
            csv_data['Vermelho'].append('Sim' if jogador.get('Vermelho') else 'Não')
            # Indica se é tempo de saída ou entrada
            csv_data['Tempo de Saída/Entrada'].append(jogador.get('Tempo de Saída', ''))
            csv_data['Gols'].append(team_data.get('Gols', ''))
            csv_data['Marcadores'].append(team_data.get('Marcadores', ''))
        for jogador in team_data['Suplentes']:
            csv_data['Time'].append(team_data['Nome'] or f"Time {team[-1]}")
            csv_data['Número'].append(jogador.get('Número', ''))
            csv_data['Nome'].append(jogador.get('Nome', ''))
            csv_data['Posição'].append(jogador.get('Posição', ''))
            csv_data['Titular/Suplente'].append('Suplente')
            csv_data['Amarelo'].append('Sim' if jogador.get('Amarelo') else 'Não')
            csv_data['Vermelho'].append('Sim' if jogador.get('Vermelho') else 'Não')
            csv_data['Tempo de Saída/Entrada'].append(jogador.get('Tempo de Entrada', ''))
            csv_data['Gols'].append(team_data.get('Gols', ''))
            csv_data['Marcadores'].append(team_data.get('Marcadores', ''))

    df_csv = pd.DataFrame(csv_data)
    try:
        csv_bytes = df_csv.to_csv(index=False).encode('utf-8')
    except Exception as e:
        st.error(f"Erro ao gerar o CSV: {e}")
        csv_bytes = None
    return csv_bytes

# Coleta de informações gerais da partida
st.title("Gerador de Súmula de Jogo")

st.header("Informações da Partida")
# Organizar os campos na mesma linha
col_partida1, col_partida2, col_partida3, col_partida4 = st.columns(4)

with col_partida1:
    estadio = st.text_input("Estádio")

with col_partida2:
    data_jogo = st.date_input("Data do Jogo", value=datetime.today())

with col_partida3:
    horario_jogo = st.time_input("Horário do Jogo", value=time(15, 0))

with col_partida4:
    campeonato = st.text_input("Campeonato")

# Coleta de informações dos times em colunas lado a lado
st.header("Informações dos Times")
col_time1, col_time2 = st.columns(2)

with col_time1:
    st.subheader("Time 1")
    info_time1 = coletar_info_time(1)

with col_time2:
    st.subheader("Time 2")
    info_time2 = coletar_info_time(2)

# Coleta das substituições após a inclusão dos jogadores
st.header("Substituições")
substituicoes_descricao = st.text_area("Descreva as substituições ocorridas durante o jogo")

# Geração da súmula e arquivos
st.header("Súmula do Jogo")

match_data = {
    'Team1': info_time1,
    'Team2': info_time2,
    'Estádio': estadio,
    'Data': data_jogo,
    'Horário': horario_jogo,
    'Campeonato': campeonato,
    'Substituições': substituicoes_descricao
}

# Gerar PDF e CSV apenas se informações mínimas forem fornecidas
required_fields_filled = (
    estadio and campeonato and
    info_time1['Nome'] and info_time2['Nome']
)

if required_fields_filled:
    pdf_data = gerar_pdf(match_data)
    csv_data = gerar_csv(match_data)

    # Exibir a súmula
    st.write(f"### {info_time1.get('Nome', 'Time 1')} {info_time1.get('Gols', 0)} x {info_time2.get('Gols', 0)} {info_time2.get('Nome', 'Time 2')}")
    st.write(f"**Estádio:** {estadio}")
    st.write(f"**Data e Hora:** {data_jogo.strftime('%d/%m/%Y')} às {horario_jogo.strftime('%H:%M')}")
    st.write(f"**Campeonato:** {campeonato}")
    if substituicoes_descricao:
        st.write("**Substituições:**")
        st.write(substituicoes_descricao)

    st.markdown("---")
    st.header("Download dos Arquivos")
    col8, col9 = st.columns(2)
    with col8:
        if csv_data:
            st.download_button(
                label="📥 Baixar CSV",
                data=csv_data,
                file_name='sumula_jogo.csv',
                mime='text/csv'
            )
    with col9:
        if pdf_data:
            st.download_button(
                label="📥 Baixar PDF",
                data=pdf_data,
                file_name='sumula_jogo.pdf',
                mime='application/pdf'
            )
else:
    st.warning("Por favor, preencha todas as informações obrigatórias para gerar a súmula e os arquivos.")