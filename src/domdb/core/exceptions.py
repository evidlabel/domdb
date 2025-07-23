class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass


class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass


class EvidConversionError(Exception):
    """Custom exception for EVID conversion errors."""
    pass
