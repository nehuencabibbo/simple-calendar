#!/usr/bin/env python3

# A4 estándar: 297 × 210 mm (horizontal al generar el PDF)

"""Create a clean, print-ready A4 landscape monthly calendar PDF.

Requires ReportLab: python -m pip install reportlab
"""

from __future__ import annotations

import argparse
import calendar
from datetime import date
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


MONTHS_ES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)
WEEKDAYS_ES = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")

MARGIN_X = 0
MARGIN_TOP = 0
MARGIN_BOTTOM = 0
TITLE_HEIGHT = 58
WEEKDAY_HEIGHT = 35
INK = colors.HexColor("#171717")
PAPER = colors.white


def draw_crossed_cell(pdf: canvas.Canvas, x: float, y: float, width: float, height: float) -> None:
    """Draw the prominent X used for days that do not belong to the selected month."""
    inset = 0
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.95)
    pdf.line(x + inset, y + inset, x + width - inset, y + height - inset)
    pdf.line(x + inset, y + height - inset, x + width - inset, y + inset)


def draw_date_badge(
    pdf: canvas.Canvas, day: int, x: float, y: float, width: float, height: float
) -> None:
    """Draw a small rounded date label in the cell's upper-right corner."""
    badge_w = 27
    badge_h = 27
    inset = 0
    badge_x = x + width - badge_w - inset
    badge_y = y + height - badge_h - inset
    pdf.setFillColor(PAPER)
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.9)
    pdf.rect(badge_x, badge_y, badge_w, badge_h, stroke=1, fill=1)
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(badge_x + badge_w / 2, badge_y + 8, str(day))


def draw_month(pdf: canvas.Canvas, year: int, month: int, page_width: float, page_height: float) -> None:
    """Draw one fixed-layout A4 landscape month on the current PDF page."""

    # Reference-inspired page with a framed title and independent weekday tabs.
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, page_width, page_height, stroke=0, fill=1)
    content_width = page_width - (2 * MARGIN_X)
    title_y = page_height - MARGIN_TOP - TITLE_HEIGHT
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(1.1)
    pdf.rect(MARGIN_X, title_y, content_width, TITLE_HEIGHT, stroke=1, fill=0)
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 23)
    pdf.drawCentredString(page_width / 2, title_y + 20, f"{MONTHS_ES[month - 1].upper()} {year}")

    grid_x = MARGIN_X
    grid_width = content_width
    cell_width = grid_width / 7
    # The three bands meet directly, with no decorative gaps between them.
    weekday_y = title_y - WEEKDAY_HEIGHT
    grid_top = weekday_y
    grid_bottom = MARGIN_BOTTOM
    cell_height = (grid_top - grid_bottom) / 6

    # Separate weekday tabs make the day headings easy to scan.
    pdf.setFont("Helvetica-Bold", 11)
    for column, weekday in enumerate(WEEKDAYS_ES):
        x = grid_x + column * cell_width
        pdf.setStrokeColor(INK)
        pdf.setLineWidth(1.0)
        pdf.rect(x, weekday_y, cell_width, WEEKDAY_HEIGHT, stroke=1, fill=0)
        pdf.setFillColor(INK)
        pdf.drawCentredString(x + cell_width / 2, weekday_y + 12, weekday)

    # A stable six-week grid makes every generated month use the full printable area.
    month_matrix = calendar.Calendar(firstweekday=calendar.MONDAY).monthdayscalendar(year, month)
    month_matrix.extend([[0] * 7 for _ in range(6 - len(month_matrix))])

    # Draw one rounded outer frame then the internal rules to prevent double borders.
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(1.05)
    pdf.rect(grid_x, grid_bottom, grid_width, grid_top - grid_bottom, stroke=1, fill=0)
    pdf.setLineWidth(0.8)
    for column in range(1, 7):
        x = grid_x + column * cell_width
        pdf.line(x, grid_bottom, x, grid_top)
    for row in range(1, 6):
        y = grid_top - row * cell_height
        pdf.line(grid_x + 1, y, grid_x + grid_width - 1, y)

    for row, week in enumerate(month_matrix):
        y = grid_top - (row + 1) * cell_height
        for column, day in enumerate(week):
            x = grid_x + column * cell_width
            if day:
                draw_date_badge(pdf, day, x, y, cell_width, cell_height)
            else:
                draw_crossed_cell(pdf, x, y, cell_width, cell_height)


def create_calendar(year: int, months: Iterable[int], destination: Path) -> None:
    """Write the selected months for *year* to one A4 landscape PDF."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(str(destination), pagesize=(page_width, page_height))
    pdf.setTitle(f"Calendario {year}")
    pdf.setAuthor("Calendar Generator")

    for month in months:
        draw_month(pdf, year, month, page_width, page_height)
        pdf.showPage()

    pdf.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera un calendario mensual o anual minimalista en PDF A4 horizontal."
    )
    parser.add_argument("year", type=int, nargs="?", help="Año de cuatro cifras (por ejemplo, 2026).")
    parser.add_argument(
        "month", type=int, choices=range(1, 13), nargs="?", metavar="MONTH",
        help="Mes opcional: 1 (enero) a 12 (diciembre).",
    )
    parser.add_argument(
        "--from-current-month", action="store_true",
        help="Genera desde el mes actual hasta diciembre del año actual.",
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        help="Archivo PDF de salida.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.from_current_month:
        if args.year is not None or args.month is not None:
            raise SystemExit("--from-current-month no admite YEAR ni MONTH.")
        today = date.today()
        year = today.year
        months = range(today.month, 13)
        default_name = f"calendario-{year:04d}-{today.month:02d}.pdf"
    else:
        if args.year is None:
            raise SystemExit("Indique YEAR o use --from-current-month.")
        year = args.year
        months = (args.month,) if args.month is not None else range(1, 13)
        default_name = (
            f"calendario-{year:04d}-{args.month:02d}.pdf"
            if args.month is not None
            else f"calendario-{year:04d}-01.pdf"
        )

    if not 1 <= year <= 9999:
        raise SystemExit("El año debe estar entre 1 y 9999.")
    output = args.output or Path(default_name)
    if output.suffix.lower() != ".pdf":
        output = output.with_suffix(".pdf")
    create_calendar(year, months, output)
    print(f"Calendario creado: {output.resolve()}")


if __name__ == "__main__":
    main()
