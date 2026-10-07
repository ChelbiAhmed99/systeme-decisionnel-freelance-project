from __future__ import annotations

import html
import json
import os
import re
import sys
import traceback
from pathlib import Path

# Configuration minimale de l'environnement avant le chargement des bibliothèques
# graphiques et de l'interface Qt.
os.environ.setdefault("QT_API", "pyqt6")  # pour matplotlib

import numpy as np
import pandas as pd

import indicateurs as ind
from moteur_reco import RecommenderEngine, selfcheck

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))           # ressources embarquées
APP_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

# Mode de contrôle utilisé par l'installeur ou le notebook, sans démarrer l'interface.
if __name__ == "__main__" and "--selfcheck" in sys.argv:  # avant l'import de PyQt : fonctionne sans interface
    _ok, _msg = selfcheck(APP_DIR)
    print(("OK  " if _ok else "ÉCART  ") + _msg)
    sys.exit(0 if _ok else 1)

# =========================================================================== INTERFACE (PyQt6)
# Imports Qt, matplotlib et WebEngine. WebEngine reste optionnel afin de permettre
# l'utilisation de l'application même lorsque les rapports intégrés ne sont pas disponibles.
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.ticker as mtick
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QStandardPaths, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (QBrush, QColor, QDesktopServices, QGuiApplication, QIcon, QKeySequence, QPalette, QPixmap,
                         QShortcut)
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QButtonGroup, QComboBox, QCompleter, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSpinBox,
    QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem, QTabWidget, QToolButton, QVBoxLayout, QWidget,
)

try:  # le navigateur intégré est optionnel : sans lui, le rapport s'ouvre dans le navigateur système
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

CONFIG_PATH = APP_DIR / "config.json"
LOGO_PATH = next((p for p in [APP_DIR / "assets" / "logo.png", BASE_DIR / "assets" / "logo.png"] if p.exists()), None)
APP_NAME = "TravelBI"
APP_TAGLINE = "Système décisionnel de l'agence de voyage"
VERSION = "2.0.0"

# ============================================================================ thème
# Palette et feuille de style communes à toutes les pages de l'application.
NAVY = "#16324F"          # couleur d'en-tête de la version précédente, reprise pour le bandeau latéral
PRIMARY = "#2A5D8C"
SKY = "#7FA7C9"
CORAL = "#E07A5F"         # accent « soleil couchant » : sélection, étiquettes de section
CORAL_DARK = "#C4613F"
CORAL_SOFT = "#FBEAE4"
SAND = "#F2C14E"
PAGE = "#F4F6FA"
INK = "#16243A"
SLATE = "#5B6B7F"
LINE = "#DDE3EB"
GREEN = "#2E8B57"
RED = "#C0392B"
COMPONENT_COLORS = [PRIMARY, SKY, CORAL, SAND]      # Content-Based, MF, booster, popularité

QSS = f"""
* {{ font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial; font-size: 10pt; color: {INK}; }}
QMainWindow, #content {{ background: {PAGE}; }}
#sidebar {{ background: {NAVY}; }}
#brand {{ color: white; font-size: 20pt; font-weight: 700; }}
#tagline {{ color: #A9BCD0; font-size: 9pt; }}
#logoTile {{ background: white; border-radius: 12px; }}
#navButton {{
    background: transparent; color: #C8D6E5; border: none; border-radius: 9px;
    text-align: left; padding: 11px 16px; font-size: 10.5pt;
}}
#navButton:hover {{ background: rgba(255,255,255,0.08); color: white; }}
#navButton:checked {{ background: {CORAL}; color: white; font-weight: 600; }}
#sidebarFooter {{ color: #8FA6BF; font-size: 8.5pt; }}
#pill {{ background: {CORAL}; color: white; border-radius: 11px; padding: 3px 14px; font-weight: 600; font-size: 9pt; }}
#pageTitle {{ font-size: 19pt; font-weight: 600; color: {NAVY}; }}
#pageSubtitle {{ color: {SLATE}; font-size: 10pt; }}
#card, #panel {{ background: white; border: 1px solid {LINE}; border-radius: 12px; }}
#cardTitle {{ font-weight: 600; font-size: 10.5pt; color: {NAVY}; }}
#kpiTitle {{ color: {SLATE}; font-size: 9pt; }}
#kpiValue {{ font-size: 17pt; font-weight: 600; color: {NAVY}; }}
#kpiSub {{ font-size: 9pt; color: {SLATE}; }}
#kpiSub[tone="up"] {{ color: {GREEN}; font-weight: 600; }}
#kpiSub[tone="down"] {{ color: {RED}; font-weight: 600; }}
#sectionLabel {{ font-weight: 600; color: {CORAL_DARK}; font-size: 10pt; padding-top: 4px; }}
#hint {{ color: {SLATE}; font-size: 9pt; }}
#emptyTitle {{ font-size: 14pt; font-weight: 600; color: {NAVY}; }}
#profileCard {{ background: {PAGE}; border: 1px solid {LINE}; border-radius: 10px; padding: 10px 12px; }}
QPushButton {{ background: white; border: 1px solid {LINE}; border-radius: 8px; padding: 7px 14px; color: {NAVY}; }}
QPushButton:hover {{ border-color: {PRIMARY}; background: #EEF3F9; }}
QPushButton:disabled {{ color: #A7B1BE; background: #F2F4F7; }}
QPushButton#primary {{ background: {PRIMARY}; border: none; color: white; font-weight: 600; padding: 9px 14px; }}
QPushButton#primary:hover {{ background: {NAVY}; }}
QPushButton#danger {{ color: {RED}; }}
QPushButton#segment {{ border-radius: 0; padding: 8px 10px; }}
QPushButton#segment:checked {{ background: {NAVY}; color: white; border-color: {NAVY}; font-weight: 600; }}
QToolButton {{ background: transparent; border: none; border-radius: 6px; padding: 5px 8px; color: {NAVY}; }}
QToolButton:hover {{ background: {CORAL_SOFT}; }}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background: white; border: 1px solid {LINE}; border-radius: 7px; padding: 5px 8px; selection-background-color: {PRIMARY};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{ border: 1px solid {PRIMARY}; }}
QComboBox QAbstractItemView {{ selection-background-color: {CORAL_SOFT}; selection-color: {INK}; }}
QListWidget {{ background: white; border: 1px solid {LINE}; border-radius: 10px; padding: 4px; outline: 0; }}
QListWidget::item {{ padding: 7px 8px; border-radius: 6px; }}
QListWidget::item:selected {{ background: {CORAL_SOFT}; color: {CORAL_DARK}; font-weight: 600; }}
QTabWidget::pane {{ border: 1px solid {LINE}; border-radius: 10px; background: white; top: -1px; }}
QTabBar::tab {{ background: transparent; padding: 8px 16px; color: {SLATE}; border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ color: {NAVY}; border-bottom: 2px solid {CORAL}; font-weight: 600; }}
QTableWidget {{ background: white; border: none; alternate-background-color: #F7F9FC; gridline-color: {LINE}; }}
QHeaderView::section {{ background: #E8EEF5; color: {NAVY}; padding: 6px; border: none; font-weight: 600; }}
QProgressBar {{ border: none; background: transparent; max-height: 3px; }}
QProgressBar::chunk {{ background: {CORAL}; }}
QStatusBar {{ background: white; color: {SLATE}; border-top: 1px solid {LINE}; }}
QScrollArea {{ border: none; background: transparent; }}
QSplitter::handle {{ background: transparent; }}
"""


# ============================================================================ utilitaires
# Fonctions de formatage et composants graphiques réutilisés par les différentes pages.
def fmt_int(x) -> str:
    """Convertit une valeur en entier lisible avec des espaces comme séparateurs."""
    try:
        return f"{float(x):,.0f}".replace(",", " ")
    except (TypeError, ValueError):
        return "—"


def fmt_tnd(x, compact: bool = False) -> str:
    """Formate un montant en dinars tunisiens, éventuellement en notation compacte."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    if compact and abs(x) >= 1e6:
        return f"{x / 1e6:.2f} M TND".replace(".", ",")
    if compact and abs(x) >= 1e3:
        return f"{x / 1e3:.1f} k TND".replace(".", ",")
    return f"{fmt_int(x)} TND"


def fmt_delta(v, unit: str = "%") -> tuple[str, str]:
    """Retourne le texte d'évolution et le ton visuel correspondant."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "", "neutral"
    tone = "neutral" if abs(v) < 0.05 else ("up" if v > 0 else "down")
    return f"{v:+.1f} {unit} vs année précédente".replace(".", ","), tone


def pill(text: str) -> QLabel:
    """Crée une étiquette colorée utilisée dans les en-têtes de page."""
    lb = QLabel(text)
    lb.setObjectName("pill")
    lb.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lb


