import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from time import sleep

console = Console()

ascii_title = r"""

   ('-.         .-') _        _   .-')       ('-.          .-')      ('-.   ('-.     _  .-')             ('-. .-. 
  ( OO ).-.    ( OO ) )      ( '.( OO )_   _(  OO)        ( OO ).  _(  OO) ( OO ).-.( \( -O )           ( OO )  / 
  / . --. /,--./ ,--,' ,-.-') ,--.   ,--.)(,------.      (_)---\_)(,------./ . --. / ,------.   .-----. ,--. ,--. 
  | \-.  \ |   \ |  |\ |  |OO)|   `.'   |  |  .---'      /    _ |  |  .---'| \-.  \  |   /`. ' '  .--./ |  | |  | 
.-'-'  |  ||    \|  | )|  |  \|         |  |  |          \  :` `.  |  |  .-'-'  |  | |  /  | | |  |('-. |   .|  | 
 \| |_.'  ||  .     |/ |  |(_/|  |'.'|  | (|  '--.        '..`''.)(|  '--.\| |_.'  | |  |_.' |/_) |OO  )|       | 
  |  .-.  ||  |\    | ,|  |_.'|  |   |  |  |  .--'       .-._)   \ |  .--' |  .-.  | |  .  '.'||  |`-'| |  .-.  | 
  |  | |  ||  | \   |(_|  |   |  |   |  |  |  `---.      \       / |  `---.|  | |  | |  |\  \(_'  '--'\ |  | |  | 
  `--' `--'`--'  `--'  `--'   `--'   `--'  `------'       `-----'  `------'`--' `--' `--' '--'  `-----' `--' `--' 





"""

def print_welcome():
    console.print(Text(ascii_title, style="bold magenta"))
    welcome_text = "[bold green]Welcome to Anime Insight CLI[/bold green]\n" \
                   "[red]Explore anime ratings, posters, and top charts[/red]"
    console.print(Panel(welcome_text, title="[bold magenta]Start[/bold magenta]", border_style="green"))

def print_menu():
    table = Table(title="Main Menu", box=box.DOUBLE_EDGE, border_style="magenta")
    table.add_column("Option", style="bold green")
    table.add_column("Description", style="bold red")
    table.add_row("1", "Search for an anime")
    table.add_row("2", "View top anime")
    table.add_row("3", "Random anime")
    table.add_row("4", "Exit")
    console.print(table)

def rating_to_stars(score):
    stars = int(round(float(score)))
    return "★" * stars + "☆" * (10 - stars)

def fetch_top_anime_anilist():
    url = "https://graphql.anilist.co"
    query = '''
    query {
      Page(perPage: 5) {
        media(type: ANIME, sort: SCORE_DESC) {
          title { romaji }
          averageScore
          coverImage { large }
        }
      }
    }
    '''
    response = requests.post(url, json={"query": query})
    data = response.json()["data"]["Page"]["media"]
    anime_data = []
    for anime in data:
        title = anime["title"]["romaji"]
        score = anime["averageScore"] / 10 if anime["averageScore"] else 0
        image_url = anime["coverImage"]["large"]
        anime_data.append({
            "title": title,
            "score": f"{score:.1f}",
            "stars": rating_to_stars(score),
            "image": image_url
        })
    return anime_data

def fetch_top_anime_kitsu():
    url = "https://kitsu.io/api/edge/anime?sort=-averageRating&page[limit]=5"
    response = requests.get(url)
    data = response.json()["data"]
    anime_data = []
    for anime in data:
        attr = anime["attributes"]
        title = attr["canonicalTitle"]
        score = float(attr["averageRating"] or 0) / 10
        image_url = attr["posterImage"]["original"]
        anime_data.append({
            "title": title,
            "score": f"{score:.1f}",
            "stars": rating_to_stars(score),
            "image": image_url
        })
    return anime_data

def show_top_anime(source):
    console.print(Panel(f"🔥 [bold red]Top Anime Right Now ({source})[/bold red]", border_style="bright_magenta"))
    if source == "AniList":
        top_anime = fetch_top_anime_anilist()
    elif source == "Kitsu":
        top_anime = fetch_top_anime_kitsu()
    else:
        console.print("[red]Unknown source![/red]")
        return
    for anime in top_anime:
        panel_text = (
            f"[bold cyan]{anime['title']}[/bold cyan]\n"
            f"Score: [yellow]{anime['score']}[/yellow]  {anime['stars']}\n"
            f"[blue]Image:[/blue] {anime['image']}"
        )
        console.print(Panel(panel_text, border_style="green"))
        sleep(0.5)

