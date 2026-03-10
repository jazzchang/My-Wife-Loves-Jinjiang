import sys
import re
import os
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, 
                             QLineEdit, QPushButton, QMessageBox,
                             QGraphicsDropShadowEffect, QFrame)
from PyQt6.QtGui import QFontDatabase, QFont, QPainter, QPixmap, QColor
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect

from crawler_engine import get_chapter, parse_novel_info

CONFIG_FILE = "config.json"

class CrawlerWorker(QThread):
    progress_signal = pyqtSignal(int, int, str)
    finished_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str)

    def __init__(self, novel_url, save_dir):
        super().__init__()
        self.novel_url = novel_url
        self.save_dir = save_dir
        
    def run(self):
        try:
            m = re.search(r'novelid=(\d+)', self.novel_url)
            if not m:
                self.error_signal.emit("Invalid JJWXC URL. Need novelid.")
                return
            novel_id = m.group(1)
            
            self.progress_signal.emit(0, 0, "Fetching novel info...")
            
            title, author, total_chapters = parse_novel_info(self.novel_url)
            
            if total_chapters == 0:
                 total_chapters = 166 
            
            file_name = f"{title}_{novel_id}.txt"
            file_name = "".join([c for c in file_name if c.isalpha() or c.isdigit() or c==' ' or c=='_']).rstrip() + ".txt"
            
            file_path = os.path.join(self.save_dir, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"{title}\nAuthor: {author}\n\n" + "="*50 + "\n\n")
                
                for i in range(1, total_chapters + 1):
                    chapter_url = f'https://www.jjwxc.net/onebook.php?novelid={novel_id}&chapterid={i}'
                    self.progress_signal.emit(i, total_chapters, f"Ready • {i}/{total_chapters}")
                    
                    c_title, c_text = get_chapter(chapter_url)
                    
                    if c_title:
                        f.write(f"\n\n\n{c_title}\n\n")
                    f.write(f"{c_text}\n")
                    
                    self.msleep(500)
            
            self.finished_signal.emit(file_path, title)
            
        except Exception as e:
            self.error_signal.emit(str(e))

