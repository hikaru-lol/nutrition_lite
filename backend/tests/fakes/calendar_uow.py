from app.application.calendar.ports.calendar_unit_of_work_port import CalendarUnitOfWorkPort
from tests.fakes.calendar_repositories import InMemoryCalendarRepository


class FakeCalendarUnitOfWork(CalendarUnitOfWorkPort):
    """カレンダー Unit of Work のフェイク実装"""

    def __init__(self, calendar_repo: InMemoryCalendarRepository):
        self.calendar_repo = calendar_repo
        self._entered = False

    def __enter__(self):
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._entered = False
        # Fakeなので実際のトランザクション処理は不要