def search_anime_anilist(query):
    url = "https://graphql.anilist.co"
    gql = '''
    query ($search: String) {
      Page(perPage: 5) {
        media(search: $search, type: ANIME) {
          title { romaji }
          siteUrl
        }
      }
    }
    '''
    variables = {"search": query}
    response = requests.post(url, json={"query": gql, "variables": variables})
    data = response.json()["data"]["Page"]["media"]
    anime_list = [f"[bold cyan]{a['title']['romaji']}[/bold cyan] - {a['siteUrl']}" for a in data]
    return anime_list or ["[red]No results found.[/red]"]

def search_anime_kitsu(query):
    url = f"https://kitsu.io/api/edge/anime?filter[text]={query}&page[limit]=5"
    response = requests.get(url)
    data = response.json()["data"]
    anime_list = [f"[bold cyan]{a['attributes']['canonicalTitle']}[/bold cyan] - https://kitsu.io/anime/{a['id']}" for a in data]
    return anime_list or ["[red]No results found.[/red]"]

def random_anime_anilist():
    url = "https://graphql.anilist.co"
    gql = '''
    query {
      Page(perPage: 50) {
        media(type: ANIME, sort: POPULARITY_DESC) {
          title { romaji }
          siteUrl
          description
        }
      }
    }
    '''
    try:
        response = requests.post(url, json={"query": gql})
        data = response.json()["data"]["Page"]["media"]
        if data:
            import random
            anime = random.choice(data)
            return f"[bold cyan]{anime['title']['romaji']}[/bold cyan] - {anime['siteUrl']}"
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    return "[red]No random anime found.[/red]"

def random_anime_kitsu():
    import random
    url = "https://kitsu.io/api/edge/anime?page[limit]=1&page[offset]=" + str(random.randint(0, 10000))
    response = requests.get(url)
    data = response.json()["data"]
    if data:
        a = data[0]
        return f"[bold cyan]{a['attributes']['canonicalTitle']}[/bold cyan] - https://kitsu.io/anime/{a['id']}"
    return "[red]No random anime found.[/red]"

# Main flow
print_welcome()
sleep(1)
print_menu()

option = console.input("\n[bold magenta]Select an option:[/bold magenta] ")

if option == "1":
    source_table = Table(title="Select Source", box=box.SIMPLE, border_style="cyan")
    source_table.add_column("Option", style="bold green")
    source_table.add_column("Source", style="bold yellow")
    source_table.add_row("1", "AniList")
    source_table.add_row("2", "Kitsu")
    console.print(source_table)
    src = console.input("[bold cyan]Choose source (1-2):[/bold cyan] ")
    query = console.input("[bold magenta]Enter anime title:[/bold magenta] ")
    if src == "1":
        results = search_anime_anilist(query)
    elif src == "2":
        results = search_anime_kitsu(query)
    else:
        results = ["[red]Invalid source![/red]"]
    for r in results:
        console.print(r)

elif option == "2":
    source_table = Table(title="Select Source", box=box.SIMPLE, border_style="cyan")
    source_table.add_column("Option", style="bold green")
    source_table.add_column("Source", style="bold yellow")
    source_table.add_row("1", "AniList")
    source_table.add_row("2", "Kitsu")
    console.print(source_table)
    src = console.input("[bold cyan]Choose source (1-2):[/bold cyan] ")
    if src == "1":
        show_top_anime("AniList")
    elif src == "2":
        show_top_anime("Kitsu")
    else:
        console.print("[red]Invalid source![/red]")

elif option == "3":
    source_table = Table(title="Select Source", box=box.SIMPLE, border_style="cyan")
    source_table.add_column("Option", style="bold green")
    source_table.add_column("Source", style="bold yellow")
    source_table.add_row("1", "AniList")
    source_table.add_row("2", "Kitsu")
    console.print(source_table)
    src = console.input("[bold cyan]Choose source (1-2):[/bold cyan] ")
    if src == "1":
        result = random_anime_anilist()
    elif src == "2":
        result = random_anime_kitsu()
    else:
        result = "[red]Invalid source![/red]"
    console.print(result)

elif option == "4":
    console.print("[bold green]Goodbye![/bold green]")
    exit()
else:
    console.print("[red]Invalid option![/red]")
