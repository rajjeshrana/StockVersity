from __future__ import annotations

import csv
import json
import threading
import uuid
import zipfile
import xml.etree.ElementTree as ET

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# =====================================================
# EXPORT JOB
# =====================================================

@dataclass(slots=True)
class ExportJob:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    export_type: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    output_file: Optional[
        Path
    ] = None

    rows: int = 0

    status: str = "completed"

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# EXPORT MANAGER
# =====================================================

class ExportManager:

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

        self.export_directory = (

            Path.home()

            / ".stockversity"

            / "exports"

        )

        self.export_directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.history: List[
            ExportJob
        ] = []

    # =====================================================
    # CREATE JOB
    # =====================================================

    def create(

        self,

        name: str,

        export_type: str,

    ):

        job = ExportJob(

            name=name,

            export_type=export_type,

        )

        self.history.append(

            job

        )

        return job

    # =====================================================
    # EXPORT JSON
    # =====================================================

    def export_json(

        self,

        name: str,

        data: List[Dict],

    ):

        job = self.create(

            name,

            "json",

        )

        file = (

            self.export_directory

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

        job.output_file = file

        job.rows = len(

            data

        )

        return job

    # =====================================================
    # EXPORT CSV
    # =====================================================

    def export_csv(

        self,

        name: str,

        data: List[Dict],

    ):

        job = self.create(

            name,

            "csv",

        )

        file = (

            self.export_directory

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

        job.output_file = file

        job.rows = len(

            data

        )

        return job

    # =====================================================
    # EXPORT XML
    # =====================================================

    def export_xml(

        self,

        name: str,

        data: List[Dict],

    ):

        job = self.create(

            name,

            "xml",

        )

        file = (

            self.export_directory

            / f"{name}.xml"

        )

        root = ET.Element(

            "records"

        )

        for row in data:

            record = ET.SubElement(

                root,

                "record",

            )

            for key, value in row.items():

                node = ET.SubElement(

                    record,

                    key,

                )

                node.text = str(

                    value

                )

        ET.ElementTree(

            root

        ).write(

            file,

            encoding="utf-8",

            xml_declaration=True,

        )

        job.output_file = file

        job.rows = len(

            data

        )

        return job

    # =====================================================
    # EXPORT HTML
    # =====================================================

    def export_html(

        self,

        name: str,

        data: List[Dict],

    ):

        job = self.create(

            name,

            "html",

        )

        file = (

            self.export_directory

            / f"{name}.html"

        )

        html = [

            "<html>",

            "<body>",

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

        job.output_file = file

        job.rows = len(

            data

        )

        return job

    # =====================================================
    # LIST EXPORTS
    # =====================================================

    def list_exports(

        self,

    ):

        return list(

            self.history

        )
        # =====================================================
    # GET EXPORT
    # =====================================================

    def get_export(

        self,

        export_id: str,

    ):

        for job in self.history:

            if job.id == export_id:

                return job

        return None

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
        implementation.
        """

        job = self.export_csv(

            name,

            data,

        )

        job.export_type = "excel"

        return job

    # =====================================================
    # EXPORT PDF
    # =====================================================

    def export_pdf(

        self,

        name: str,

        data: List[Dict],

    ):

        """
        Placeholder.

        Replace using reportlab.
        """

        job = self.create(

            name,

            "pdf",

        )

        file = (

            self.export_directory

            / f"{name}.pdf.txt"

        )

        lines = []

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

        job.output_file = file

        job.rows = len(

            data

        )

        return job

    # =====================================================
    # EXPORT PNG
    # =====================================================

    def export_png(

        self,

        name: str,

    ):

        """
        Placeholder.

        Future:
        Export charts/widgets
        as PNG.
        """

        job = self.create(

            name,

            "png",

        )

        file = (

            self.export_directory

            / f"{name}.png"

        )

        file.touch(

            exist_ok=True

        )

        job.output_file = file

        return job

    # =====================================================
    # EXPORT JPEG
    # =====================================================

    def export_jpeg(

        self,

        name: str,

    ):

        job = self.create(

            name,

            "jpeg",

        )

        file = (

            self.export_directory

            / f"{name}.jpg"

        )

        file.touch(

            exist_ok=True

        )

        job.output_file = file

        return job

    # =====================================================
    # ZIP EXPORTS
    # =====================================================

    def zip_exports(

        self,

        archive_name: str,

    ):

        archive = (

            self.export_directory

            / f"{archive_name}.zip"

        )

        with zipfile.ZipFile(

            archive,

            "w",

            zipfile.ZIP_DEFLATED,

        ) as zipf:

            for job in self.history:

                if (

                    job.output_file

                    and job.output_file.exists()

                ):

                    zipf.write(

                        job.output_file,

                        arcname=job.output_file.name,

                    )

        return archive

    # =====================================================
    # BATCH EXPORT
    # =====================================================

    def batch_export(

        self,

        exports: List[Dict],

    ):

        results = []

        for item in exports:

            export_type = item.get(

                "type",

                "json",

            )

            name = item.get(

                "name",

                "export",

            )

            data = item.get(

                "data",

                [],

            )

            if export_type == "json":

                results.append(

                    self.export_json(

                        name,

                        data,

                    )

                )

            elif export_type == "csv":

                results.append(

                    self.export_csv(

                        name,

                        data,

                    )

                )

            elif export_type == "xml":

                results.append(

                    self.export_xml(

                        name,

                        data,

                    )

                )

            elif export_type == "html":

                results.append(

                    self.export_html(

                        name,

                        data,

                    )

                )

            elif export_type == "excel":

                results.append(

                    self.export_excel(

                        name,

                        data,

                    )

                )

            elif export_type == "pdf":

                results.append(

                    self.export_pdf(

                        name,

                        data,

                    )

                )

        return results

    # =====================================================
    # DELETE EXPORT
    # =====================================================

    def delete_export(

        self,

        export_id: str,

    ):

        job = self.get_export(

            export_id

        )

        if job is None:

            return False

        if (

            job.output_file

            and job.output_file.exists()

        ):

            job.output_file.unlink()

        self.history.remove(

            job

        )

        return True
        # =====================================================
    # SEARCH EXPORTS
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            job

            for job in self.history

            if (

                keyword in job.name.lower()

                or keyword

                in job.export_type.lower()

            )

        ]

    # =====================================================
    # FILTER
    # =====================================================

    def filter(

        self,

        export_type: str,

    ):

        return [

            job

            for job in self.history

            if job.export_type == export_type

        ]

    # =====================================================
    # EXPORT METADATA
    # =====================================================

    def export_metadata(

        self,

    ):

        metadata = []

        for job in self.history:

            metadata.append(

                {

                    "id": job.id,

                    "name": job.name,

                    "export_type": job.export_type,

                    "created_at": job.created_at.isoformat(),

                    "output_file": (

                        str(

                            job.output_file

                        )

                        if job.output_file

                        else ""

                    ),

                    "rows": job.rows,

                    "status": job.status,

                    "metadata": job.metadata,

                }

            )

        return metadata

    # =====================================================
    # IMPORT METADATA
    # =====================================================

    def import_metadata(

        self,

        metadata: List[Dict],

    ):

        imported = 0

        for item in metadata:

            job = ExportJob(

                id=item["id"],

                name=item["name"],

                export_type=item["export_type"],

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

                status=item.get(

                    "status",

                    "completed",

                ),

                metadata=item.get(

                    "metadata",

                    {},

                ),

            )

            self.history.append(

                job

            )

            imported += 1

        return imported

    # =====================================================
    # EXPORT STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "total_exports": len(

                self.history

            ),

            "json": len(

                self.filter(

                    "json"

                )

            ),

            "csv": len(

                self.filter(

                    "csv"

                )

            ),

            "xml": len(

                self.filter(

                    "xml"

                )

            ),

            "html": len(

                self.filter(

                    "html"

                )

            ),

            "pdf": len(

                self.filter(

                    "pdf"

                )

            ),

            "excel": len(

                self.filter(

                    "excel"

                )

            ),

            "png": len(

                self.filter(

                    "png"

                )

            ),

            "jpeg": len(

                self.filter(

                    "jpeg"

                )

            ),

            "rows": sum(

                job.rows

                for job in self.history

            ),

        }

    # =====================================================
    # QUEUE EXPORT
    # =====================================================

    def queue_export(

        self,

        export_callable,

        *args,

        **kwargs,

    ):

        """
        Placeholder for future
        background worker support.
        """

        return export_callable(

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

        for job in self.history:

            if (

                job.output_file

                and job.output_file.exists()

            ):

                active.append(

                    job

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

            for job in self.history

            if (

                job.output_file

                and job.output_file.exists()

            )

        )

        return {

            "exports": len(

                self.history

            ),

            "existing": existing,

            "missing": len(

                self.history

            )

            - existing,

            "directory": str(

                self.export_directory

            ),

        }

    # =====================================================
    # TOTAL SIZE
    # =====================================================

    def total_size(

        self,

    ):

        total = 0

        for job in self.history:

            if (

                job.output_file

                and job.output_file.exists()

            ):

                total += (

                    job.output_file.stat().st_size

                )

        return total

    # =====================================================
    # LATEST EXPORT
    # =====================================================

    def latest_export(

        self,

    ):

        if not self.history:

            return None

        return max(

            self.history,

            key=lambda job: job.created_at,

        )
        # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        """
        Reset export history.
        Exported files remain on disk.
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
        persisted export metadata.
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

        Reserved for persisting
        export metadata.
        """

        return {

            "exports": len(

                self.history

            ),

            "storage": self.total_size(),

        }

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        export_id: str,

    ):

        return self.get_export(

            export_id

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

            "ExportManager("

            f"exports={stats['total_exports']}, "

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

            "Export Manager\n"

            f"Exports       : {stats['total_exports']}\n"

            f"JSON          : {stats['json']}\n"

            f"CSV           : {stats['csv']}\n"

            f"XML           : {stats['xml']}\n"

            f"HTML          : {stats['html']}\n"

            f"PDF           : {stats['pdf']}\n"

            f"Excel         : {stats['excel']}\n"

            f"PNG           : {stats['png']}\n"

            f"JPEG          : {stats['jpeg']}\n"

            f"Rows          : {stats['rows']}\n"

            f"Storage (B)   : {self.total_size()}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

export_manager = ExportManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "ExportJob",

    "ExportManager",

    "export_manager",

]