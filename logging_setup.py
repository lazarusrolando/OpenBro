import logging
import os
import warnings


SUPPRESSED_LOG_MESSAGES = (
    "Skipping import of cpp extensions due to incompatible torch version",
    "Redirects are currently not supported in Windows or MacOs",
)


class DependencyWarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not any(text in message for text in SUPPRESSED_LOG_MESSAGES)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "true")
    os.environ.setdefault("BITSANDBYTES_NOWELCOME", "1")

    warnings.filterwarnings(
        "ignore",
        message=r".*Skipping import of cpp extensions due to incompatible torch version.*",
    )
    logging.captureWarnings(True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    dependency_filter = DependencyWarningFilter()
    root_logger = logging.getLogger()
    root_logger.addFilter(dependency_filter)
    for handler in root_logger.handlers:
        handler.addFilter(dependency_filter)

    logging.getLogger("py.warnings").addFilter(dependency_filter)
    logging.getLogger("torchao").setLevel(logging.ERROR)
    logging.getLogger("torch.distributed.elastic.multiprocessing.redirects").setLevel(
        logging.ERROR
    )

    return logging.getLogger(__name__)
