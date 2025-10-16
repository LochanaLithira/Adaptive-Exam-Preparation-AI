"""
Quiz UI Styling Module
Separated CSS styles for clean code organization
"""

# Glass Card Style - Updated to match dark theme
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

# Gradient backgrounds matching your auth theme
GRADIENT_BACKGROUNDS = {
    "primary": "linear-gradient(135deg, #3182ce 0%, #2c5282 100%)",
    "success": "linear-gradient(135deg, #48bb78 0%, #38a169 100%)",
    "warning": "linear-gradient(135deg, #f6ad55 0%, #ed8936 100%)",
    "error": "linear-gradient(135deg, #fc8181 0%, #f56565 100%)",
    "subtle": "linear-gradient(145deg, #2d3748 0%, #1a202c 100%)",
    "dark": "linear-gradient(135deg, #1a202c 0%, #0f1419 100%)"
}

# Complete CSS for Quiz UI - Dark Professional Theme
QUIZ_CUSTOM_CSS = """
    <style>
    /* Main container - Dark background matching auth */
    .main {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%);
    }

    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%);
    }

    /* Glass Card Style - Dark professional theme */
    .settings-card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }

    /* Section headers - Primary blue gradient */
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
    }

    /* Quiz question styling - Dark card */
    .quiz-question-card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .quiz-question-card h3 {
        color: #e2e8f0 !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        margin: 0 0 8px 0 !important;
        line-height: 1.4;
    }

    .quiz-question-card p {
        color: #e2e8f0 !important;
        font-size: 18px !important;
        font-weight: 500 !important;
        margin: 0 !important;
        line-height: 1.6;
    }

    /* Progress bar - Primary blue gradient */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3182ce 0%, #2c5282 100%);
    }

    /* Button styling - Matching auth buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 12px 24px;
        border: none;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
        color: white;
        border: none;
    }

    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2c5282 0%, #2a4365 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(49, 130, 206, 0.4);
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

    /* Success button variant */
    .success-button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
    }

    .success-button:hover {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
        box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4) !important;
    }

    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #3182ce, transparent);
        margin: 30px 0;
        border-radius: 2px;
    }

    /* Progress text */
    .progress-text {
        text-align: center;
        font-size: 16px;
        color: #a0aec0;
        margin: 15px 0;
        font-weight: 600;
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

    /* Number inputs - Dark theme */
    .stNumberInput > div > div > input {
        background-color: #1a202c;
        border: 2px solid #4a5568;
        border-radius: 10px;
        color: #e2e8f0;
    }

    .stNumberInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background-color: #2d3748;
    }

    /* Checkbox styling */
    .stCheckbox > label {
        color: #e2e8f0;
    }

    /* Radio buttons */
    .stRadio > label {
        color: #e2e8f0;
    }

    /* Expander */
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

    /* Success/Info messages */
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

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""