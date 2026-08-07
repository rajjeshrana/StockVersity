from __future__ import annotations

import csv
import json
import threading
import uuid

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


# =====================================================
# REPORT
# =====================================================

@dataclass(slots=True)
class Report:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    report_type: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    output_file: Optional[
        Path
    ] = None

    rows: int = 0

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# REPORT MANAGER
# =====================================================

class ReportManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.report_directory = (

            Path.home()

            / ".stockversity"

            / "reports"

        )

        self.report_directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.history: List[
            Report
        ] = []

    # =====================================================
    # CREATE REPORT
    # =====================================================

    def create(

        self,

        name: str,

        report_type: str,

    ):

        report = Report(

            name=name,

            report_type=report_type,

        )

        self.history.append(

            report

        )

        return report

    # =====================================================
    # GET REPORT
    # =====================================================

    def get(

        self,

        report_id: str,

    ):

        for report in self.history:

            if report.id == report_id:

                return report

        return None

    # =====================================================
    # LIST REPORTS
    # =====================================================

    def list_reports(

        self,

    ):

        return list(

            self.history

        )

    # =====================================================
    # EXPORT JSON
    # =====================================================

    def export_json(

        self,

        name: str,

        data: List[Dict],

    ):

        report = self.create(

            name,

            "json",

        )

        file = (

            self.report_directory

            / f"{name}.json"

        )

        with open(

            file,

            "w",

            encoding="utf-8",

        ) as fp:

            json.dump(

                data,

                fp,

                indent=4,

                default=str,

            )

        report.output_file = file

        report.rows = len(

            data

        )

        return report

    # =====================================================
    # EXPORT CSV
    # =====================================================

    def export_csv(

        self,

        name: str,

        data: List[Dict],

    ):

        report = self.create(

            name,

            "csv",

        )

        file = (

            self.report_directory

            / f"{name}.csv"

        )

        if data:

            with open(

                file,

                "w",

                newline="",

                encoding="utf-8",

            ) as fp:

                writer = csv.DictWriter(

                    fp,

                    fieldnames=list(

                        data[0].keys()

                    ),

                )

                writer.writeheader()

                writer.writerows(

                    data

                )

        report.output_file = file

        report.rows = len(

            data

        )

        return report

    # =====================================================
    # EXPORT HTML
    # =====================================================

    def export_html(

        self,

        name: str,

        data: List[Dict],

        title: str = "Report",

    ):

        report = self.create(

            name,

            "html",

        )

        file = (

            self.report_directory

            / f"{name}.html"

        )

        html = [

            "<html>",

            "<head>",

            f"<title>{title}</title>",

            "</head>",

            "<body>",

            f"<h2>{title}</h2>",

            "<table border='1'>",

        ]

        if data:

            html.append("<tr>")

            for key in data[0]:

                html.append(

                    f"<th>{key}</th>"

                )

            html.append("</tr>")

            for row in data:

                html.append("<tr>")

                for value in row.values():

                    html.append(

                        f"<td>{value}</td>"

                    )

                html.append("</tr>")

        html.extend(

            [

                "</table>",

                "</body>",

                "</html>",

            ]

        )

        file.write_text(

            "\n".join(html),

            encoding="utf-8",

        )

        report.output_file = file

        report.rows = len(

            data

        )

        return report

    # =====================================================
    # DELETE REPORT
    # =====================================================

    def delete(

        self,

        report_id: str,

    ):

        report = self.get(

            report_id

        )

        if report is None:

            return False

        if (

            report.output_file

            and report.output_file.exists()

        ):

            report.output_file.unlink()

        self.history.remove(

            report

        )

        return True
        # =====================================================
    # EXPORT PDF
    # =====================================================

    def export_pdf(

        self,

        name: str,

        data: List[Dict],

        title: str = "StockVersity Report",

    ):

        """
        Placeholder PDF exporter.

        Can later be upgraded using
        reportlab.
        """

        report = self.create(

            name,

            "pdf",

        )

        file = (

            self.report_directory

            / f"{name}.pdf.txt"

        )

        lines = [

            title,

            "=" * len(title),

            "",

        ]

        for row in data:

            for key, value in row.items():

                lines.append(

                    f"{key}: {value}"

                )

            lines.append("")

        file.write_text(

            "\n".join(lines),

            encoding="utf-8",

        )

        report.output_file = file

        report.rows = len(data)

        return report

    # =====================================================
    # EXPORT EXCEL
    # =====================================================

    def export_excel(

        self,

        name: str,

        data: List[Dict],

    ):

        """
        Placeholder.

        Replace with openpyxl
        implementation later.
        """

        return self.export_csv(

            name,

            data,

        )

    # =====================================================
    # SCANNER REPORT
    # =====================================================

    def scanner_report(

        self,

        scan_results: List[Dict],

        name: str = "scanner_results",

    ):

        return self.export_html(

            name=name,

            data=scan_results,

            title="Scanner Results",

        )

    # =====================================================
    # AI REPORT
    # =====================================================

    def ai_report(

        self,

        opportunities: List[Dict],

        name: str = "ai_opportunities",

    ):

        return self.export_html(

            name=name,

            data=opportunities,

            title="AI Opportunities",

        )

    # =====================================================
    # PORTFOLIO REPORT
    # =====================================================

    def portfolio_report(

        self,

        holdings: List[Dict],

        name: str = "portfolio",

    ):

        return self.export_html(

            name=name,

            data=holdings,

            title="Portfolio Report",

        )

    # =====================================================
    # DAILY REPORT
    # =====================================================

    def daily_report(

        self,

        data: List[Dict],

    ):

        return self.export_html(

            name=datetime.now().strftime(

                "daily_%Y%m%d"

            ),

            data=data,

            title="Daily Market Report",

        )

    # =====================================================
    # WEEKLY REPORT
    # =====================================================

    def weekly_report(

        self,

        data: List[Dict],

    ):

        week = datetime.now().strftime(

            "%Y_week_%W"

        )

        return self.export_html(

            name=f"weekly_{week}",

            data=data,

            title="Weekly Report",

        )

    # =====================================================
    # MONTHLY REPORT
    # =====================================================

    def monthly_report(

        self,

        data: List[Dict],

    ):

        month = datetime.now().strftime(

            "%Y_%m"

        )

        return self.export_html(

            name=f"monthly_{month}",

            data=data,

            title="Monthly Report",

        )

    # =====================================================
    # TEMPLATE
    # =====================================================

    def template(

        self,

        title: str,

        columns: List[str],

    ):

        return {

            "title": title,

            "columns": columns,

            "generated": datetime.utcnow(),

        }

    # =====================================================
    # APPLY TEMPLATE
    # =====================================================

    def apply_template(

        self,

        template: Dict,

        data: List[Dict],

    ):

        columns = template.get(

            "columns",

            [],

        )

        formatted = []

        for row in data:

            formatted.append(

                {

                    column: row.get(

                        column,

                        "",

                    )

                    for column in columns

                }

            )

        return formatted
        # =====================================================
    # SEARCH REPORTS
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            report

            for report in self.history

            if (

                keyword in report.name.lower()

                or keyword

                in report.report_type.lower()

            )

        ]

    # =====================================================
    # FILTER REPORT TYPE
    # =====================================================

    def filter(

        self,

        report_type: str,

    ):

        return [

            report

            for report in self.history

            if report.report_type == report_type

        ]

    # =====================================================
    # REPORT STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        json_reports = len(

            self.filter(

                "json"

            )

        )

        csv_reports = len(

            self.filter(

                "csv"

            )

        )

        html_reports = len(

            self.filter(

                "html"

            )

        )

        pdf_reports = len(

            self.filter(

                "pdf"

            )

        )

        excel_reports = len(

            self.filter(

                "excel"

            )

        )

        total_rows = sum(

            report.rows

            for report in self.history

        )

        return {

            "total_reports": len(

                self.history

            ),

            "json": json_reports,

            "csv": csv_reports,

            "html": html_reports,

            "pdf": pdf_reports,

            "excel": excel_reports,

            "rows": total_rows,

        }

    # =====================================================
    # EXPORT METADATA
    # =====================================================

    def export_metadata(

        self,

    ):

        exported = []

        for report in self.history:

            exported.append(

                {

                    "id": report.id,

                    "name": report.name,

                    "report_type": report.report_type,

                    "created_at": report.created_at.isoformat(),

                    "output_file": (

                        str(

                            report.output_file

                        )

                        if report.output_file

                        else ""

                    ),

                    "rows": report.rows,

                    "metadata": report.metadata,

                }

            )

        return exported

    # =====================================================
    # IMPORT METADATA
    # =====================================================

    def import_metadata(

        self,

        metadata: List[Dict],

    ):

        imported = 0

        for item in metadata:

            report = Report(

                id=item["id"],

                name=item["name"],

                report_type=item["report_type"],

                created_at=datetime.fromisoformat(

                    item["created_at"]

                ),

                output_file=(

                    Path(

                        item["output_file"]

                    )

                    if item.get(

                        "output_file"

                    )

                    else None

                ),

                rows=item.get(

                    "rows",

                    0,

                ),

                metadata=item.get(

                    "metadata",

                    {},

                ),

            )

            self.history.append(

                report

            )

            imported += 1

        return imported

    # =====================================================
    # SCHEDULE REPORT
    # =====================================================

    def schedule_report(

        self,

        generator,

        *args,

        **kwargs,

    ):

        """
        Placeholder scheduling helper.

        Integrate with
        SchedulerManager.
        """

        return generator(

            *args,

            **kwargs,

        )

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(

        self,

    ):

        removed = 0

        active = []

        for report in self.history:

            if (

                report.output_file

                and report.output_file.exists()

            ):

                active.append(

                    report

                )

            else:

                removed += 1

        self.history = active

        return removed

    # =====================================================
    # HEALTH
    # =====================================================

    def health(

        self,

    ):

        existing = sum(

            1

            for report in self.history

            if (

                report.output_file

                and report.output_file.exists()

            )

        )

        missing = len(

            self.history

        ) - existing

        return {

            "reports": len(

                self.history

            ),

            "existing": existing,

            "missing": missing,

            "directory": str(

                self.report_directory

            ),

        }

    # =====================================================
    # LATEST REPORT
    # =====================================================

    def latest_report(

        self,

    ):

        if not self.history:

            return None

        return max(

            self.history,

            key=lambda report: report.created_at,

        )

    # =====================================================
    # TOTAL SIZE
    # =====================================================

    def total_size(

        self,

    ):

        total = 0

        for report in self.history:

            if (

                report.output_file

                and report.output_file.exists()

            ):

                total += (

                    report.output_file.stat().st_size

                )

        return total
        # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        """
        Reset report history.
        Generated report files
        are not deleted.
        """

        self.history.clear()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

    ):

        """
        Startup hook.

        Reserved for loading
        persisted report metadata.
        """

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        """
        Shutdown hook.

        Reserved for saving
        report metadata.
        """

        return {

            "reports": len(

                self.history

            ),

            "storage": self.total_size(),

        }

    # =====================================================
    # REPORT EXISTS
    # =====================================================

    def exists(

        self,

        report_id: str,

    ):

        return self.get(

            report_id

        ) is not None

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_history(

        self,

    ):

        count = len(

            self.history

        )

        self.history.clear()

        return count

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.statistics()

        return (

            "ReportManager("

            f"reports={stats['total_reports']}, "

            f"rows={stats['rows']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Report Manager\n"

            f"Reports       : {stats['total_reports']}\n"

            f"JSON          : {stats['json']}\n"

            f"CSV           : {stats['csv']}\n"

            f"HTML          : {stats['html']}\n"

            f"PDF           : {stats['pdf']}\n"

            f"Excel         : {stats['excel']}\n"

            f"Rows          : {stats['rows']}\n"

            f"Storage (B)   : {self.total_size()}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

report_manager = ReportManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Report",

    "ReportManager",

    "report_manager",

]