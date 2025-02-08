import unicodedata


def is_allowed_path_character(s, i, r):
    if r == " ":
        return False

    # Check for the most likely first (faster).
    is_allowed = r.isalnum()  # Letter or digit
    is_allowed = is_allowed or r in {".", "/", "\\", "_", "#", "+", "~", "-", "@"}
    is_allowed = is_allowed or unicodedata.category(r).startswith("M")  # Unicode marks
    is_allowed = is_allowed or (
        r == "%" and i + 2 < len(s) and is_hex(s[i + 1]) and is_hex(s[i + 2])
    )
    return is_allowed


def is_hex(c):
    return c in "0123456789abcdefABCDEF"


def sanitize(s):
    will_change = False
    for i, r in enumerate(s):
        if not is_allowed_path_character(s, i, r):
            will_change = True
            break

    if not will_change:
        # Prevent allocation when nothing changes.
        return s

    target = []
    prepend_hyphen = False
    was_hyphen = False

    for i, r in enumerate(s):
        is_allowed = is_allowed_path_character(s, i, r)

        if is_allowed:
            # Track explicit hyphen in input; no need to add a new hyphen if we just saw one.
            was_hyphen = r == "-"

            if prepend_hyphen:
                # If currently have a hyphen, don't prepend an extra one.
                if not was_hyphen:
                    target.append("-")
                prepend_hyphen = False
            target.append(r)
        elif len(target) > 0 and not was_hyphen and r.isspace():
            prepend_hyphen = True

    return "".join(target)


def get_taxonomy(str):
    match str:
        case "book" | "Book":
            return "books"
        case "comic" | "Comic":
            return "comics"
        case "film" | "Film":
            return "films"
        case "graphic-novel" | "Graphic Novel":
            return "graphic-novels"
        case "Live Theatre":
            return "live-theatre"
        case "Manga":
            return "manga"
        case "TV":
            return "tv-series"
        case "video-game" | "Video Game":
            return "video-games"
        case _:
            return str


def get_taxonomy_title(str):
    match str:
        case "tv-series":
            return "TV Series"
        case _:
            return str.replace("-", " ").title()
