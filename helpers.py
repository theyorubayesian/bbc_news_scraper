def clean_string(x: str) -> str:
    return (
        x.replace(" ", "_")
        .replace("\\", "")
        .replace("/", "")
        .replace("(", "")
        .replace(")", "")
    )


def _is_valid_url_afr(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")

    if href.startswith("/afrique/articles/") or href.startswith("/afrique/region/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/afrique/monde-")
        or href.startswith("/afrique/region-")
        or href.startswith("/afrique/media-")
        or href.startswith("/afrique")
    ):
        if not (
            href.startswith("/afrique/topics")
            or href.startswith("/afrique/bbc_afrique_radio")
        ):
            return True
    else:
        return False


def _is_valid_url_amh(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")

    if href.startswith("/amharic/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/amharic/news-")
        or href.startswith("/amharic")
    ):
        if not (
            href.startswith("/amharic/topics")
            or href.startswith("/amharic/bbc_amharic_radio")
        ):
            return True
    else:
        return False


def _is_valid_url_gah(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")

    if href.startswith("/gahuza/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/gahuza/amakuru-")
        or href.startswith("/gahuza")
    ):
        if not (
            href.startswith("/gahuza/topics")
        ):
            return True
    else:
        return False


def _is_valid_url_hau(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")

    if href.startswith("/hausa/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/hausa/wasanni")
        or href.startswith("/hausa/labarai")
        or href.startswith("/hausa/media")
        or href.startswith("/hausa")
    ) :
        if not (
            href.startswith("/hausa/topics")
            or href.startswith("/hausa/bbc_hausa_radio/")
        ):
            return True
    else:
        return False


def _is_valid_url_igb(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")

    if href.startswith("/igbo/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/igbo/afirika-")
        or href.startswith("/igbo/media-")
        or href.startswith("/igbo/egwuregwu-")
        or href.startswith("/igbo/")
    ):
        if not href.startswith("/igbo/topics"):
            return True
    else:
        return False


def _is_valid_url_afa(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")

    if href.startswith("/afaanoromoo/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/afaanoromoo/oduu")
        or href.startswith("/afaanoromoo")
    ):
        if not href.startswith("/afaanoromoo/topics"):
            return True
    else:
        return False


def _is_valid_url_som(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")
    
    if href.startswith("/somali/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/somali/cayaaraha") 
        or href.startswith("/somali/war") 
        or href.startswith("/somali/")
    ):
        if not (
            href.startswith("/somali/topics")
            or href.startswith("/somali/bbc_somali_radio/")
        ):
            return True
    else:
        return False


def _is_valid_url_swa(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")
     
    if href.startswith("/swahili/articles/"):
        return True
    elif href.startswith("/swahili/habari-") or href.startswith("/swahili/"):
        if not (
            href.startswith("/swahili/topics")
            or href.startswith("/swahili/michezo")
            or href.startswith("/swahili/bbc_swahili_radio")
            or href.startswith("/swahili/dira-tv")
            or href.startswith('/swahili/media')
            or href.startswith("/swahili/taasisi")
        ):
            if href[-1].isdigit():
                return True
    else:
        return False


def _is_valid_url_tig(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")
     
    if href.startswith("/tigrinya/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/tigrinya/news-")
        or href.startswith("/tigrinya/")
    ):
        if not href.startswith("/tigrinya/topics"):
            return True
    else:
        return False
    
def _is_valid_url_yor(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")
     
    if href.startswith("/yoruba/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/yoruba/afrika")
        or href.startswith("/yoruba")
    ):
        if not href.startswith("/yoruba/topics"):
            return True
    else:
        return False

def _is_valid_url_pid(href: str) -> bool:
    href = href.replace("https://www.bbc.com", "")
     
    if href.startswith("/pidgin/articles/"):
        return True
    elif href[-1].isdigit() and (
        href.startswith("/pidgin/media")
        or href.startswith("/pidgin/popular")
        or href.startswith("/pidgin/tori")
        or href.startswith("/pidgin")
    ):
        if not href.startswith("/pidgin/topics"):
            return True
    else:
        return False


is_valid_url_factory = {
    "afr": _is_valid_url_afr,
    "amh": _is_valid_url_amh,
    "gah": _is_valid_url_gah,
    "hau": _is_valid_url_hau,
    "igb": _is_valid_url_igb,
    "afa": _is_valid_url_afa,
    "som": _is_valid_url_som,
    "swa": _is_valid_url_swa,
    "tig": _is_valid_url_tig,
    "yor": _is_valid_url_yor,
    "pid": _is_valid_url_pid
}