class PageHeader(QWidget):
    """En-tête réutilisable composé d'une étiquette, d'un titre et d'un sous-titre."""

    def __init__(self, tag: str, title: str, subtitle: str = ""):
        """Construit l'en-tête de la page."""
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 6)
        lay.setSpacing(4)
        lay.addWidget(pill(tag))
        t = QLabel(title)
        t.setObjectName("pageTitle")
        lay.addWidget(t)
        self.sub = QLabel(subtitle)
        self.sub.setObjectName("pageSubtitle")
        self.sub.setWordWrap(True)
        lay.addWidget(self.sub)


class KpiTile(QFrame):
    """Tuile affichant la valeur d'un indicateur et son évolution."""

    def __init__(self, title: str):
        """Construit une tuile KPI avec un titre et des valeurs initiales vides."""
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 13, 16, 13)
        lay.setSpacing(2)
        self.t = QLabel(title)
        self.t.setObjectName("kpiTitle")
        self.v = QLabel("—")
        self.v.setObjectName("kpiValue")
        self.v.setWordWrap(True)
        self.s = QLabel("")
        self.s.setObjectName("kpiSub")
        self.s.setWordWrap(True)
        for w in (self.t, self.v, self.s):
            lay.addWidget(w)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set(self, value: str, sub: str = "", tone: str = "neutral"):
        """Met à jour la valeur, le sous-texte et la couleur de la tuile."""
        self.v.setText(value)
        self.s.setText(sub)
        self.s.setProperty("tone", tone)
        self.s.style().unpolish(self.s)
        self.s.style().polish(self.s)


def card(title: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    """Crée un panneau blanc réutilisable et retourne son widget et son layout."""
    f = QFrame()
    f.setObjectName("card")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(16, 12, 16, 12)
    if title:
        t = QLabel(title)
        t.setObjectName("cardTitle")
        lay.addWidget(t)
    return f, lay


def empty_state(title: str, text: str = "", button: QPushButton | None = None) -> tuple[QWidget, QLabel]:
    """Crée une vue centrée pour signaler l'absence de données."""
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    t = QLabel(title)
    t.setObjectName("emptyTitle")
    t.setAlignment(Qt.AlignmentFlag.AlignCenter)
    s = QLabel(text)
    s.setObjectName("pageSubtitle")
    s.setAlignment(Qt.AlignmentFlag.AlignCenter)
    s.setWordWrap(True)
    s.setMaximumWidth(640)
    lay.addWidget(t)
    lay.addWidget(s, alignment=Qt.AlignmentFlag.AlignCenter)
    if button:
        lay.addSpacing(10)
        lay.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
    return w, s


def make_table(columns=None) -> QTableWidget:
    """Crée un tableau configuré pour sélectionner des lignes sans les modifier."""
    t = QTableWidget(0, len(columns or []))
    if columns:
        t.setHorizontalHeaderLabels(columns)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setAlternatingRowColors(True)
    t.setWordWrap(True)
    t.verticalHeader().setVisible(False)
    return t


def table_item(value, center: bool = False, right: bool = False) -> QTableWidgetItem:
    """Transforme une valeur en cellule de tableau avec l'alignement demandé."""
    item = QTableWidgetItem(str(value))
    if center:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    elif right:
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    return item


class Chart(FigureCanvas):
    """Canvas matplotlib partagé par les graphiques du tableau de bord et des modèles."""

    MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

    def __init__(self, height: float = 3.0):
        """Initialise un canvas matplotlib intégré dans un widget Qt."""
        self.fig = Figure(figsize=(6, height), dpi=100, facecolor="white")
        super().__init__(self.fig)
        self.setMinimumHeight(int(height * 72))

    def _ax(self):
        """Prépare un axe vide avec le style graphique de l'application."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(LINE)
        ax.tick_params(colors=SLATE, labelsize=8)
        ax.set_axisbelow(True)
        return ax

    def _done(self):
        """Ajuste la mise en page puis redessine le graphique."""
        self.fig.tight_layout()
        self.draw_idle()

    def message(self, text: str):
        """Affiche un message lorsqu'un graphique ne contient aucune donnée."""
        ax = self._ax()
        ax.axis("off")
        ax.text(0.5, 0.5, text, ha="center", va="center", color=SLATE, fontsize=10, transform=ax.transAxes)
        self._done()

    @staticmethod
    def _money_axis(axis):
        """Formate l'axe des montants en milliers ou en millions."""
        axis.set_major_formatter(mtick.FuncFormatter(
            lambda v, _: f"{v / 1e6:.1f} M" if abs(v) >= 1e6 else f"{v / 1e3:.0f} k"))

    def monthly(self, s: pd.Series):
        """Dessine l'évolution mensuelle d'une série de chiffre d'affaires."""
        if s.empty:
            return self.message("Aucune réservation confirmée")
        ax = self._ax()
        x = np.arange(len(s))
        ax.fill_between(x, s.values, color=SKY, alpha=0.25, lw=0)
        ax.plot(x, s.values, color=PRIMARY, lw=2.2, marker="o", ms=3.5)
        imax = int(np.argmax(s.values))
        ax.plot(x[imax], s.values[imax], "o", color=CORAL, ms=7)
        ax.annotate(f"{s.values[imax] / 1e3:,.0f} k".replace(",", " "), (x[imax], s.values[imax]),
                    textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8, color=CORAL_DARK)
        step = 1 if len(s) <= 12 else 2
        ax.set_xticks(x[::step])
        ax.set_xticklabels([f"{self.MOIS[p.month - 1]}\n{str(p.year)[2:]}" for p in s.index[::step]], fontsize=7.5)
        self._money_axis(ax.yaxis)
        ax.grid(axis="y", color=LINE, lw=0.8)
        ax.set_ylim(bottom=0)
        self._done()

    def ranking(self, s: pd.Series, color: str = PRIMARY, labels: list[str] | None = None):
        """Dessine un classement horizontal à partir d'une série de valeurs."""
        if s.empty:
            return self.message("Aucune donnée")
        ax = self._ax()
        s = s.iloc[::-1]
        names = [n if len(n) <= 24 else n[:23] + "…" for n in map(str, s.index)]
        cols = [CORAL if i == len(s) - 1 else color for i in range(len(s))]
        bars = ax.barh(names, s.values, color=cols, height=0.62)
        lab = labels[::-1] if labels else [f"  {v / 1e3:,.0f} k".replace(",", " ") for v in s.values]
        for b, t in zip(bars, lab):
            ax.text(b.get_width(), b.get_y() + b.get_height() / 2, t, va="center", fontsize=8, color=SLATE)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_xlim(0, s.max() * 1.35 if s.max() > 0 else 1)
        ax.tick_params(axis="y", labelsize=8.5, colors=INK, length=0)
        self._done()


# ============================================================================ 1. Tableau de bord
# Présente les KPI commerciaux et les graphiques calculés à partir des réservations.
class DashboardPage(QWidget):
    """Page présentant les KPI et les analyses graphiques des réservations."""

    def __init__(self):
        """Construit la page du tableau de bord et connecte ses contrôles."""
        super().__init__()
        self.fact = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 18)
        root.setSpacing(12)
        top = QHBoxLayout()
        self.header = PageHeader("Tableau de bord", "Activité de l'agence",
                                 "Chiffre d'affaires des réservations confirmées ; taux d'annulation sur toutes les réservations.")
        top.addWidget(self.header, 1)
        box = QVBoxLayout()
        box.addStretch(1)
        lbl = QLabel("Période")
        lbl.setObjectName("hint")
        self.year = QComboBox()
        self.year.setMinimumWidth(170)
        box.addWidget(lbl)
        box.addWidget(self.year)
        top.addLayout(box)
        root.addLayout(top)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(12)
        grid = QGridLayout()
        grid.setSpacing(12)
        self.tiles = {}
        for i, (k, t) in enumerate([("ca", "Chiffre d'affaires"), ("reservations", "Réservations"),
                                    ("panier_moyen", "Panier moyen"), ("taux_annulation", "Taux d'annulation"),
                                    ("satisfaction", "Satisfaction moyenne"), ("clients_actifs", "Clients actifs")]):
            self.tiles[k] = KpiTile(t)
            grid.addWidget(self.tiles[k], 0, i)
        cl.addLayout(grid)

        c1, l1 = card("Chiffre d'affaires mensuel")
        self.ch_month = Chart(2.5)
        l1.addWidget(self.ch_month)
        cl.addWidget(c1, 5)
        row = QHBoxLayout()
        row.setSpacing(12)
        c2, l2 = card("Destinations les plus rentables")
        self.ch_dest = Chart(2.7)
        l2.addWidget(self.ch_dest)
        c3, l3 = card("Canaux de vente (CA et taux d'annulation)")
        self.ch_canal = Chart(2.7)
        l3.addWidget(self.ch_canal)
        c4, l4 = card("Chiffre d'affaires par type de voyage")
        self.ch_type = Chart(2.7)
        l4.addWidget(self.ch_type)
        row.addWidget(c2, 1)
        row.addWidget(c3, 1)
        row.addWidget(c4, 1)
        cl.addLayout(row, 6)
        self.stack.addWidget(content)
        self.empty, self.empty_msg = empty_state("Données du tableau de bord indisponibles")
        self.stack.addWidget(self.empty)
        self.year.currentIndexChanged.connect(self.refresh)
        self.reload()

    def reload(self):
        """Recharge les données de réservation et la liste des années disponibles."""
        try:
            self.fact = ind.charger(APP_DIR)
        except Exception as exc:  # noqa: BLE001
            self.fact = None
            self.empty_msg.setText(f"{exc}\nLe tableau de bord Power BI reste accessible dans la section Rapports.")
            self.stack.setCurrentIndex(1)
            self.year.setEnabled(False)
            return
        years = ind.annees(self.fact)
        self.year.blockSignals(True)
        self.year.clear()
        self.year.addItem("Toutes les années", None)
        for y in reversed(years):
            self.year.addItem(str(y), y)
        self.year.setCurrentIndex(1 if years else 0)
        self.year.blockSignals(False)
        self.year.setEnabled(True)
        self.stack.setCurrentIndex(0)
        self.refresh()

    def refresh(self, *_):
        """Recalcule les KPI et les graphiques pour la période sélectionnée."""
        if self.fact is None:
            return
        y = self.year.currentData()
        k = ind.kpis(self.fact, y)
        v = k["variation"]
        self.tiles["ca"].set(fmt_tnd(k["ca"], compact=True), *fmt_delta(v.get("ca")))
        self.tiles["reservations"].set(fmt_int(k["reservations"]), *fmt_delta(v.get("reservations")))
        self.tiles["panier_moyen"].set(fmt_tnd(k["panier_moyen"]), *fmt_delta(v.get("panier_moyen")))
        txt, tone = fmt_delta(v.get("taux_annulation"), "pt")
        tone = {"up": "down", "down": "up"}.get(tone, tone)          # une hausse des annulations est négative
        self.tiles["taux_annulation"].set(f"{k['taux_annulation']:.1f} %".replace(".", ","), txt, tone)
        self.tiles["satisfaction"].set(f"{k['satisfaction']:.2f} / 5".replace(".", ","),
                                       *fmt_delta(v.get("satisfaction"), "pt"))
        self.tiles["clients_actifs"].set(fmt_int(k["clients_actifs"]), *fmt_delta(v.get("clients_actifs")))
        periode = "sur l'ensemble de l'historique (24 derniers mois affichés)" if y is None else f"en {y}"
        self.header.sub.setText(f"Réservations {periode}. Chiffre d'affaires des réservations confirmées ; "
                                "taux d'annulation calculé sur toutes les réservations.")
        self.ch_month.monthly(ind.ca_mensuel(self.fact, y))
        self.ch_dest.ranking(ind.top_destinations(self.fact, y, 7))
        canal = ind.par_canal(self.fact, y)
        self.ch_canal.ranking(canal["ca"], SKY, [f"  {fmt_int(c / 1e3)} k, annulations {t:.0f} %"
                                                 for c, t in zip(canal["ca"], canal["taux_annulation"])])
        self.ch_type.ranking(ind.par_type(self.fact, y), PRIMARY)


