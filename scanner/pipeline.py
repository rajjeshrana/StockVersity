"""
=========================================================
StockVersity Scanner Pro
Scanner Pipeline
Version : 2.0
=========================================================

Execution pipeline for scanner processing.

Responsibilities
----------------
• Manage scanner processing stages
• Execute stages in sequence
• Pass data between stages
• Track pipeline errors
• Support custom stages
• Enable / disable stages
• Stop pipeline when required
• Provide execution diagnostics
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from threading import RLock

from time import perf_counter

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional


# =========================================================
# PIPELINE STATUS
# =========================================================

class PipelineStatus(str, Enum):

    IDLE = "IDLE"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    STOPPED = "STOPPED"


# =========================================================
# STAGE STATUS
# =========================================================

class PipelineStageStatus(str, Enum):

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    SKIPPED = "SKIPPED"


# =========================================================
# STAGE HANDLER
# =========================================================

PipelineHandler = Callable[
    [Any, Dict[str, Any]],
    Any,
]


# =========================================================
# PIPELINE STAGE
# =========================================================

@dataclass(slots=True)
class PipelineStage:

    name: str

    handler: PipelineHandler

    enabled: bool = True

    stop_on_error: bool = True

    order: int = 0

    # =====================================================
    # VALIDATE
    # =====================================================

    def __post_init__(
        self,
    ) -> None:

        self.name = str(
            self.name
        ).strip()

        if not self.name:

            raise ValueError(
                "Pipeline stage name cannot be empty."
            )

        if not callable(
            self.handler
        ):

            raise TypeError(
                "Pipeline stage handler must be callable."
            )


# =========================================================
# STAGE RESULT
# =========================================================

@dataclass(slots=True)
class PipelineStageResult:

    stage_name: str

    status: PipelineStageStatus = (
        PipelineStageStatus.PENDING
    )

    started_at: Optional[
        datetime
    ] = None

    completed_at: Optional[
        datetime
    ] = None

    duration_seconds: float = 0.0

    error: str = ""

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "stage_name":
                self.stage_name,

            "status":
                self.status.value,

            "started_at":
                (
                    self.started_at.isoformat()
                    if self.started_at
                    else None
                ),

            "completed_at":
                (
                    self.completed_at.isoformat()
                    if self.completed_at
                    else None
                ),

            "duration_seconds":
                round(
                    self.duration_seconds,
                    6,
                ),

            "error":
                self.error,
        }


# =========================================================
# PIPELINE RESULT
# =========================================================

@dataclass(slots=True)
class PipelineResult:

    status: PipelineStatus = (
        PipelineStatus.IDLE
    )

    input_data: Any = None

    output_data: Any = None

    stages: List[
        PipelineStageResult
    ] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    started_at: Optional[
        datetime
    ] = None

    completed_at: Optional[
        datetime
    ] = None

    duration_seconds: float = 0.0

    # =====================================================
    # SUCCESS
    # =====================================================

    @property
    def successful(
        self,
    ) -> bool:

        return (
            self.status
            == PipelineStatus.COMPLETED
            and not self.errors
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "status":
                self.status.value,

            "successful":
                self.successful,

            "started_at":
                (
                    self.started_at.isoformat()
                    if self.started_at
                    else None
                ),

            "completed_at":
                (
                    self.completed_at.isoformat()
                    if self.completed_at
                    else None
                ),

            "duration_seconds":
                round(
                    self.duration_seconds,
                    6,
                ),

            "stage_count":
                len(
                    self.stages
                ),

            "errors":
                list(
                    self.errors
                ),

            "stages": [

                stage.to_dict()

                for stage
                in self.stages
            ],
        }


# =========================================================
# SCANNER PIPELINE
# =========================================================

class ScannerPipeline:
    """
    Generic processing pipeline for scanner operations.
    """

    def __init__(
        self,
        *,
        name: str = "ScannerPipeline",
    ) -> None:

        self.name = str(
            name
        ).strip() or "ScannerPipeline"

        self._stages: Dict[
            str,
            PipelineStage
        ] = {}

        self._status = (
            PipelineStatus.IDLE
        )

        self._stop_requested = False

        self._last_result: Optional[
            PipelineResult
        ] = None

        self._lock = RLock()

    # =====================================================
    # NORMALIZE
    # =====================================================

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:

        return (
            str(name)
            .strip()
            .lower()
        )

    # =====================================================
    # ADD STAGE
    # =====================================================

    def add_stage(
        self,
        name: str,
        handler: PipelineHandler,
        *,
        enabled: bool = True,
        stop_on_error: bool = True,
        order: Optional[int] = None,
        replace: bool = False,
    ) -> PipelineStage:

        key = self._normalize_name(
            name
        )

        if not key:

            raise ValueError(
                "Pipeline stage name cannot be empty."
            )

        with self._lock:

            if (
                key in self._stages
                and not replace
            ):

                return self._stages[
                    key
                ]

            if order is None:

                order = (
                    len(self._stages)
                    + 1
                )

            stage = PipelineStage(

                name=str(
                    name
                ).strip(),

                handler=handler,

                enabled=bool(
                    enabled
                ),

                stop_on_error=bool(
                    stop_on_error
                ),

                order=int(
                    order
                ),
            )

            self._stages[
                key
            ] = stage

            return stage

    # =====================================================
    # REMOVE STAGE
    # =====================================================

    def remove_stage(
        self,
        name: str,
    ) -> bool:

        key = self._normalize_name(
            name
        )

        with self._lock:

            if key not in self._stages:

                return False

            del self._stages[
                key
            ]

            return True

    # =====================================================
    # GET STAGE
    # =====================================================

    def get_stage(
        self,
        name: str,
    ) -> Optional[
        PipelineStage
    ]:

        key = self._normalize_name(
            name
        )

        with self._lock:

            return self._stages.get(
                key
            )

    # =====================================================
    # ENABLE STAGE
    # =====================================================

    def enable_stage(
        self,
        name: str,
    ) -> bool:

        with self._lock:

            stage = self.get_stage(
                name
            )

            if stage is None:

                return False

            stage.enabled = True

            return True

    # =====================================================
    # DISABLE STAGE
    # =====================================================

    def disable_stage(
        self,
        name: str,
    ) -> bool:

        with self._lock:

            stage = self.get_stage(
                name
            )

            if stage is None:

                return False

            stage.enabled = False

            return True

    # =====================================================
    # ORDERED STAGES
    # =====================================================

    def ordered_stages(
        self,
    ) -> List[
        PipelineStage
    ]:

        with self._lock:

            return sorted(

                self._stages.values(),

                key=lambda stage:
                    stage.order,
            )

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        input_data: Any,
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> PipelineResult:
        """
        Execute enabled pipeline stages sequentially.

        Each handler receives:

            handler(current_data, context)

        The output of one stage becomes the input
        of the next stage.
        """

        execution_context = (
            dict(context)
            if context
            else {}
        )

        result = PipelineResult(

            status=(
                PipelineStatus.RUNNING
            ),

            input_data=input_data,

            output_data=input_data,

            started_at=datetime.now(),
        )

        started_timer = (
            perf_counter()
        )

        with self._lock:

            self._status = (
                PipelineStatus.RUNNING
            )

            self._stop_requested = False

        current_data = input_data

        try:

            for stage in (
                self.ordered_stages()
            ):

                # -------------------------------------
                # STOP REQUEST
                # -------------------------------------

                with self._lock:

                    stop_requested = (
                        self._stop_requested
                    )

                if stop_requested:

                    result.status = (
                        PipelineStatus.STOPPED
                    )

                    break

                # -------------------------------------
                # STAGE RESULT
                # -------------------------------------

                stage_result = (
                    PipelineStageResult(
                        stage_name=stage.name
                    )
                )

                result.stages.append(
                    stage_result
                )

                # -------------------------------------
                # DISABLED
                # -------------------------------------

                if not stage.enabled:

                    stage_result.status = (
                        PipelineStageStatus.SKIPPED
                    )

                    continue

                # -------------------------------------
                # RUN STAGE
                # -------------------------------------

                stage_result.status = (
                    PipelineStageStatus.RUNNING
                )

                stage_result.started_at = (
                    datetime.now()
                )

                stage_timer = (
                    perf_counter()
                )

                try:

                    current_data = (
                        stage.handler(
                            current_data,
                            execution_context,
                        )
                    )

                    stage_result.status = (
                        PipelineStageStatus.COMPLETED
                    )

                except Exception as exc:

                    message = (

                        f"{stage.name}: "
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )

                    stage_result.status = (
                        PipelineStageStatus.FAILED
                    )

                    stage_result.error = (
                        message
                    )

                    result.errors.append(
                        message
                    )

                    if stage.stop_on_error:

                        result.status = (
                            PipelineStatus.FAILED
                        )

                        break

                finally:

                    stage_result.completed_at = (
                        datetime.now()
                    )

                    stage_result.duration_seconds = max(
                        0.0,
                        perf_counter()
                        - stage_timer,
                    )

            # -----------------------------------------
            # FINAL STATUS
            # -----------------------------------------

            if (
                result.status
                == PipelineStatus.RUNNING
            ):

                if result.errors:

                    result.status = (
                        PipelineStatus.FAILED
                    )

                else:

                    result.status = (
                        PipelineStatus.COMPLETED
                    )

            result.output_data = (
                current_data
            )

        except Exception as exc:

            message = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            result.errors.append(
                message
            )

            result.status = (
                PipelineStatus.FAILED
            )

        finally:

            result.completed_at = (
                datetime.now()
            )

            result.duration_seconds = max(
                0.0,
                perf_counter()
                - started_timer,
            )

            with self._lock:

                self._status = (
                    result.status
                )

                self._last_result = (
                    result
                )

                self._stop_requested = False

        return result

    # =====================================================
    # REQUEST STOP
    # =====================================================

    def stop(
        self,
    ) -> bool:

        with self._lock:

            if (
                self._status
                != PipelineStatus.RUNNING
            ):

                return False

            self._stop_requested = True

            return True

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        with self._lock:

            if (
                self._status
                == PipelineStatus.RUNNING
            ):

                raise RuntimeError(
                    "Cannot clear running pipeline."
                )

            self._stages.clear()

            self._status = (
                PipelineStatus.IDLE
            )

            self._last_result = None

            self._stop_requested = False

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        with self._lock:

            if (
                self._status
                == PipelineStatus.RUNNING
            ):

                return

            self._status = (
                PipelineStatus.IDLE
            )

            self._stop_requested = False

            self._last_result = None

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def status(
        self,
    ) -> PipelineStatus:

        with self._lock:

            return self._status

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return (
            self.status
            == PipelineStatus.RUNNING
        )

    # =====================================================
    # LAST RESULT
    # =====================================================

    @property
    def last_result(
        self,
    ) -> Optional[
        PipelineResult
    ]:

        with self._lock:

            return self._last_result

    # =====================================================
    # STAGE NAMES
    # =====================================================

    @property
    def stage_names(
        self,
    ) -> List[str]:

        return [

            stage.name

            for stage
            in self.ordered_stages()
        ]

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> Dict[str, Any]:

        last_result = (
            self.last_result
        )

        return {

            "name":
                self.name,

            "status":
                self.status.value,

            "running":
                self.running,

            "stage_count":
                len(
                    self._stages
                ),

            "stages":
                self.stage_names,

            "last_result":
                (
                    last_result.to_dict()
                    if last_result
                    else None
                ),
        }

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._stages
            )


# =========================================================
# GLOBAL PIPELINE
# =========================================================

scanner_pipeline = ScannerPipeline(
    name="StockVersityScannerPipeline"
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def add_scanner_pipeline_stage(
    name: str,
    handler: PipelineHandler,
    *,
    enabled: bool = True,
    stop_on_error: bool = True,
    order: Optional[int] = None,
) -> PipelineStage:

    return scanner_pipeline.add_stage(

        name,

        handler,

        enabled=enabled,

        stop_on_error=stop_on_error,

        order=order,
    )


def execute_scanner_pipeline(
    input_data: Any,
    *,
    context: Optional[
        Dict[str, Any]
    ] = None,
) -> PipelineResult:

    return scanner_pipeline.execute(
        input_data,
        context=context,
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "PipelineStatus",

    "PipelineStageStatus",

    "PipelineHandler",

    "PipelineStage",

    "PipelineStageResult",

    "PipelineResult",

    "ScannerPipeline",

    "scanner_pipeline",

    "add_scanner_pipeline_stage",

    "execute_scanner_pipeline",
]


# ==========================
# END OF FILE
# ==========================