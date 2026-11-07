"""EngrLean Brand Styling & Custom CSS."""

ENGRLEAN_CSS = """
<style>
/* Main Background & Font Styling */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header & Banner Container */
.engrlean-header {
    background: linear-gradient(135deg, #1E222A 0%, #2B3E50 100%);
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 24px;
    border: 1px solid rgba(0, 173, 181, 0.25);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.engrlean-title {
    color: #FFFFFF !important;
    font-size: 28px;
    font-weight: 800;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.engrlean-title span {
    color: #00ADB5;
}

.engrlean-tagline {
    color: #00D2DF;
    font-size: 14px;
    font-weight: 600;
    margin-top: 6px;
    letter-spacing: 0.5px;
}

.engrlean-subtext {
    color: #CBD5E1;
    font-size: 13px;
    margin-top: 4px;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #171B21;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-pillar-card {
    background: rgba(43, 62, 80, 0.4);
    border-left: 3px solid #00ADB5;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 12px;
}

.sidebar-pillar-title {
    color: #00ADB5;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 3px;
}

.sidebar-pillar-desc {
    color: #94A3B8;
    font-size: 11px;
    line-height: 1.4;
}

/* Chat Message Bubbles */
.stChatMessage {
    border-radius: 10px;
    margin-bottom: 12px;
}

/* Primary Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00ADB5 0%, #008389 100%);
    color: white;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.2s ease-in-out;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #00D2DF 0%, #00ADB5 100%);
    box-shadow: 0 4px 12px rgba(0, 173, 181, 0.35);
    transform: translateY(-1px);
}

/* Status Badges */
.status-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    background-color: rgba(0, 173, 181, 0.15);
    color: #00D2DF;
    border: 1px solid rgba(0, 173, 181, 0.3);
}

/* Contact Links in Sidebar */
.contact-btn {
    display: block;
    text-align: center;
    background: #2B3E50;
    color: #FFFFFF !important;
    text-decoration: none;
    padding: 9px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: background 0.2s;
}

.contact-btn:hover {
    background: #00ADB5;
    color: #FFFFFF !important;
}
</style>
"""

