#!/usr/bin/env python3
# laptop_analysis.py
# Análisis completo de dataset de portátiles

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import os

# Configuración inicial
pd.set_option('display.max_columns', None)
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

def ensure_dir(directory):
    """Asegura que un directorio exista"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def rupee_formatter(x, pos):
    """Formateador para valores en rupias"""
    return '₹{:,.0f}'.format(x)

def load_data(file_path):
    """
    Carga el dataset desde un archivo CSV
    
    Args:
        file_path (str): Ruta al archivo CSV
        
    Returns:
        pandas.DataFrame: DataFrame con los datos cargados o None si hay error
    """
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Dataset cargado correctamente. Filas: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Error al cargar {file_path}: {str(e)}")
        return None

def clean_data(df):
    """
    Realiza limpieza y transformación del dataset de portátiles
    
    Args:
        df (pandas.DataFrame): DataFrame original
        
    Returns:
        pandas.DataFrame: DataFrame limpio y transformado
    """
    # Copia del dataframe
    clean_df = df.copy()
    
    # Limpieza de precios
    clean_df['Price'] = (
        clean_df['Price']
        .str.replace('₹', '')
        .str.replace(',', '')
        .astype(float)
    )
    
    # Extracción de valores numéricos
    for col in ['Ram', 'SSD']:
        clean_df[col] = clean_df[col].str.extract('(\d+)').astype(float)
    
    # Normalización de columnas
    clean_df.columns = (
        clean_df.columns
        .str.lower()
        .str.replace(' ', '_')
    )
    
    # Manejo de valores faltantes
    clean_df['rating'] = clean_df['rating'].fillna(0)
    
    # Extracción y normalización de marcas
    clean_df['brand'] = clean_df['model'].str.split().str[0]
    brand_mapping = {
        'Apple': 'Apple', 'HP': 'HP', 'Lenovo': 'Lenovo',
        'Dell': 'Dell', 'Asus': 'Asus', 'Acer': 'Acer',
        'MSI': 'MSI', 'Samsung': 'Samsung', 'Xiaomi': 'Xiaomi',
        'Honor': 'Honor', 'Huawei': 'Huawei'
    }
    clean_df['brand'] = clean_df['brand'].replace(brand_mapping)
    
    print("✅ Datos limpiados y transformados")
    return clean_df

def perform_eda(df, save_dir='../reports/images'):
    """
    Realiza análisis exploratorio y guarda visualizaciones
    
    Args:
        df (pandas.DataFrame): DataFrame limpio
        save_dir (str): Directorio para guardar imágenes
    """
    ensure_dir(save_dir)
    
    # Estadísticas descriptivas
    print("\n📊 Estadísticas Descriptivas:")
    print(df[['price', 'ram', 'ssd', 'rating']].describe())
    
    # Matriz de correlación
    corr_matrix = df[['price', 'ram', 'ssd', 'rating']].corr()
    print("\n📈 Matriz de Correlación:")
    print(corr_matrix)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Matriz de Correlación')
    plt.tight_layout()
    plt.savefig(f'{save_dir}/correlation_matrix.png', dpi=300)
    plt.close()
    
    # Conteo por marca
    top_brands = df['brand'].value_counts().head(10)
    print("\n🏷️ Top 10 Marcas por cantidad:")
    print(top_brands)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_brands.index, y=top_brands.values)
    plt.title('Top 10 Marcas por Cantidad de Modelos')
    plt.xlabel('Marca')
    plt.ylabel('Cantidad')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{save_dir}/brands_count.png', dpi=300)
    plt.close()

def create_main_visualizations(df, save_dir='../reports/images'):
    """
    Crea visualizaciones principales del análisis
    
    Args:
        df (pandas.DataFrame): DataFrame limpio
        save_dir (str): Directorio para guardar imágenes
    """
    ensure_dir(save_dir)
    
    plt.figure(figsize=(16, 12))
    
    # 1. Distribución de precios
    plt.subplot(2, 2, 1)
    sns.histplot(df['price'], bins=30, kde=True)
    plt.gca().xaxis.set_major_formatter(FuncFormatter(rupee_formatter))
    plt.title('Distribución de Precios')
    
    # 2. RAM vs Precio
    plt.subplot(2, 2, 2)
    sns.boxplot(x='ram', y='price', data=df)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(rupee_formatter))
    plt.title('RAM vs Precio')
    
    # 3. Rating por marca
    plt.subplot(2, 2, 3)
    rating_df = df[df['rating'] > 0]
    sns.boxplot(x='brand', y='rating', data=rating_df)
    plt.xticks(rotation=45)
    plt.title('Rating por Marca')
    plt.ylim(40, 80)
    
    # 4. SSD vs Precio
    plt.subplot(2, 2, 4)
    sns.scatterplot(x='ssd', y='price', data=df, hue='ram', palette='viridis')
    plt.gca().yaxis.set_major_formatter(FuncFormatter(rupee_formatter))
    plt.title('SSD vs Precio (por RAM)')
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/main_analysis.png', dpi=300)
    plt.close()

def analyze_categories(df, save_dir='../reports/images'):
    """
    Analiza y visualiza datos por categorías
    
    Args:
        df (pandas.DataFrame): DataFrame limpio
        save_dir (str): Directorio para guardar imágenes
    """
    # Crear categorías
    df['category'] = 'General'
    df.loc[df['model'].str.contains('Gaming', case=False), 'category'] = 'Gaming'
    df.loc[df['brand'] == 'Apple', 'category'] = 'Apple'
    df.loc[df['model'].str.contains('Ultrabook|Thin|Slim', case=False), 'category'] = 'Ultrabook'
    
    print("\n🎮 Distribución por categorías:")
    print(df['category'].value_counts())
    
    # Visualización
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='category', y='price', data=df)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(rupee_formatter))
    plt.title('Precios por Categoría')
    plt.tight_layout()
    plt.savefig(f'{save_dir}/price_by_category.png', dpi=300)
    plt.close()

def main():
    """Función principal del análisis"""
    print("\n🖥️ Análisis de Portátiles - Inicio\n")
    
    # Obtener la ruta del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # Cargar datos
    data_path = os.path.join(project_dir, "data", "laptop.csv")
    df = load_data(data_path)
    
    if df is not None:
        # Limpieza
        clean_df = clean_data(df)
        
        # Definir directorio de reportes
        reports_dir = os.path.join(project_dir, "reports", "images")
        
        # Análisis exploratorio
        perform_eda(clean_df, reports_dir)
        
        # Visualizaciones
        create_main_visualizations(clean_df, reports_dir)
        
        # Análisis por categorías
        analyze_categories(clean_df, reports_dir)
        
        print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()