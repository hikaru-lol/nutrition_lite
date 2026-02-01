class CalendarError(Exception):
    """カレンダー機能のベース例外"""
    pass


class InvalidDateRangeError(CalendarError):
    """不正な日付範囲エラー"""
    pass