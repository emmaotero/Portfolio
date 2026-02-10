"""
Utilidades para obtener datos de mercado y calcular indicadores técnicos
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

# Tasa de cambio USD/ARS (puedes obtenerla de una API en el futuro)
@st.cache_data(ttl=3600)
def get_usd_ars_rate() -> float:
    """
    Obtener tasa de cambio USD a ARS
    En el futuro puedes usar una API como exchangerate-api.com
    """
    try:
        # Usar Yahoo Finance para obtener el tipo de cambio
        usd_ars = yf.Ticker("USDARS=X")
        data = usd_ars.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        # Fallback a tasa aproximada
        return 1000.0
    except:
        # Fallback si falla la API
        return 1000.0

def detect_currency(ticker: str) -> str:
    """
    Detectar la moneda de un ticker basado en su sufijo
    
    Args:
        ticker: Símbolo del ticker
        
    Returns:
        str: Código de moneda (USD, ARS, etc.)
    """
    ticker_upper = ticker.upper()
    
    # Tickers argentinos
    if ticker_upper.endswith('.BA'):
        return 'ARS'
    
    # Tickers brasileños
    elif ticker_upper.endswith('.SA'):
        return 'BRL'
    
    # Tickers mexicanos
    elif ticker_upper.endswith('.MX'):
        return 'MXN'
    
    # Por defecto USD (acciones US, ADRs como MELI)
    else:
        return 'USD'

def convert_to_usd(price: float, currency: str) -> float:
    """
    Convertir un precio a USD
    
    Args:
        price: Precio en moneda original
        currency: Código de moneda
        
    Returns:
        float: Precio en USD
    """
    if currency == 'USD':
        return price
    
    elif currency == 'ARS':
        usd_ars = get_usd_ars_rate()
        return price / usd_ars
    
    # Puedes agregar más monedas aquí
    elif currency == 'BRL':
        # Aproximado - idealmente usar API
        return price / 5.0
    
    elif currency == 'MXN':
        # Aproximado - idealmente usar API
        return price / 17.0
    
    else:
        return price

@st.cache_data(ttl=300)
def get_current_price(ticker: str) -> dict:
    """
    Obtener precio actual de un ticker con información de moneda
    
    Args:
        ticker: Símbolo del ticker (ej: AAPL, MELI, COME.BA)
        
    Returns:
        dict: {'price': float, 'currency': str, 'price_usd': float} o None si hay error
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        
        if not data.empty:
            price = round(data['Close'].iloc[-1], 2)
            currency = detect_currency(ticker)
            price_usd = convert_to_usd(price, currency)
            
            return {
                'price': price,
                'currency': currency,
                'price_usd': round(price_usd, 2),
                'ticker': ticker
            }
        return None
    except Exception as e:
        print(f"Error obteniendo precio de {ticker}: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_stock_info(ticker: str) -> dict:
    """
    Obtener información general de un ticker
    
    Args:
        ticker: Símbolo del ticker
        
    Returns:
        dict: Información del ticker
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'currency': info.get('currency', 'USD')
        }
    except Exception as e:
        print(f"Error obteniendo info de {ticker}: {str(e)}")
        return {
            'name': ticker,
            'sector': 'N/A',
            'industry': 'N/A',
            'currency': 'USD'
        }

@st.cache_data(ttl=3600)
def get_historical_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Obtener datos históricos de un ticker
    
    Args:
        ticker: Símbolo del ticker
        period: Período de datos (1mo, 3mo, 6mo, 1y, 2y, 5y)
        
    Returns:
        DataFrame: Datos históricos con OHLCV
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error obteniendo datos históricos de {ticker}: {str(e)}")
        return pd.DataFrame()

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calcular RSI (Relative Strength Index)
    
    Args:
        data: DataFrame con precios
        period: Período para el cálculo (default: 14)
        
    Returns:
        Series: Valores de RSI
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    Calcular MACD (Moving Average Convergence Divergence)
    
    Args:
        data: DataFrame con precios
        fast: Período EMA rápida (default: 12)
        slow: Período EMA lenta (default: 26)
        signal: Período línea de señal (default: 9)
        
    Returns:
        tuple: (MACD line, Signal line, Histogram)
    """
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return macd, signal_line, histogram

def calculate_sma(data: pd.DataFrame, period: int) -> pd.Series:
    """
    Calcular SMA (Simple Moving Average)
    
    Args:
        data: DataFrame con precios
        period: Período para el promedio móvil
        
    Returns:
        Series: Valores de SMA
    """
    return data['Close'].rolling(window=period).mean()

def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> tuple:
    """
    Calcular Bandas de Bollinger
    
    Args:
        data: DataFrame con precios
        period: Período para el cálculo (default: 20)
        std_dev: Desviaciones estándar (default: 2)
        
    Returns:
        tuple: (Upper band, Middle band, Lower band)
    """
    middle_band = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band

def get_technical_indicators(ticker: str, period: str = "1y") -> dict:
    """
    Obtener todos los indicadores técnicos para un ticker
    
    Args:
        ticker: Símbolo del ticker
        period: Período de datos
        
    Returns:
        dict: Diccionario con todos los indicadores
    """
    try:
        data = get_historical_data(ticker, period)
        
        if data.empty:
            return None
        
        # Calcular todos los indicadores
        rsi = calculate_rsi(data)
        macd, signal, histogram = calculate_macd(data)
        sma_50 = calculate_sma(data, 50)
        sma_200 = calculate_sma(data, 200)
        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(data)
        
        # Obtener valores actuales
        current_price = data['Close'].iloc[-1]
        
        return {
            'data': data,
            'current_price': round(current_price, 2),
            'rsi': round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None,
            'macd': {
                'macd': round(macd.iloc[-1], 2) if not pd.isna(macd.iloc[-1]) else None,
                'signal': round(signal.iloc[-1], 2) if not pd.isna(signal.iloc[-1]) else None,
                'histogram': round(histogram.iloc[-1], 2) if not pd.isna(histogram.iloc[-1]) else None,
                'series': {'macd': macd, 'signal': signal, 'histogram': histogram}
            },
            'sma_50': round(sma_50.iloc[-1], 2) if not pd.isna(sma_50.iloc[-1]) else None,
            'sma_200': round(sma_200.iloc[-1], 2) if not pd.isna(sma_200.iloc[-1]) else None,
            'bollinger_bands': {
                'upper': round(upper_bb.iloc[-1], 2) if not pd.isna(upper_bb.iloc[-1]) else None,
                'middle': round(middle_bb.iloc[-1], 2) if not pd.isna(middle_bb.iloc[-1]) else None,
                'lower': round(lower_bb.iloc[-1], 2) if not pd.isna(lower_bb.iloc[-1]) else None,
                'series': {'upper': upper_bb, 'middle': middle_bb, 'lower': lower_bb}
            },
            'series': {
                'rsi': rsi,
                'sma_50': sma_50,
                'sma_200': sma_200
            }
        }
    except Exception as e:
        print(f"Error calculando indicadores para {ticker}: {str(e)}")
        return None

def interpret_rsi(rsi: float) -> dict:
    """
    Interpretar valor de RSI
    
    Args:
        rsi: Valor de RSI
        
    Returns:
        dict: Interpretación y señal
    """
    if rsi is None:
        return {'signal': 'neutral', 'description': 'Datos insuficientes'}
    
    if rsi >= 70:
        return {'signal': 'sobrecompra', 'description': 'Posible sobrecompra, considerar venta'}
    elif rsi <= 30:
        return {'signal': 'sobreventa', 'description': 'Posible sobreventa, considerar compra'}
    else:
        return {'signal': 'neutral', 'description': 'En rango neutral'}

def interpret_macd(macd: float, signal: float) -> dict:
    """
    Interpretar MACD
    
    Args:
        macd: Valor MACD
        signal: Valor señal
        
    Returns:
        dict: Interpretación y señal
    """
    if macd is None or signal is None:
        return {'signal': 'neutral', 'description': 'Datos insuficientes'}
    
    if macd > signal:
        return {'signal': 'alcista', 'description': 'Tendencia alcista'}
    else:
        return {'signal': 'bajista', 'description': 'Tendencia bajista'}

def interpret_sma(current_price: float, sma_50: float, sma_200: float) -> dict:
    """
    Interpretar SMAs
    
    Args:
        current_price: Precio actual
        sma_50: SMA de 50 días
        sma_200: SMA de 200 días
        
    Returns:
        dict: Interpretación y señal
    """
    if sma_50 is None or sma_200 is None:
        return {'signal': 'neutral', 'description': 'Datos insuficientes'}
    
    if sma_50 > sma_200 and current_price > sma_50:
        return {'signal': 'muy_alcista', 'description': 'Golden Cross - Fuerte tendencia alcista'}
    elif sma_50 < sma_200 and current_price < sma_50:
        return {'signal': 'muy_bajista', 'description': 'Death Cross - Fuerte tendencia bajista'}
    elif current_price > sma_50:
        return {'signal': 'alcista', 'description': 'Por encima de SMA 50'}
    else:
        return {'signal': 'bajista', 'description': 'Por debajo de SMA 50'}

def interpret_bollinger(current_price: float, upper: float, middle: float, lower: float) -> dict:
    """
    Interpretar Bandas de Bollinger
    
    Args:
        current_price: Precio actual
        upper: Banda superior
        middle: Banda media
        lower: Banda inferior
        
    Returns:
        dict: Interpretación y señal
    """
    if upper is None or middle is None or lower is None:
        return {'signal': 'neutral', 'description': 'Datos insuficientes'}
    
    band_range = upper - lower
    position = (current_price - lower) / band_range if band_range > 0 else 0.5
    
    if position >= 0.9:
        return {'signal': 'sobrecompra', 'description': 'Cerca de banda superior - Posible sobrecompra'}
    elif position <= 0.1:
        return {'signal': 'sobreventa', 'description': 'Cerca de banda inferior - Posible sobreventa'}
    elif position > 0.5:
        return {'signal': 'alcista', 'description': 'Por encima de la media'}
    else:
        return {'signal': 'bajista', 'description': 'Por debajo de la media'}