class HoverSvgButton(QPushButton):
    def __init__(self, svg_path, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #222222;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #888888;
            }
        """)
        # Insert the SVG widget inside the button
        self.svg_icon = QSvgWidget(svg_path, self)
        # Manually positioned centered
        self.svg_icon.setGeometry(30, 10, 45, 16)
        # Pass clicks through the SVG to the button
        self.svg_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

class JinjiangApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.initUI()
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"save_dir": "/Users/jazz/Downloads"}
        
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def resolve_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def initUI(self):
        self.setFixedSize(400, 600)
        self.setWindowTitle("My Wife Loves Jinjiang")
        
        # 1. Background Image
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 400, 600)
        bg_pixmap = QPixmap(self.resolve_path("bg.png"))
        if not bg_pixmap.isNull():
            self.bg_label.setPixmap(bg_pixmap.scaled(400, 600, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # 2. Hamburger Settings Button (Top Right SVG)
        self.settings_btn = QPushButton(self)
        self.settings_btn.setGeometry(350, 20, 30, 30)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("background: transparent; border: none;")
        self.settings_svg = QSvgWidget(self.resolve_path("settings_icon.svg"), self.settings_btn)
        self.settings_svg.setGeometry(5, 5, 20, 20)
        self.settings_svg.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.settings_btn.clicked.connect(self.show_settings)

        # 3. Input Field (50% white fill, pink border)
        self.url_input = QLineEdit(self)
        self.url_input.setGeometry(40, 120, 320, 60)
        self.url_input.setPlaceholderText("网址粘贴到这里")
        self.url_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.5);
                border: 1px solid rgba(255, 136, 167, 0.7);
                border-radius: 30px;
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                padding: 0 25px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 136, 167, 1.0);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)

        # 4. Progress Text Label (50% Opacity)
        self.progress_label = QLabel("Ready •  0/0", self)
        self.progress_label.setGeometry(60, 185, 200, 20)
        self.progress_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 13px;")

        # 5. Start Button (Black rounded capsule + SVG)
        self.download_btn = HoverSvgButton(self.resolve_path("start_icon.svg"), self)
        self.download_btn.setGeometry(255, 240, 105, 36)
        self.download_btn.clicked.connect(self.start_download)

        # 6. Giant logo (Bottom Left SVG)
        self.logo_svg = QSvgWidget(self.resolve_path("logo.svg"), self)
        self.logo_svg.setGeometry(30, 330, 240, 200)

        # 7. Settings Overlay (Hidden by default)
        self.build_settings_overlay()
        
        # 8. Success Dialog Overlay (Hidden by default)
        self.build_success_overlay()

    def build_settings_overlay(self):
        # Full screen blocker
        self.overlay = QFrame(self)
        self.overlay.setGeometry(0, 0, 400, 600)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0);") # Invisible backdrop
        self.overlay.hide()
        
        # The central white card
        self.settings_card = QFrame(self.overlay)
        self.settings_card.setGeometry(40, 100, 320, 220)
        self.settings_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 20px;
            }
        """)
        
        # Super soft high-radius drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 10)
        self.settings_card.setGraphicsEffect(shadow)

        # Card Contents
        title = QLabel("位置", self.settings_card)
        title.setGeometry(20, 30, 50, 20)
        title.setStyleSheet("color: #333; font-size: 14px; background: transparent;")
        
        # Pink Separator Line
        line = QFrame(self.settings_card)
        line.setGeometry(20, 60, 180, 1)
        line.setStyleSheet("background-color: #ff9a9e;")
        
        # Path Label
        self.path_label = QLabel(self.config.get("save_dir", "未设置"), self.settings_card)
        self.path_label.setGeometry(20, 75, 280, 20)
        self.path_label.setStyleSheet("color: #111; font-size: 14px; background: transparent;")
        
        # Change Button
        self.change_btn = QPushButton("更改", self.settings_card)
        self.change_btn.setGeometry(210, 20, 90, 32)
        self.change_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #222;
            }
        """)
        from PyQt6.QtWidgets import QFileDialog
        self.change_btn.clicked.connect(self.select_directory)

        # Close Button
        self.close_btn = QPushButton("关闭", self.settings_card)
        self.close_btn.setGeometry(110, 150, 100, 36)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333;
                border: 1px solid #ff9a9e;
                border-radius: 18px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 154, 158, 0.1);
            }
        """)
        self.close_btn.clicked.connect(self.hide_settings)

    def show_settings(self):
        self.path_label.setText(self.config.get("save_dir", "未设置"))
        self.overlay.raise_()
        self.overlay.show()

    def hide_settings(self):
        self.overlay.hide()

    def build_success_overlay(self):
        # Full screen blocker
        self.success_overlay = QFrame(self)
        self.success_overlay.setGeometry(0, 0, 400, 600)
        self.success_overlay.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);") # slight frosted
        self.success_overlay.hide()
        
        # The central white card
        self.success_card = QFrame(self.success_overlay)
        self.success_card.setGeometry(40, 170, 320, 220)
        self.success_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 24px;
            }
        """)
        
        # Super soft high-radius drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 10)
        self.success_card.setGraphicsEffect(shadow)
        
        # Heart Icon
        self.heart_svg = QSvgWidget(self.resolve_path("heart_icon.svg"), self.success_card)
        self.heart_svg.setGeometry(135, 25, 50, 45) # Center top
        self.heart_svg.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Text 1
        msg1 = QLabel("现在可以和老婆汇报已经下载好了", self.success_card)
        msg1.setGeometry(20, 85, 280, 20)
        msg1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg1.setStyleSheet("color: #111; font-size: 14px; background: transparent;")
        
        # Text 2 (Title)
        self.success_title = QLabel("《》", self.success_card)
        self.success_title.setGeometry(20, 110, 280, 20)
        self.success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_title.setStyleSheet("color: #111; font-size: 15px; background: transparent;")

        # Close Button
        self.success_close_btn = QPushButton("关闭", self.success_card)
        self.success_close_btn.setGeometry(110, 160, 100, 36)
        self.success_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.success_close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333;
                border: 1px solid #ff9a9e;
                border-radius: 18px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 154, 158, 0.1);
            }
        """)
        self.success_close_btn.clicked.connect(self.hide_success_overlay)

    def show_success_overlay(self, title):
        # Truncate title if extremely long
        if len(title) > 16:
            display_title = title[:15] + "..."
        else:
            display_title = title
        self.success_title.setText(f"《{display_title}》")
        self.success_overlay.raise_()
        self.success_overlay.show()

    def hide_success_overlay(self):
        self.success_overlay.hide()

    def select_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "选择下载图库", self.config.get("save_dir", ""))
        if dir_path:
            self.config["save_dir"] = dir_path
            self.save_config()
            self.path_label.setText(dir_path)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a valid URL.")
            return
            
        if "jjwxc.net" not in url:
            QMessageBox.warning(self, "Warning", "Please enter a valid JJWXC URL.")
            return
            
        self.download_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.progress_label.setText("Preparing...")
        
        self.worker = CrawlerWorker(url, self.config["save_dir"])
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.download_finished)
        self.worker.error_signal.connect(self.download_error)
        self.worker.start()

    def update_progress(self, current, total, text):
        self.progress_label.setText(text)

    def download_finished(self, file_path, title):
        self.progress_label.setText("Ready • Done!")
        self.download_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        
        self.show_success_overlay(title)

    def download_error(self, err_msg):
        self.progress_label.setText("Ready • Error")
        self.download_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{err_msg}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JinjiangApp()
    window.show()
    sys.exit(app.exec())
