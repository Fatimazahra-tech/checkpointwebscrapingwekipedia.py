import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 1) Fonction pour récupérer et analyser le contenu HTML d'une page Wikipédia
def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()  # Vérifie si la requête a réussi
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


# 2) Fonction pour extraire le titre de l'article
def extract_title(soup):
    title = soup.find("h1")
    return title.get_text(strip=True) if title else "Titre non trouvé"


# 3) Fonction pour extraire le texte de chaque paragraphe
#    et l'associer aux titres correspondants dans un dictionnaire
def extract_paragraphs_by_heading(soup):
    content = {}
    current_heading = "Introduction"
    content[current_heading] = []

    main_content = soup.find("div", class_="mw-parser-output")

    if not main_content:
        return content

    # On parcourt les éléments principaux de l'article
    for element in main_content.find_all(["h2", "h3", "p"], recursive=False):
        if element.name in ["h2", "h3"]:
            heading_text = element.get_text(strip=True)
            # Supprimer le [modifier] ou autres textes parasites si présents
            heading_text = heading_text.replace("[modifier | modifier le code]", "").strip()
            current_heading = heading_text
            content[current_heading] = []

        elif element.name == "p":
            paragraph_text = element.get_text(strip=True)
            if paragraph_text:
                content[current_heading].append(paragraph_text)

    return content


# 4) Fonction pour collecter tous les liens internes Wikipédia
def extract_internal_links(soup, base_url="https://fr.wikipedia.org"):
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Liens internes Wikipédia
        if href.startswith("/wiki/") and ":" not in href:
            full_link = urljoin(base_url, href)
            links.add(full_link)

    return list(links)


# 5) Fonction globale qui regroupe tout
def scrape_wikipedia_page(url):
    soup = get_soup(url)

    data = {
        "url": url,
        "title": extract_title(soup),
        "paragraphs_by_heading": extract_paragraphs_by_heading(soup),
        "internal_links": extract_internal_links(soup)
    }

    return data


# 6) Test sur une page Wikipédia de votre choix
url = "https://fr.wikipedia.org/wiki/Maroc"

result = scrape_wikipedia_page(url)

print("=== TITRE DE L'ARTICLE ===")
print(result["title"])

print("\n=== PARAGRAPHES PAR SECTION ===")
for heading, paragraphs in result["paragraphs_by_heading"].items():
    print(f"\n--- {heading} ---")
    for p in paragraphs:
        print(p)

print("\n=== LIENS INTERNES WIKIPÉDIA ===")
for link in result["internal_links"][:20]:  # afficher seulement les 20 premiers
    print(link)
print(f"\nNombre total de liens internes : {len(result['internal_links'])}")