# ============================================================================ 2. Rapports Power BI
# Gère les liens Power BI enregistrés, leur validation et leur affichage intégré.
PBI_HOSTS = ("powerbi.com", "powerbi.microsoft.com", "fabric.microsoft.com", "powerbigov.us")


def normalize_pbi_url(text: str) -> str:
    """Nettoie une URL Power BI ou extrait l'URL d'un code iframe."""
    text = (text or "").strip()
    m = re.search(r"""src\s*=\s*["']([^"']+)["']""", text, flags=re.I)
    if m:
        text = m.group(1)
    text = html.unescape(text).strip()
    if text and not re.match(r"^https?://", text, flags=re.I):
        text = "https://" + text
    if "/reportEmbed" in text and "autoAuth" not in text:
        text += ("&" if "?" in text else "?") + "autoAuth=true"
    return text


def is_pbi_url(url: str) -> bool:
    """Vérifie que l'hôte de l'URL appartient à la liste des domaines Power BI."""
    host = QUrl(url).host().lower()
    return any(host == h or host.endswith("." + h) for h in PBI_HOSTS)


def link_kind(url: str) -> str:
    """Décrit le type de lien Power BI afin de l'afficher à l'utilisateur."""
    if "/view?r=" in url:
        return "Publier sur le web (public, sans connexion)"
    if "/reportEmbed" in url:
        return "Incorporation sécurisée (connexion Microsoft requise)"
    if "/groups/" in url or "/reports/" in url:
        return "Lien Power BI Service (connexion Microsoft requise)"
    return "Lien personnalisé"


