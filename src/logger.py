import logging
import sys

from aqt.qt import QWidget

logger = logging.getLogger(__name__)

# Set to `DEBUG` to enable debug messages. Be sure to revert to `WARNING`
# before committing.
logger.setLevel(logging.WARNING)

formatter = logging.Formatter(
    '[%(levelname)s](%(asctime)s) File "%(pathname)s",'
    ' line %(lineno)d, in %(funcName)s: "%(message)s"'
)

# console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def log_widget_destroyed(widget: QWidget) -> None:
    widget.destroyed.connect(
        lambda: logger.debug(f"{widget.__class__.__name__} destroyed!")
    )
