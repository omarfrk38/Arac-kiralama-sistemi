import sys
from datetime import datetime, timedelta
import sqlite3
import random
import string
from contextlib import contextmanager
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QMessageBox,
    QTabWidget, QFrame, QTextEdit, QDateEdit, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False


# ============ MODERN STYLE SHEET ============

MODERN_STYLE = """
    QMainWindow {
        background-color: #0f0f1a;
    }
    QTabWidget::pane {
        border: none;
        background-color: #1a1a2e;
        border-radius: 10px;
    }
    QTabBar::tab {
        background-color: #16213e;
        color: #e2e2e2;
        padding: 12px 35px;
        margin-right: 5px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: bold;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #00adb5;
        color: white;
    }
    QTabBar::tab:hover:!selected {
        background-color: #0f3460;
    }
    QTableWidget {
        background-color: #1a1a2e;
        alternate-background-color: #16213e;
        color: #e2e2e2;
        gridline-color: #0f3460;
        border: none;
        border-radius: 10px;
    }
    QTableWidget::item {
        padding: 8px;
    }
    QHeaderView::section {
        background-color: #0f3460;
        color: white;
        font-weight: bold;
        padding: 10px;
        border: none;
    }
    QPushButton {
        background-color: #0f3460;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #1a4a80;
    }
    QPushButton:pressed {
        background-color: #0a2a4a;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
        background-color: #16213e;
        border: 1px solid #0f3460;
        border-radius: 6px;
        padding: 8px;
        color: #e2e2e2;
        font-size: 12px;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #00adb5;
    }
    QLabel {
        color: #e2e2e2;
    }
    QDialog {
        background-color: #1a1a2e;
    }
    QMessageBox {
        background-color: #1a1a2e;
    }
    QMessageBox QLabel {
        color: #e2e2e2;
    }
    QMessageBox QPushButton {
        min-width: 80px;
    }
    QTextEdit {
        background-color: #16213e;
        border: 1px solid #0f3460;
        border-radius: 10px;
        color: #e2e2e2;
        font-family: monospace;
        font-size: 11px;
    }
"""


# ============ DATABASE MANAGER ============

