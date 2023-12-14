import injector

from controllers.programmer import Programmer
from controllers.data import Data
from controllers.provider import Provider
from controllers.calendar import Calendar


class AppModule(injector.Module):

    @injector.provider
    def provide_calendar(self) -> Calendar:
        return Calendar()
    
    @injector.provider
    def provide_provider(self) -> Provider:
        return Provider()
    
    @injector.provider
    def provide_data(self, provider: Provider) -> Data:
        return Data(provider)

    @injector.provider
    def provide_programmer(self, data: Data, calendar: Calendar) -> Programmer:
        return Programmer(data, calendar)
    
app = injector.Injector(AppModule())