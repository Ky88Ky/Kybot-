def format_compact_number(n: int) -> str:
    try:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n / 1_000:.1f}K"
        return str(n)
    except Exception:
        return str(n)


def format_compact_time(seconds: int) -> str:
    try:
        minutes = seconds // 60
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        elif minutes > 0:
            return f"{minutes}m"
        return f"{seconds}s"
    except Exception:
        return f"{seconds}s"