from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "naiyo24-technology-architecture-report.pdf"

PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 0.58 * inch
RIGHT_MARGIN = 0.58 * inch
TOP_MARGIN = 0.55 * inch
BOTTOM_MARGIN = 0.62 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5E6B7C")
LINE = colors.HexColor("#D8DEE8")
SOFT = colors.HexColor("#F4F7FB")
SOFT_BLUE = colors.HexColor("#EAF2FB")
BLUE = colors.HexColor("#174A7C")
TEAL = colors.HexColor("#087B78")
GREEN = colors.HexColor("#24734D")
AMBER = colors.HexColor("#9A650C")
RED = colors.HexColor("#9A2F2F")
PURPLE = colors.HexColor("#7A4A87")
WHITE = colors.white


def make_styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            "CoverEyebrow",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#B9DDEC"),
            uppercase=True,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            "CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=31,
            textColor=WHITE,
            spaceAfter=10,
        )
    )
    base.add(
        ParagraphStyle(
            "CoverSub",
            fontName="Helvetica",
            fontSize=10.7,
            leading=16,
            textColor=colors.HexColor("#DCECF4"),
        )
    )
    base.add(
        ParagraphStyle(
            "H1",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=BLUE,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            "H2",
            fontName="Helvetica-Bold",
            fontSize=12.4,
            leading=15,
            textColor=BLUE,
            spaceBefore=6,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            "BodyTight",
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.1,
            textColor=MUTED,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9.4,
            leading=13.6,
            textColor=MUTED,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            "Lead",
            fontName="Helvetica",
            fontSize=10.2,
            leading=14.8,
            textColor=MUTED,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            "Small",
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=MUTED,
        )
    )
    base.add(
        ParagraphStyle(
            "TinyHead",
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=INK,
            spaceAfter=2,
        )
    )
    base.add(
        ParagraphStyle(
            "AppBullet",
            fontName="Helvetica",
            fontSize=8.8,
            leading=12.2,
            leftIndent=12,
            firstLineIndent=-7,
            textColor=MUTED,
            spaceAfter=3,
        )
    )
    base.add(
        ParagraphStyle(
            "TableHead",
            fontName="Helvetica-Bold",
            fontSize=7.1,
            leading=9,
            textColor=WHITE,
        )
    )
    base.add(
        ParagraphStyle(
            "TableCell",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.2,
            textColor=colors.HexColor("#3F4F62"),
        )
    )
    base.add(
        ParagraphStyle(
            "TableCellStrong",
            parent=base["TableCell"],
            fontName="Helvetica-Bold",
            textColor=INK,
        )
    )
    return base


STYLES = make_styles()


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def bullet_list(items: Iterable[str]) -> list[Paragraph]:
    return [Paragraph(item, STYLES["AppBullet"], bulletText="-") for item in items]


def section_header(title: str, subtitle: str = "") -> list:
    right = Paragraph(subtitle, ParagraphStyle("HeaderSub", parent=STYLES["Small"], alignment=TA_RIGHT))
    title_p = Paragraph(title, STYLES["H1"])
    tbl = Table([[title_p, right]], colWidths=[CONTENT_WIDTH * 0.58, CONTENT_WIDTH * 0.42])
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, 0), (-1, -1), 1.3, LINE),
            ]
        )
    )
    return [tbl, Spacer(1, 12)]


def panel(title: str, body: Sequence, width: float | None = None, fill=WHITE) -> Table:
    flow = [Paragraph(title, STYLES["H2"])]
    flow.extend(body)
    t = Table([[flow]], colWidths=[width or CONTENT_WIDTH])
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), fill),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return t


def two_columns(left, right, gap=12):
    col_w = (CONTENT_WIDTH - gap) / 2
    t = Table([[left, right]], colWidths=[col_w, col_w])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t


