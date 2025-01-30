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