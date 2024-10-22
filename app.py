import logging
import sys

from dynpy import logger
from dynpy.service.convert import ConvertService
from dynpy.ui.app import DynPyAppView

log = logging.getLogger(__name__)


def show_app(service: ConvertService):
    app_view = DynPyAppView(service)
    app_view.center_on_screen()
    app_view.mainloop()


def close_app(service: ConvertService):
    if service.can_save_config:
        log.info('Saving config')
        service.config_save()
    log.info('Closing app')


def main():
    service = ConvertService()
    try:
        log.info('Starting app')
        show_app(service)
    except Exception as ex:
        log.exception("Unhandled Exception", exc_info=ex, stack_info=True)
        sys.exit(1)
    else:
        close_app(service)


if __name__ == "__main__":
    logger.config_logger(logging.INFO)
    main()