class CoverBand(Flowable):
    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 260

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(BLUE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 18, fill=1, stroke=1)
        c.setFillColor(TEAL)
        c.roundRect(self.width * 0.66, 0, self.width * 0.34, self.height, 18, fill=1, stroke=0)
        c.setFillColor(colors.Color(1, 1, 1, alpha=0.10))
        for x in (self.width * 0.58, self.width * 0.72, self.width * 0.86):
            c.circle(x, self.height * 0.70, 58, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#B9DDEC"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(26, self.height - 36, "TECHNOLOGY ARCHITECTURE REPORT")
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 28)
        draw_wrapped(c, "Naiyo24 Transfer File Sharing System", 26, self.height - 70, self.width * 0.64, "Helvetica-Bold", 28, 31, WHITE)
        c.setFillColor(colors.HexColor("#DCECF4"))
        c.setFont("Helvetica", 10.6)
        subtitle = (
            "Professional architecture overview for the Flutter client, FastAPI backend, "
            "object-storage layer, database model, background jobs, deployment topology, "
            "and current implementation boundaries found in the repository."
        )
        draw_wrapped(c, subtitle, 26, self.height - 155, self.width * 0.61, "Helvetica", 10.2, 14.6, colors.HexColor("#DCECF4"))

        cards = [
            ("GENERATED", "June 8, 2026"),
            ("REPOSITORY", "naiyo24-file-sharing-system"),
            ("SCOPE", "Source inspection and architecture documentation"),
        ]
        card_w = (self.width - 52 - 20) / 3
        y = 23
        for i, (label, value) in enumerate(cards):
            x = 26 + i * (card_w + 10)
            c.setFillColor(colors.Color(1, 1, 1, alpha=0.10))
            c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.22))
            c.roundRect(x, y, card_w, 48, 10, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#B9DDEC"))
            c.setFont("Helvetica-Bold", 6.6)
            c.drawString(x + 10, y + 30, label)
            c.setFillColor(colors.HexColor("#F0F7FB"))
            c.setFont("Helvetica", 8.1)
            draw_wrapped(c, value, x + 10, y + 20, card_w - 18, "Helvetica", 8.1, 10, colors.HexColor("#F0F7FB"))
        c.restoreState()


def draw_wrapped(c, text, x, y, width, font, size, leading, color, max_lines=None):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if stringWidth(probe, font, size) <= width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines:
        lines = lines[:max_lines]
    c.setFont(font, size)
    c.setFillColor(color)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return y - len(lines) * leading


class ArchitectureDiagram(Flowable):
    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.base_w = 980
        self.base_h = 620
        self.scale = width / self.base_w
        self.height = self.base_h * self.scale

    def draw(self):
        c = self.canv
        s = self.scale
        c.saveState()
        c.scale(s, s)
        c.setLineWidth(1.2)

        def rr(x, y, w, h, fill, stroke=LINE, radius=14):
            c.setFillColor(fill)
            c.setStrokeColor(stroke)
            c.roundRect(x, self.base_h - y - h, w, h, radius, fill=1, stroke=1)

        def label(x, y, text, font="Helvetica-Bold", size=12, color=INK):
            c.setFillColor(color)
            c.setFont(font, size)
            c.drawString(x, self.base_h - y, text)

        def arrow(x1, y1, x2, y2, color=BLUE):
            c.setStrokeColor(color)
            c.setLineWidth(2.2)
            c.line(x1, self.base_h - y1, x2, self.base_h - y2)
            draw_arrow_head(c, x1, self.base_h - y1, x2, self.base_h - y2, color)

        rr(22, 20, 936, 118, colors.HexColor("#F5F8FC"))
        rr(22, 156, 936, 206, colors.HexColor("#F5F8FC"))
        rr(22, 386, 936, 184, colors.HexColor("#F5F8FC"))
        label(42, 48, "CLIENT AND EDGE", "Helvetica-Bold", 9, colors.HexColor("#526072"))
        label(42, 184, "APPLICATION SERVICES", "Helvetica-Bold", 9, colors.HexColor("#526072"))
        label(42, 414, "DATA, STORAGE, AND BACKGROUND WORK", "Helvetica-Bold", 9, colors.HexColor("#526072"))

        boxes = [
            (52, 70, 170, 72, "Flutter App", ["Material UI, Riverpod", "Dio, file_picker, JWT"], SOFT_BLUE, colors.HexColor("#8BB2D8")),
            (260, 70, 170, 72, "Authenticated User", ["Login/register", "Upload and copy link"], SOFT_BLUE, colors.HexColor("#8BB2D8")),
            (496, 70, 170, 72, "Nginx", ["/api proxy, /health", "rate limit, body limit"], colors.HexColor("#FDF6E8"), colors.HexColor("#D9B66C")),
            (742, 70, 170, 72, "Recipient", ["Share info and download", "Presigned or direct stream"], SOFT_BLUE, colors.HexColor("#8BB2D8")),
            (68, 208, 200, 104, "FastAPI Entrypoint", ["app.main lifespan", "CORS middleware", "/api router group"], colors.HexColor("#EEF7F6"), colors.HexColor("#8CC4C0")),
            (314, 202, 322, 120, "API Routes", ["/auth: register, login, me", "/upload: start, chunk, finalize, simple", "/share: create, info, my, revoke", "/download: redirect, stream, HEAD"], colors.HexColor("#EEF7F6"), colors.HexColor("#8CC4C0")),
            (686, 202, 222, 120, "Service Layer", ["upload_service", "share_service", "download_service", "storage_service"], colors.HexColor("#EEF7F6"), colors.HexColor("#8CC4C0")),
            (62, 438, 194, 96, "PostgreSQL", ["users, files, shares", "downloads metadata", "SQLAlchemy async"], colors.HexColor("#EFF8F2"), colors.HexColor("#93C4A6")),
            (304, 438, 194, 96, "Redis", ["upload_session:* hashes", "TTL and progress state", "Celery broker/results"], colors.HexColor("#EFF8F2"), colors.HexColor("#93C4A6")),
            (546, 438, 194, 96, "MinIO / S3", ["chunks and final objects", "multipart assembly", "presigned downloads"], colors.HexColor("#EFF8F2"), colors.HexColor("#93C4A6")),
            (786, 438, 160, 96, "Celery", ["cleanup tasks", "expired shares", "Flower monitor"], colors.HexColor("#F7EFF8"), colors.HexColor("#C69AD0")),
        ]
        for x, y, w, h, title, lines, fill, stroke in boxes:
            rr(x, y, w, h, fill, stroke, 12)
            label(x + 20, y + 27, title, "Helvetica-Bold", 12, INK)
            for i, line in enumerate(lines):
                label(x + 20, y + 47 + i * 15, line, "Helvetica", 9.5, MUTED)

        arrow(222, 106, 260, 106)
        arrow(430, 106, 496, 106)
        arrow(666, 106, 742, 106)
        arrow(581, 142, 190, 208)
        arrow(268, 260, 314, 260, TEAL)
        arrow(636, 260, 686, 260, TEAL)
        arrow(742, 322, 176, 438, GREEN)
        arrow(784, 322, 414, 438, GREEN)
        arrow(826, 322, 648, 438, GREEN)
        arrow(866, 438, 818, 322, TEAL)
        arrow(794, 438, 436, 438, TEAL)
        c.restoreState()


class DataModelDiagram(Flowable):
    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.base_w = 930
        self.base_h = 280
        self.scale = width / self.base_w
        self.height = self.base_h * self.scale

    def draw(self):
        c = self.canv
        s = self.scale
        c.saveState()
        c.scale(s, s)

        def rr(x, y, w, h, fill, stroke=LINE, radius=12):
            c.setFillColor(fill)
            c.setStrokeColor(stroke)
            c.roundRect(x, self.base_h - y - h, w, h, radius, fill=1, stroke=1)

        def text(x, y, value, font="Helvetica", size=10, color=MUTED):
            c.setFillColor(color)
            c.setFont(font, size)
            c.drawString(x, self.base_h - y, value)

        def entity(x, y, w, h, name, fields):
            rr(x, y, w, h, WHITE)
            rr(x, y, w, 32, BLUE, BLUE)
            text(x + 18, y + 21, name, "Helvetica-Bold", 12, WHITE)
            for i, field in enumerate(fields):
                text(x + 18, y + 56 + i * 17, field, "Helvetica", 9.4, MUTED)

        def arrow(x1, y1, x2, y2, label):
            c.setStrokeColor(BLUE)
            c.setLineWidth(2)
            c.line(x1, self.base_h - y1, x2, self.base_h - y2)
            draw_arrow_head(c, x1, self.base_h - y1, x2, self.base_h - y2, BLUE)
            text((x1 + x2) / 2 - 18, y1 - 10, label, "Helvetica-Bold", 8.6, BLUE)

        entity(20, 38, 178, 182, "users", ["id PK", "email unique", "password hash", "is_active", "created_at"])
        entity(272, 26, 210, 206, "files", ["id PK", "filename, original_filename", "size, mime_type", "storage_url S3 key", "uploaded_by FK users.id", "is_deleted", "created_at"])
        entity(548, 26, 196, 206, "shares", ["id PK", "file_id FK files.id", "token unique", "expiry_time", "password hash optional", "download_limit/count", "is_active, created_at"])
        entity(786, 52, 170, 158, "downloads", ["id PK", "file_id FK files.id", "share_id FK shares.id", "ip_address, user_agent", "downloaded_at"])
        arrow(198, 132, 272, 132, "owns")
        arrow(482, 132, 548, 132, "shares")
        arrow(744, 132, 786, 132, "logs")
        c.setStrokeColor(BLUE)
        c.setLineWidth(2)
        c.line(482, self.base_h - 205, 786, self.base_h - 205)
        draw_arrow_head(c, 482, self.base_h - 205, 786, self.base_h - 205, BLUE)
        text(595, 195, "download belongs to file", "Helvetica-Bold", 8.6, BLUE)
        c.restoreState()


def draw_arrow_head(c, x1, y1, x2, y2, color):
    import math

    angle = math.atan2(y2 - y1, x2 - x1)
    size = 7
    p1 = (x2, y2)
    p2 = (x2 - size * math.cos(angle - 0.45), y2 - size * math.sin(angle - 0.45))
    p3 = (x2 - size * math.cos(angle + 0.45), y2 - size * math.sin(angle + 0.45))
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.line(p2[0], p2[1], p1[0], p1[1])
    c.line(p3[0], p3[1], p1[0], p1[1])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7.2)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    y = 0.34 * inch
    canvas.drawString(LEFT_MARGIN, y, "Naiyo24 Transfer Technology Architecture Report")
    canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, y, f"Page {doc.page}")
    canvas.restoreState()


