"""
Home UI Styling Module
Dark professional theme matching QuizUI styles
"""

# Glass Card Style - Matching QuizUI dark theme
GLASS_CARD_STYLE = """
background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
border-radius: 15px;
padding: 1.5rem;
border: 1px solid rgba(255,255,255,0.1);
backdrop-filter: blur(10px);
box-shadow: 0 8px 32px rgba(0,0,0,0.3);
transition: all 0.3s ease;
margin-bottom: 1rem;
"""

# Complete CSS for Home UI - Dark Professional Theme (Matching QuizUI)
HOME_CUSTOM_CSS = """
    <style>
    /* Main container - Dark background matching QuizUI */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%) !important;
    }
    
    .stApp > header {
        background: transparent !important;
    }
    
    /* Main content area alignment */
    .main .block-container {
        background: transparent !important;
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .stApp .main {
        background: transparent !important;
        padding: 0 !important;
    }
    
    /* Fix content alignment when sidebar is open */
    .main {
        margin-left: 0 !important;
        width: 100% !important;
    }

    /* Title and subtitle styling */
    .title-text {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
        color: #e2e8f0;
        padding: 20px 24px;
        border-radius: 12px;
        margin: 10px 0 20px 0;
        font-weight: 700;
        font-size: 28px;
        box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .subtitle-text {
        color: #e2e8f0;
        font-size: 18px;
        text-align: center;
        margin: 15px 0;
        font-weight: 500;
    }

    /* Section headers - Primary blue gradient matching QuizUI */
    .section-header {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
        color: #e2e8f0;
        padding: 16px 24px;
        border-radius: 12px;
        margin: 10px 0 20px 0;
        font-weight: 600;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Glass Card Style - Dark professional theme */
    .card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    /* Action cards with hover effects */
    .action-card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        margin-bottom: 15px;
        height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .action-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(49, 130, 206, 0.3);
        border-color: rgba(49, 130, 206, 0.5);
    }

    .action-card h3 {
        color: #e2e8f0;
        font-size: 20px;
        margin: 15px 0 10px 0;
        font-weight: 600;
    }

    .action-card p {
        color: #a0aec0;
        font-size: 14px;
        margin: 0;
        line-height: 1.6;
    }

    /* Activity cards */
    .activity-card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .activity-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(49, 130, 206, 0.3);
        border-color: rgba(49, 130, 206, 0.5);
    }

    /* Metrics styling */
    .metric-container {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(49, 130, 206, 0.2);
    }

    .metric-value {
        color: #3182ce;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .metric-label {
        color: #a0aec0;
        font-size: 14px;
        font-weight: 500;
    }

    /* Button styling - Matching QuizUI buttons */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        padding: 12px 24px !important;
        border: none !important;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
        color: white !important;
        border: none !important;
    }

    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2c5282 0%, #2a4365 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(49, 130, 206, 0.4) !important;
    }

    .stButton>button[kind="secondary"] {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        color: #e2e8f0;
    }

    .stButton>button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 85, 104, 0.4);
    }

    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #3182ce, transparent);
        margin: 30px 0;
        border-radius: 2px;
    }

    /* Info messages - Blue style matching QuizUI */
    .info-message-blue {
        background-color: rgba(49, 130, 206, 0.1);
        border: 1px solid #3182ce;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #e2e8f0;
    }

    /* Progress messages */
    .progress-message {
        background-color: rgba(40, 120, 200, 0.1);
        border: 1px solid #3182ce;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: #e2e8f0;
        margin: 10px 0;
    }

    /* Sidebar styling - Proper layout */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        height: 100vh !important;
        position: relative !important;
    }

    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
        height: 100% !important;
        padding: 1rem !important;
    }
    
    section[data-testid="stSidebar"] .css-6qob1r {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
    }
    
    /* Force sidebar content visibility */
    section[data-testid="stSidebar"] .css-1d391kg {
        background: transparent !important;
    }
    
    /* Main content area alignment - when sidebar is visible */
    div[data-testid="stAppViewContainer"] > .main {
        width: 100% !important;
        max-width: none !important;
        padding: 1rem 2rem !important;
    }
    
    /* Ensure proper spacing and alignment */
    .stApp .main .block-container {
        padding: 1rem !important;
        margin: 0 auto !important;
        width: 100% !important;
        max-width: 1200px !important;
    }
    
    /* Column alignment fixes */
    .row-widget {
        width: 100% !important;
    }
    
    div[data-testid="column"] {
        width: 100% !important;
    }
    
    /* Sidebar button styling */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        width: 100% !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
        transform: translateY(-1px) !important;
    }

    /* Text inputs - Dark theme */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #4a5568;
        background-color: #1a202c;
        color: #e2e8f0;
        padding: 12px;
        font-size: 16px;
    }

    .stTextInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background-color: #2d3748;
    }

    /* Select boxes - Dark theme */
    .stSelectbox > div > div {
        background-color: #1a202c;
        border: 2px solid #4a5568;
        border-radius: 10px;
        color: #e2e8f0;
    }

    .stSelectbox > div > div:focus-within {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
    }

    /* Success/Info/Warning/Error messages */
    .stSuccess {
        background-color: rgba(72, 187, 120, 0.1);
        border: 1px solid #48bb78;
        border-radius: 10px;
        color: #e2e8f0;
    }

    .stInfo {
        background-color: rgba(49, 130, 206, 0.1);
        border: 1px solid #3182ce;
        border-radius: 10px;
        color: #e2e8f0;
    }

    .stWarning {
        background-color: rgba(246, 173, 85, 0.1);
        border: 1px solid #f6ad55;
        border-radius: 10px;
        color: #e2e8f0;
    }

    .stError {
        background-color: rgba(252, 129, 129, 0.1);
        border: 1px solid #fc8181;
        border-radius: 10px;
        color: #e2e8f0;
    }

    /* Progress bar - Primary blue gradient */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3182ce 0%, #2c5282 100%);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d3748;
        color: #e2e8f0;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .streamlit-expanderContent {
        background-color: #1a202c;
        border-radius: 0 0 10px 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Modern Streamlit class targeting */
    .stApp > div[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%) !important;
    }
    
    .stApp > div[data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }
    
    /* Text color fixes */
    .stApp, .stApp * {
        color: #e2e8f0 !important;
    }
    
    /* Force apply to all text elements */
    p, h1, h2, h3, h4, h5, h6, span, div {
        color: #e2e8f0 !important;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""