import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from PIL                 import Image
from io                  import BytesIO


custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Função para ler os dados
@st.cache(show_spinner= True, allow_output_mutation=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data)
    except:
        return pd.read_excel(file_data)

# Função para filtrar baseado na multiseleção de categorias
@st.cache(allow_output_mutation=True)
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


#funcao main
def main():
    # Configuração inicial da página da aplicação
    st.set_page_config(page_title = 'Preço carro 0KM',
        #page_icon = '../img/telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded')

    # Título principal da aplicação
    st.write('# Preço carro 0KM')
    st.markdown("---")
    
    # Apresenta a imagem na barra lateral da aplicação
    #image = Image.open("../img/Bank-Branding.jpg")
    #st.sidebar.image(image)

    #lendo arquivo 
    df = load_data('DF_TRATADOC.csv')
    df['Mês de referência'] = pd.to_datetime(df['Mês de referência'])
    
    #categorizar por faixa de preco
    def categorizar(row):
        same_date_rows = df[df['Mês de referência'] == row['Mês de referência']]
        price_percentiles = same_date_rows['Preço Médio'].quantile([0.1, 0.5, 0.7, 0.9])
        if row['Preço Médio'] <= price_percentiles[0.1]:
            return 'popular'
        elif (row['Preço Médio'] > price_percentiles[0.1]) & (row['Preço Médio'] <= price_percentiles[0.5]):
            return 'intermediario'
        elif (row['Preço Médio'] > price_percentiles[0.5]) & (row['Preço Médio'] <= price_percentiles[0.9]):
            return 'luxo'
        elif row['Preço Médio'] > price_percentiles[0.9]:
            return 'ultra luxo'
    @st.cache_data
    def gerar_categoria(df):
        df['categoria'] = df.apply(categorizar, axis=1)
        return df
    df = gerar_categoria(df)
    #criando sidebar
    with st.sidebar.form(key='my_form'):

        cat_opt = ['Todas'] + df['categoria'].unique().tolist()
        cat  = st.sidebar.selectbox('categoria',cat_opt)
        if cat != 'Todas':
            df = df[df['categoria'] == cat]



        # ano
        min_data = df['Mês de referência'].min()
        max_data = df['Mês de referência'].max()
        data_inicial = st.sidebar.date_input('Data inicial', 
                        value = min_data,
                        min_value = min_data,
                        max_value = max_data)
        data_final = st.sidebar.date_input('Data final', 
                        value = max_data,
                        min_value = min_data,
                        max_value = max_data)
        #escolhendo marca e modelo
        marca_opt = ['Todas'] + df['Marca'].unique().tolist()
        marca  = st.sidebar.selectbox('marca',marca_opt)
        if marca != 'Todas':
            df = df[df['Marca'] == marca]
            modelo_opt = ['Todas'] + df['Modelo'].unique().tolist()
            modelo  = st.sidebar.selectbox('Modelo',modelo_opt)
            if modelo != 'Todas':
                df = df[df['Modelo'] == modelo]

        df_filtrado =  df.loc[(df['Mês de referência'] >= pd.to_datetime(data_inicial)) & (df['Mês de referência'] <= pd.to_datetime(data_final))]
        submit_button = st.form_submit_button(label='Aplicar')


    st.write('## Após os filtros')
    st.write(df_filtrado)
    st.markdown("---")
    
    plot = sns.lineplot(y = df_filtrado['Preço Médio'],x = df_filtrado['Mês de referência'])

    #salvando imagem na memoria 
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    #mostando imagem
    st.image(image_stream, use_column_width=True)

    # criando botao para download da imagem
    st.download_button(
        label='Download Plot Image',
        data=image_stream,
        file_name='plot.png',
        mime='image/png')


if __name__ == '__main__':
	main()