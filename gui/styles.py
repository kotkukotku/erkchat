
MAIN_STYLE = """
    QMainWindow, QWidget {
        background-color: #1e1f22;
        color: #eeeeF2;
        font-family: Sans Serif;
        font-size: 14px;
    }

    QFrame#sidebar {
        background-color: #17181c;
    }

    QFrame#members {
        background-color: #232429;
    }

    QLabel#app_title {
        color: #b49aff;
        font-size: 22px;
        font-weight: bold;
    }

    QLabel#section_title {
        color: #92949c;
        font-size: 11px;
        font-weight: bold;
    }

    QLabel#channel_title {
        font-size: 19px;
        font-weight: bold;
    }

    QListWidget {
        background-color: transparent;
        border: none;
        outline: none;
    }

    QListWidget::item {
        padding: 11px;
        border-radius: 6px;
    }

    QListWidget::item:selected {
        background-color: #49405f;
    }

    QLineEdit {
        background-color: #383a40;
        border: none;
        border-radius: 9px;
        padding: 13px;
        color: white;
    }

    QPushButton {
        background-color: #7955db;
        border: none;
        border-radius: 8px;
        padding: 11px 18px;
        color: white;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #916ff0;
    }
"""
