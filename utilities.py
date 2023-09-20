import plotly as py
import plotly.figure_factory as ff
import requests
import datetime
import wikipedia


# Create a shared session for making requests
session = requests.Session()

# URL template for the Wikipedia API.
WIKI_API_URL_TEMPLATE = "https://{lang}.wikipedia.org/w/api.php"

# Generate parameters for a Wikipedia API request
def generate_params(page_title, direction, prop):
    """
    This function generates parameters for Wikipedia API requests.

    Args:
        page_title: Title of the Wikipedia page.
        direction: Direction for fetching revisions. Should be 'newer' or 'older'.
        prop: Property to fetch for revisions.

    Returns:
        A dictionary of parameters to be used in a Wikipedia API request.
    """
    return {
        "action": "query",
        "prop": "revisions",
        "titles": page_title,
        "format": "json",
        "rvlimit": 1,
        "rvdir": direction,
        "rvprop": prop,
    }

# Fetch the creation date of a Wikipedia article
def get_creation_date(page_title, lang):
    """
    This function fetches the creation date of a Wikipedia article.

    Args:
        page_title: Title of the Wikipedia page.
        lang: The language edition of Wikipedia to fetch from.

    Returns:
        The creation date of the Wikipedia article as a string in the format YYYY-MM-DD.
    """
    page_title = page_title.replace(" ", "_")
    url = WIKI_API_URL_TEMPLATE.format(lang=lang)
    params = generate_params(page_title, "newer", "timestamp")
    response = session.get(url=url, params=params)
    data = response.json()
    pages = data["query"]["pages"]
    for _, page in pages.items():
        timestamp = page["revisions"][0]["timestamp"]
        creation_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return creation_datetime.strftime("%Y-%m-%d")

# Fetch the last modification date of a Wikipedia article
def get_modification_date(page_title, lang):
    """
    This function fetches the last modification date of a Wikipedia article.

    Args:
        page_title: Title of the Wikipedia page.
        lang: The language edition of Wikipedia to fetch from.

    Returns:
        The last modification date of the Wikipedia article as a string in the format YYYY-MM-DD.
    """
    page_title = page_title.replace(" ", "_")
    url = WIKI_API_URL_TEMPLATE.format(lang=lang)
    params = generate_params(page_title, "older", "timestamp")
    response = session.get(url=url, params=params)
    data = response.json()
    pages = data["query"]["pages"]
    for _, page in pages.items():
        timestamp = page["revisions"][0]["timestamp"]
        modification_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return modification_datetime.strftime("%Y-%m-%d")

# Get first and last revision ID of a Wikipedia article
def get_first_last_revision_id(page_title, lang='en'):
    """
    This function fetches the first and last revision ID of a Wikipedia article.

    Args:
        page_title: Title of the Wikipedia page.
        lang: The language edition of Wikipedia to fetch from.

    Returns:
        The first and last revision IDs of the Wikipedia article.
    """
    page_title = page_title.replace(" ", "_")
    url = WIKI_API_URL_TEMPLATE.format(lang=lang)
    # Fetch the first revision ID
    params_newer = generate_params(page_title, "newer", "ids")
    response_newer = session.get(url=url, params=params_newer)
    data_newer = response_newer.json()
    pages_newer = data_newer["query"]["pages"]
    for _, page in pages_newer.items():
        first_revision_id = page["revisions"][0]["revid"]
    # Fetch the last revision ID
    params_older = generate_params(page_title, "older", "ids")
    response_older = session.get(url=url, params=params_older)
    data_older = response_older.json()
    pages_older = data_older["query"]["pages"]
    for _, page in pages_older.items():
        last_revision_id = page["revisions"][0]["revid"]
    return first_revision_id, last_revision_id

# Calculate the revision frequency of a Wikipedia article
def calculate_revision_frequency(page_title, lang):
    """
    This function calculates the revision frequency of a Wikipedia article.

    Args:
        page_title: Title of the Wikipedia page.
        lang: The language edition of Wikipedia to fetch from.

    Returns:
        The revision frequency of the Wikipedia article.
    """
    first_revision_id, last_revision_id = get_first_last_revision_id(page_title, lang)
    url = f'https://{lang}.wikipedia.org/w/rest.php/v1/page/{page_title.replace(" ", "_")}/history/counts/edits'
    headers = {'User-Agent': 'OpenAI ChatGPT example/0.1 (https://openai.com)'}
    response = requests.get(url, headers=headers, params={'from': first_revision_id, 'to': last_revision_id})
    if response.status_code == 200:
        data = response.json()
        return data['count']
    else:
        return None

# Get the translated name of a Wikipedia article in a specific language
def get_translated_article_name(english_article_name, lang):
    """
    This function fetches the translated name of a Wikipedia article in a specific language.

    Args:
        english_article_name: The English name of the Wikipedia article.
        lang: The language code for the desired language.

    Returns:
        The translated name of the Wikipedia article.
    """
    if lang == 'en':
        return english_article_name
    else:
        url = f'https://en.wikipedia.org/w/api.php?action=query&titles={english_article_name}&prop=langlinks&lllang={lang}&format=json'
        response = requests.get(url)
        data = response.json()
        langlinks = list(data['query']['pages'].values())[0]["langlinks"]
        for langlink in langlinks:
            translated_article_name = langlink["*"]
        return translated_article_name
