"""
Portfolio - Gestión de posiciones
"""

import streamlit as st
from utils.database import (get_user_positions, add_position, update_position, 
                            delete_position, calculate_portfolio_metrics)
from utils.market_data import get_current_price, get_stock_info, detect_currency, convert_to_usd
from datetime import datetime, date
import pandas as pd

def show(supabase, user):
    """Mostrar página de gestión de portfolio"""
    
    st.markdown("# 💼 Mi Portfolio")
    st.markdown("Gestiona tus posiciones de inversión")
    
    tab1, tab2 = st.tabs(["📋 Ver Posiciones", "➕ Agregar Posición"])
    
    with tab1:
        show_positions(supabase, user)
    
    with tab2:
        add_new_position(supabase, user)

def show_positions(supabase, user):
    """Mostrar y gestionar posiciones existentes"""
    
    positions = get_user_positions(supabase, user['id'])
    
    if not positions:
        st.info("No tienes posiciones en tu portfolio. Agrega una nueva posición usando la pestaña de arriba.")
        return
    
    # Obtener precios actuales
    with st.spinner("Actualizando precios..."):
        current_prices = {}
        for position in positions:
            ticker = position['ticker']
            price_info = get_current_price(ticker)
            if price_info:
                current_prices[ticker] = price_info
            else:
                currency = detect_currency(ticker)
                current_prices[ticker] = {
                    'price': position['purchase_price'],
                    'currency': currency,
                    'price_usd': convert_to_usd(position['purchase_price'], currency)
                }
    
    # Calcular métricas
    metrics = calculate_portfolio_metrics(positions, current_prices)
    
    # Mostrar cada posición con opciones de edición
    st.markdown("### Tus Posiciones")
    
    for detail in metrics['positions_detail']:
        with st.expander(f"**{detail['ticker']}** - ${detail['current_value']:,.2f} USD", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Información de la Posición")
                st.markdown(f"**Cantidad:** {detail['quantity']:.4f}")
                st.markdown(f"**Precio de Compra:** ${detail['purchase_price']:.2f} {detail['currency']}")
                st.markdown(f"**Precio Actual:** ${detail['current_price']:.2f} {detail['currency']}")
                st.markdown(f"**Fecha de Compra:** {detail['purchase_date']}")
            
            with col2:
                st.markdown("#### 💰 Rendimiento (en USD)")
                st.markdown(f"**Invertido:** ${detail['invested']:,.2f} USD")
                st.markdown(f"**Valor Actual:** ${detail['current_value']:,.2f} USD")
                
                pnl_color = "green" if detail['pnl'] >= 0 else "red"
                st.markdown(f"**P&L:** :{pnl_color}[${detail['pnl']:,.2f} ({detail['pnl_pct']:.2f}%)]")
                st.markdown(f"**Distribución:** {detail['allocation']:.1f}%")
            
            st.markdown("---")
            
            # Opciones de eliminación
            if st.button(f"🗑️ Eliminar {detail['ticker']}", key=f"delete_{detail['id']}", use_container_width=True):
                if delete_position(supabase, detail['id']):
                    st.success(f"Posición {detail['ticker']} eliminada correctamente")
                    st.rerun()

def add_new_position(supabase, user):
    """Formulario para agregar nueva posición"""
    
    st.markdown("### Agregar Nueva Posición")
    
    # Banner informativo destacado
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%); 
                padding: 1.5rem; 
                border-radius: 12px; 
                border-left: 4px solid #00d4aa; 
                margin-bottom: 1.5rem;">
        <h4 style="margin-top: 0; color: #00d4aa;">📋 Guía Rápida de Tickers</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <strong style="color: #10b981;">🇺🇸 USA / ADRs:</strong><br>
                <code>AAPL</code> <code>MSFT</code> <code>MELI</code> <code>GOOGL</code><br>
                <small style="color: #9ca3af;">Sin sufijo</small>
            </div>
            <div>
                <strong style="color: #f59e0b;">🇦🇷 Argentina / CEDEARs:</strong><br>
                <code>YPFD.BA</code> <code>AAPL.BA</code> <code>MSFT.BA</code><br>
                <small style="color: #9ca3af;">⚠️ Agregar <strong>.BA</strong> al final</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Ingresa los detalles de tu nueva inversión")
    
    with st.form("add_position_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input(
                "Ticker *", 
                placeholder="Ej: AAPL, MELI, YPFD.BA, AAPL.BA",
                help="Acciones USA: AAPL | Acciones ARG: YPFD.BA | CEDEARs: AAPL.BA"
            ).upper()
        
        st.markdown("---")
        
        # Preview de la inversión
        if ticker and quantity > 0 and purchase_price > 0:
            total_invested = quantity * purchase_price
            currency = detect_currency(ticker)
            
            st.markdown("#### 📊 Vista Previa")
            col_prev1, col_prev2, col_prev3, col_prev4 = st.columns(4)
            
            with col_prev1:
                st.metric("Ticker", ticker)
            with col_prev2:
                st.metric("Moneda", currency)
            with col_prev3:
                st.metric("Cantidad", f"{quantity:.4f}")
            with col_prev4:
                st.metric("Inversión Total", f"${total_invested:,.2f} {currency}")
            
            # Validar ticker con Yahoo Finance
            with st.spinner("Validando ticker..."):
                price_info = get_current_price(ticker)
                stock_info = get_stock_info(ticker)
                
                if price_info:
                    st.success(f"✅ Ticker válido - **{stock_info['name']}** - Precio actual: ${price_info['price']:.2f} {price_info['currency']}")
                else:
                    st.warning("⚠️ No se pudo validar el ticker. Asegúrate de que sea correcto.")
        
        submit = st.form_submit_button("➕ Agregar Posición", use_container_width=True, type="primary")
        
        if submit:
            if ticker and quantity > 0 and purchase_price > 0:
                try:
                    result = add_position(supabase, user['id'], ticker, quantity, 
                                  purchase_price, str(purchase_date))
                    
                    if result:
                        st.success(f"✅ Posición {ticker} agregada correctamente!")
                        st.balloons()
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ No se pudo agregar la posición.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Por favor completa todos los campos requeridos")
