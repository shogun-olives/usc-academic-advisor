from bs4 import BeautifulSoup as bs
import urllib.request
import ssl
import os


def get_security_context() -> ssl.SSLContext:
    """
    Creates a security context for the webpage.

    Returns:
        ctx (ssl.SSLContext): The security context for the webpage.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def store_webpage(url: str, ctx: ssl.SSLContext, fn: str) -> None:
    """
    stores a webpage in a file

    Args:
        url (str): The URL of the webpage to store.
        ctx (ssl.SSLContext): The security context for the webpage.
        fn (str): The filename to store the webpage in.

    Returns:
        None
    """
    # Try to open the URL and read the page
    with urllib.request.urlopen(url, context=ctx) as page:
        soup = bs(page.read(), "html.parser")

    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "w", encoding="utf-8") as f:
        print(soup, file=f)


def load_webpage(url: str, ctx: ssl.SSLContext) -> bs:
    """
    loads a webpage from a file

    Args:
        url (str): The URL of the webpage to load.
        ctx (ssl.SSLContext): The security context for the webpage.

    Returns:
        soup (BeautifulSoup): The BeautifulSoup object of the loaded webpage.
    """
    with urllib.request.urlopen(url, context=ctx) as page:
        soup = bs(page.read(), "html.parser")
    return soup


def scrape(web_url: str, overwrite: bool = False) -> bs:
    """
    Scrapes a webpage and returns the BeautifulSoup object.
    If the site already exists in cache, it will not overwrite it unless specified.

    Args:
        web_url (str): The URL of the webpage to scrape.
        overwrite (bool): Whether to overwrite the existing file if it exists. (default: False)

    Returns:
        soup (BeautifulSoup): The BeautifulSoup object of the scraped webpage.
    """
    fn = f"./data/cache/scrape/{web_url.removeprefix("https://").removesuffix("/").replace('/', '_')}.html"
    ctx = get_security_context()

    if overwrite or not os.path.exists(fn) or os.path.getsize(fn) == 0:
        store_webpage(web_url, ctx, fn)

    file_url = "file:///" + os.path.abspath(fn)
    soup = load_webpage(file_url, ctx)
    return soup