class ReportStore:
    """Liste des rapports dans config.json. Reprend automatiquement l'ancienne clé « powerbi_url »."""

    def __init__(self, path: Path):
        """Charge les rapports depuis le fichier de configuration et migre l'ancien format."""
        self.path = path
        self.cfg: dict = {}
        try:
            self.cfg = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.cfg = {}
        self.reports = [r for r in self.cfg.get("reports", []) if r.get("url")]
        legacy = (self.cfg.get("powerbi_url") or "").strip()
        if legacy and not any(r["url"] == normalize_pbi_url(legacy) for r in self.reports):
            self.reports.insert(0, {"name": "Tableau de bord TravelBI", "url": normalize_pbi_url(legacy), "description": ""})
            self.save()

    def save(self):
        """Enregistre la liste actuelle des rapports dans config.json."""
        self.cfg["reports"] = self.reports
        self.cfg.pop("powerbi_url", None)
        try:
            self.path.write_text(json.dumps(self.cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass


class ReportDialog(QDialog):
    def __init__(self, parent=None, report: dict | None = None):
        """Construit la boîte de dialogue d'ajout ou de modification d'un rapport."""
        super().__init__(parent)
        self.setWindowTitle("Modifier le rapport" if report else "Ajouter un rapport Power BI")
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)
        self.name = QLineEdit((report or {}).get("name", ""))
        self.name.setPlaceholderText("Ex. Ventes et réservations, vue direction")
        self.url = QPlainTextEdit((report or {}).get("url", ""))
        self.url.setPlaceholderText("Collez le lien du rapport ou le code <iframe> fourni par Power BI Service")
        self.url.setFixedHeight(90)
        self.desc = QLineEdit((report or {}).get("description", ""))
        self.desc.setPlaceholderText("Facultatif")
        form.addRow("Nom", self.name)
        form.addRow("Lien", self.url)
        form.addRow("Description", self.desc)
        lay.addLayout(form)
        hint = QLabel(
            "Où trouver le lien dans Power BI Service : ouvrez le rapport, puis Fichier › Intégrer le rapport.\n"
            "« Site web ou portail » : lien sécurisé, chaque utilisateur se connecte avec son compte Microsoft.\n"
            "« Publier sur le web (public) » : lien sans connexion, visible par toute personne qui l'a.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        bb.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        bb.button(QDialogButtonBox.StandardButton.Save).setObjectName("primary")
        bb.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        bb.accepted.connect(self._validate)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def _validate(self):
        """Valide les champs saisis et prépare le rapport à enregistrer."""
        url = normalize_pbi_url(self.url.toPlainText())
        if not self.name.text().strip():
            QMessageBox.warning(self, "Nom manquant", "Donnez un nom au rapport pour le retrouver dans la liste.")
            return
        if not QUrl(url).isValid() or not QUrl(url).host():
            QMessageBox.warning(self, "Lien invalide", "Le lien n'est pas une adresse web valide.")
            return
        if not is_pbi_url(url):
            r = QMessageBox.question(self, "Lien hors Power BI",
                                     "Ce lien ne pointe pas vers app.powerbi.com. L'enregistrer quand même ?")
            if r != QMessageBox.StandardButton.Yes:
                return
        self.result_report = {"name": self.name.text().strip(), "url": url, "description": self.desc.text().strip()}
        self.accept()


if HAS_WEBENGINE:
    class PbiPage(QWebEnginePage):
        """Ouvre les fenêtres de connexion Microsoft dans une fenêtre dédiée partageant la session."""

        def __init__(self, profile, parent=None):
            """Crée une page WebEngine partageant le profil de connexion Power BI."""
            super().__init__(profile, parent)
            self._popups = []

        def createWindow(self, _type):
            """Ouvre une nouvelle fenêtre WebEngine pour les fenêtres secondaires."""
            par = self.parent()
            dlg = PopupWindow(self.profile(), par.window() if isinstance(par, QWidget) else None)
            self._popups.append(dlg)
            dlg.finished.connect(lambda *_: self._popups.remove(dlg) if dlg in self._popups else None)
            dlg.show()
            return dlg.view.page()

    class PopupWindow(QDialog):
        def __init__(self, profile, parent=None):
            """Crée une fenêtre dédiée aux connexions Microsoft ouvertes par Power BI."""
            super().__init__(parent)
            self.setWindowTitle("Connexion Microsoft")
            self.resize(520, 680)
            lay = QVBoxLayout(self)
            lay.setContentsMargins(0, 0, 0, 0)
            self.view = QWebEngineView(self)
            page = PbiPage(profile, self.view)
            self.view.setPage(page)
            page.windowCloseRequested.connect(self.close)
            lay.addWidget(self.view)


ERROR_HTML = f"""<html><body style="font-family:Segoe UI,Arial;background:{PAGE};color:{NAVY};padding:48px 64px">
<h2>Le rapport ne s'est pas chargé</h2>
<p>Vérifiez la connexion Internet et le lien du rapport, puis cliquez sur Actualiser.<br>
Si le rapport est en accès sécurisé, connectez-vous avec votre compte Microsoft dans cette fenêtre.</p></body></html>"""


class ReportsPage(QWidget):
    """Page de gestion et d'affichage des rapports Power BI."""

    presentationRequested = pyqtSignal(bool)

    def __init__(self, store: ReportStore):
        """Construit la liste des rapports et la zone de visualisation."""
        super().__init__()
        self.store = store
        self.presenting = False
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 18)
        root.setSpacing(12)
        self.header = PageHeader("Rapports", "Rapports Power BI",
                                 "Rapports publiés sur Power BI Service, affichés ici sans quitter l'application.")
        root.addWidget(self.header)
        self.split = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(self.split, 1)

        left = QFrame()
        left.setObjectName("panel")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        lbl = QLabel("Mes rapports")
        lbl.setObjectName("sectionLabel")
        ll.addWidget(lbl)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._open_current)
        self.list.itemDoubleClicked.connect(lambda *_: self._edit())
        ll.addWidget(self.list, 1)
        self.btn_add = QPushButton("Ajouter un rapport")
        self.btn_add.setObjectName("primary")
        self.btn_add.clicked.connect(self._add)
        row = QHBoxLayout()
        self.btn_edit = QPushButton("Modifier")
        self.btn_edit.clicked.connect(self._edit)
        self.btn_del = QPushButton("Supprimer")
        self.btn_del.setObjectName("danger")
        self.btn_del.clicked.connect(self._delete)
        row.addWidget(self.btn_edit)
        row.addWidget(self.btn_del)
        ll.addWidget(self.btn_add)
        ll.addLayout(row)
        left.setMinimumWidth(240)
        left.setMaximumWidth(340)
        self.left = left
        self.split.addWidget(left)

        right = QFrame()
        right.setObjectName("panel")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        bar = QHBoxLayout()
        bar.setContentsMargins(10, 6, 10, 6)
        self.title = QLabel("")
        self.title.setStyleSheet(f"font-weight:600; color:{NAVY};")
        self.kind = QLabel("")
        self.kind.setObjectName("hint")
        bar.addWidget(self.title)
        bar.addSpacing(8)
        bar.addWidget(self.kind)
        bar.addStretch(1)
        self.tb = {}
        for key, text, tip in [("back", "‹ Retour", "Page précédente"), ("reload", "Actualiser", "Recharger le rapport (F5)"),
                               ("zoom_out", "−", "Zoom arrière"), ("zoom_in", "+", "Zoom avant"),
                               ("browser", "Ouvrir dans le navigateur", "Ouvrir le rapport dans le navigateur par défaut"),
                               ("present", "Mode présentation", "Plein écran (Échap pour quitter)")]:
            b = QToolButton()
            b.setText(text)
            b.setToolTip(tip)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            bar.addWidget(b)
            self.tb[key] = b
        rl.addLayout(bar)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        rl.addWidget(self.progress)

        self.viewer_stack = QStackedWidget()
        rl.addWidget(self.viewer_stack, 1)
        add_btn = QPushButton("Ajouter un rapport")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self._add)
        self.viewer_stack.addWidget(empty_state(
            "Ajoutez votre premier rapport Power BI",
            "Dans Power BI Service, ouvrez le rapport, puis Fichier › Intégrer le rapport ; "
            "copiez le lien (ou le code <iframe> complet) et collez-le ici.", add_btn)[0])
        if HAS_WEBENGINE:
            self._init_web()
            self.viewer_stack.addWidget(self.view)
        else:
            b = QPushButton("Ouvrir dans le navigateur")
            b.setObjectName("primary")
            b.clicked.connect(self._open_browser)
            self.viewer_stack.addWidget(empty_state(
                "L'affichage intégré n'est pas disponible",
                "Le module PyQt6-WebEngine n'est pas installé (pip install PyQt6-WebEngine). "
                "En attendant, le rapport s'ouvre dans votre navigateur.", b)[0])
        self.split.addWidget(right)
        self.split.setStretchFactor(1, 1)
        self.split.setSizes([280, 1000])

        self.tb["browser"].clicked.connect(self._open_browser)
        self.tb["present"].clicked.connect(lambda: self.presentationRequested.emit(not self.presenting))
        QShortcut(QKeySequence("F5"), self).activated.connect(self._reload)
        self._refresh_list()

    def _init_web(self):
        """Initialise le navigateur intégré avec une session Microsoft persistante."""
        data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)) / "webprofile"
        data_dir.mkdir(parents=True, exist_ok=True)
        # profil persistant (session Microsoft conservée) ; parent = QApplication pour une fermeture propre
        self.profile = QWebEngineProfile("travelbi_powerbi", QApplication.instance())
        self.profile.setPersistentStoragePath(str(data_dir))
        self.profile.setCachePath(str(data_dir / "cache"))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpUserAgent(re.sub(r"\s*QtWebEngine/\S+", "", self.profile.httpUserAgent()))
        self.view = QWebEngineView()
        page = PbiPage(self.profile, self.view)
        self.view.setPage(page)
        s = page.settings()
        for attr in (QWebEngineSettings.WebAttribute.FullScreenSupportEnabled,
                     QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,
                     QWebEngineSettings.WebAttribute.LocalStorageEnabled):
            s.setAttribute(attr, True)
        page.fullScreenRequested.connect(self._on_fullscreen_request)
        self.view.loadProgress.connect(self.progress.setValue)
        self.view.loadFinished.connect(self._on_finished)
        self.tb["back"].clicked.connect(self.view.back)
        self.tb["reload"].clicked.connect(self._reload)
        self.tb["zoom_in"].clicked.connect(lambda: self.view.setZoomFactor(min(3.0, self.view.zoomFactor() + 0.1)))
        self.tb["zoom_out"].clicked.connect(lambda: self.view.setZoomFactor(max(0.4, self.view.zoomFactor() - 0.1)))

    def _on_finished(self, ok: bool):
        """Met à jour la progression et affiche une page d'erreur si le chargement échoue."""
        self.progress.setValue(100 if ok else 0)
        if not ok and self.current():
            self.view.setHtml(ERROR_HTML)

    def _on_fullscreen_request(self, request):
        """Accepte ou quitte le plein écran demandé par le rapport Power BI."""
        request.accept()
        self.presentationRequested.emit(request.toggleOn())

    def shutdown(self):
        """Arrête proprement le navigateur intégré avant la fermeture de l'application."""
        if HAS_WEBENGINE:
            self.view.stop()

    def _refresh_list(self, select: int | None = None):
        """Recharge la liste graphique et active les boutons selon son contenu."""
        self.list.blockSignals(True)
        self.list.clear()
        for r in self.store.reports:
            it = QListWidgetItem(r["name"])
            it.setToolTip(r.get("description") or r["url"])
            self.list.addItem(it)
        self.list.blockSignals(False)
        has = bool(self.store.reports)
        self.btn_edit.setEnabled(has)
        self.btn_del.setEnabled(has)
        for b in self.tb.values():
            b.setEnabled(has)
        if has:
            self.list.setCurrentRow(select if select is not None else 0)   # déclenche _open_current
        else:
            self.viewer_stack.setCurrentIndex(0)
            self.title.setText("")
            self.kind.setText("")

    def current(self) -> dict | None:
        """Retourne le dictionnaire du rapport actuellement sélectionné."""
        i = self.list.currentRow()
        return self.store.reports[i] if 0 <= i < len(self.store.reports) else None

    def _open_current(self, _row: int):
        """Affiche le rapport sélectionné dans le navigateur intégré."""
        r = self.current()
        if not r:
            return
        self.title.setText(r["name"])
        self.kind.setText(link_kind(r["url"]))
        self.viewer_stack.setCurrentIndex(1)
        if HAS_WEBENGINE:
            self.progress.setValue(5)
            self.view.setUrl(QUrl(r["url"]))

    def _reload(self):
        """Recharge l'URL du rapport actuellement ouvert."""
        r = self.current()
        if HAS_WEBENGINE and r:
            self.view.setUrl(QUrl(r["url"]))

    def _open_browser(self):
        """Ouvre le rapport actif dans le navigateur par défaut du système."""
        r = self.current()
        if r:
            QDesktopServices.openUrl(QUrl(r["url"]))

    def _add(self):
        """Ajoute un rapport après validation de la boîte de dialogue."""
        dlg = ReportDialog(self)
        if dlg.exec():
            self.store.reports.append(dlg.result_report)
            self.store.save()
            self._refresh_list(len(self.store.reports) - 1)

    def _edit(self):
        """Modifie le rapport sélectionné puis sauvegarde la nouvelle version."""
        i = self.list.currentRow()
        if i < 0:
            return
        dlg = ReportDialog(self, self.store.reports[i])
        if dlg.exec():
            self.store.reports[i] = dlg.result_report
            self.store.save()
            self._refresh_list(i)

    def _delete(self):
        """Supprime le rapport sélectionné après confirmation de l'utilisateur."""
        r = self.current()
        if not r:
            return
        if QMessageBox.question(self, "Supprimer le rapport",
                                f"Retirer « {r['name']} » de la liste ?\nLe rapport reste disponible dans Power BI Service."
                                ) == QMessageBox.StandardButton.Yes:
            self.store.reports.pop(self.list.currentRow())
            self.store.save()
            self._refresh_list()

    def set_presentation(self, on: bool):
        """Masque ou affiche les panneaux de navigation en mode présentation."""
        self.presenting = on
        self.header.setVisible(not on)
        self.left.setVisible(not on)
        self.tb["present"].setText("Quitter la présentation" if on else "Mode présentation")