def cover_story() -> list:
    brief = panel(
        "Executive Summary",
        [
            p(
                "The application is a cross-platform file-transfer experience. "
                "The visible Flutter client authenticates users, lets them select a file, "
                "chooses a short expiry window, uploads through the API, and returns a copyable "
                "share link. The backend is a Python FastAPI service that separates authentication, "
                "upload, share, and download responsibilities behind typed Pydantic schemas and "
                "SQLAlchemy data models.",
                "Lead",
            )
        ],
        width=(CONTENT_WIDTH - 12) * 0.58,
    )
    facts = panel(
        "Key Facts",
        [
            p("<b>Core pattern:</b> Metadata in PostgreSQL, binaries in S3-compatible storage, transient upload state in Redis.", "BodyTight"),
            p("<b>Primary stack:</b> Flutter, Riverpod, Dio, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, MinIO/S3, Nginx.", "BodyTight"),
            p("<b>Current client path:</b> The Flutter UI calls <font name='Courier-Bold'>/api/upload/simple</font>; chunked upload endpoints are implemented on the backend.", "BodyTight"),
        ],
        width=(CONTENT_WIDTH - 12) * 0.42,
        fill=SOFT,
    )
    table = Table([[brief, facts]], colWidths=[(CONTENT_WIDTH - 12) * 0.58, (CONTENT_WIDTH - 12) * 0.42])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    contents = panel(
        "Contents",
        [
            p(
                "System architecture diagram; technology stack; client and backend layers; "
                "primary workflows; data model and storage; security, reliability, operations; "
                "implementation notes and source map.",
                "BodyTight",
            )
        ],
        fill=SOFT,
    )
    return [CoverBand(CONTENT_WIDTH), Spacer(1, 20), table, Spacer(1, 12), contents, Spacer(1, 12)]


