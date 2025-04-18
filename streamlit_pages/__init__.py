# This file makes the streamlit_ui directory a Python package

"""
Streamlit pages package for the Archon UI.
"""

from .database import database_tab
from .documentation import documentation_tab
from .environment import environment_tab
from .chat import chat_tab
from .future_enhancements import future_enhancements_tab
from .intro import intro_tab
from .mcp import mcp_tab
#from .styles import apply_styles

__all__ = [
    'database_tab',
    'documentation_tab',
    'environment_tab',
    'chat_tab',
    'future_enhancements_tab',
    'intro_tab',
    'mcp_tab'
#    'apply_styles'
]
