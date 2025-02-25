import re


def is_valid_url(url: str):
    regex = re.compile("^(?:https?:)?(?:\\/\\/)?(?:youtu\\.be\\/|(?:www\\.|m\\.)?((youtube\\.com\\/)|(youtu.be\\/))(?:watch|v|embed)(?:\\.php)?(?:\\?.*v=|\\/))([a-zA-Z0-9\\_-]{7,15})(?:[\\?&][a-zA-Z0-9\\_-]+=[a-zA-Z0-9\\_-]+)*(?:[&\\/\\#].*)?$")
    return regex.match(url) != None
