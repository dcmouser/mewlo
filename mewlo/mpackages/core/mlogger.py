"""
mlogger.py

"""


# helper imports
import helpers.event.logger as logger



class MewloLogManager(logger.LogManager):
    """
    MewloLogManager - the main supervisor class that manages a collection of Loggers
    """

    def __init__(self, debugmode):
        super(MewloLogManager,self).__init__(debugmode)

    def startup(self, mewlosite, eventlist):
        """Startup everything, we are about to exit."""
        self.mewlosite = mewlosite
        super(MewloLogManager,self).startup()


    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        super(MewloLogManager,self).shutdown()

