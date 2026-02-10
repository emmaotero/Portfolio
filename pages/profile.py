"""
Perfil del Inversor - Configuración de preferencias
"""

import streamlit as st
from utils.database import get_investor_profile, update_investor_profile

def show(supabase, user):
    """Mostrar página de perfil del inversor"""
    
    st.markdown("# 👤 Perfil del Inversor")
    st.markdown("Define tu estrategia y preferencias de inversión")
    
    # Obtener perfil actual
    profile = get_investor_profile(supabase, user['id'])
    
    if not profile:
        profile = {
            'investment_horizon': 'medio_plazo',
            'risk_tolerance': 'moderado',
            'investment_goal': 'capitalizacion'
        }
    
    st.markdown("---")
    
    # Formulario de perfil
    with st.form("investor_profile_form"):
        st.markdown("### 🎯 Objetivos de Inversión")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Horizonte de inversión
            st.markdown("#### ⏱️ Horizonte de Inversión")
            st.markdown("¿Cuánto tiempo planeas mantener tus inversiones?")
            
            investment_horizon = st.radio(
                "Horizonte",
                options=["corto_plazo", "medio_plazo", "largo_plazo"],
                index=["corto_plazo", "medio_plazo", "largo_plazo"].index(profile.get('investment_horizon', 'medio_plazo')),
                format_func=lambda x: {
                    "corto_plazo": "📅 Corto Plazo (< 1 año)",
                    "medio_plazo": "📆 Medio Plazo (1-5 años)",
                    "largo_plazo": "🗓️ Largo Plazo (> 5 años)"
                }[x],
                label_visibility="collapsed"
            )
            
            # Mostrar descripción
            horizon_descriptions = {
                "corto_plazo": "Ideal para trading activo y ganancias rápidas. Mayor volatilidad.",
                "medio_plazo": "Balance entre crecimiento y estabilidad. Enfoque balanceado.",
                "largo_plazo": "Maximizar acumulación de capital. Enfoque en fundamentales."
            }
            st.info(horizon_descriptions[investment_horizon])
        
        with col2:
            # Objetivo de inversión
            st.markdown("#### 🎯 Objetivo Principal")
            st.markdown("¿Qué buscas lograr con tus inversiones?")
            
            investment_goal = st.radio(
                "Objetivo",
                options=["capitalizacion", "ingresos", "preservacion", "trading"],
                index=["capitalizacion", "ingresos", "preservacion", "trading"].index(profile.get('investment_goal', 'capitalizacion')),
                format_func=lambda x: {
                    "capitalizacion": "📈 Capitalización (Growth)",
                    "ingresos": "💰 Ingresos (Dividendos)",
                    "preservacion": "🛡️ Preservación de Capital",
                    "trading": "⚡ Trading Activo"
                }[x],
                label_visibility="collapsed"
            )
            
            # Mostrar descripción
            goal_descriptions = {
                "capitalizacion": "Buscar acciones de crecimiento y maximizar el valor del portfolio.",
                "ingresos": "Priorizar acciones que paguen dividendos consistentes.",
                "preservacion": "Minimizar riesgo y proteger el capital existente.",
                "trading": "Aprovechar movimientos de corto plazo del mercado."
            }
            st.info(goal_descriptions[investment_goal])
        
        st.markdown("---")
        
        # Tolerancia al riesgo
        st.markdown("### ⚖️ Tolerancia al Riesgo")
        st.markdown("¿Cuánta volatilidad estás dispuesto a aceptar?")
        
        risk_tolerance = st.select_slider(
            "Nivel de riesgo",
            options=["conservador", "moderado_conservador", "moderado", "moderado_agresivo", "agresivo"],
            value=profile.get('risk_tolerance', 'moderado'),
            format_func=lambda x: {
                "conservador": "🛡️ Conservador",
                "moderado_conservador": "🔒 Moderado-Conservador",
                "moderado": "⚖️ Moderado",
                "moderado_agresivo": "📊 Moderado-Agresivo",
                "agresivo": "🚀 Agresivo"
            }[x],
            label_visibility="collapsed"
        )
        
        # Descripción del nivel de riesgo
        risk_descriptions = {
            "conservador": """
            **Perfil Conservador:**
            - Prioridad en preservar capital
            - Baja tolerancia a pérdidas
            - Preferencia por bonos, acciones estables y blue chips
            - Volatilidad esperada: Baja
            """,
            "moderado_conservador": """
            **Perfil Moderado-Conservador:**
            - Balance inclinado hacia seguridad
            - Acepta algo de riesgo por mejores retornos
            - Mix de acciones estables y algunos growth
            - Volatilidad esperada: Baja-Media
            """,
            "moderado": """
            **Perfil Moderado:**
            - Balance equilibrado entre riesgo y retorno
            - Acepta volatilidad temporal
            - Portfolio diversificado en sectores
            - Volatilidad esperada: Media
            """,
            "moderado_agresivo": """
            **Perfil Moderado-Agresivo:**
            - Busca crecimiento superior
            - Acepta volatilidad significativa
            - Mayor exposición a growth stocks
            - Volatilidad esperada: Media-Alta
            """,
            "agresivo": """
            **Perfil Agresivo:**
            - Maximizar retornos potenciales
            - Alta tolerancia a pérdidas temporales
            - Exposición a activos de alto crecimiento
            - Volatilidad esperada: Alta
            """
        }
        
        st.markdown(risk_descriptions[risk_tolerance])
        
        st.markdown("---")
        
        # Botón de guardar
        submit = st.form_submit_button("💾 Guardar Perfil", use_container_width=True, type="primary")
        
        if submit:
            if update_investor_profile(
                supabase, 
                user['id'],
                investment_horizon=investment_horizon,
                risk_tolerance=risk_tolerance,
                investment_goal=investment_goal
            ):
                st.success("✅ Perfil actualizado correctamente!")
                st.balloons()
            else:
                st.error("❌ Error al actualizar el perfil")
    
    st.markdown("---")
    
    # Recomendaciones basadas en el perfil
    show_recommendations(investment_horizon, risk_tolerance, investment_goal)