# ============================================================================ 3. Recommandations
# Permet de générer et d'exporter des recommandations pour un client existant
# ou à partir du profil d'un nouveau client.
class RecoPage(QWidget):
    """Page permettant de produire et d'exporter des recommandations de destinations."""

    RESULT_COLUMNS = ["Rang", "Destination", "Type", "Continent", "Budget moyen", "Score / 5",
                      "Pourquoi cette recommandation ?"]

    def __init__(self):
        """Construit les panneaux de saisie et de résultats de recommandation."""
        super().__init__()
        self.engine: RecommenderEngine | None = None
        self.result_df = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 18)
        root.setSpacing(12)
        self.header = PageHeader("Recommandations", "Recommandation de destinations",
                                 "Modèle hybride du notebook : similarité de profil, filtrage collaboratif, "
                                 "booster supervisé et popularité.")
        root.addWidget(self.header)
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        body = QWidget()
        bl = QHBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(14)
        bl.addWidget(self._build_left())
        bl.addLayout(self._build_right(), 1)
        self.stack.addWidget(body)
        self.empty, self.empty_msg = empty_state("Le modèle de recommandation n'est pas chargé")
        self.stack.addWidget(self.empty)

    # ---- panneau de gauche : paramètres du profil et de la génération
    def _build_left(self) -> QWidget:
        """Construit les contrôles de sélection du client et de génération."""
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(360)
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        seg = QHBoxLayout()
        seg.setSpacing(0)
        self.mode_group = QButtonGroup(self)
        for i, t in enumerate(["Client existant", "Nouveau client"]):
            b = QPushButton(t)
            b.setObjectName("segment")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.mode_group.addButton(b, i)
            seg.addWidget(b)
        self.mode_group.button(0).setChecked(True)
        self.mode_group.button(0).setStyleSheet("border-top-left-radius:8px; border-bottom-left-radius:8px;")
        self.mode_group.button(1).setStyleSheet("border-top-right-radius:8px; border-bottom-right-radius:8px;")
        lay.addLayout(seg)

        self.mode_stack = QStackedWidget()
        self.mode_group.idClicked.connect(self._on_mode)
        lay.addWidget(self.mode_stack)

        # page 0 : client existant
        p0 = QWidget()
        l0 = QVBoxLayout(p0)
        l0.setContentsMargins(0, 6, 0, 0)
        l0.setSpacing(8)
        lab = QLabel("Client")
        lab.setObjectName("sectionLabel")
        l0.addWidget(lab)
        self.client_combo = QComboBox()
        self.client_combo.setEditable(True)
        self.client_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.client_combo.lineEdit().setPlaceholderText("Nom, identifiant ou segment…")
        self.client_combo.currentIndexChanged.connect(self._on_client_changed)
        self.client_combo.lineEdit().editingFinished.connect(self._match_client_text)
        l0.addWidget(self.client_combo)
        self.profile_card = QLabel()
        self.profile_card.setObjectName("profileCard")
        self.profile_card.setWordWrap(True)
        self.profile_card.setTextFormat(Qt.TextFormat.RichText)
        l0.addWidget(self.profile_card)
        l0.addStretch(1)
        self.mode_stack.addWidget(p0)

        # page 1 : nouveau client
        p1 = QWidget()
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(0, 6, 0, 0)
        lab = QLabel("Profil du nouveau client")
        lab.setObjectName("sectionLabel")
        l1.addWidget(lab)
        form = QFormLayout()
        form.setVerticalSpacing(8)
        self.age_spin = QSpinBox()
        self.age_spin.setRange(18, 90)
        self.age_spin.setValue(35)
        self.age_spin.setSuffix(" ans")
        self.income_spin = QSpinBox()
        self.income_spin.setRange(0, 50000)
        self.income_spin.setSingleStep(100)
        self.income_spin.setValue(1500)
        self.income_spin.setSuffix(" TND / mois")
        self.type_combo = QComboBox()
        self.budget_spin = QSpinBox()
        self.budget_spin.setRange(300, 40000)
        self.budget_spin.setSingleStep(500)
        self.budget_spin.setValue(4000)
        self.budget_spin.setSuffix(" TND")
        self.acts_list = QListWidget()
        self.acts_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.acts_list.setMinimumHeight(190)
        form.addRow("Âge", self.age_spin)
        form.addRow("Revenu", self.income_spin)
        form.addRow("Type préféré", self.type_combo)
        form.addRow("Budget max.", self.budget_spin)
        l1.addLayout(form)
        lab2 = QLabel("Activités appréciées (plusieurs choix)")
        lab2.setObjectName("hint")
        l1.addWidget(lab2)
        l1.addWidget(self.acts_list)
        note = QLabel("Sans historique, la composante collaborative se limite au biais moyen de la destination ; "
                      "le profil déclaré et la popularité portent la recommandation.")
        note.setWordWrap(True)
        note.setObjectName("hint")
        l1.addWidget(note)
        l1.addStretch(1)
        self.mode_stack.addWidget(p1)

        lay.addStretch(1)
        row = QHBoxLayout()
        lab = QLabel("Nombre de destinations")
        lab.setObjectName("hint")
        self.n_spin = QSpinBox()
        self.n_spin.setRange(1, 15)
        self.n_spin.setValue(5)
        self.n_spin.valueChanged.connect(self._auto_generate)
        row.addWidget(lab)
        row.addStretch(1)
        row.addWidget(self.n_spin)
        lay.addLayout(row)
        self.btn_generate = QPushButton("Générer les recommandations")
        self.btn_generate.setObjectName("primary")
        self.btn_generate.clicked.connect(self.generate)
        lay.addWidget(self.btn_generate)
        self.btn_export = QPushButton("Exporter en CSV")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_csv)
        lay.addWidget(self.btn_export)
        return panel

    # ---- panneau de droite : résultats et décomposition du score
    def _build_right(self) -> QVBoxLayout:
        """Construit le tableau des résultats et le graphique des contributions."""
        lay = QVBoxLayout()
        lay.setSpacing(12)
        self.result_title = QLabel("Choisissez un client : les recommandations s'affichent automatiquement.")
        self.result_title.setStyleSheet(f"font-size:12pt; font-weight:600; color:{NAVY};")
        self.result_title.setWordWrap(True)
        lay.addWidget(self.result_title)
        c1, l1 = card()
        self.table = make_table(self.RESULT_COLUMNS)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(len(self.RESULT_COLUMNS) - 1, QHeaderView.ResizeMode.Stretch)
        l1.addWidget(self.table)
        lay.addWidget(c1, 3)
        c2, l2 = card("Décomposition du score hybride")
        self.canvas = Chart(2.6)
        l2.addWidget(self.canvas)
        lay.addWidget(c2, 2)
        return lay

    # ---- chargement du modèle et gestion des interactions
    def set_engine(self, engine: RecommenderEngine | None, error: str = ""):
        """Charge le moteur et initialise les clients, types et activités disponibles."""
        self.engine = engine
        if engine is None:
            self.empty_msg.setText(error or "Relancez la section 15 du notebook et placez le dossier exporté à côté de app.py.")
            self.stack.setCurrentIndex(1)
            return
        self.client_combo.blockSignals(True)
        self.client_combo.clear()
        for cid in engine.client_ids:
            self.client_combo.addItem(engine.client_label(cid), cid)
        comp = self.client_combo.completer()
        comp.setFilterMode(Qt.MatchFlag.MatchContains)
        comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        comp.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.client_combo.blockSignals(False)
        self.type_combo.clear()
        self.type_combo.addItems(engine.types)
        self.acts_list.clear()
        self.acts_list.addItems(engine.acts)
        w = engine.weights
        self.header.sub.setText(
            f"Modèle hybride du notebook : Content-Based {w[0]:g}, filtrage collaboratif {w[1]:g}, "
            f"{engine.best_booster_name} {w[2]:g}, popularité {w[3]:g}. "
            f"{len(engine.client_ids)} clients, {len(engine.dest_ids)} destinations.")
        self.stack.setCurrentIndex(0)
        self.client_combo.setCurrentIndex(0)
        self._on_client_changed()

    def _on_mode(self, i: int):
        """Change le formulaire entre client existant et nouveau client."""
        self.mode_stack.setCurrentIndex(i)
        self.btn_generate.setText("Générer les recommandations")
        if i == 0:
            self._auto_generate()

    def _match_client_text(self):
        """Sélectionne le premier client correspondant au texte saisi."""
        txt = self.client_combo.lineEdit().text().strip()
        i = self.client_combo.findText(txt, Qt.MatchFlag.MatchContains)
        if i >= 0 and i != self.client_combo.currentIndex():
            self.client_combo.setCurrentIndex(i)

    def _selected_client(self):
        """Retourne l'identifiant du client sélectionné dans la liste."""
        return self.client_combo.currentData()

    def _on_client_changed(self, *_):
        """Actualise le profil et les recommandations après un changement de client."""
        self._update_profile_card()
        self._auto_generate()

    def _auto_generate(self, *_):
        """Génère automatiquement les résultats pour un client existant sélectionné."""
        if self.engine is not None and self.mode_group.checkedId() == 0 and self._selected_client() is not None:
            self.generate()

    def _update_profile_card(self):
        """Affiche les informations et l'historique du client sélectionné."""
        cid = self._selected_client()
        if cid is None or self.engine is None:
            self.profile_card.setText("")
            return
        e = self.engine
        r = e.clients.loc[cid]
        booked = [e.dests.loc[d, "nom_destination"] for d in sorted(e.booked.get(cid, set())) if d in e.dests.index]
        g = lambda k, default="—": r[k] if k in r.index and pd.notna(r[k]) else default  # noqa: E731
        self.profile_card.setText(
            f"<b style='font-size:11pt'>{g('prenom', '')} {g('nom', '')}</b><br>"
            f"{g('age')} ans, {g('ville')}<br>"
            f"Segment : <b>{g('segment_latent')}</b> (cluster {g('segment_client')})<br>"
            f"Type préféré : <b>{g('type_voyage_prefere')}</b>, budget max. <b>{fmt_int(g('budget_max_tnd', 0))} TND</b><br>"
            f"Activités : {str(g('activites_preferees')).replace(';', ', ')}<br>"
            f"{float(g('frequence', 0)):.0f} réservations, {fmt_int(g('montant_total', 0))} TND, "
            f"annulations {float(g('taux_annulation', 0)) * 100:.0f} %<br>"
            f"<span style='color:{SLATE}'>Déjà réservé (exclu) : {', '.join(booked) or 'aucune destination'}</span>")

    def generate(self):
        """Calcule une liste de recommandations pour le profil courant."""
        if self.engine is None:
            return
        n = self.n_spin.value()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if self.mode_group.checkedId() == 0:
                cid = self._selected_client()
                if cid is None:
                    QMessageBox.information(self, "Client", "Sélectionnez un client dans la liste.")
                    return
                df = self.engine.recommend_for_client(cid, n)
                title = f"Top {len(df)} pour {self.engine.client_label(cid)}"
            else:
                acts = [i.text() for i in self.acts_list.selectedItems()]
                if not acts:
                    QMessageBox.information(self, "Activités", "Sélectionnez au moins une activité.")
                    return
                prof = self.engine.new_client_profile(self.age_spin.value(), self.income_spin.value(),
                                                      self.type_combo.currentText(), acts, self.budget_spin.value())
                df = self.engine.recommend_for_profile(prof, n)
                title = f"Top {len(df)} pour un nouveau client ({self.type_combo.currentText()}, " \
                        f"budget {fmt_int(self.budget_spin.value())} TND)"
        except Exception as exc:  # noqa: BLE001 — on affiche l'erreur à l'utilisateur
            QMessageBox.critical(self, "Erreur de recommandation", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        self.result_df = df
        self.result_title.setText(title)
        self._fill_table(df)
        self._draw_chart(df)
        self.btn_export.setEnabled(True)

    def _fill_table(self, df: pd.DataFrame):
        """Remplit le tableau avec les destinations et leurs scores."""
        self.table.setRowCount(len(df))
        for r, (_, row) in enumerate(df.iterrows()):
            values = [row["rang"], row["nom_destination"], row["type_voyage"], row["pays_continent"],
                      f"{fmt_int(row['budget_moyen_tnd'])} TND", f"{row['score']:.2f}".replace(".", ","),
                      row["explication"]]
            for c, v in enumerate(values):
                item = table_item(v, center=c in (0, 5), right=c == 4)
                if c == 5:
                    item.setBackground(QBrush(QColor(224, 122, 95, int(30 + 150 * row["score"] / 5))))
                self.table.setItem(r, c, item)
        self.table.resizeRowsToContents()

    def _draw_chart(self, df: pd.DataFrame):
        """Dessine la contribution de chaque composante du score hybride."""
        w = self.engine.weights
        parts = [("contrib_content", f"Content-Based ({w[0]:g})"),
                 ("contrib_collab", f"Filtrage collaboratif ({w[1]:g})"),
                 ("contrib_booster", f"{self.engine.best_booster_name} ({w[2]:g})"),
                 ("contrib_popularite", f"Popularité ({w[3]:g})")]
        ax = self.canvas._ax()
        names = df["nom_destination"].to_numpy()[::-1]
        left = np.zeros(len(df))
        for (key, label), color in zip(parts, COMPONENT_COLORS):
            vals = df[key].to_numpy(dtype=float)[::-1]
            ax.barh(names, vals, left=left, label=label, color=color, height=0.62)
            left += vals
        for y, tot in enumerate(left):
            ax.text(tot, y, f"  {tot:.2f}".replace(".", ","), va="center", fontsize=8, color=SLATE)
        ax.set_xlim(0, max(left.max() * 1.15, 0.5))
        ax.set_xlabel("Contribution au score (sur 5)", fontsize=8, color=SLATE)
        ax.tick_params(axis="y", labelsize=8.5, colors=INK, length=0)
        ax.legend(fontsize=8, loc="lower right", frameon=False)
        self.canvas._done()

    def export_csv(self):
        """Exporte les recommandations affichées dans un fichier CSV."""
        if self.result_df is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exporter les recommandations", "recommandations.csv", "CSV (*.csv)")
        if path:
            cols = ["rang", "destination_id", "nom_destination", "type_voyage", "pays_continent",
                    "budget_moyen_tnd", "score", "explication"]
            self.result_df[cols].to_csv(path, index=False, encoding="utf-8-sig", sep=";", decimal=",")
            QMessageBox.information(self, "Export terminé", f"Recommandations enregistrées :\n{path}")


# ============================================================================ 4. Performance des modèles
# Compare les métriques produites par le notebook et affiche le modèle retenu.
class ModelsPage(QWidget):
    """Page comparant les performances des modèles de recommandation."""

    def __init__(self):
        """Construit les KPI, le tableau détaillé et les graphiques de comparaison."""
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 18)
        root.setSpacing(12)
        root.addWidget(PageHeader("Modèles", "Performance des modèles",
                                  "Comparaison des approches sur le jeu de test du notebook (Section 11)."))
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(12)
        grid = QGridLayout()
        grid.setSpacing(12)
        self.tiles = [KpiTile(t) for t in ("Meilleur modèle", "Taux de réussite", "NDCG", "Pondération du modèle hybride")]
        for i, t in enumerate(self.tiles):
            grid.addWidget(t, 0, i)
        bl.addLayout(grid)
        split = QHBoxLayout()
        split.setSpacing(12)
        c1, l1 = card("Résultats détaillés")
        self.table = make_table()
        l1.addWidget(self.table)
        split.addWidget(c1, 1)
        c2, l2 = card()
        self.tabs = QTabWidget()
        self.ch_rank = Chart(3.4)
        self.ch_rmse = Chart(3.4)
        self.tabs.addTab(self.ch_rank, "Métriques de classement")
        self.tabs.addTab(self.ch_rmse, "Erreur de score (RMSE)")
        l2.addWidget(self.tabs)
        split.addWidget(c2, 1)
        bl.addLayout(split, 1)
        foot = QLabel("Les métriques de classement (plus haut = meilleur) mesurent la qualité de la liste Top-K, ce qui "
                      "compte pour un recommandeur. Le RMSE (plus bas = meilleur) mesure l'erreur sur le score prédit.")
        foot.setWordWrap(True)
        foot.setObjectName("hint")
        bl.addWidget(foot)
        self.stack.addWidget(body)
        self.empty, self.empty_msg = empty_state("Comparaison des modèles indisponible")
        self.stack.addWidget(self.empty)

    def set_data(self, engine: RecommenderEngine | None):
        """Charge les métriques, identifie le meilleur modèle et actualise la page."""
        path = APP_DIR / "data" / "comparaison_modeles.csv"
        try:
            df = pd.read_csv(path)
        except Exception as exc:  # noqa: BLE001
            self.empty_msg.setText(f"data/comparaison_modeles.csv illisible ou absent.\n{exc}")
            self.stack.setCurrentIndex(1)
            return
        df.columns = ["Modèle"] + [c.strip() for c in df.columns[1:]]
        ndcg = next(c for c in df.columns if c.startswith("NDCG@"))
        hit = next(c for c in df.columns if c.startswith("HitRate@"))
        rank_cols = [c for c in df.columns if c not in ("Modèle", "RMSE")]
        best_idx = int(df[ndcg].idxmax())
        best = df.loc[best_idx]
        k = hit.split("@")[1]

        self.tiles[0].set(str(best["Modèle"]), f"Sélectionné sur le {ndcg} le plus élevé")
        self.tiles[1].set(f"{best[hit] * 100:.1f} %".replace(".", ","),
                          f"Au moins une bonne destination dans le Top-{k} ({hit})")
        second = df[ndcg].drop(best_idx).max() if len(df) > 1 else np.nan
        self.tiles[2].set(f"{best[ndcg]:.3f}".replace(".", ","),
                          f"{(best[ndcg] / second - 1) * 100:+.1f} % vs 2e approche".replace(".", ",")
                          if second and not np.isnan(second) else "", "up")
        if engine is not None:
            w = engine.weights
            self.tiles[3].set(f"{w[0]:g} / {w[1]:g} / {w[2]:g} / {w[3]:g}",
                              f"Content-Based / MF / {engine.best_booster_name} / popularité")
        else:
            self.tiles[3].set("—", "Modèle non chargé")

        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(list(df.columns))
        self.table.setRowCount(len(df))
        for r in range(len(df)):
            for c, col in enumerate(df.columns):
                v = df.iloc[r][col]
                item = table_item(v if col == "Modèle" else f"{v:.4f}", center=col != "Modèle")
                if r == best_idx:
                    item.setBackground(QBrush(QColor(224, 122, 95, 55)))
                    f = item.font()
                    f.setBold(True)
                    item.setFont(f)
                self.table.setItem(r, c, item)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        ax = self.ch_rank._ax()
        x = np.arange(len(df))
        width = 0.8 / len(rank_cols)
        palette = [PRIMARY, SKY, "#9BB7D4", CORAL, SAND]
        for i, col in enumerate(rank_cols):
            ax.bar(x + i * width, df[col], width, label=col, color=palette[i % len(palette)])
        ax.set_xticks(x + width * (len(rank_cols) - 1) / 2)
        ax.set_xticklabels([m.replace("Supervisé ", "").replace("Collaborative Filtering", "Collab.") for m in df["Modèle"]],
                           rotation=20, ha="right", fontsize=8)
        ax.grid(axis="y", color=LINE, lw=0.8)
        ax.legend(fontsize=7.5, frameon=False, ncol=len(rank_cols), loc="upper left")
        self.ch_rank._done()
        if "RMSE" in df.columns:
            s = df.set_index("Modèle")["RMSE"].sort_values(ascending=False)
            self.ch_rmse.ranking(s, SKY, [f"  {v:.3f}" for v in s.values])
        self.stack.setCurrentIndex(0)


