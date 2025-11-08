import streamlit as st


def load_custom_ui(theme: str = "auto", title: str = "Investment Decision Predictor"):
    """Load enhanced custom CSS with improved styling, animations, and user experience.

    Parameters
    - theme: 'auto' | 'light' | 'dark'  -> chooses which CSS variable set to inject
    - title: header title to display on the page
    """

    # --- Custom CSS Styling ---
    # We keep two flavours of variables and choose based on `theme` parameter.
    # 'auto' will still include prefers-color-scheme fallback so user's OS/theme works.
    if theme not in ("auto", "light", "dark"):
        theme = "auto"

    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* === Elegant Versatile Color Palette === */
        /* Default/light theme variables (we may override via separate block for dark) */
        :root {
            --bg-primary: #f8f9fa;
            --bg-secondary: #ffffff;
            --bg-gradient-start: #f8f9fa;
            --bg-gradient-end: #ffffff;
            --sidebar-gradient-start: #f1f3f4;
            --sidebar-gradient-end: #e8eaed;
            --result-box-gradient-start: #ffffff;
            --result-box-gradient-end: #f8f9fa;
            --text-primary: #202124;
            --text-secondary: #5f6368;
            --text-sidebar: #3c4043;
            --text-positive: #1e8e3e;
            --text-negative: #d93025;
            --text-warning: #ea8600;
            --border-color: #dadce0;
            --button-gradient-start: #1a73e8;
            --button-gradient-end: #1557b0;
            --button-hover-start: #2979ff;
            --button-hover-end: #1a73e8;
            --card-accent: #1a73e8;
            --shadow-color: rgba(60, 64, 67, 0.15);
            --shadow-hover-color: rgba(60, 64, 67, 0.3);
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Explicit dark theme variables (used when theme == 'dark' or OS prefers dark in 'auto') */
        .theme-dark {
            --bg-primary: #1e1e1e;
            --bg-secondary: #2d2d2d;
            --bg-gradient-start: #252525;
            --bg-gradient-end: #1e1e1e;
            --sidebar-gradient-start: #2d2d2d;
            --sidebar-gradient-end: #252525;
            --result-box-gradient-start: #2d2d2d;
            --result-box-gradient-end: #363636;
            --text-primary: #e8eaed;
            --text-secondary: #9aa0a6;
            --text-sidebar: #dadce0;
            --text-positive: #34a853;
            --text-negative: #f28b82;
            --text-warning: #fbbc04;
            --border-color: #3c4043;
            --button-gradient-start: #8ab4f8;
            --button-gradient-end: #669df6;
            --button-hover-start: #aecbfa;
            --button-hover-end: #8ab4f8;
            --card-accent: #8ab4f8;
            --shadow-color: rgba(0, 0, 0, 0.4);
            --shadow-hover-color: rgba(0, 0, 0, 0.6);
        }

        /* Auto fallback for OS theme preference (only used when theme == 'auto') */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-primary: #1e1e1e;
                --bg-secondary: #2d2d2d;
                --bg-gradient-start: #252525;
                --bg-gradient-end: #1e1e1e;
                --sidebar-gradient-start: #2d2d2d;
                --sidebar-gradient-end: #252525;
                --result-box-gradient-start: #2d2d2d;
                --result-box-gradient-end: #363636;
                --text-primary: #e8eaed;
                --text-secondary: #9aa0a6;
                --text-sidebar: #dadce0;
                --text-positive: #34a853;
                --text-negative: #f28b82;
                --text-warning: #fbbc04;
                --border-color: #3c4043;
                --button-gradient-start: #8ab4f8;
                --button-gradient-end: #669df6;
                --button-hover-start: #aecbfa;
                --button-hover-end: #8ab4f8;
                --card-accent: #8ab4f8;
                --shadow-color: rgba(0, 0, 0, 0.4);
                --shadow-hover-color: rgba(0, 0, 0, 0.6);
            }
        }

        /* === Global Typography and Font === */
        body, .stApp {
            font-family: var(--font-family) !important;
        }

        /* === Smooth Transitions === */
        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }

        /* === Global Background === */
        .stApp {
            background: linear-gradient(180deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            background-attachment: fixed;
        }

        /* === Main Header === */
        .main-header {
            font-size: 2.5rem;
            color: var(--text-primary);
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            animation: fadeInDown 0.8s ease;
        }

        /* === Sub Header === */
        .sub-header {
            font-size: 1.5rem;
            color: var(--text-secondary);
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
            letter-spacing: -0.25px;
        }

        /* === Result Box === */
        .result-box {
            background: linear-gradient(135deg, var(--result-box-gradient-start) 0%, var(--result-box-gradient-end) 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 12px var(--shadow-color);
            animation: fadeIn 0.6s ease;
            position: relative;
            overflow: hidden;
        }

        /* === Role Selection Section === */
        .section-header {
            font-size: 1.2rem;
            color: var(--text-primary);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }

        /* === Header and Role Selection Section === */
        .header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 2rem;
        }

        .role-selection-card {
            background: var(--bg-secondary);
            border-radius: 1rem;
            box-shadow: 0 4px 12px var(--shadow-color);
            padding: 2rem;
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }

        .role-selection-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--card-accent), transparent);
            animation: shimmer 2s infinite;
        }

        .role-selection-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .role-selection-header h2 {
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-size: 1.8rem;
        }

        .role-selection-header p {
            color: var(--text-secondary);
            font-size: 1rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Simple button styling for role selection */
        div[data-testid="stHorizontalBlock"] > div {
            padding: 0.5rem;
        }

        button[kind="primary"] {
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 0.75rem !important;
            padding: 1.5rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            height: auto !important;
            min-height: 100px !important;
        }

        button[kind="primary"]:hover {
            border-color: var(--card-accent) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px var(--shadow-hover-color) !important;
        }

        .result-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--card-accent), transparent);
            animation: shimmer 2s infinite;
        }

        /* === Metric Cards === */
        .metric-card {
            background: var(--bg-secondary);
            padding: 1.25rem;
            border-radius: 1rem;
            box-shadow: 0 4px 12px var(--shadow-color);
            margin: 0.75rem;
            border-left: 5px solid var(--card-accent);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .metric-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 8px 24px var(--shadow-hover-color);
        }

        .metric-card::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, var(--card-accent) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .metric-card:hover::after {
            opacity: 0.05;
        }

        /* === Text Colors for Results === */
        .positive {
            color: var(--text-positive);
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .positive::before {
            content: '↑';
            font-size: 0.8em;
        }

        .negative {
            color: var(--text-negative);
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .negative::before {
            content: '↓';
            font-size: 0.8em;
        }

        .warning {
            color: var(--text-warning);
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .warning::before {
            content: '⚠';
            font-size: 0.8em;
        }

        /* === Streamlit Sidebar Styling === */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--sidebar-gradient-start) 0%, var(--sidebar-gradient-end) 100%);
            border-right: 1px solid var(--border-color);
            padding-top: 1rem;
        }

        /* Sidebar Titles */
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown {
            color: var(--text-sidebar) !important;
            font-weight: 500;
        }

        /* === Enhanced Buttons === */
        div.stButton > button {
            background: linear-gradient(90deg, var(--button-gradient-start) 0%, var(--button-gradient-end) 100%);
            color: white;
            border: none;
            border-radius: 0.75rem;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-family: var(--font-family);
            box-shadow: 0 4px 12px var(--shadow-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        div.stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        div.stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }

        div.stButton > button:hover {
            background: linear-gradient(90deg, var(--button-hover-start) 0%, var(--button-hover-end) 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--shadow-hover-color);
        }

        div.stButton > button:active {
            transform: translateY(0);
        }

        /* === Enhanced Input Fields === */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            padding: 0.75rem !important;
            font-family: var(--font-family) !important;
            transition: all 0.3s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--card-accent) !important;
            box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1) !important;
        }

        /* === Enhanced Tables === */
        .stTable {
            background: var(--bg-secondary) !important;
            border-radius: 0.75rem !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: 0 4px 12px var(--shadow-color);
            overflow: hidden;
        }

        .stTable table {
            border-collapse: separate;
            border-spacing: 0;
        }

        .stTable th {
            background: var(--bg-primary) !important;
            color: var(--text-sidebar) !important;
            font-weight: 600 !important;
            padding: 1rem !important;
            border-bottom: 2px solid var(--border-color) !important;
        }

        .stTable td {
            padding: 0.75rem 1rem !important;
            border-bottom: 1px solid var(--border-color) !important;
        }

        .stTable tr:hover td {
            background: var(--bg-primary) !important;
        }

        /* === Footer === */
        footer {
            visibility: hidden;
        }

        /* === Ensure text visibility in all components === */
        .stMarkdown, .stText, .stCaption {
            color: var(--text-primary) !important;
            line-height: 1.6;
        }

        /* === Enhanced Dataframe styling === */
        .dataframe {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border-radius: 0.75rem !important;
            overflow: hidden;
        }

        .dataframe th {
            background-color: var(--bg-primary) !important;
            color: var(--text-sidebar) !important;
            font-weight: 600 !important;
        }

        /* === Enhanced Tabs === */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--bg-secondary) !important;
            border-radius: 0.75rem !important;
            padding: 0.25rem !important;
            box-shadow: 0 2px 8px var(--shadow-color);
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--text-secondary) !important;
            border-radius: 0.5rem !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--bg-primary) !important;
            color: var(--text-sidebar) !important;
            font-weight: 600 !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: var(--bg-primary) !important;
        }

        /* === Enhanced Slider === */
        .stSlider > div > div > div {
            background-color: var(--card-accent) !important;
            box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3) !important;
        }

        /* === Enhanced Checkbox === */
        .stCheckbox > label {
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }

        .stCheckbox input[type="checkbox"]:checked + div {
            background-color: var(--card-accent) !important;
        }

        /* === Enhanced Radio === */
        .stRadio > div > label {
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }

        /* === Enhanced Progress Bar === */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--card-accent), var(--button-hover-start)) !important;
            box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3) !important;
        }

        /* === Animations === */
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

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes shimmer {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(100%);
            }
        }

        /* === Success/Error Messages === */
        .stSuccess {
            background: linear-gradient(135deg, #d4edda, #c3e6cb) !important;
            border-left: 5px solid var(--text-positive) !important;
            color: #155724 !important;
        }

        .stError {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb) !important;
            border-left: 5px solid var(--text-negative) !important;
            color: #721c24 !important;
        }

        .stWarning {
            background: linear-gradient(135deg, #fff3cd, #ffeeba) !important;
            border-left: 5px solid var(--text-warning) !important;
            color: #856404 !important;
        }

        /* === Tooltip Enhancement === */
        .stTooltip {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            box-shadow: 0 4px 12px var(--shadow-color) !important;
        }

        /* === Scrollbar Styling === */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Theme toggle script: explicitly apply dark class when requested ---
    if theme == "dark":
        st.markdown(
            """
            <script>
            (function(){
                try{document.documentElement.classList.add('theme-dark');}catch(e){}
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )
    elif theme == "light":
        st.markdown(
            """
            <script>
            (function(){
                try{document.documentElement.classList.remove('theme-dark');}catch(e){}
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

    # --- Page Header ---
    st.markdown(f'<h1 class="main-header">💰 {title}</h1>', unsafe_allow_html=True)
    st.markdown("""
    This application uses **machine learning** to predict cash flows and guide investment decisions.  
    Enter your project parameters in the sidebar to get a detailed financial and risk analysis.
    """)