"""
Estilos personalizados para Portfolio Manager
Diseño moderno, minimalista y profesional con modo oscuro
"""

import streamlit as st

def apply_custom_styles():
    """Aplicar estilos CSS personalizados a la aplicación"""
    
    st.markdown("""
    <style>
    /* Importar fuentes únicas y modernas */
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');
    
    /* Variables de color - Tema oscuro profesional */
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #141821;
        --bg-card: #1a1f2e;
        --bg-hover: #232938;
        --accent-primary: #00d4aa;
        --accent-secondary: #7c3aed;
        --text-primary: #e8eaed;
        --text-secondary: #9ca3af;
        --text-muted: #6b7280;
        --border-color: #2d3748;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Reset y estilos base */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f1419 100%);
        font-family: 'Sora', sans-serif;
        color: var(--text-primary);
    }
    
    /* Sidebar personalizado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }
    
    /* Información de usuario en sidebar */
    .user-info {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .user-avatar {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    
    .user-details {
        flex: 1;
        min-width: 0;
    }
    
    .user-email {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .user-role {
        font-size: 0.75rem;
        color: var(--accent-primary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }
    
    /* Botones personalizados */
    .stButton > button {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        font-family: 'Sora', sans-serif;
    }
    
    .stButton > button:hover {
        background: var(--bg-hover);
        border-color: var(--accent-primary);
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.2);
        transform: translateY(-2px);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-primary), #00b894);
        border: none;
        color: var(--bg-primary);
        font-weight: 600;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 24px rgba(0, 212, 170, 0.3);
    }
    
    /* Inputs y forms */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem;
        font-family: 'Sora', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-card);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-primary), #00b894);
        color: var(--bg-primary);
    }
    
    /* Métricas personalizadas */
    [data-testid="stMetricValue"] {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'Space Mono', monospace;
        font-weight: 600;
    }
    
    /* Cards y containers */
    .metric-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 8px 32px rgba(0, 212, 170, 0.15);
        transform: translateY(-4px);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .metric-change.positive {
        color: var(--success);
    }
    
    .metric-change.negative {
        color: var(--danger);
    }
    
    /* Auth page */
    .auth-header {
        text-align: center;
        padding: 3rem 1rem;
        margin-bottom: 2rem;
    }
    
    .auth-header h1 {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    
    .auth-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
    }
    
    /* Dataframe personalizado */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--accent-primary);
    }
    
    /* Sidebar footer */
    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-primary);
        font-family: 'Sora', sans-serif;
    }
    
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    h3 {
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }
    
    /* Alerts personalizados */
    .stAlert {
        border-radius: 12px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--accent-primary) transparent transparent transparent;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: var(--bg-card);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: var(--accent-primary);
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .auth-header h1 {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