def show_recommendations(horizon, risk, goal):
    """Mostrar recomendaciones basadas en el perfil"""
    
    st.markdown("### 💡 Recomendaciones Personalizadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Asignación de Activos Sugerida")
        
        # Determinar asignación basada en perfil
        allocations = get_asset_allocation(risk)
        
        for asset, percentage in allocations.items():
            st.markdown(f"**{asset}:** {percentage}%")
            st.progress(percentage / 100)
    
    with col2:
        st.markdown("#### 🎯 Estrategias Recomendadas")
        
        strategies = get_recommended_strategies(horizon, risk, goal)
        
        for strategy in strategies:
            st.markdown(f"✓ {strategy}")
    
    st.markdown("---")
    
    # Tips adicionales
    st.markdown("#### 📚 Consejos de Inversión")
    
    tips = get_investment_tips(risk, goal)
    
    for tip in tips:
        st.info(tip)

def get_asset_allocation(risk_level):
    """Obtener asignación de activos basada en tolerancia al riesgo"""
    
    allocations = {
        "conservador": {
            "Acciones Blue Chip": 30,
            "Bonos": 50,
            "Efectivo": 15,
            "Otros": 5
        },
        "moderado_conservador": {
            "Acciones Blue Chip": 40,
            "Acciones Growth": 10,
            "Bonos": 40,
            "Efectivo": 10
        },
        "moderado": {
            "Acciones Blue Chip": 35,
            "Acciones Growth": 25,
            "Bonos": 30,
            "Efectivo": 10
        },
        "moderado_agresivo": {
            "Acciones Blue Chip": 25,
            "Acciones Growth": 45,
            "Bonos": 20,
            "Efectivo": 10
        },
        "agresivo": {
            "Acciones Growth": 60,
            "Acciones Blue Chip": 20,
            "Bonos": 10,
            "Efectivo": 10
        }
    }
    
    return allocations.get(risk_level, allocations["moderado"])

def get_recommended_strategies(horizon, risk, goal):
    """Obtener estrategias recomendadas"""
    
    strategies = []
    
    # Estrategias basadas en horizonte
    if horizon == "largo_plazo":
        strategies.append("Dollar Cost Averaging (DCA) - Inversión periódica constante")
        strategies.append("Buy and Hold - Mantener inversiones a largo plazo")
    elif horizon == "medio_plazo":
        strategies.append("Rebalanceo trimestral del portfolio")
        strategies.append("Mix de value y growth investing")
    else:
        strategies.append("Trading con análisis técnico")
        strategies.append("Stop-loss para limitar pérdidas")
    
    # Estrategias basadas en objetivo
    if goal == "ingresos":
        strategies.append("Enfocarse en acciones con dividendos altos y consistentes")
    elif goal == "capitalizacion":
        strategies.append("Priorizar empresas con alto potencial de crecimiento")
    elif goal == "trading":
        strategies.append("Usar indicadores técnicos para timing de entrada/salida")
    
    return strategies

def get_investment_tips(risk, goal):
    """Obtener consejos de inversión"""
    
    tips = []
    
    # Tips generales
    tips.append("🎯 Diversifica tu portfolio para reducir riesgo no sistemático")
    tips.append("📊 Revisa y rebalancea tu portfolio regularmente")
    tips.append("📚 Mantente informado sobre las empresas en las que inviertes")
    
    # Tips específicos por riesgo
    if risk in ["conservador", "moderado_conservador"]:
        tips.append("🛡️ Considera ETFs de índices para diversificación automática")
    elif risk in ["moderado_agresivo", "agresivo"]:
        tips.append("⚠️ Usa stop-loss para proteger ganancias y limitar pérdidas")
    
    # Tips específicos por objetivo
    if goal == "ingresos":
        tips.append("💰 Considera el rendimiento de dividendos y la consistencia de pagos")
    elif goal == "trading":
        tips.append("⚡ No inviertas dinero que puedas necesitar en el corto plazo")
    
    return tips
