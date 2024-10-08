import logging
import sys
from dynpy import logger as log
from dynpy.ui.app import AppView
from dynpy.ui.utils import widget as ui


def main():
    logger = logging.getLogger(__name__)
    try:
        app_view = AppView()
        ui.center_on_screen(app_view)
        app_view.mainloop()
    except Exception as ex:  # pylint: disable=broad-except
        logger.exception("Unhandled Exception", exc_info=ex, stack_info=True)
        sys.exit(-1)
    else:
        logger.info('Closing app')


if __name__ == '__main__':
    log.config_logger()
    main()