# ============================================================================ 5. À propos
# Explique l'architecture de TravelBI et vérifie la présence des fichiers exportés.
class AboutPage(QWidget):
    """Page présentant le système et l'état des fichiers nécessaires à son fonctionnement."""

    reloadRequested = pyqtSignal()
    checkRequested = pyqtSignal()

    FILES = [("models/artifacts_meta.json", "Paramètres du modèle"), ("models/mf_embeddings.npz", "Embeddings MF"),
             ("models/content_vectors.npz", "Vecteurs de contenu"), ("models/client_features_for_app.csv", "Features clients"),
             ("models/destination_features_for_app.csv", "Features destinations"),
             ("data/interactions.csv", "Historique client × destination"),
             ("data/reference_recos.csv", "Recommandations de référence"),
             ("data/comparaison_modeles.csv", "Comparaison des modèles"),
             ("data/fact_reservations.csv", "Réservations (tableau de bord)")]

    def __init__(self):
        """Construit la présentation, la fiche du modèle et le tableau des fichiers."""
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        inner = QWidget()
        inner.setObjectName("content")
        scroll.setWidget(inner)
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 22, 28, 18)
        root.setSpacing(12)
        root.addWidget(PageHeader("À propos", "Le système décisionnel", ""))
        c0, l0 = card()
        txt = QLabel(
            "<b>TravelBI</b> réunit le système décisionnel de l'agence de voyage réalisé dans le cadre du PFE :<br><br>"
            "<b>Un entrepôt en étoile et des KPI</b> (réservations, destinations, clients, canaux) exportés vers "
            "Power BI, et repris ici dans le tableau de bord.<br><br>"
            "<b>Un moteur de recommandation hybride</b> combinant filtrage par contenu, factorisation matricielle "
            "implémentée from scratch, un booster supervisé (LightGBM, XGBoost ou CatBoost, choisi automatiquement) "
            "et la popularité ; les poids sont optimisés sur le NDCG.<br><br>"
            "<b>Cette application</b>, qui recalcule les recommandations localement à partir des artefacts du "
            "notebook, pour un client existant comme pour un nouveau client.")
        txt.setWordWrap(True)
        txt.setTextFormat(Qt.TextFormat.RichText)
        txt.setMaximumWidth(900)
        l0.addWidget(txt)
        root.addWidget(c0)

        mid = QHBoxLayout()
        mid.setSpacing(12)
        c1, l1 = card("Fiche du modèle")
        self.form = QFormLayout()
        self.form.setVerticalSpacing(8)
        l1.addLayout(self.form)
        l1.addStretch(1)
        self.check_lbl = QLabel("")
        self.check_lbl.setWordWrap(True)
        l1.addWidget(self.check_lbl)
        b_check = QPushButton("Vérifier la cohérence avec le notebook")
        b_check.clicked.connect(self.checkRequested.emit)
        l1.addWidget(b_check, alignment=Qt.AlignmentFlag.AlignLeft)
        mid.addWidget(c1, 1)
        c2, l2 = card("Fichiers du dossier exporté")
        self.table = make_table(["Fichier", "Rôle", "État"])
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setMinimumHeight(300)
        l2.addWidget(self.table)
        hint = QLabel("Après un nouvel export (section 15 du notebook), remplacez les dossiers models/ et data/ puis rechargez.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        l2.addWidget(hint)
        b = QPushButton("Recharger les données et le modèle")
        b.setObjectName("primary")
        b.clicked.connect(self.reloadRequested.emit)
        l2.addWidget(b, alignment=Qt.AlignmentFlag.AlignLeft)
        mid.addWidget(c2, 1)
        root.addLayout(mid)
        root.addStretch(1)

    def set_state(self, engine: RecommenderEngine | None, error: str = ""):
        """Affiche les informations du modèle et vérifie les fichiers exportés."""
        while self.form.rowCount():
            self.form.removeRow(0)
        if engine is not None:
            m, w = engine.meta, engine.weights
            rows = [("Modèle retenu", engine.best_model_name),
                    ("Booster", f"{engine.best_booster_name} ({', '.join(s['file'] for s in m['booster_specs'])})"),
                    ("Pondération", f"Content-Based {w[0]:g}, MF {w[1]:g}, booster {w[2]:g}, popularité {w[3]:g}"),
                    ("Clients / destinations", f"{len(engine.client_ids)} / {len(engine.dest_ids)}"),
                    ("Types de voyage", ", ".join(engine.types)),
                    ("Évaluation", f"Top-{engine.k_eval}"),
                    ("Exporté le", m.get("exported_at", "—"))]
        else:
            rows = [("État", error or "Modèle non chargé")]
        for k, v in rows:
            lk = QLabel(k)
            lk.setObjectName("hint")
            lv = QLabel(str(v))
            lv.setWordWrap(True)
            lv.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.form.addRow(lk, lv)
        self.check_lbl.setText("")
        self.table.setRowCount(len(self.FILES))
        for r, (f, role) in enumerate(self.FILES):
            ok = (APP_DIR / f).exists()
            it = table_item("Présent" if ok else "Manquant")
            it.setForeground(QBrush(QColor(GREEN if ok else RED)))
            self.table.setItem(r, 0, table_item(f))
            self.table.setItem(r, 1, table_item(role))
            self.table.setItem(r, 2, it)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def show_check(self, ok: bool, msg: str):
        """Affiche le résultat de la vérification de cohérence du modèle."""
        self.check_lbl.setText(("Conforme : " if ok else "Écart détecté : ") + msg)
        self.check_lbl.setStyleSheet(f"color:{GREEN if ok else RED}; font-weight:600;")


# ============================================================================ fenêtre principale
# Assemble la navigation latérale, les pages, le chargement du modèle et les raccourcis.
class MainWindow(QMainWindow):
    """Fenêtre principale qui coordonne la navigation et les cinq pages."""

    def __init__(self):
        """Construit la fenêtre, les pages, les raccourcis et les connexions principales."""
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_TAGLINE}")
        icon = APP_DIR / "assets" / "app.ico"
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))
        self.resize(1440, 900)
        self.setMinimumSize(1200, 740)
        self.engine, self.engine_error = None, ""

        central = QWidget()
        lay = QHBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setCentralWidget(central)

        # -- bandeau latéral
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        sl = QVBoxLayout(self.sidebar)
        sl.setContentsMargins(16, 22, 16, 16)
        sl.setSpacing(6)
        if LOGO_PATH is not None:
            tile = QFrame()
            tile.setObjectName("logoTile")
            tl = QVBoxLayout(tile)
            tl.setContentsMargins(12, 10, 12, 10)
            logo = QLabel()
            logo.setPixmap(QPixmap(str(LOGO_PATH)).scaledToWidth(176, Qt.TransformationMode.SmoothTransformation))
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tl.addWidget(logo)
            sl.addWidget(tile)
        else:
            brand = QLabel(APP_NAME)
            brand.setObjectName("brand")
            sl.addWidget(brand)
        tag = QLabel(APP_TAGLINE)
        tag.setObjectName("tagline")
        tag.setWordWrap(True)
        sl.addWidget(tag)
        sl.addSpacing(20)
        self.nav = QButtonGroup(self)
        self.nav.setExclusive(True)
        for i, text in enumerate(["Tableau de bord", "Rapports Power BI", "Recommandations",
                                  "Performance des modèles", "À propos"]):
            b = QPushButton(text)
            b.setObjectName("navButton")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav.addButton(b, i)
            sl.addWidget(b)
        sl.addStretch(1)
        foot = QLabel(f"version {VERSION}\nF11 : plein écran")
        foot.setObjectName("sidebarFooter")
        sl.addWidget(foot)
        lay.addWidget(self.sidebar)

        # -- pages
        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        self.dashboard = DashboardPage()
        self.reports = ReportsPage(ReportStore(CONFIG_PATH))
        self.reco = RecoPage()
        self.models = ModelsPage()
        self.about = AboutPage()
        for p in (self.dashboard, self.reports, self.reco, self.models, self.about):
            self.stack.addWidget(p)
        lay.addWidget(self.stack, 1)

        self.nav.idClicked.connect(self.go)
        self.reports.presentationRequested.connect(self.set_presentation)
        self.about.reloadRequested.connect(self.reload)
        self.about.checkRequested.connect(self.run_check)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(lambda: self.set_presentation(False))
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)
        for i in range(5):
            QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self).activated.connect(lambda i=i: self.go(i))
        self.load_engine()
        self.go(0)

    def load_engine(self):
        """Charge le moteur de recommandation et transmet son état aux pages."""
        try:
            self.engine, self.engine_error = RecommenderEngine(APP_DIR), ""
        except Exception as exc:  # noqa: BLE001 — les autres sections restent utilisables
            self.engine = None
            self.engine_error = (f"Le modèle n'a pas pu être chargé depuis {APP_DIR / 'models'}.\n"
                                 f"{type(exc).__name__} : {exc}")
        self.reco.set_engine(self.engine, self.engine_error)
        self.models.set_data(self.engine)
        self.about.set_state(self.engine, self.engine_error)
        self._update_status()

    def reload(self):
        """Recharge les données du tableau de bord et le moteur de recommandation."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.dashboard.reload()
            self.load_engine()
        finally:
            QApplication.restoreOverrideCursor()
        self.statusBar().showMessage("Données et modèle rechargés.", 5000)

    def run_check(self):
        """Exécute le contrôle de cohérence entre les artefacts et le notebook."""
        if self.engine is None:
            self.about.show_check(False, self.engine_error or "modèle non chargé.")
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            ok, msg = selfcheck(APP_DIR, self.engine)
        except Exception as exc:  # noqa: BLE001
            ok, msg = False, str(exc)
        finally:
            QApplication.restoreOverrideCursor()
        self.about.show_check(ok, msg)

    def go(self, i: int):
        """Affiche la page correspondant à l'index de navigation fourni."""
        self.stack.setCurrentIndex(i)
        self.nav.button(i).setChecked(True)

    def _update_status(self):
        """Met à jour la barre d'état avec l'état du modèle et de WebEngine."""
        e = self.engine
        txt = (f"Modèle chargé : {len(e.client_ids)} clients, {len(e.dest_ids)} destinations, booster {e.best_booster_name}"
               if e else "Modèle non chargé : les sections Tableau de bord et Rapports Power BI restent disponibles")
        if not HAS_WEBENGINE:
            txt += "   |   PyQt6-WebEngine absent : les rapports s'ouvrent dans le navigateur"
        self.statusBar().showMessage(txt)

    def toggle_fullscreen(self):
        """Bascule entre l'affichage maximisé et le plein écran."""
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def set_presentation(self, on: bool):
        """Active ou désactive le mode de présentation du rapport Power BI."""
        if on == self.reports.presenting:
            return
        self.sidebar.setVisible(not on)
        self.statusBar().setVisible(not on)
        self.reports.set_presentation(on)
        if on:
            self.go(1)
            self.showFullScreen()
        else:
            self.showMaximized()

    def closeEvent(self, e):
        """Arrête les ressources intégrées avant de fermer la fenêtre."""
        self.reports.shutdown()
        super().closeEvent(e)


