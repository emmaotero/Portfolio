"""
Paquete de páginas para Portfolio Manager
"""

from . import dashboard, portfolio, analysis, profile

__all__ = ['dashboard', 'portfolio', 'analysis', 'profile']
```

4. Commit
5. Luego agrega uno por uno:
   - `pages/dashboard.py`
   - `pages/portfolio.py`
   - `pages/analysis.py`
   - `pages/profile.py`

---

## 🚀 Método Rápido: Subir Carpetas Completas

Si tienes los archivos en tu computadora:

### Opción A: Arrastrar y Soltar (Desktop)

1. En tu repo de GitHub
2. **Click "Add file" → "Upload files"**
3. **Arrastra la carpeta completa `utils/`** desde tu computadora
4. GitHub subirá toda la carpeta con sus archivos
5. Commit
6. Repite con carpeta `pages/`

### Opción B: Usar GitHub Desktop (si lo tienes instalado)

1. Clona el repo
2. Copia las carpetas `utils/` y `pages/` a la carpeta local
3. Commit
4. Push

---

## 📊 Visual: Cómo crear carpeta con archivo
```
En el campo de nombre del archivo, escribe:

┌────────────────────────────────┐
│ utils/__init__.py              │  ← La "/" crea la carpeta
└────────────────────────────────┘
      ↑      ↑
   carpeta  archivo
```

GitHub lo interpreta como:
- Crear carpeta `utils`
- Dentro, crear archivo `__init__.py`

---

## ✅ Estructura Final Esperada

Después de crear todo, tu repo debe verse así:
```
📦 tu-repositorio
├── 📄 app.py
├── 📄 requirements.txt
├── 📁 .streamlit/
│   └── 📄 config.toml
├── 📁 pages/
│   ├── 📄 __init__.py
│   ├── 📄 dashboard.py
│   ├── 📄 portfolio.py
│   ├── 📄 analysis.py
│   └── 📄 profile.py
└── 📁 utils/
    ├── 📄 __init__.py
    ├── 📄 auth.py
    ├── 📄 database.py
    ├── 📄 market_data.py
    └── 📄 styles.py
