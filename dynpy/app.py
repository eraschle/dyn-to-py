import logging
import sys
from dynpy import logger as log
from dynpy.service.convert import ConvertService
from dynpy.ui.app import ConvertAppView
from dynpy.ui import utils as ui


def main():
    logger = logging.getLogger(__name__)
    service = ConvertService()
    try:
        app_view = ConvertAppView(service)
        ui.center_on_screen(app_view)
        app_view.mainloop()
    except Exception as ex:
        logger.exception("Unhandled Exception", exc_info=ex, stack_info=True)
        sys.exit(1)
    else:
        if service.can_save_config:
            logger.info('Saving config')
            service.config_save()
        logger.info('Closing app')


if __name__ == '__main__':
    log.config_logger()
    main()