# ============================================================================ point d'entrée
# Prépare Qt, applique la palette de l'application puis lance la fenêtre principale.
def light_palette() -> QPalette:
    """Construit la palette claire utilisée par l'application Qt."""
    p = QPalette()
    for role, color in {
        QPalette.ColorRole.Window: PAGE, QPalette.ColorRole.WindowText: INK, QPalette.ColorRole.Base: "#FFFFFF",
        QPalette.ColorRole.AlternateBase: "#F7F9FC", QPalette.ColorRole.Text: INK, QPalette.ColorRole.Button: "#FFFFFF",
        QPalette.ColorRole.ButtonText: INK, QPalette.ColorRole.ToolTipBase: "#FFFFFF", QPalette.ColorRole.ToolTipText: INK,
        QPalette.ColorRole.Highlight: PRIMARY, QPalette.ColorRole.HighlightedText: "#FFFFFF",
        QPalette.ColorRole.PlaceholderText: SLATE, QPalette.ColorRole.Link: PRIMARY,
    }.items():
        p.setColor(role, QColor(color))
    return p


def _excepthook(exc_type, exc, tb):
    """Affiche les exceptions non gérées dans la console et dans une boîte de dialogue."""
    msg = "".join(traceback.format_exception(exc_type, exc, tb))
    sys.stderr.write(msg)
    if QApplication.instance():
        QMessageBox.critical(None, "Erreur inattendue", f"{exc}\n\nDétails :\n{msg[-1500:]}")


def main():
    """Configure Qt, crée la fenêtre principale et démarre la boucle graphique."""
    sys.excepthook = _excepthook
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TravelBI.Desktop")
        except Exception:  # noqa: BLE001
            pass
    app = QApplication(sys.argv)
    app.setApplicationName("TravelBI")
    app.setOrganizationName("TravelBI")
    try:                                   # Qt 6.8+ : ignorer le thème sombre du système
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)
    except Exception:  # noqa: BLE001
        pass
    app.setStyle("Fusion")
    app.setPalette(light_palette())
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
