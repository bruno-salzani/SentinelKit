def format_size(bytes_size: float) -> str:
    """
    Formats a size in bytes to a human-readable string (e.g., "1.23 MB").
    """
    try:
        bytes_size = float(bytes_size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"
    except (ValueError, TypeError):
        return "0 B"

VIDEO_PORT = 5000
CONTROL_PORT = 5001
CHUNK_SIZE = 4096
