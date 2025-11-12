"""
Configure Reportlab related settings, and package to be passed to submodules
M. Capotosto 11/9/2025

Adapted from T. Caracappa's source.

Rev -
"""
import os

from contextlib import contextmanager
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    Paragraph,
    PageBreak,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1, \
      ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Flowable, KeepTogether


from dataclasses import dataclass, field
from typing import List

from initialize_dut import DUT

# -----------------------------
# Define a small container for visual style dictionaries
# `slots=True` prevents Python from creating a dynamic __dict__ for each
# instance
# -----------------------------


@contextmanager
def channel_section(ctx: "ReportContext", chan: int, page_break=True):
    # local bucket for this channel
    bucket = []
    # heading
    title_style = ParagraphStyle('ChanHdr', parent=ctx.styles['Heading2'],
                                 alignment=TA_CENTER)
    bucket.append(Spacer(1, 0.15*inch))
    bucket.append(Paragraph(f"Channel {chan}", title_style))
    bucket.append(Spacer(1, 0.1*inch))
    # hand the list to callers
    yield bucket
    # close: wrap & append to doc
    ctx.elements.append(KeepTogether(bucket))
    if page_break:
        ctx.elements.append(PageBreak())


@dataclass(slots=True)
class ReportTheme:
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.9)
    good = dict(boxstyle="round", facecolor="palegreen", alpha=0.9)
    bad = dict(boxstyle="round", facecolor="pink", alpha=0.9)


# -----------------------------
# Define a container for all report-wide shared resources
# -----------------------------


@dataclass
class ReportContext:
    doc: SimpleDocTemplate

    # A nested theme object holding all the color/boxstyle dictionaries
    theme: ReportTheme = field(default_factory=ReportTheme)

    # ReportLab style sheet used by Paragraphs and other flowables
    styles: StyleSheet1 = field(default_factory=getSampleStyleSheet)

    # A list to accumulate report elements (Paragraphs, Tables, etc.)
    elements: List[Flowable] = field(default_factory=list)


def _cover_table(dut: DUT) -> Table:
    tdata = [
        ["PSC Functional Test Results", 0],
        ["Power Supply Controller Configuration", 0],
        ["Serial Number", dut.psc_sn],
        ["Number of Channels", dut.num_channels],
        ["Resolution", dut.resolution],
        ["Bandwidth", dut.bandwidth],
        ["Polarity", dut.polarity],
    ]

    rowH = [0.4*inch, 0.35*inch, *(0.27*inch for _ in range(5))]

    colH = [3*inch, 3*inch]

    style = [
            ("SPAN", (0, 0), (1, 0)),
            ("SPAN", (0, 1), (1, 1)),
            ("ALIGN", (0, 0), (1, 1), "CENTER"),
            ("FONTSIZE", (0, 0), (1, 0), 16),
            ("FONTSIZE", (0, 1), (1, 1), 14),
            ("VALIGN", (0, 0), (1, 6), "MIDDLE"),
            ("LINEABOVE", (0, 1), (1, 2), 2, colors.black),
            ("BACKGROUND", (0, 0), (1, 1), colors.lemonchiffon),
            ("BACKGROUND", (0, 2), (0, 6), colors.lightblue),
            ("FONTSIZE", (0, 1), (1, 6), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
        ]
    return Table(tdata, colH, rowH, style=style)


def _make_filename(dut: DUT) -> str:
    return (f"{dut.num_channels}ch_{dut.resolution[:2]}"
            f"{dut.bandwidth[:1]}_SN{dut.psc_sn}_"
            f"{dut.dir_timestamp}.pdf")


def _create_context(pdf_path: str) -> ReportContext:
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    theme = ReportTheme()
    return ReportContext(doc=doc, styles=styles, elements=[],
                         theme=theme)


def start_report(dut: DUT, output_dir: str | None = None) -> tuple:
    base_dir = dut.report_dir
    pdf_name = _make_filename(dut)
    pdf_path = os.path.abspath(os.path.join(base_dir, pdf_name))

    ctx = _create_context(pdf_path)

    title_style = ParagraphStyle(
        'TitleCenter', parent=ctx.styles['Heading1'],
        alignment=TA_CENTER
    )
    ctx.elements.append(Paragraph("PSC Functional Test Report", title_style))
    ctx.elements.append(Spacer(1, 0.2*inch))

    ctx.elements.append(_cover_table(dut))

    return ctx, pdf_path


def finalize_report(ctx: ReportContext) -> str:
    pdf_path = ctx.doc.filename
    ctx.doc.build(ctx.elements)
    return pdf_path
