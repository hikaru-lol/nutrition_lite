from abc import ABC, abstractmethod
from app.application.calendar.ports.calendar_repository_port import CalendarRepositoryPort


class CalendarUnitOfWorkPort(ABC):
    """カレンダー用 Unit of Work ポート"""
    calendar_repo: CalendarRepositoryPort

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