def tech_stack_table():
    rows = [
        ("Layer", "Technology", "Role in the application"),
        ("Client application", "Flutter, Dart SDK 3.2.5+, Material 3", "Cross-platform UI for login, registration, upload selection, expiry configuration, and share-link display."),
        ("Client state", "flutter_riverpod, shared_preferences", "StateNotifier providers manage authentication and upload UI state; the JWT is persisted under auth_token."),
        ("Client networking", "Dio, file_picker", "Dio sends auth and upload requests with an Authorization interceptor; file_picker selects local files for upload."),
        ("Backend API", "FastAPI, Uvicorn, Pydantic v2", "Typed API routes, request/response schemas, form handling, file upload handling, and OpenAPI-compatible service structure."),
        ("Database", "PostgreSQL 16, SQLAlchemy 2 async, asyncpg", "Stores users, file metadata, share-link policy, and download audit records. Binary files are not stored in the database."),
        ("Object storage", "boto3, MinIO/S3-compatible storage", "Stores uploaded chunks and final files. The backend generates S3v4 presigned URLs and supports direct range streaming."),
        ("Transient state and jobs", "Redis, Celery, Flower", "Redis tracks chunked upload sessions and powers Celery broker/result storage; Flower exposes task monitoring."),
        ("Edge and deployment", "Nginx, Docker Compose, Alembic", "Nginx proxies /api, applies request limits, and exposes health. Compose defines local backend infrastructure."),
        ("Testing", "pytest, pytest-asyncio, flutter_test", "Backend route and utility tests use mocked dependencies; Flutter widget tests cover the unauthenticated app state and keyboard layout."),
    ]
    data = []
    for i, row in enumerate(rows):
        style = "TableHead" if i == 0 else "TableCell"
        strong = "TableHead" if i == 0 else "TableCellStrong"
        data.append([p(row[0], strong), p(row[1], style), p(row[2], style)])
    t = Table(data, colWidths=[CONTENT_WIDTH * 0.25, CONTENT_WIDTH * 0.27, CONTENT_WIDTH * 0.48], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return t


def source_table():
    rows = [
        ("Source file", "Evidence used"),
        ("pubspec.yaml", "Flutter dependencies: Dio, Riverpod, file_picker, shared_preferences, Google Fonts, and lints."),
        ("lib/main.dart, lib/providers/*, lib/services/api_service.dart", "Client routing, auth persistence, API base URL, bearer-token interceptor, upload flow, and state model."),
        ("filesharingbackend/backend/app/main.py", "FastAPI initialization, lifespan startup, CORS policy, router mounting, and health endpoint."),
        ("app/api/routes/*.py", "Auth, upload, share, and download endpoint contracts and HTTP behavior."),
        ("app/services/*.py", "Upload sessions, chunk assembly, S3/MinIO operations, share validation, presigned URLs, and direct streaming."),
        ("app/models/*.py", "SQLAlchemy entities for users, files, shares, and downloads."),
        ("docker-compose.yml, nginx/nginx.conf", "Container topology, service ports, dependency order, reverse proxy, rate limiting, and upload body limit."),
        ("backend/tests/*, test/widget_test.dart", "Backend and Flutter test coverage areas."),
    ]
    data = []
    for i, row in enumerate(rows):
        data.append([p(row[0], "TableHead" if i == 0 else "TableCellStrong"), p(row[1], "TableHead" if i == 0 else "TableCell")])
    t = Table(data, colWidths=[CONTENT_WIDTH * 0.38, CONTENT_WIDTH * 0.62], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return t


def build_story() -> list:
    story: list = []
    story.extend(cover_story())
    story.append(PageBreak())

    story.extend(section_header("System Architecture Diagram", "Logical runtime view of the deployed application and request/data flow."))
    story.append(ArchitectureDiagram(CONTENT_WIDTH))
    story.append(Spacer(1, 8))
    story.append(p("Diagram describes the repository implementation: Docker Compose runs the backend, PostgreSQL, Redis, MinIO, Nginx, Celery worker, and Flower. The Flutter client is configured separately and reaches the backend through its API base URL.", "Small"))
    story.append(Spacer(1, 10))
    legend = Table(
        [[
            p("Client and users", "Small"),
            p("Edge gateway", "Small"),
            p("Application service", "Small"),
            p("Persistence and storage", "Small"),
        ]],
        colWidths=[CONTENT_WIDTH / 4] * 4,
    )
    legend.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, LINE), ("BACKGROUND", (0, 0), (0, 0), SOFT_BLUE), ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FDF6E8")), ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EEF7F6")), ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#EFF8F2")), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(legend)
    story.append(PageBreak())

    story.extend(section_header("Technology Stack", "Exact technologies observed from project manifests, dependency files, and source code."))
    story.append(tech_stack_table())
    story.append(Spacer(1, 12))
    third = (CONTENT_WIDTH - 16) / 3
    cards = Table(
        [[
            panel("Separation of concerns", [p("The backend keeps route handlers thin. Routes delegate upload, sharing, download, and storage behavior to dedicated service modules.", "BodyTight")], third),
            panel("Metadata versus files", [p("SQL tables track ownership and policy. File bytes live in object storage, reducing database pressure and enabling presigned downloads.", "BodyTight")], third),
            panel("Two upload modes", [p("The backend supports chunked sessions for larger uploads. The current Flutter UI uses the simple multipart endpoint for its visible flow.", "BodyTight")], third),
        ]],
        colWidths=[third, third, third],
    )
    cards.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(cards)
    story.append(PageBreak())

    story.extend(section_header("Client Application Layer", "Flutter architecture and the UI-to-API contract used by the app."))
    story.append(
        two_columns(
            panel(
                "Application shell",
                [
                    p("lib/main.dart wraps the app in ProviderScope, reads authProvider, and selects a loading view, UploadScreen, or LoginScreen. The theme is defined centrally in AppTheme.dark().", "BodyTight"),
                    *bullet_list(["<b>State:</b> Riverpod StateNotifier providers expose immutable state objects.", "<b>Persistence:</b> shared_preferences stores the bearer token locally.", "<b>Navigation:</b> login/register replace the stack with the upload screen after success."]),
                ],
                (CONTENT_WIDTH - 12) / 2,
            ),
            panel(
                "API service",
                [
                    p("lib/services/api_service.dart creates one Dio client with a base URL from API_BASE_URL at compile time, falling back to a local network IP. An interceptor injects Authorization: Bearer when a saved token exists.", "BodyTight"),
                    *bullet_list(["<b>Auth calls:</b> /api/auth/login and /api/auth/register.", "<b>Upload call:</b> /api/upload/simple with multipart file and expiry minutes.", "<b>Error handling:</b> maps common API status codes to user-facing messages."]),
                ],
                (CONTENT_WIDTH - 12) / 2,
            ),
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        two_columns(
            panel("Authentication state", [p("AuthNotifier checks for a saved token on startup, performs login/register requests, writes the returned JWT, and clears it on logout. Screens react to provider state.", "BodyTight")], (CONTENT_WIDTH - 12) / 2),
            panel("File transfer state", [p("FileNotifier tracks selected path, loading status, generated link, and expiry minutes. The UI bounds expiry between 10 and 60 minutes, then calls the API service to upload and receive the share URL.", "BodyTight")], (CONTENT_WIDTH - 12) / 2),
        )
    )
    story.append(Spacer(1, 10))
    story.append(panel("Current client implementation boundary", [p("The backend implements chunked upload endpoints, but the current Flutter upload workflow uses the simple single-file endpoint. This matters for deployment planning because Nginx currently sets client_max_body_size 10M; larger files should use the chunked flow or adjust edge limits.", "BodyTight")], fill=colors.HexColor("#FFF8EB")))
    story.append(Spacer(1, 12))
    story.extend(section_header("Backend API Layer", "FastAPI route groups, service responsibilities, and request validation."))
    story.append(
        two_columns(
            panel("FastAPI app lifecycle", [p("app.main starts a FastAPI application, applies CORS, mounts /api, verifies database tables through SQLAlchemy metadata, and attempts object-storage bucket initialization during lifespan startup.", "BodyTight")], (CONTENT_WIDTH - 12) / 2),
            panel("Route groups", [p("app.api.router mounts auth, upload, share, and download routers. Each route uses Pydantic schemas and FastAPI dependencies for authenticated user and database session injection.", "BodyTight")], (CONTENT_WIDTH - 12) / 2),
        )
    )
    story.append(PageBreak())

    story.extend(section_header("Primary Workflows", "End-to-end behavior for authentication, upload, share-link creation, and download."))
    story.append(
        two_columns(
            panel(
                "Visible Flutter upload flow",
                numbered_steps(
                    [
                        ("User authenticates", "The client submits email/password and stores the JWT returned from /api/auth/login."),
                        ("User selects file and expiry", "file_picker supplies a local path; expiry is constrained to 10-60 minutes."),
                        ("Client posts multipart upload", "/api/upload/simple uploads bytes to object storage, creates a file row, and creates a share row."),
                        ("Share URL returns to UI", "The response includes link and expiry_time; the UI displays a copy button."),
                    ]
                ),
                (CONTENT_WIDTH - 12) / 2,
            ),
            panel(
                "Backend chunked upload capability",
                numbered_steps(
                    [
                        ("Start session", "/api/upload/start validates size, calculates chunks, creates a Redis hash, and sets TTL."),
                        ("Upload chunks", "/api/upload/chunk validates owner/index and stores each chunk at an S3 key."),
                        ("Finalize file", "/api/upload/finalize verifies completeness and assembles the final object using S3 multipart upload."),
                        ("Create metadata", "The route writes a files record with the final storage key and user ownership."),
                    ]
                ),
                (CONTENT_WIDTH - 12) / 2,
            ),
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        two_columns(
            panel(
                "Share-link policy",
                [
                    p("share_service validates file ownership, generates a unique token, computes expiry from minutes or hours, optionally hashes a password, and stores download limits and counters in the shares table.", "BodyTight"),
                    *bullet_list(["Default expiry is configured as 72 hours.", "Minute-based expiry supports 10-60 minutes.", "Protected links use bcrypt-hashed passwords."]),
                ],
                (CONTENT_WIDTH - 12) / 2,
            ),
            panel(
                "Download behavior",
                [
                    p("download_service validates token state, expiry, password, active flag, and download limit. It then logs the request, increments download count, and either redirects to a presigned object URL or streams the object directly with HTTP range support.", "BodyTight"),
                    *bullet_list(["GET /api/download/{token} returns a 307 redirect.", "GET /api/download/{token}/direct streams bytes.", "HEAD /api/download/{token} exposes size and range support."]),
                ],
                (CONTENT_WIDTH - 12) / 2,
            ),
        )
    )
    story.append(PageBreak())

    story.extend(section_header("Data Model and Storage", "Persistence model and object-storage ownership strategy."))
    story.append(DataModelDiagram(CONTENT_WIDTH))
    story.append(Spacer(1, 12))
    story.append(
        two_columns(
            panel(
                "Database responsibilities",
                [
                    p("PostgreSQL stores identities, ownership, object-storage keys, share policy, and audit data. The async SQLAlchemy session dependency commits successful request work and rolls back exceptions.", "BodyTight"),
                    *bullet_list(["<b>Users:</b> unique email, password hash, active flag.", "<b>Files:</b> original name, generated name, size, MIME type, S3 key, owner.", "<b>Shares:</b> token, expiry, optional password, limits, active flag.", "<b>Downloads:</b> file/share references plus client IP and user agent."]),
                ],
                (CONTENT_WIDTH - 12) / 2,
            ),
            panel(
                "Object-storage strategy",
                [
                    p("The storage service uses boto3 against S3 or MinIO. Chunks are stored under uploads/{user_id}/{upload_id}/chunks/{index}. Final files are assembled into uploads/{user_id}/{upload_id}/{filename}.", "BodyTight"),
                    *bullet_list(["Bucket creation is attempted during app startup and before uploads.", "Multipart copy avoids loading every chunk into backend memory.", "Presigned URLs expire after one hour for download redirects.", "Range reads support resumable direct downloads."]),
                ],
                (CONTENT_WIDTH - 12) / 2,
            ),
        )
    )
    story.append(Spacer(1, 10))
    story.append(panel("Schema migration note", [p("The checked-in Alembic initial migration is currently a placeholder with no generated DDL. At runtime, Base.metadata.create_all verifies and creates tables during FastAPI startup. For production, explicit Alembic migrations should replace startup schema creation.", "BodyTight")], fill=colors.HexColor("#FFF8EB")))
    story.append(PageBreak())

    story.extend(section_header("Security, Reliability, and Operations", "Security controls and operational mechanisms directly present in source code."))
    story.append(
        two_columns(
            panel(
                "Security controls",
                bullet_list(
                    [
                        "<b>Password hashing:</b> bcrypt via Passlib for user passwords and optional share-link passwords.",
                        "<b>JWT authentication:</b> HS256 bearer tokens with configurable expiry, defaulting to 60 minutes.",
                        "<b>Ownership checks:</b> upload sessions and share creation validate current-user ownership.",
                        "<b>Public download gates:</b> token state, active flag, expiry, password, and download limit are validated.",
                        "<b>Filename handling:</b> utility functions sanitize names and generate storage-safe unique identifiers.",
                    ]
                ),
                (CONTENT_WIDTH - 12) / 2,
            ),
            panel(
                "Reliability controls",
                bullet_list(
                    [
                        "<b>Database sessions:</b> request-scoped async sessions commit, rollback, and close predictably.",
                        "<b>Redis TTL:</b> upload sessions expire after the configured TTL and reset on chunk activity.",
                        "<b>Chunk cleanup:</b> cancel and scheduled Celery tasks remove stale upload artifacts.",
                        "<b>Range downloads:</b> direct streaming supports HTTP Range headers for resume-capable clients.",
                        "<b>Object-store retries:</b> boto3 client config enables adaptive retry behavior.",
                    ]
                ),
                (CONTENT_WIDTH - 12) / 2,
            ),
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        two_columns(
            panel("Deployment topology", [p("filesharingbackend/docker-compose.yml defines backend, PostgreSQL, Redis, MinIO, Nginx, Celery worker, and Flower services on a bridge network. The backend is served by Uvicorn on port 8000.", "BodyTight"), *bullet_list(["Backend: 8000", "Nginx: 80", "PostgreSQL: 5432", "Redis: 6379", "MinIO API/console: 9000 / 9001", "Flower: 5555"])], (CONTENT_WIDTH - 12) / 2),
            panel("Nginx edge behavior", [p("nginx.conf proxies /api/ to the backend, forwards client headers, exposes /health, applies 100r/m per-IP rate limiting, and configures extended proxy timeouts for file-transfer requests.", "BodyTight"), *bullet_list(["client_max_body_size 10M is compatible with 5 MB chunks plus buffer.", "Rate limit burst is set to 20 requests with no delay.", "Proxy read/send timeout is 300 seconds for large transfers."])], (CONTENT_WIDTH - 12) / 2),
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        two_columns(
            panel("Background processing", [p("Celery uses Redis as broker and result backend. Scheduled tasks deactivate expired share links every hour and clean up nearly expired in-progress upload sessions every 30 minutes.", "BodyTight")], (CONTENT_WIDTH - 12) / 2),
            panel("Environment configuration", [p("pydantic-settings centralizes app, database, Redis, object storage, file-size, expiry, and CDN settings. Sensitive values such as secret keys and access keys are expected from environment variables.", "BodyTight")], (CONTENT_WIDTH - 12) / 2),
        )
    )
    story.append(PageBreak())

    story.extend(section_header("Implementation Notes and Source Map", "Precise boundaries, known considerations, and source evidence used for this report."))
    notes = [
        ("Current UI is focused, not administrative.", "The Flutter screens expose authentication, file selection, expiry selection, upload, and copyable link output. Backend routes include additional share listing, file listing, revoke, progress, cancel, and direct-download capabilities."),
        ("Object storage is S3-compatible, with MinIO configured locally.", "Dependencies include boto3/botocore, and Compose includes a MinIO service. The code can target MinIO through MINIO_ENDPOINT or generic S3-style storage when configured differently."),
        ("Testing exists but is primarily mocked at the API boundary.", "Backend route tests patch service calls and dependency overrides. Flutter widget tests check initial unauthenticated rendering and keyboard behavior."),
        ("Documentation source is the codebase.", "README.md is empty, so this PDF is based on direct inspection of implementation files, manifests, and tests."),
    ]
    for title, body in notes:
        story.append(panel(title, [p(body, "BodyTight")], fill=SOFT))
        story.append(Spacer(1, 6))
    story.append(Spacer(1, 4))
    story.append(source_table())
    story.append(Spacer(1, 8))
    story.append(p("Prepared as a professional technical architecture PDF for the Naiyo24 Transfer repository. No assumptions were taken from external documentation.", "Small"))
    return story


def numbered_steps(steps: Sequence[tuple[str, str]]) -> list:
    output = []
    for i, (title, body) in enumerate(steps, start=1):
        data = [[p(str(i), "TableCellStrong"), [p(title, "TinyHead"), p(body, "Small")]]]
        t = Table(data, colWidths=[22, None])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), SOFT_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        output.append(t)
        output.append(Spacer(1, 5))
    return output


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="Naiyo24 Transfer Technology Architecture Report",
        author="OpenAI Codex",
    )
    doc.build(build_story(), onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build_pdf()
    print(OUT)