class DatabaseManager:
    def __init__(self, db_name="car_rental_system.db"):
        self.db_name = db_name
        self.create_tables()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sistem_kullanicilari (
                    kullanici_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kullanici_adi TEXT UNIQUE NOT NULL,
                    sifre TEXT NOT NULL,
                    ad TEXT NOT NULL,
                    soyad TEXT NOT NULL,
                    rol TEXT DEFAULT 'user',
                    durum TEXT DEFAULT 'Aktif',
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS araclar (
                    arac_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marka TEXT NOT NULL,
                    model TEXT NOT NULL,
                    yil INTEGER NOT NULL,
                    kilometre INTEGER NOT NULL,
                    plaka TEXT UNIQUE NOT NULL,
                    musait_mi INTEGER DEFAULT 1,
                    olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS musteriler (
                    musteri_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    soyad TEXT NOT NULL,
                    ehliyet_no TEXT UNIQUE NOT NULL,
                    telefon TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kiralamalar (
                    kiralama_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arac_id INTEGER NOT NULL,
                    musteri_id INTEGER NOT NULL,
                    gunluk_fiyat REAL NOT NULL,
                    baslangic TIMESTAMP,
                    bitis TIMESTAMP,
                    baslangic_km INTEGER,
                    bitis_km INTEGER,
                    durum TEXT DEFAULT 'Devam ediyor',
                    FOREIGN KEY (arac_id) REFERENCES araclar (arac_id),
                    FOREIGN KEY (musteri_id) REFERENCES musteriler (musteri_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hediyeler (
                    hediye_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gonderen_musteri_id INTEGER NOT NULL,
                    alan_musteri_id INTEGER NOT NULL,
                    arac_id INTEGER NOT NULL,
                    gunluk_fiyat REAL NOT NULL,
                    hediye_kodu TEXT UNIQUE NOT NULL,
                    not_mesaji TEXT,
                    durum TEXT DEFAULT 'Beklemede',
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gonderen_musteri_id) REFERENCES musteriler (musteri_id),
                    FOREIGN KEY (alan_musteri_id) REFERENCES musteriler (musteri_id),
                    FOREIGN KEY (arac_id) REFERENCES araclar (arac_id)
                )
            ''')

            cursor.execute('SELECT COUNT(*) FROM sistem_kullanicilari WHERE kullanici_adi = "admin"')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO sistem_kullanicilari (kullanici_adi, sifre, ad, soyad, rol)
                    VALUES ('admin', 'admin123', 'Admin', 'Kullanıcı', 'admin')
                ''')

            cursor.execute('SELECT COUNT(*) FROM sistem_kullanicilari WHERE kullanici_adi = "user"')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO sistem_kullanicilari (kullanici_adi, sifre, ad, soyad, rol)
                    VALUES ('user', 'user123', 'Normal', 'Kullanıcı', 'user')
                ''')

    def kullanici_kontrol(self, kullanici_adi, sifre):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sistem_kullanicilari
                WHERE kullanici_adi = ? AND sifre = ? AND durum = 'Aktif'
            ''', (kullanici_adi, sifre))
            result = cursor.fetchone()
            return dict(result) if result else None

    def kullanici_ekle(self, kullanici_adi, sifre, ad, soyad, rol='user'):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sistem_kullanicilari (kullanici_adi, sifre, ad, soyad, rol)
                VALUES (?, ?, ?, ?, ?)
            ''', (kullanici_adi, sifre, ad, soyad, rol))
            return cursor.lastrowid

    def kullanicilari_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sistem_kullanicilari ORDER BY kullanici_id')
            return [dict(row) for row in cursor.fetchall()]

    def kullanici_sil(self, kullanici_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sistem_kullanicilari WHERE kullanici_id = ?', (kullanici_id,))

    def arac_ekle(self, marka, model, yil, kilometre, plaka):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO araclar (marka, model, yil, kilometre, plaka, musait_mi)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (marka, model, yil, kilometre, plaka))
            return cursor.lastrowid

    def araclari_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM araclar ORDER BY arac_id')
            return [dict(row) for row in cursor.fetchall()]

    def arac_sil(self, arac_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM kiralamalar WHERE arac_id = ? AND bitis IS NULL', (arac_id,))
            aktif_kiralama = cursor.fetchone()['count']
            if aktif_kiralama > 0:
                raise ValueError("Bu araç kirada olduğu için silinemez!")
            cursor.execute('DELETE FROM araclar WHERE arac_id = ?', (arac_id,))

    def arac_durum_guncelle(self, arac_id, musait_mi):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE araclar SET musait_mi = ? WHERE arac_id = ?',
                          (1 if musait_mi else 0, arac_id))

    def arac_kilometre_guncelle(self, arac_id, kilometre):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE araclar SET kilometre = ? WHERE arac_id = ?', (kilometre, arac_id))

    def musteri_ekle(self, ad, soyad, ehliyet_no, telefon, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO musteriler (ad, soyad, ehliyet_no, telefon, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (ad, soyad, ehliyet_no, telefon, email))
            return cursor.lastrowid

    def musterileri_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM musteriler ORDER BY musteri_id')
            return [dict(row) for row in cursor.fetchall()]

    def musteri_sil(self, musteri_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM kiralamalar WHERE musteri_id = ? AND bitis IS NULL', (musteri_id,))
            aktif_kiralama = cursor.fetchone()['count']
            if aktif_kiralama > 0:
                raise ValueError("Bu müşterinin aktif kiralaması var! Önce kiralamayı bitirin.")
            cursor.execute('DELETE FROM musteriler WHERE musteri_id = ?', (musteri_id,))

    def kiralama_ekle(self, arac_id, musteri_id, gunluk_fiyat):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as count FROM kiralamalar WHERE musteri_id = ? AND bitis IS NULL', (musteri_id,))
            aktif_kiralama = cursor.fetchone()['count']
            if aktif_kiralama > 0:
                raise ValueError("Bu müşterinin zaten aktif bir kiralaması var! Önce bitirmelisiniz.")

            cursor.execute('SELECT musait_mi, kilometre FROM araclar WHERE arac_id = ?', (arac_id,))
            arac = cursor.fetchone()
            if not arac or arac['musait_mi'] == 0:
                raise ValueError("Bu araç zaten kirada!")

            baslangic_km = arac['kilometre']
            cursor.execute('''
                INSERT INTO kiralamalar (arac_id, musteri_id, gunluk_fiyat, baslangic, baslangic_km, durum)
                VALUES (?, ?, ?, ?, ?, 'Devam ediyor')
            ''', (arac_id, musteri_id, gunluk_fiyat, datetime.now(), baslangic_km))

            cursor.execute('UPDATE araclar SET musait_mi = 0 WHERE arac_id = ?', (arac_id,))
            return cursor.lastrowid

    def kiralama_bitir(self, kiralama_id, bitis_km):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT baslangic_km, arac_id FROM kiralamalar WHERE kiralama_id = ?', (kiralama_id,))
            kiralama = cursor.fetchone()
            if not kiralama:
                raise ValueError("Kiralama bulunamadı!")

            baslangic_km = kiralama['baslangic_km']
            arac_id = kiralama['arac_id']

            if bitis_km < baslangic_km:
                raise ValueError(f"Bitiş KM ({bitis_km}), başlangıç KM'den ({baslangic_km}) küçük olamaz!")

            cursor.execute('''
                UPDATE kiralamalar
                SET bitis = ?, bitis_km = ?, durum = 'Tamamlandı'
                WHERE kiralama_id = ?
            ''', (datetime.now(), bitis_km, kiralama_id))

            cursor.execute('UPDATE araclar SET musait_mi = 1, kilometre = ? WHERE arac_id = ?', (bitis_km, arac_id))

    def kiralamalari_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT k.*, a.marka, a.model, a.kilometre as arac_km,
                       m.ad, m.soyad, m.telefon, m.email
                FROM kiralamalar k
                JOIN araclar a ON k.arac_id = a.arac_id
                JOIN musteriler m ON k.musteri_id = m.musteri_id
                ORDER BY k.kiralama_id DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def aktif_kiralamalari_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT k.*, a.marka, a.model, a.kilometre as arac_km,
                       m.ad, m.soyad, m.telefon, m.email
                FROM kiralamalar k
                JOIN araclar a ON k.arac_id = a.arac_id
                JOIN musteriler m ON k.musteri_id = m.musteri_id
                WHERE k.bitis IS NULL
                ORDER BY k.kiralama_id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def toplam_ciro_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM kiralamalar WHERE bitis IS NOT NULL')
            kiralamalar = [dict(row) for row in cursor.fetchall()]
            toplam = 0
            for kir in kiralamalar:
                if kir['baslangic'] and kir['bitis']:
                    baslangic = datetime.fromisoformat(kir['baslangic'].replace(' ', 'T'))
                    bitis = datetime.fromisoformat(kir['bitis'].replace(' ', 'T'))
                    gun_farki = max(1, (bitis - baslangic).days)
                    toplam += gun_farki * kir['gunluk_fiyat']
            return toplam

    def aktif_kiralama_sayisi(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM kiralamalar WHERE bitis IS NULL')
            return cursor.fetchone()['count']

    # ============ HEDİYE METODLARI ============

    def hediye_olustur(self, gonderen_id, alan_id, arac_id, gun_sayisi, not_mesaji=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            hediye_kodu = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            cursor.execute('''
                INSERT INTO hediyeler (gonderen_musteri_id, alan_musteri_id, arac_id, gunluk_fiyat, hediye_kodu, not_mesaji, durum)
                VALUES (?, ?, ?, ?, ?, ?, 'Beklemede')
            ''', (gonderen_id, alan_id, arac_id, 0, hediye_kodu, not_mesaji))

            return hediye_kodu

    def hediyeleri_getir(self, musteri_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if musteri_id:
                cursor.execute('''
                    SELECT h.*,
                           g.ad as gonderen_ad, g.soyad as gonderen_soyad,
                           a.ad as alan_ad, a.soyad as alan_soyad,
                           ar.marka, ar.model, ar.plaka, ar.yil
                    FROM hediyeler h
                    JOIN musteriler g ON h.gonderen_musteri_id = g.musteri_id
                    JOIN musteriler a ON h.alan_musteri_id = a.musteri_id
                    JOIN araclar ar ON h.arac_id = ar.arac_id
                    WHERE h.gonderen_musteri_id = ? OR h.alan_musteri_id = ?
                    ORDER BY h.olusturma_tarihi DESC
                ''', (musteri_id, musteri_id))
            else:
                cursor.execute('''
                    SELECT h.*,
                           g.ad as gonderen_ad, g.soyad as gonderen_soyad,
                           a.ad as alan_ad, a.soyad as alan_soyad,
                           ar.marka, ar.model, ar.plaka, ar.yil
                    FROM hediyeler h
                    JOIN musteriler g ON h.gonderen_musteri_id = g.musteri_id
                    JOIN musteriler a ON h.alan_musteri_id = a.musteri_id
                    JOIN araclar ar ON h.arac_id = ar.arac_id
                    ORDER BY h.olusturma_tarihi DESC
                ''')
            return [dict(row) for row in cursor.fetchall()]

    def hediye_kullan(self, hediye_kodu, kullanan_musteri_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM hediyeler WHERE hediye_kodu = ? AND durum = "Beklemede"', (hediye_kodu,))
            hediye = cursor.fetchone()

            if not hediye:
                raise ValueError("Geçersiz veya kullanılmış hediye kodu!")

            if hediye['alan_musteri_id'] != kullanan_musteri_id:
                raise ValueError("Bu hediye kodu size ait değil!")

            cursor.execute('''
                UPDATE hediyeler SET durum = 'Kullanıldı' WHERE hediye_kodu = ?
            ''', (hediye_kodu,))

            cursor.execute('SELECT kilometre FROM araclar WHERE arac_id = ?', (hediye['arac_id'],))
            arac = cursor.fetchone()
            arac_km = arac['kilometre'] if arac else 0

            cursor.execute('''
                INSERT INTO kiralamalar (arac_id, musteri_id, gunluk_fiyat, baslangic, baslangic_km, durum)
                VALUES (?, ?, ?, ?, ?, 'Devam ediyor')
            ''', (hediye['arac_id'], hediye['alan_musteri_id'], 0, datetime.now(), arac_km))

            cursor.execute('UPDATE araclar SET musait_mi = 0 WHERE arac_id = ?', (hediye['arac_id'],))

            cursor.execute('SELECT ad, soyad FROM musteriler WHERE musteri_id = ?', (hediye['gonderen_musteri_id'],))
            gonderen = cursor.fetchone()

            cursor.execute('SELECT marka, model FROM araclar WHERE arac_id = ?', (hediye['arac_id'],))
            arac_bilgi = cursor.fetchone()

            return {
                'gonderen_ad': gonderen['ad'] if gonderen else '',
                'gonderen_soyad': gonderen['soyad'] if gonderen else '',
                'marka': arac_bilgi['marka'] if arac_bilgi else '',
                'model': arac_bilgi['model'] if arac_bilgi else ''
            }

    def hediye_iptal(self, hediye_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE hediyeler SET durum = 'İptal Edildi' WHERE hediye_id = ?
            ''', (hediye_id,))


# ============ YARDIMCI FONKSİYONLAR ==========

def email_gecerli_mi(email):
    return "@" in email and "." in email

def telefon_gecerli_mi(telefon):
    return telefon.isdigit() and len(telefon) >= 10


# ============ LOGIN DIALOG ==========

class LoginDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Premium Araç Kiralama - Giriş")
        self.setGeometry(400, 300, 450, 380)
        self.setStyleSheet(MODERN_STYLE)
        self.setModal(True)
        self.init_ui()
        self.kullanici = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30, 30)

        baslik = QLabel("🚗 PREMIUM ARAÇ KİRALAMA")
        baslik_font = QFont("Arial", 18, QFont.Bold)
        baslik.setFont(baslik_font)
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00adb5; margin-bottom: 20px;")

        alt_baslik = QLabel("Sisteme Giriş Yapın")
        alt_baslik.setFont(QFont("Arial", 12))
        alt_baslik.setAlignment(Qt.AlignCenter)
        alt_baslik.setStyleSheet("color: #e2e2e2; margin-bottom: 30px;")

        kadi_label = QLabel("Kullanıcı Adı")
        kadi_label.setFont(QFont("Arial", 11, QFont.Bold))
        kadi_label.setStyleSheet("color: #00adb5;")
        self.kadi_input = QLineEdit()
        self.kadi_input.setPlaceholderText("Kullanıcı adınızı girin")
        self.kadi_input.setStyleSheet("padding: 12px; font-size: 12px;")

        sifre_label = QLabel("Şifre")
        sifre_label.setFont(QFont("Arial", 11, QFont.Bold))
        sifre_label.setStyleSheet("color: #00adb5;")
        self.sifre_input = QLineEdit()
        self.sifre_input.setEchoMode(QLineEdit.Password)
        self.sifre_input.setPlaceholderText("Şifrenizi girin")
        self.sifre_input.setStyleSheet("padding: 12px; font-size: 12px;")
        self.sifre_input.returnPressed.connect(self.giris_yap)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        giris_btn = QPushButton("Giriş Yap")
        giris_btn.setStyleSheet("background-color: #00adb5; color: white; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 13px;")
        giris_btn.clicked.connect(self.giris_yap)

        iptal_btn = QPushButton("Çıkış")
        iptal_btn.setStyleSheet("background-color: #f05454; color: white; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 13px;")
        iptal_btn.clicked.connect(self.reject)

        button_layout.addWidget(giris_btn)
        button_layout.addWidget(iptal_btn)

        layout.addWidget(baslik)
        layout.addWidget(alt_baslik)
        layout.addWidget(kadi_label)
        layout.addWidget(self.kadi_input)
        layout.addWidget(sifre_label)
        layout.addWidget(self.sifre_input)
        layout.addSpacing(20)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def giris_yap(self):
        kadi = self.kadi_input.text().strip()
        sifre = self.sifre_input.text().strip()

        if not kadi or not sifre:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı ve şifre giriniz!")
            return

        kullanici = self.db.kullanici_kontrol(kadi, sifre)
        if kullanici:
            self.kullanici = kullanici
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")


# ============ DİĞER DİALOGLAR ==========

class AracEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Araç Ekle")
        self.setGeometry(200, 200, 450, 550)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.result = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik = QLabel("🚗 Yeni Araç Kaydı")
        baslik.setFont(QFont("Arial", 14, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00adb5; margin-bottom: 10px;")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Marka:"), 0, 0)
        self.marka_input = QLineEdit()
        self.marka_input.setPlaceholderText("Örn: BMW, Mercedes, Audi...")
        grid.addWidget(self.marka_input, 0, 1)

        grid.addWidget(QLabel("Model:"), 1, 0)
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Örn: X5, C200, A4...")
        grid.addWidget(self.model_input, 1, 1)

        grid.addWidget(QLabel("Üretim Yılı:"), 2, 0)
        self.yil_input = QSpinBox()
        self.yil_input.setMinimum(1990)
        self.yil_input.setMaximum(datetime.now().year)
        self.yil_input.setValue(datetime.now().year)
        grid.addWidget(self.yil_input, 2, 1)

        grid.addWidget(QLabel("Kilometre:"), 3, 0)
        self.km_input = QSpinBox()
        self.km_input.setMaximum(1000000)
        grid.addWidget(self.km_input, 3, 1)

        grid.addWidget(QLabel("Plaka:"), 4, 0)
        self.plaka_input = QLineEdit()
        self.plaka_input.setPlaceholderText("Örn: 34ABC123")
        grid.addWidget(self.plaka_input, 4, 1)

        layout.addWidget(baslik)
        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        ekle_btn = QPushButton("✓ Ekle")
        ekle_btn.setStyleSheet("background-color: #00adb5; padding: 12px; border-radius: 8px; font-weight: bold;")
        ekle_btn.clicked.connect(self.ekle)
        iptal_btn = QPushButton("✗ İptal")
        iptal_btn.setStyleSheet("background-color: #f05454; padding: 12px; border-radius: 8px; font-weight: bold;")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(iptal_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def ekle(self):
        if (self.marka_input.text().strip() and self.model_input.text().strip() and self.plaka_input.text().strip()):
            self.result = (
                self.marka_input.text().strip().upper(),
                self.model_input.text().strip().capitalize(),
                self.yil_input.value(),
                self.km_input.value(),
                self.plaka_input.text().strip().upper()
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")


class MusteriEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Müşteri Ekle")
        self.setGeometry(200, 200, 450, 550)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.result = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik = QLabel("👤 Yeni Müşteri Kaydı")
        baslik.setFont(QFont("Arial", 14, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00adb5; margin-bottom: 10px;")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Ad:"), 0, 0)
        self.ad_input = QLineEdit()
        grid.addWidget(self.ad_input, 0, 1)

        grid.addWidget(QLabel("Soyad:"), 1, 0)
        self.soyad_input = QLineEdit()
        grid.addWidget(self.soyad_input, 1, 1)

        grid.addWidget(QLabel("Ehliyet No:"), 2, 0)
        self.eh_input = QLineEdit()
        grid.addWidget(self.eh_input, 2, 1)

        grid.addWidget(QLabel("Telefon:"), 3, 0)
        self.tel_input = QLineEdit()
        self.tel_input.setPlaceholderText("10 haneli")
        grid.addWidget(self.tel_input, 3, 1)

        grid.addWidget(QLabel("Email:"), 4, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@mail.com")
        grid.addWidget(self.email_input, 4, 1)

        layout.addWidget(baslik)
        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        ekle_btn = QPushButton("✓ Ekle")
        ekle_btn.setStyleSheet("background-color: #00adb5; padding: 12px; border-radius: 8px; font-weight: bold;")
        ekle_btn.clicked.connect(self.ekle)
        iptal_btn = QPushButton("✗ İptal")
        iptal_btn.setStyleSheet("background-color: #f05454; padding: 12px; border-radius: 8px; font-weight: bold;")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(iptal_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def ekle(self):
        if (self.ad_input.text().strip() and self.soyad_input.text().strip() and
            self.eh_input.text().strip() and self.tel_input.text().strip() and self.email_input.text().strip()):
            if not telefon_gecerli_mi(self.tel_input.text()):
                QMessageBox.warning(self, "Hata", "Geçerli telefon numarası giriniz!")
                return
            if not email_gecerli_mi(self.email_input.text()):
                QMessageBox.warning(self, "Hata", "Geçerli email giriniz!")
                return
            self.result = (
                self.ad_input.text().strip().capitalize(),
                self.soyad_input.text().strip().capitalize(),
                self.eh_input.text().strip().upper(),
                self.tel_input.text().strip(),
                self.email_input.text().strip()
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")


class KiralamaBaslatDialog(QDialog):
    def __init__(self, araclar, musteriler, parent=None):
        super().__init__(parent)
        self.araclar = araclar
        self.musteriler = musteriler
        self.setWindowTitle("Kiralama Başlat")
        self.setGeometry(200, 200, 450, 450)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.result = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik = QLabel("🔑 Yeni Kiralama İşlemi")
        baslik.setFont(QFont("Arial", 14, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00adb5; margin-bottom: 10px;")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Araç Seçin:"), 0, 0)
        self.arac_combo = QComboBox()
        for arac in self.araclar:
            if arac['musait_mi']:
                self.arac_combo.addItem(f"🚗 {arac['marka']} {arac['model']} ({arac['yil']}) - {arac['plaka']}", arac['arac_id'])
        grid.addWidget(self.arac_combo, 0, 1)

        grid.addWidget(QLabel("Müşteri Seçin:"), 1, 0)
        self.musteri_combo = QComboBox()
        for mus in self.musteriler:
            self.musteri_combo.addItem(f"👤 {mus['ad']} {mus['soyad']} - {mus['telefon']}", mus['musteri_id'])
        grid.addWidget(self.musteri_combo, 1, 1)

        grid.addWidget(QLabel("Günlük Fiyat (TL):"), 2, 0)
        self.fiyat_input = QDoubleSpinBox()
        self.fiyat_input.setMaximum(500000)
        self.fiyat_input.setMinimum(1)
        self.fiyat_input.setValue(500)
        grid.addWidget(self.fiyat_input, 2, 1)

        layout.addWidget(baslik)
        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        baslat_btn = QPushButton("✓ Başlat")
        baslat_btn.setStyleSheet("background-color: #00adb5; padding: 12px; border-radius: 8px; font-weight: bold;")
        baslat_btn.clicked.connect(self.baslat)
        iptal_btn = QPushButton("✗ İptal")
        iptal_btn.setStyleSheet("background-color: #f05454; padding: 12px; border-radius: 8px; font-weight: bold;")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(baslat_btn)
        button_layout.addWidget(iptal_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def baslat(self):
        arac_id = self.arac_combo.currentData()
        mus_id = self.musteri_combo.currentData()
        if arac_id and mus_id and self.fiyat_input.value() > 0:
            self.result = (arac_id, mus_id, self.fiyat_input.value())
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Geçerli seçim yapınız!")


class KiralamaBitirDialog(QDialog):
    def __init__(self, kiralamalar, parent=None):
        super().__init__(parent)
        self.kiralamalar = kiralamalar
        self.setWindowTitle("Kiralama Bitir")
        self.setGeometry(200, 200, 450, 400)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.result = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik = QLabel("🔓 Kiralama İşlemini Bitir")
        baslik.setFont(QFont("Arial", 14, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00adb5; margin-bottom: 10px;")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Aktif Kiralama Seçin:"), 0, 0)
        self.kir_combo = QComboBox()
        for kir in self.kiralamalar:
            self.kir_combo.addItem(f"🚗 {kir['marka']} {kir['model']} → 👤 {kir['ad']} {kir['soyad']}", kir['kiralama_id'])
        grid.addWidget(self.kir_combo, 0, 1)

        grid.addWidget(QLabel("Araç Son Kilometre:"), 1, 0)
        self.km_input = QSpinBox()
        self.km_input.setMaximum(1000000)
        self.km_input.setMinimum(0)
        grid.addWidget(self.km_input, 1, 1)

        layout.addWidget(baslik)
        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        bitir_btn = QPushButton("✓ Bitir")
        bitir_btn.setStyleSheet("background-color: #00adb5; padding: 12px; border-radius: 8px; font-weight: bold;")
        bitir_btn.clicked.connect(self.bitir)
        iptal_btn = QPushButton("✗ İptal")
        iptal_btn.setStyleSheet("background-color: #f05454; padding: 12px; border-radius: 8px; font-weight: bold;")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(bitir_btn)
        button_layout.addWidget(iptal_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def bitir(self):
        kir_id = self.kir_combo.currentData()
        if kir_id and self.km_input.value() >= 0:
            self.result = (kir_id, self.km_input.value())
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Geçerli seçim yapınız!")


class SistemKullaniciDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Sistem Kullanıcısı Ekle")
        self.setGeometry(200, 200, 450, 550)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.result = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik = QLabel("👤 Yeni Sistem Kullanıcısı")
        baslik.setFont(QFont("Arial", 14, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00adb5; margin-bottom: 10px;")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Ad:"), 0, 0)
        self.ad_input = QLineEdit()
        grid.addWidget(self.ad_input, 0, 1)

        grid.addWidget(QLabel("Soyad:"), 1, 0)
        self.soyad_input = QLineEdit()
        grid.addWidget(self.soyad_input, 1, 1)

        grid.addWidget(QLabel("Kullanıcı Adı:"), 2, 0)
        self.kadi_input = QLineEdit()
        grid.addWidget(self.kadi_input, 2, 1)

        grid.addWidget(QLabel("Şifre:"), 3, 0)
        self.sifre_input = QLineEdit()
        self.sifre_input.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.sifre_input, 3, 1)

        grid.addWidget(QLabel("Rol:"), 4, 0)
        self.rol_combo = QComboBox()
        self.rol_combo.addItems(["user", "admin"])
        grid.addWidget(self.rol_combo, 4, 1)

        layout.addWidget(baslik)
        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        ekle_btn = QPushButton("✓ Ekle")
        ekle_btn.setStyleSheet("background-color: #00adb5; padding: 12px; border-radius: 8px; font-weight: bold;")
        ekle_btn.clicked.connect(self.ekle)
        iptal_btn = QPushButton("✗ İptal")
        iptal_btn.setStyleSheet("background-color: #f05454; padding: 12px; border-radius: 8px; font-weight: bold;")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(iptal_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def ekle(self):
        if (self.ad_input.text().strip() and self.soyad_input.text().strip() and
            self.kadi_input.text().strip() and self.sifre_input.text().strip()):
            self.result = (
                self.kadi_input.text().strip(),
                self.sifre_input.text().strip(),
                self.ad_input.text().strip().capitalize(),
                self.soyad_input.text().strip().capitalize(),
                self.rol_combo.currentText()
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")


class HediyeOlusturDialog(QDialog):
    def __init__(self, musteriler, araclar, parent=None):
        super().__init__(parent)
        self.musteriler = musteriler
        self.araclar = [a for a in araclar if a['musait_mi']]
        self.setWindowTitle("Hediye Kiralama Oluştur")
        self.setGeometry(200, 200, 550, 600)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.result = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik = QLabel("🎁 Hediye Kiralama Oluştur")
        baslik.setFont(QFont("Arial", 14, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #f5a623; margin-bottom: 10px;")

        aciklama = QLabel("Bir arkadaşınıza araba kiralamayı hediye edin!")
        aciklama.setAlignment(Qt.AlignCenter)
        aciklama.setStyleSheet("color: #e2e2e2; margin-bottom: 15px;")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Siz (Gönderen):"), 0, 0)
        self.gonderen_combo = QComboBox()
        for mus in self.musteriler:
            self.gonderen_combo.addItem(f"👤 {mus['ad']} {mus['soyad']} - {mus['telefon']}", mus['musteri_id'])
        grid.addWidget(self.gonderen_combo, 0, 1)

        grid.addWidget(QLabel("Hediye Alacak Kişi:"), 1, 0)
        self.alan_combo = QComboBox()
        for mus in self.musteriler:
            self.alan_combo.addItem(f"🎁 {mus['ad']} {mus['soyad']} - {mus['telefon']}", mus['musteri_id'])
        grid.addWidget(self.alan_combo, 1, 1)

        grid.addWidget(QLabel("Hediye Edilecek Araç:"), 2, 0)
        self.arac_combo = QComboBox()
        for arac in self.araclar:
            self.arac_combo.addItem(f"🚗 {arac['marka']} {arac['model']} ({arac['yil']}) - {arac['plaka']}", arac['arac_id'])
        grid.addWidget(self.arac_combo, 2, 1)

        grid.addWidget(QLabel("Hediye Notu:"), 3, 0)
        self.not_text = QTextEdit()
        self.not_text.setPlaceholderText("Hediye notunuzu buraya yazabilirsiniz...\nÖrn: Doğum günün kutlu olsun! 🎂")
        self.not_text.setMaximumHeight(100)
        grid.addWidget(self.not_text, 3, 1)

        layout.addWidget(baslik)
        layout.addWidget(aciklama)
        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        olustur_btn = QPushButton("🎁 Hediyeyi Oluştur")
        olustur_btn.setStyleSheet("background-color: #f5a623; padding: 12px; border-radius: 8px; font-weight: bold;")
        olustur_btn.clicked.connect(self.olustur)
        iptal_btn = QPushButton("✗ İptal")
        iptal_btn.setStyleSheet("background-color: #f05454; padding: 12px; border-radius: 8px; font-weight: bold;")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(olustur_btn)
        button_layout.addWidget(iptal_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def olustur(self):
        gonderen_id = self.gonderen_combo.currentData()
        alan_id = self.alan_combo.currentData()
        arac_id = self.arac_combo.currentData()
        not_mesaji = self.not_text.toPlainText()

        if gonderen_id == alan_id:
            QMessageBox.warning(self, "Hata", "Kendinize hediye gönderemezsiniz!")
            return

        if gonderen_id and alan_id and arac_id:
            self.result = (gonderen_id, alan_id, arac_id, 1, not_mesaji)
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")


# ============ GRAFİKLER ==========

class ModernStatisticsWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.figure = Figure(figsize=(14, 6), dpi=100, facecolor='#1a1a2e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_charts(self):
        self.figure.clear()
        araclar = self.db.araclari_getir()
        musteriler = self.db.musterileri_getir()
        aktif_kiralama = self.db.aktif_kiralama_sayisi()
        kiralamalar = self.db.kiralamalari_getir()

        ax1 = self.figure.add_subplot(121)
        ax1.set_facecolor('#1a1a2e')
        if araclar:
            musait = sum(1 for a in araclar if a['musait_mi'])
            kirada = aktif_kiralama
            sizes = [musait, kirada]
            labels = [f'Müsait Araçlar\n{musait} adet', f'Kiradaki Araçlar\n{kirada} adet']
            colors = ['#00adb5', '#f05454']
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                colors=colors, startangle=90, textprops={'fontsize': 11, 'color': '#e2e2e2'})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            ax1.set_title('Araç Durumu Dağılımı', fontsize=14, fontweight='bold', color='#00adb5', pad=20)
        else:
            ax1.text(0.5, 0.5, 'Henüz Araç Yok', ha='center', va='center', fontsize=14, color='#e2e2e2')
            ax1.set_title('Araç Durumu Dağılımı', fontsize=14, fontweight='bold', color='#00adb5', pad=20)

        ax2 = self.figure.add_subplot(122)
        ax2.set_facecolor('#1a1a2e')
        labels = ['🚗 Araçlar', '👥 Müşteriler', '🔑 Kiralamalar']
        values = [len(araclar), len(musteriler), len(kiralamalar)]
        colors_bar = ['#00adb5', '#4ecca3', '#f5a623']
        bars = ax2.bar(labels, values, color=colors_bar, edgecolor='none', linewidth=0, width=0.6)
        ax2.set_title('Sistem İstatistikleri', fontsize=14, fontweight='bold', color='#00adb5', pad=20)
        ax2.set_ylabel('Sayı', fontsize=12, color='#e2e2e2')
        ax2.tick_params(axis='y', colors='#e2e2e2')
        ax2.tick_params(axis='x', colors='#e2e2e2', labelsize=11)
        ax2.set_ylim(0, max(values) + 5 if values else 10)

        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=12, color='#e2e2e2')

        self.figure.tight_layout()
        self.canvas.draw()


# ============ ANA PENCERE ==========

class AracKiralamaMainWindow(QMainWindow):
    def __init__(self, kullanici, db):
        super().__init__()
        self.kullanici = kullanici
        self.db = db
        self.setWindowTitle(f"🚗 Premium Araç Kiralama Sistemi - Hoşgeldiniz, {kullanici['ad']} {kullanici['soyad']}")
        self.setGeometry(50, 50, 1400, 850)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.load_data()

    def load_data(self):
        self.arac_listele()
        self.musteri_listele()
        self.kir_listele()
        self.hediye_listele()
        if self.kullanici['rol'] == 'admin':
            self.sistem_kullanici_listele()
        self.refresh_all()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #16213e; border-radius: 15px;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)

        header = QLabel("🚗 PREMIUM ARAÇ KİRALAMA SİSTEMİ")
        header_font = QFont("Arial", 22, QFont.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #00adb5;")

        # SAĞ TARAF - ARAMA KUTUSU VE KULLANICI BİLGİSİ
        right_widget = QWidget()
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(0, 0, 0, 0)

        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 1px solid #0f3460;
                border-radius: 25px;
                padding: 2px;
            }
            QFrame:focus-within {
                border: 1px solid #00adb5;
            }
        """)
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        search_layout.setContentsMargins(12, 5, 12, 5)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #00adb5; font-size: 14px; background: transparent;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ara...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: #e2e2e2;
                font-size: 12px;
                padding: 5px 0;
                min-width: 180px;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        self.search_input.setFocusPolicy(Qt.StrongFocus)
        self.search_input.textChanged.connect(self.arama_yap)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        search_frame.setLayout(search_layout)

        kullanici_label = QLabel(f"👤 {self.kullanici['ad']} {self.kullanici['soyad']} [{self.kullanici['rol']}]")
        kullanici_label.setFont(QFont("Arial", 11, QFont.Bold))
        kullanici_label.setStyleSheet("color: #00adb5; background-color: #1a1a2e; padding: 8px 15px; border-radius: 20px;")

        cikis_btn = QPushButton("🚪 Çıkış")
        cikis_btn.setStyleSheet("background-color: #f05454; padding: 8px 20px; border-radius: 20px; font-weight: bold;")
        cikis_btn.clicked.connect(self.cikis_yap)

        right_layout.addWidget(search_frame)
        right_layout.addWidget(kullanici_label)
        right_layout.addWidget(cikis_btn)
        right_widget.setLayout(right_layout)

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(right_widget)
        header_frame.setLayout(header_layout)

        # Dashboard Kartları
        dashboard_layout = QHBoxLayout()
        dashboard_layout.setSpacing(20)

        arac_card = self.create_modern_card("🚗 Toplam Araç", "0", "#00adb5")
        musteri_card = self.create_modern_card("👥 Toplam Müşteri", "0", "#4ecca3")
        kir_card = self.create_modern_card("🔑 Aktif Kiralamalar", "0", "#f5a623")
        ciro_card = self.create_modern_card("💰 Toplam Ciro", "0 TL", "#f05454")

        dashboard_layout.addWidget(arac_card)
        dashboard_layout.addWidget(musteri_card)
        dashboard_layout.addWidget(kir_card)
        dashboard_layout.addWidget(ciro_card)

        self.arac_label = arac_card.findChild(QLabel, "value_label")
        self.musteri_label = musteri_card.findChild(QLabel, "value_label")
        self.kir_label = kir_card.findChild(QLabel, "value_label")
        self.ciro_label = ciro_card.findChild(QLabel, "value_label")

        # Sekmeler
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.sekme_degisti)

        self.arac_tab = self.create_arac_tab()
        self.musteri_tab = self.create_musteri_tab()
        self.kir_tab = self.create_kir_tab()
        self.hediye_tab = self.create_hediye_tab()
        self.stats_widget = ModernStatisticsWidget(self.db)
        self.rapor_tab = self.create_rapor_tab()

        self.tabs.addTab(self.arac_tab, "  🚗 Araçlar  ")
        self.tabs.addTab(self.musteri_tab, "  👥 Müşteriler  ")
        self.tabs.addTab(self.kir_tab, "  🔑 Kiralamalar  ")
        self.tabs.addTab(self.hediye_tab, "  🎁 Hediyeler  ")
        self.tabs.addTab(self.stats_widget, "  📊 İstatistikler  ")
        self.tabs.addTab(self.rapor_tab, "  📄 Raporlar  ")

        if self.kullanici['rol'] == 'admin':
            self.kullanici_tab = self.create_sistem_kullanici_tab()
            self.tabs.addTab(self.kullanici_tab, "  👤 Kullanıcılar  ")

        main_layout.addWidget(header_frame)
        main_layout.addLayout(dashboard_layout)
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(1000)

    def arama_yap(self):
        arama_metni = self.search_input.text().strip().lower()

        if not arama_metni:
            self.arac_listele()
            self.musteri_listele()
            self.kir_listele()
            self.hediye_listele()
            if self.kullanici['rol'] == 'admin':
                self.sistem_kullanici_listele()
            return

        # Araçlarda ara
        self.arac_table.setRowCount(0)
        for arac in self.db.araclari_getir():
            if (arama_metni in arac['marka'].lower() or
                arama_metni in arac['model'].lower() or
                arama_metni in arac['plaka'].lower() or
                arama_metni in str(arac['yil'])):
                row = self.arac_table.rowCount()
                self.arac_table.insertRow(row)
                self.arac_table.setItem(row, 0, QTableWidgetItem(str(arac['arac_id'])))
                self.arac_table.setItem(row, 1, QTableWidgetItem(arac['marka']))
                self.arac_table.setItem(row, 2, QTableWidgetItem(arac['model']))
                self.arac_table.setItem(row, 3, QTableWidgetItem(str(arac['yil'])))
                self.arac_table.setItem(row, 4, QTableWidgetItem(f"{arac['kilometre']:,}"))
                self.arac_table.setItem(row, 5, QTableWidgetItem(arac['plaka']))
                durum_widget = QTableWidgetItem("✅ Müsait" if arac['musait_mi'] else "❌ Kirada")
                if not arac['musait_mi']:
                    durum_widget.setForeground(QColor("#f05454"))
                else:
                    durum_widget.setForeground(QColor("#4ecca3"))
                self.arac_table.setItem(row, 6, durum_widget)

        # Müşterilerde ara
        self.musteri_table.setRowCount(0)
        for mus in self.db.musterileri_getir():
            if (arama_metni in mus['ad'].lower() or
                arama_metni in mus['soyad'].lower() or
                arama_metni in mus['ehliyet_no'].lower() or
                arama_metni in mus['telefon'] or
                arama_metni in mus['email'].lower()):
                row = self.musteri_table.rowCount()
                self.musteri_table.insertRow(row)
                self.musteri_table.setItem(row, 0, QTableWidgetItem(str(mus['musteri_id'])))
                self.musteri_table.setItem(row, 1, QTableWidgetItem(mus['ad']))
                self.musteri_table.setItem(row, 2, QTableWidgetItem(mus['soyad']))
                self.musteri_table.setItem(row, 3, QTableWidgetItem(mus['ehliyet_no']))
                self.musteri_table.setItem(row, 4, QTableWidgetItem(mus['telefon']))
                self.musteri_table.setItem(row, 5, QTableWidgetItem(mus['email']))

        # Kiralamalarda ara
        self.kir_table.setRowCount(0)
        for kir in self.db.kiralamalari_getir():
            if (arama_metni in kir['marka'].lower() or
                arama_metni in kir['model'].lower() or
                arama_metni in kir['ad'].lower() or
                arama_metni in kir['soyad'].lower() or
                arama_metni in kir['durum'].lower()):
                row = self.kir_table.rowCount()
                self.kir_table.insertRow(row)
                baslangic_km = kir['baslangic_km'] if kir['baslangic_km'] else 0
                bitis_km = kir['bitis_km'] if kir['bitis_km'] else 0
                kullanilan_km = bitis_km - baslangic_km if bitis_km > 0 else 0
                ucret = 0
                if kir['baslangic'] and kir['bitis']:
                    baslangic = datetime.fromisoformat(kir['baslangic'].replace(' ', 'T'))
                    bitis = datetime.fromisoformat(kir['bitis'].replace(' ', 'T'))
                    gun_farki = max(1, (bitis - baslangic).days)
                    ucret = gun_farki * kir['gunluk_fiyat']
                elif kir['baslangic'] and not kir['bitis']:
                    baslangic = datetime.fromisoformat(kir['baslangic'].replace(' ', 'T'))
                    gun_farki = max(1, (datetime.now() - baslangic).days)
                    ucret = gun_farki * kir['gunluk_fiyat']
                self.kir_table.setItem(row, 0, QTableWidgetItem(str(kir['kiralama_id'])))
                self.kir_table.setItem(row, 1, QTableWidgetItem(f"{kir['marka']} {kir['model']}"))
                self.kir_table.setItem(row, 2, QTableWidgetItem(f"{kir['ad']} {kir['soyad']}"))
                self.kir_table.setItem(row, 3, QTableWidgetItem(f"{baslangic_km:,}"))
                self.kir_table.setItem(row, 4, QTableWidgetItem(f"{bitis_km:,}" if bitis_km else "-"))
                self.kir_table.setItem(row, 5, QTableWidgetItem(f"{kullanilan_km:,} KM"))
                self.kir_table.setItem(row, 6, QTableWidgetItem(f"{ucret:,.2f}"))
                self.kir_table.setItem(row, 7, QTableWidgetItem(kir['durum']))

        # Hediyelerde ara
        self.hediye_table.setRowCount(0)
        for hediye in self.db.hediyeleri_getir():
            if (arama_metni in hediye.get('gonderen_ad', '').lower() or
                arama_metni in hediye.get('gonderen_soyad', '').lower() or
                arama_metni in hediye.get('alan_ad', '').lower() or
                arama_metni in hediye.get('alan_soyad', '').lower() or
                arama_metni in hediye.get('marka', '').lower() or
                arama_metni in hediye.get('model', '').lower() or
                arama_metni in hediye.get('hediye_kodu', '').lower() or
                arama_metni in hediye.get('durum', '').lower()):
                row = self.hediye_table.rowCount()
                self.hediye_table.insertRow(row)
                self.hediye_table.setItem(row, 0, QTableWidgetItem(str(hediye['hediye_id'])))
                self.hediye_table.setItem(row, 1, QTableWidgetItem(hediye['hediye_kodu']))
                self.hediye_table.setItem(row, 2, QTableWidgetItem(f"{hediye['gonderen_ad']} {hediye['gonderen_soyad']}"))
                self.hediye_table.setItem(row, 3, QTableWidgetItem(f"{hediye['alan_ad']} {hediye['alan_soyad']}"))
                self.hediye_table.setItem(row, 4, QTableWidgetItem(f"{hediye['marka']} {hediye['model']}"))
                self.hediye_table.setItem(row, 5, QTableWidgetItem("🎁 Hediye"))
                durum_widget = QTableWidgetItem(hediye['durum'])
                if hediye['durum'] == 'Kullanıldı':
                    durum_widget.setForeground(QColor("#4ecca3"))
                elif hediye['durum'] == 'İptal Edildi':
                    durum_widget.setForeground(QColor("#f05454"))
                else:
                    durum_widget.setForeground(QColor("#f5a623"))
                self.hediye_table.setItem(row, 6, durum_widget)

        if self.kullanici['rol'] == 'admin':
            self.kullanici_table.setRowCount(0)
            for k in self.db.kullanicilari_getir():
                if (arama_metni in k['kullanici_adi'].lower() or
                    arama_metni in k['ad'].lower() or
                    arama_metni in k['soyad'].lower() or
                    arama_metni in k['rol'].lower()):
                    row = self.kullanici_table.rowCount()
                    self.kullanici_table.insertRow(row)
                    self.kullanici_table.setItem(row, 0, QTableWidgetItem(str(k['kullanici_id'])))
                    self.kullanici_table.setItem(row, 1, QTableWidgetItem(k['kullanici_adi']))
                    self.kullanici_table.setItem(row, 2, QTableWidgetItem(k['ad']))
                    self.kullanici_table.setItem(row, 3, QTableWidgetItem(k['soyad']))
                    self.kullanici_table.setItem(row, 4, QTableWidgetItem(k['rol']))
                    durum_widget = QTableWidgetItem(k['durum'])
                    if k['durum'] == 'Aktif':
                        durum_widget.setForeground(QColor("#4ecca3"))
                    else:
                        durum_widget.setForeground(QColor("#f05454"))
                    self.kullanici_table.setItem(row, 5, durum_widget)

    def sekme_degisti(self, index):
        if not self.search_input.text():
            return
        self.arama_yap()

    def cikis_yap(self):
        reply = QMessageBox.question(self, "Çıkış", "Oturumu kapatmak istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            self.yeni_giris()

    def yeni_giris(self):
        login = LoginDialog(self.db)
        if login.exec_() == QDialog.Accepted and login.kullanici:
            self.kullanici = login.kullanici
            self.setWindowTitle(f"🚗 Premium Araç Kiralama Sistemi - Hoşgeldiniz, {self.kullanici['ad']} {self.kullanici['soyad']}")

            for widget in self.centralWidget().findChildren(QLabel):
                if "👤" in widget.text() and "[" in widget.text():
                    widget.setText(f"👤 {self.kullanici['ad']} {self.kullanici['soyad']} [{self.kullanici['rol']}]")

            admin_sekme_var = False
            for i in range(self.tabs.count()):
                if "Kullanıcılar" in self.tabs.tabText(i):
                    admin_sekme_var = True
                    break

            if self.kullanici['rol'] == 'admin' and not admin_sekme_var:
                self.kullanici_tab = self.create_sistem_kullanici_tab()
                self.tabs.addTab(self.kullanici_tab, "  👤 Kullanıcılar  ")
            elif self.kullanici['rol'] != 'admin' and admin_sekme_var:
                for i in range(self.tabs.count()):
                    if "Kullanıcılar" in self.tabs.tabText(i):
                        self.tabs.removeTab(i)
                        break

            self.load_data()
            self.show()
        else:
            sys.exit()

    def create_modern_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 #1a1a2e);
                border-radius: 15px;
                padding: 20px;
                min-width: 200px;
            }}
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_font = QFont("Arial", 12, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")

        value_label = QLabel(value)
        value_font = QFont("Arial", 28, QFont.Bold)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: white;")
        value_label.setObjectName("value_label")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        return card

    def create_arac_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        button_panel = QFrame()
        button_panel.setStyleSheet("background-color: #16213e; border-radius: 10px; padding: 10px;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ekle_btn = QPushButton("➕ Yeni Araç Ekle")
        ekle_btn.setStyleSheet("background-color: #00adb5; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        ekle_btn.clicked.connect(self.arac_ekle)

        sil_btn = QPushButton("🗑️ Seçili Aracı Sil")
        sil_btn.setStyleSheet("background-color: #f05454; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        sil_btn.clicked.connect(self.arac_sil)

        yenile_btn = QPushButton("🔄 Yenile")
        yenile_btn.setStyleSheet("background-color: #0f3460; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        yenile_btn.clicked.connect(self.arac_listele)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(sil_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()
        button_panel.setLayout(button_layout)

        self.arac_table = QTableWidget()
        self.arac_table.setColumnCount(7)
        self.arac_table.setHorizontalHeaderLabels(["ID", "Marka", "Model", "Yıl", "Kilometre", "Plaka", "Durum"])
        self.arac_table.setAlternatingRowColors(True)
        self.arac_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(button_panel)
        layout.addWidget(self.arac_table)
        widget.setLayout(layout)
        return widget

    def create_musteri_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        button_panel = QFrame()
        button_panel.setStyleSheet("background-color: #16213e; border-radius: 10px; padding: 10px;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ekle_btn = QPushButton("➕ Yeni Müşteri Ekle")
        ekle_btn.setStyleSheet("background-color: #00adb5; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        ekle_btn.clicked.connect(self.musteri_ekle)

        sil_btn = QPushButton("🗑️ Seçili Müşteriyi Sil")
        sil_btn.setStyleSheet("background-color: #f05454; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        sil_btn.clicked.connect(self.musteri_sil)

        yenile_btn = QPushButton("🔄 Yenile")
        yenile_btn.setStyleSheet("background-color: #0f3460; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        yenile_btn.clicked.connect(self.musteri_listele)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(sil_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()
        button_panel.setLayout(button_layout)

        self.musteri_table = QTableWidget()
        self.musteri_table.setColumnCount(6)
        self.musteri_table.setHorizontalHeaderLabels(["ID", "Ad", "Soyad", "Ehliyet No", "Telefon", "Email"])
        self.musteri_table.setAlternatingRowColors(True)
        self.musteri_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(button_panel)
        layout.addWidget(self.musteri_table)
        widget.setLayout(layout)
        return widget

    def create_kir_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        button_panel = QFrame()
        button_panel.setStyleSheet("background-color: #16213e; border-radius: 10px; padding: 10px;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        baslat_btn = QPushButton("🔑 Yeni Kiralama Başlat")
        baslat_btn.setStyleSheet("background-color: #00adb5; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        baslat_btn.clicked.connect(self.kir_baslat)

        hediye_et_btn = QPushButton("🎁 Hediye Et")
        hediye_et_btn.setStyleSheet("background-color: #f5a623; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        hediye_et_btn.clicked.connect(self.hediye_et)

        bitir_btn = QPushButton("🔓 Kiralama Bitir")
        bitir_btn.setStyleSheet("background-color: #f05454; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        bitir_btn.clicked.connect(self.kir_bitir)

        yenile_btn = QPushButton("🔄 Yenile")
        yenile_btn.setStyleSheet("background-color: #0f3460; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        yenile_btn.clicked.connect(self.kir_listele)

        button_layout.addWidget(baslat_btn)
        button_layout.addWidget(hediye_et_btn)
        button_layout.addWidget(bitir_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()
        button_panel.setLayout(button_layout)

        self.kir_table = QTableWidget()
        self.kir_table.setColumnCount(8)
        self.kir_table.setHorizontalHeaderLabels(["ID", "Araç", "Müşteri", "Başlangıç KM", "Bitiş KM", "Kullanılan KM", "Ücret (TL)", "Durum"])
        self.kir_table.setAlternatingRowColors(True)
        self.kir_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(button_panel)
        layout.addWidget(self.kir_table)
        widget.setLayout(layout)
        return widget

    def create_hediye_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        button_panel = QFrame()
        button_panel.setStyleSheet("background-color: #16213e; border-radius: 10px; padding: 10px;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        hediye_olustur_btn = QPushButton("🎁 Yeni Hediye Oluştur")
        hediye_olustur_btn.setStyleSheet("background-color: #f5a623; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        hediye_olustur_btn.clicked.connect(self.hediye_olustur)

        hediye_kullan_btn = QPushButton("🎁 Hediye Kodu Kullan")
        hediye_kullan_btn.setStyleSheet("background-color: #00adb5; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        hediye_kullan_btn.clicked.connect(self.hediye_kullan)

        hediye_iptal_btn = QPushButton("❌ Seçili Hediyeyi İptal Et")
        hediye_iptal_btn.setStyleSheet("background-color: #f05454; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        hediye_iptal_btn.clicked.connect(self.hediye_iptal)

        yenile_btn = QPushButton("🔄 Yenile")
        yenile_btn.setStyleSheet("background-color: #0f3460; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        yenile_btn.clicked.connect(self.hediye_listele)

        button_layout.addWidget(hediye_olustur_btn)
        button_layout.addWidget(hediye_kullan_btn)
        button_layout.addWidget(hediye_iptal_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()
        button_panel.setLayout(button_layout)

        self.hediye_table = QTableWidget()
        self.hediye_table.setColumnCount(7)
        self.hediye_table.setHorizontalHeaderLabels(["ID", "Hediye Kodu", "Gönderen", "Alan", "Araç", "Ücret", "Durum"])
        self.hediye_table.setAlternatingRowColors(True)
        self.hediye_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(button_panel)
        layout.addWidget(self.hediye_table)
        widget.setLayout(layout)
        return widget

    def create_rapor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        rapor_btn = QPushButton("📋 Kapsamlı Rapor Oluştur")
        rapor_btn.setStyleSheet("background-color: #00adb5; padding: 12px 30px; border-radius: 8px; font-weight: bold; font-size: 13px; max-width: 250px;")
        rapor_btn.clicked.connect(self.rapor_olustur)

        self.rapor_text = QTextEdit()
        self.rapor_text.setReadOnly(True)

        layout.addWidget(rapor_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.rapor_text)
        widget.setLayout(layout)
        return widget

    def create_sistem_kullanici_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        button_panel = QFrame()
        button_panel.setStyleSheet("background-color: #16213e; border-radius: 10px; padding: 10px;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ekle_btn = QPushButton("➕ Yeni Kullanıcı Ekle")
        ekle_btn.setStyleSheet("background-color: #00adb5; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        ekle_btn.clicked.connect(self.sistem_kullanici_ekle)

        sil_btn = QPushButton("🗑️ Seçili Kullanıcıyı Sil")
        sil_btn.setStyleSheet("background-color: #f05454; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        sil_btn.clicked.connect(self.sistem_kullanici_sil)

        yenile_btn = QPushButton("🔄 Yenile")
        yenile_btn.setStyleSheet("background-color: #0f3460; padding: 10px 25px; border-radius: 8px; font-weight: bold;")
        yenile_btn.clicked.connect(self.sistem_kullanici_listele)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(sil_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()
        button_panel.setLayout(button_layout)

        self.kullanici_table = QTableWidget()
        self.kullanici_table.setColumnCount(6)
        self.kullanici_table.setHorizontalHeaderLabels(["ID", "Kullanıcı Adı", "Ad", "Soyad", "Rol", "Durum"])
        self.kullanici_table.setAlternatingRowColors(True)
        self.kullanici_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(button_panel)
        layout.addWidget(self.kullanici_table)
        widget.setLayout(layout)
        return widget

    # ============ ARAÇ METODLARI ============

    def arac_ekle(self):
        try:
            dialog = AracEkleDialog(self)
            if dialog.exec_() == QDialog.Accepted and dialog.result:
                self.db.arac_ekle(*dialog.result)
                QMessageBox.information(self, "Başarılı", "🚗 Araç başarıyla eklendi!")
                self.arac_listele()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu plaka ile kayıtlı araç zaten var!")

    def arac_sil(self):
        row = self.arac_table.currentRow()
        if row >= 0:
            arac_id = int(self.arac_table.item(row, 0).text())
            durum = self.arac_table.item(row, 6).text()
            if "Kirada" in durum:
                QMessageBox.warning(self, "Hata", "Kirada olan araç silinemez!")
                return
            try:
                self.db.arac_sil(arac_id)
                QMessageBox.information(self, "Başarılı", "Araç silindi!")
                self.arac_listele()
            except ValueError as e:
                QMessageBox.warning(self, "Hata", str(e))
        else:
            QMessageBox.warning(self, "Hata", "Lütfen silinecek aracı seçin!")

    def arac_listele(self):
        self.arac_table.setRowCount(0)
        for arac in self.db.araclari_getir():
            row = self.arac_table.rowCount()
            self.arac_table.insertRow(row)
            self.arac_table.setItem(row, 0, QTableWidgetItem(str(arac['arac_id'])))
            self.arac_table.setItem(row, 1, QTableWidgetItem(arac['marka']))
            self.arac_table.setItem(row, 2, QTableWidgetItem(arac['model']))
            self.arac_table.setItem(row, 3, QTableWidgetItem(str(arac['yil'])))
            self.arac_table.setItem(row, 4, QTableWidgetItem(f"{arac['kilometre']:,}"))
            self.arac_table.setItem(row, 5, QTableWidgetItem(arac['plaka']))
            durum_widget = QTableWidgetItem("✅ Müsait" if arac['musait_mi'] else "❌ Kirada")
            if not arac['musait_mi']:
                durum_widget.setForeground(QColor("#f05454"))
            else:
                durum_widget.setForeground(QColor("#4ecca3"))
            self.arac_table.setItem(row, 6, durum_widget)

    # ============ MÜŞTERİ METODLARI ============

    def musteri_ekle(self):
        try:
            dialog = MusteriEkleDialog(self)
            if dialog.exec_() == QDialog.Accepted and dialog.result:
                self.db.musteri_ekle(*dialog.result)
                QMessageBox.information(self, "Başarılı", "👤 Müşteri başarıyla eklendi!")
                self.musteri_listele()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu ehliyet no veya email ile kayıtlı müşteri zaten var!")

    def musteri_sil(self):
        row = self.musteri_table.currentRow()
        if row >= 0:
            musteri_id = int(self.musteri_table.item(row, 0).text())
            try:
                self.db.musteri_sil(musteri_id)
                QMessageBox.information(self, "Başarılı", "Müşteri silindi!")
                self.musteri_listele()
            except ValueError as e:
                QMessageBox.warning(self, "Hata", str(e))
        else:
            QMessageBox.warning(self, "Hata", "Lütfen silinecek müşteriyi seçin!")

    def musteri_listele(self):
        self.musteri_table.setRowCount(0)
        for mus in self.db.musterileri_getir():
            row = self.musteri_table.rowCount()
            self.musteri_table.insertRow(row)
            self.musteri_table.setItem(row, 0, QTableWidgetItem(str(mus['musteri_id'])))
            self.musteri_table.setItem(row, 1, QTableWidgetItem(mus['ad']))
            self.musteri_table.setItem(row, 2, QTableWidgetItem(mus['soyad']))
            self.musteri_table.setItem(row, 3, QTableWidgetItem(mus['ehliyet_no']))
            self.musteri_table.setItem(row, 4, QTableWidgetItem(mus['telefon']))
            self.musteri_table.setItem(row, 5, QTableWidgetItem(mus['email']))

    # ============ KİRALAMA METODLARI ============

    def kir_baslat(self):
        araclar = self.db.araclari_getir()
        musteriler = self.db.musterileri_getir()
        musait_araclar = [a for a in araclar if a['musait_mi']]

        if not musait_araclar:
            QMessageBox.warning(self, "Hata", "Müsait araç bulunamadı!")
            return
        if not musteriler:
            QMessageBox.warning(self, "Hata", "Kayıtlı müşteri bulunamadı!")
            return

        aktif_musteri_ids = [k['musteri_id'] for k in self.db.aktif_kiralamalari_getir()]
        uygun_musteriler = [m for m in musteriler if m['musteri_id'] not in aktif_musteri_ids]

        if not uygun_musteriler:
            QMessageBox.warning(self, "Hata", "Aktif kiralaması olmayan müşteri bulunamadı!")
            return

        dialog = KiralamaBaslatDialog(musait_araclar, uygun_musteriler, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            arac_id, mus_id, fiyat = dialog.result

            musteri_ad = ""
            for m in musteriler:
                if m['musteri_id'] == mus_id:
                    musteri_ad = f"{m['ad']} {m['soyad']}"
                    break

            try:
                self.db.kiralama_ekle(arac_id, mus_id, fiyat)
                QMessageBox.information(self, "Başarılı", f"🔑 {musteri_ad} için kiralama başlatıldı!")
                self.arac_listele()
                self.kir_listele()
            except ValueError as e:
                QMessageBox.warning(self, "Hata", str(e))

    def kir_bitir(self):
        aktif = self.db.aktif_kiralamalari_getir()
        if not aktif:
            QMessageBox.warning(self, "Hata", "Aktif kiralama bulunamadı!")
            return
        dialog = KiralamaBitirDialog(aktif, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            kir_id, yeni_km = dialog.result
            kiralama = next((k for k in aktif if k['kiralama_id'] == kir_id), None)
            if kiralama:
                try:
                    self.db.kiralama_bitir(kir_id, yeni_km)
                    QMessageBox.information(self, "Başarılı", "🔓 Kiralama tamamlandı!")
                    self.arac_listele()
                    self.kir_listele()
                except ValueError as e:
                    QMessageBox.warning(self, "Hata", str(e))

    def kir_listele(self):
        self.kir_table.setRowCount(0)
        for kir in self.db.kiralamalari_getir():
            row = self.kir_table.rowCount()
            self.kir_table.insertRow(row)
            baslangic_km = kir['baslangic_km'] if kir['baslangic_km'] else 0
            bitis_km = kir['bitis_km'] if kir['bitis_km'] else 0
            kullanilan_km = bitis_km - baslangic_km if bitis_km > 0 else 0
            ucret = 0
            if kir['baslangic'] and kir['bitis']:
                baslangic = datetime.fromisoformat(kir['baslangic'].replace(' ', 'T'))
                bitis = datetime.fromisoformat(kir['bitis'].replace(' ', 'T'))
                gun_farki = max(1, (bitis - baslangic).days)
                ucret = gun_farki * kir['gunluk_fiyat']
            elif kir['baslangic'] and not kir['bitis']:
                baslangic = datetime.fromisoformat(kir['baslangic'].replace(' ', 'T'))
                gun_farki = max(1, (datetime.now() - baslangic).days)
                ucret = gun_farki * kir['gunluk_fiyat']
            self.kir_table.setItem(row, 0, QTableWidgetItem(str(kir['kiralama_id'])))
            self.kir_table.setItem(row, 1, QTableWidgetItem(f"{kir['marka']} {kir['model']}"))
            self.kir_table.setItem(row, 2, QTableWidgetItem(f"{kir['ad']} {kir['soyad']}"))
            self.kir_table.setItem(row, 3, QTableWidgetItem(f"{baslangic_km:,}"))
            self.kir_table.setItem(row, 4, QTableWidgetItem(f"{bitis_km:,}" if bitis_km else "-"))
            self.kir_table.setItem(row, 5, QTableWidgetItem(f"{kullanilan_km:,} KM"))
            self.kir_table.setItem(row, 6, QTableWidgetItem(f"{ucret:,.2f}"))
            self.kir_table.setItem(row, 7, QTableWidgetItem(kir['durum']))

    def hediye_et(self):
        musteriler = self.db.musterileri_getir()
        araclar = self.db.araclari_getir()

        if len(musteriler) < 2:
            QMessageBox.warning(self, "Hata", "Hediye göndermek için en az 2 müşteri olmalı!")
            return

        musait_araclar = [a for a in araclar if a['musait_mi']]
        if not musait_araclar:
            QMessageBox.warning(self, "Hata", "Hediye edilecek müsait araç bulunamadı!")
            return

        dialog = HediyeOlusturDialog(musteriler, araclar, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            gonderen_id, alan_id, arac_id, gun_sayisi, not_mesaji = dialog.result

            try:
                hediye_kodu = self.db.hediye_olustur(gonderen_id, alan_id, arac_id, gun_sayisi, not_mesaji)

                msg = QMessageBox(self)
                msg.setWindowTitle("Hediye Oluşturuldu")
                msg.setText(f"🎉 Hediye başarıyla oluşturuldu!\n\n"
                           f"Hediye Kodu: {hediye_kodu}\n\n"
                           f"Bu kodu hediye ettiğiniz kişiyle paylaşın.\n"
                           f"Hediye alan kişi bu kodu 'Hediyeler' sekmesinden kullanabilir.")
                msg.setStyleSheet(MODERN_STYLE)
                msg.exec_()

                self.hediye_listele()
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    def hediye_olustur(self):
        musteriler = self.db.musterileri_getir()
        araclar = self.db.araclari_getir()

        if len(musteriler) < 2:
            QMessageBox.warning(self, "Hata", "Hediye göndermek için en az 2 müşteri olmalı!")
            return

        musait_araclar = [a for a in araclar if a['musait_mi']]
        if not musait_araclar:
            QMessageBox.warning(self, "Hata", "Hediye edilecek müsait araç bulunamadı!")
            return

        dialog = HediyeOlusturDialog(musteriler, araclar, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            gonderen_id, alan_id, arac_id, gun_sayisi, not_mesaji = dialog.result

            try:
                hediye_kodu = self.db.hediye_olustur(gonderen_id, alan_id, arac_id, gun_sayisi, not_mesaji)

                msg = QMessageBox(self)
                msg.setWindowTitle("Hediye Oluşturuldu")
                msg.setText(f"🎉 Hediye başarıyla oluşturuldu!\n\n"
                           f"Hediye Kodu: {hediye_kodu}\n\n"
                           f"Bu kodu hediye ettiğiniz kişiyle paylaşın.\n"
                           f"Hediye alan kişi bu kodu kullanarak kiralamayı başlatabilir.")
                msg.setStyleSheet(MODERN_STYLE)
                msg.exec_()

                self.hediye_listele()
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    def hediye_kullan(self):
        musteriler = self.db.musterileri_getir()

        if not musteriler:
            QMessageBox.warning(self, "Hata", "Kayıtlı müşteri bulunamadı!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Hediye Kullan")
        dialog.setGeometry(200, 200, 400, 300)
        dialog.setStyleSheet(MODERN_STYLE)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Müşteri Seçin:"))

        musteri_combo = QComboBox()
        for mus in musteriler:
            musteri_combo.addItem(f"{mus['ad']} {mus['soyad']} - {mus['telefon']}", mus['musteri_id'])
        layout.addWidget(musteri_combo)

        layout.addWidget(QLabel("Hediye Kodu:"))
        kod_input = QLineEdit()
        kod_input.setPlaceholderText("Hediye kodunu girin")
        kod_input.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(kod_input)

        button_layout = QHBoxLayout()
        kullan_btn = QPushButton("Kullan")
        kullan_btn.setStyleSheet("background-color: #00adb5;")
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet("background-color: #f05454;")
        button_layout.addWidget(kullan_btn)
        button_layout.addWidget(iptal_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def kullan():
            musteri_id = musteri_combo.currentData()
            hediye_kodu = kod_input.text().strip().upper()

            if not hediye_kodu:
                QMessageBox.warning(dialog, "Hata", "Hediye kodunu giriniz!")
                return

            try:
                result = self.db.hediye_kullan(hediye_kodu, musteri_id)
                QMessageBox.information(dialog, "Başarılı",
                    f"🎁 Hediye başarıyla kullanıldı!\n\n"
                    f"Hediye eden: {result['gonderen_ad']} {result['gonderen_soyad']}\n"
                    f"Hediye edilen araç: {result['marka']} {result['model']}\n\n"
                    f"✨ Bu hediye tamamen ücretsizdir! ✨\n"
                    f"Hediyeniz aktifleştirildi! Kiralama işleminiz başlatıldı.")
                dialog.accept()
                self.arac_listele()
                self.kir_listele()
                self.hediye_listele()
            except ValueError as e:
                QMessageBox.warning(dialog, "Hata", str(e))

        kullan_btn.clicked.connect(kullan)
        iptal_btn.clicked.connect(dialog.reject)

        dialog.exec_()

    def hediye_iptal(self):
        row = self.hediye_table.currentRow()
        if row >= 0:
            hediye_id = int(self.hediye_table.item(row, 0).text())
            durum = self.hediye_table.item(row, 6).text()

            if durum != "Beklemede":
                QMessageBox.warning(self, "Hata", "Sadece bekleyen hediyeler iptal edilebilir!")
                return

            if QMessageBox.question(self, "Onay", "Bu hediyeyi iptal etmek istediğinize emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                try:
                    self.db.hediye_iptal(hediye_id)
                    QMessageBox.information(self, "Başarılı", "Hediye iptal edildi!")
                    self.hediye_listele()
                except Exception as e:
                    QMessageBox.warning(self, "Hata", str(e))
        else:
            QMessageBox.warning(self, "Hata", "Lütfen iptal edilecek hediyeyi seçin!")

    def hediye_listele(self):
        self.hediye_table.setRowCount(0)
        for hediye in self.db.hediyeleri_getir():
            row = self.hediye_table.rowCount()
            self.hediye_table.insertRow(row)
            self.hediye_table.setItem(row, 0, QTableWidgetItem(str(hediye['hediye_id'])))
            self.hediye_table.setItem(row, 1, QTableWidgetItem(hediye['hediye_kodu']))
            self.hediye_table.setItem(row, 2, QTableWidgetItem(f"{hediye['gonderen_ad']} {hediye['gonderen_soyad']}"))
            self.hediye_table.setItem(row, 3, QTableWidgetItem(f"{hediye['alan_ad']} {hediye['alan_soyad']}"))
            self.hediye_table.setItem(row, 4, QTableWidgetItem(f"{hediye['marka']} {hediye['model']}"))
            self.hediye_table.setItem(row, 5, QTableWidgetItem("🎁 Hediye"))

            durum_widget = QTableWidgetItem(hediye['durum'])
            if hediye['durum'] == 'Kullanıldı':
                durum_widget.setForeground(QColor("#4ecca3"))
            elif hediye['durum'] == 'İptal Edildi':
                durum_widget.setForeground(QColor("#f05454"))
            else:
                durum_widget.setForeground(QColor("#f5a623"))
            self.hediye_table.setItem(row, 6, durum_widget)

    # ============ SİSTEM KULLANICI METODLARI ============

    def sistem_kullanici_ekle(self):
        try:
            dialog = SistemKullaniciDialog(self)
            if dialog.exec_() == QDialog.Accepted and dialog.result:
                self.db.kullanici_ekle(*dialog.result)
                QMessageBox.information(self, "Başarılı", "👤 Sistem kullanıcısı eklendi!")
                self.sistem_kullanici_listele()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten var!")

    def sistem_kullanici_sil(self):
        row = self.kullanici_table.currentRow()
        if row >= 0:
            kullanici_id = int(self.kullanici_table.item(row, 0).text())
            kullanici_adi = self.kullanici_table.item(row, 1).text()

            if kullanici_adi == "admin":
                QMessageBox.warning(self, "Hata", "Admin kullanıcısı silinemez!")
                return
            if kullanici_adi == self.kullanici['kullanici_adi']:
                QMessageBox.warning(self, "Hata", "Kendi hesabınızı silemezsiniz!")
                return

            if QMessageBox.question(self, "Onay", f"{kullanici_adi} kullanıcısı silinsin mi?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.db.kullanici_sil(kullanici_id)
                QMessageBox.information(self, "Başarılı", "Kullanıcı silindi!")
                self.sistem_kullanici_listele()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen silinecek kullanıcıyı seçin!")

    def sistem_kullanici_listele(self):
        self.kullanici_table.setRowCount(0)
        for k in self.db.kullanicilari_getir():
            row = self.kullanici_table.rowCount()
            self.kullanici_table.insertRow(row)
            self.kullanici_table.setItem(row, 0, QTableWidgetItem(str(k['kullanici_id'])))
            self.kullanici_table.setItem(row, 1, QTableWidgetItem(k['kullanici_adi']))
            self.kullanici_table.setItem(row, 2, QTableWidgetItem(k['ad']))
            self.kullanici_table.setItem(row, 3, QTableWidgetItem(k['soyad']))
            self.kullanici_table.setItem(row, 4, QTableWidgetItem(k['rol']))
            durum_widget = QTableWidgetItem(k['durum'])
            if k['durum'] == 'Aktif':
                durum_widget.setForeground(QColor("#4ecca3"))
            else:
                durum_widget.setForeground(QColor("#f05454"))
            self.kullanici_table.setItem(row, 5, durum_widget)

    # ============ RAPOR METODLARI ============

    def rapor_olustur(self):
        araclar = self.db.araclari_getir()
        musteriler = self.db.musterileri_getir()
        kiralamalar = self.db.kiralamalari_getir()
        hediyeler = self.db.hediyeleri_getir()
        sistem_kullanicilar = self.db.kullanicilari_getir()
        aktif_kiralama = self.db.aktif_kiralama_sayisi()

        rapor = "╔" + "═"*68 + "╗\n"
        rapor += "║" + " " * 12 + "PREMIUM ARAÇ KİRALAMA SİSTEMİ RAPORU" + " " * 12 + "║\n"
        rapor += "╚" + "═"*68 + "╝\n\n"

        rapor += "┌" + "─"*40 + "┐\n"
        rapor += "│ " + " " * 10 + "📊 GENEL İSTATİSTİKLER" + " " * 17 + "│\n"
        rapor += "├" + "─"*40 + "┤\n"
        rapor += f"│ Toplam Araç Sayısı        : {len(araclar):>15} │\n"
        rapor += f"│ Müsait Araç Sayısı        : {sum(1 for a in araclar if a['musait_mi']):>15} │\n"
        rapor += f"│ Kiradaki Araç Sayısı       : {aktif_kiralama:>15} │\n"
        rapor += f"│ Toplam Müşteri Sayısı      : {len(musteriler):>15} │\n"
        rapor += f"│ Toplam Kiralama Sayısı     : {len(kiralamalar):>15} │\n"
        rapor += f"│ Tamamlanan Kiralama Sayısı : {len([k for k in kiralamalar if k['durum'] == 'Tamamlandı']):>15} │\n"
        rapor += f"│ Toplam Hediye Sayısı       : {len(hediyeler):>15} │\n"
        rapor += f"│ Kullanılan Hediye Sayısı   : {len([h for h in hediyeler if h['durum'] == 'Kullanıldı']):>15} │\n"
        rapor += f"│ Sistem Kullanıcı Sayısı    : {len(sistem_kullanicilar):>15} │\n"
        rapor += "└" + "─"*40 + "┘\n\n"

        toplam_ciro = self.db.toplam_ciro_getir()
        rapor += "┌" + "─"*40 + "┐\n"
        rapor += "│ " + " " * 10 + "💰 CİRO RAPORU" + " " * 23 + "│\n"
        rapor += "├" + "─"*40 + "┤\n"
        rapor += f"│ Toplam Ciro                : {toplam_ciro:>15,.2f} TL │\n"
        rapor += "└" + "─"*40 + "┘\n\n"

        rapor += "┌" + "─"*40 + "┐\n"
        rapor += "│ " + " " * 10 + "🚗 ARAÇ LİSTESİ" + " " * 22 + "│\n"
        rapor += "├" + "─"*40 + "┤\n"
        for arac in araclar[:10]:
            durum = "✅ Müsait" if arac['musait_mi'] else "❌ Kirada"
            rapor += f"│ {arac['arac_id']:3}. {arac['marka']:10} {arac['model']:12} {durum:>11} │\n"
        if len(araclar) > 10:
            rapor += f"│ ... ve {len(araclar)-10} araç daha                           │\n"
        rapor += "└" + "─"*40 + "┘\n"

        self.rapor_text.setText(rapor)

    def refresh_all(self):
        araclar = self.db.araclari_getir()
        musteriler = self.db.musterileri_getir()
        aktif_kiralama = self.db.aktif_kiralama_sayisi()

        self.arac_label.setText(str(len(araclar)))
        self.musteri_label.setText(str(len(musteriler)))
        self.kir_label.setText(str(aktif_kiralama))
        self.ciro_label.setText(f"{self.db.toplam_ciro_getir():,.2f} TL")
        self.stats_widget.update_charts()


# ============ MAIN ============

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    db = DatabaseManager()

    login = LoginDialog(db)
    if login.exec_() == QDialog.Accepted:
        kullanici = login.kullanici
        window = AracKiralamaMainWindow(kullanici, db)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
