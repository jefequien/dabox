"""Make a logo."""

DABOX_LOGO = r"""
_|_|_|      _|_|    _|_|_|      _|_|    _|      _| 
_|    _|  _|    _|  _|    _|  _|    _|    _|  _|   
_|    _|  _|_|_|_|  _|_|_|    _|    _|      _|     
_|    _|  _|    _|  _|    _|  _|    _|    _|  _|   
_|_|_|    _|    _|  _|_|_|      _|_|    _|      _| 
"""


def _nice_print(msg, last=False):
    print()
    print("\033[0;31m" + msg + "\033[0m")
    if last:
        print()


def cli_logo():
    """Print logo nicely."""
    _nice_print(DABOX_LOGO, last=True)
