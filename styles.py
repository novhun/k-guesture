
DARK_THEME = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    color: #E0E0E0;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, 'Khmer OS Battambang', 'Battambang', sans-serif;
}
QTabWidget::pane {
    border: 1px solid #333;
    background: #1E1E1E;
    border-radius: 10px;
}
QTabBar::tab {
    background: #2D2D2D;
    padding: 12px 25px;
    margin-right: 2px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
QTabBar::tab:selected {
    background: #1E1E1E;
    border-bottom: 3px solid #BB86FC;
    font-weight: bold;
}
QPushButton {
    background-color: #3700B3;
    color: white;
    border-radius: 10px;
    padding: 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #6200EE;
}
QLineEdit, QComboBox {
    background-color: #2D2D2D;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 10px;
    color: white;
}
QTableWidget {
    background-color: #1E1E1E;
    gridline-color: #333;
    border-radius: 10px;
}
QHeaderView::section {
    background-color: #2D2D2D;
    padding: 8px;
    border: 1px solid #333;
    font-weight: bold;
}
QGroupBox {
    border: 2px solid #333;
    border-radius: 15px;
    margin-top: 25px;
    font-size: 18px;
    font-weight: bold;
    padding: 20px;
    background-color: #1E1E1E;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 0 10px;
    color: #BB86FC;
}
QLabel#subtitle {
    font-size: 24px;
    font-weight: bold;
    color: #BB86FC;
}
QLabel#setting_header {
    font-size: 32px;
    font-weight: bold;
    color: white;
    padding: 20px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6200EE, stop:1 #BB86FC);
    border-radius: 15px;
    margin-bottom: 20px;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #F8F9FA;
}
QWidget {
    color: #2D3436;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, 'Khmer OS Battambang', 'Battambang', sans-serif;
}
QTabWidget::pane {
    border: 1px solid #E0E0E0;
    background: white;
    border-radius: 10px;
}
QTabBar::tab {
    background: #F1F2F6;
    padding: 12px 25px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 5px;
}
QTabBar::tab:selected {
    background: white;
    border-bottom: 3px solid #6C5CE7;
    font-weight: bold;
}
QPushButton {
    background-color: #6C5CE7;
    color: white;
    border-radius: 10px;
    padding: 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #a29bfe;
}
QLineEdit, QComboBox {
    background-color: #F1F2F6;
    border: 1px solid #DFE6E9;
    border-radius: 8px;
    padding: 10px;
}
QTableWidget {
    background-color: white;
    gridline-color: #EEE;
    border-radius: 10px;
}
QHeaderView::section {
    background-color: #F8F9FA;
    padding: 8px;
    font-weight: bold;
}
QGroupBox {
    border: 1px solid #DFE6E9;
    border-radius: 15px;
    margin-top: 25px;
    font-size: 18px;
    font-weight: bold;
    padding: 20px;
    background-color: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 0 10px;
    color: #6C5CE7;
}
QLabel#subtitle {
    font-size: 24px;
    font-weight: bold;
    color: #6C5CE7;
}
QLabel#setting_header {
    font-size: 32px;
    font-weight: bold;
    color: white;
    padding: 20px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6C5CE7, stop:1 #a29bfe);
    border-radius: 15px;
    margin-bottom: 20px;
}
"""
