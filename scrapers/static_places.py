"""Kuratierte Liste permanenter Familien-Attraktionen in Berlin + Brandenburg."""

from scrapers.base import BaseScraper

# Jede Attraktion als Dict mit allen relevanten Feldern
_PLACES = [
    # ── Berlin Indoor ─────────────────────────────────────────
    {
        "source_id": "naturkundemuseum",
        "title": "Museum fuer Naturkunde",
        "description": "Dinosaurier-Skelette, interaktive Ausstellungen, Biodiversitaetswand. "
                       "Das groesste Dino-Skelett der Welt (Giraffatitan) begeistert Kinder jeden Alters.",
        "location_name": "Museum fuer Naturkunde",
        "address": "Invalidenstr. 43, 10115 Berlin",
        "lat": 52.5308, "lon": 13.3797,
        "tags": ["indoor", "wissenschaft", "tiere", "kultur"],
        "age_min": 3, "age_max": 99,
        "price_info": "8 EUR / erm. 5 EUR, unter 6 frei",
        "is_permanent": 1,
    },
    {
        "source_id": "technikmuseum",
        "title": "Deutsches Technikmuseum",
        "description": "Flugzeuge, Zuege, Schiffe, Science Center Spectrum mit Experimenten zum Anfassen. "
                       "Rosinenbomber auf dem Dach!",
        "location_name": "Deutsches Technikmuseum",
        "address": "Trebbiner Str. 9, 10963 Berlin",
        "lat": 52.4988, "lon": 13.3816,
        "tags": ["indoor", "wissenschaft", "abenteuer", "kultur"],
        "age_min": 4, "age_max": 99,
        "price_info": "8 EUR / erm. 4 EUR, unter 6 frei",
        "is_permanent": 1,
    },
    {
        "source_id": "machmit-museum",
        "title": "MACHmit! Museum fuer Kinder",
        "description": "Mitmach-Ausstellungen, Kletterregal (7 Etagen!), Druckwerkstatt, "
                       "Seifenwerkstatt. Alles zum Anfassen und Ausprobieren.",
        "location_name": "MACHmit! Museum",
        "address": "Senefelderstr. 5, 10437 Berlin",
        "lat": 52.5383, "lon": 13.4130,
        "tags": ["indoor", "kreativ", "spiel", "handwerk"],
        "age_min": 3, "age_max": 12,
        "price_info": "7.50 EUR, Familienkarte 22 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "labyrinth-kindermuseum",
        "title": "Labyrinth Kindermuseum Berlin",
        "description": "Wechselnde Mitmach-Ausstellungen fuer Kinder. Aktuell: Themen wie "
                       "Umwelt, Zusammenleben, Kreativitaet. Jede Ausstellung ist interaktiv.",
        "location_name": "Labyrinth Kindermuseum",
        "address": "Osloer Str. 12, 13359 Berlin",
        "lat": 52.5573, "lon": 13.3835,
        "tags": ["indoor", "kreativ", "spiel", "kultur"],
        "age_min": 3, "age_max": 11,
        "price_info": "7 EUR, Familien 20 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "fez-berlin",
        "title": "FEZ Berlin",
        "description": "Europas groesstes gemeinnuetziges Kinder- und Jugendfreizeitzentrum. "
                       "Schwimmbad, Theater, Raumfahrtzentrum orbitall, Wochenend-Programme.",
        "location_name": "FEZ Berlin",
        "address": "Str. zum FEZ 2, 12459 Berlin",
        "lat": 52.4543, "lon": 13.5376,
        "tags": ["indoor", "outdoor", "spiel", "wissenschaft", "sport"],
        "age_min": 2, "age_max": 16,
        "price_info": "Tagesticket 4-6 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "legoland-discovery",
        "title": "LEGOLAND Discovery Centre Berlin",
        "description": "Miniland Berlin aus LEGO, 4D-Kino, Drachenbahn, Bau-Workshops. "
                       "Indoor-Spielparadies fuer LEGO-Fans.",
        "location_name": "LEGOLAND Discovery Centre",
        "address": "Potsdamer Str. 4, 10785 Berlin",
        "lat": 52.5094, "lon": 13.3726,
        "tags": ["indoor", "spiel", "kreativ"],
        "age_min": 3, "age_max": 12,
        "price_info": "ab 17 EUR online",
        "is_permanent": 1,
    },
    {
        "source_id": "sealife-berlin",
        "title": "SEA LIFE Berlin",
        "description": "Aquarium mit Unterwassertunnel, Haien, Rochen, tropischen Fischen. "
                       "Interaktive Touchbecken fuer Kinder.",
        "location_name": "SEA LIFE Berlin",
        "address": "Spandauer Str. 3, 10178 Berlin",
        "lat": 52.5202, "lon": 13.4025,
        "tags": ["indoor", "tiere", "wasser", "wissenschaft"],
        "age_min": 2, "age_max": 99,
        "price_info": "ab 16 EUR online",
        "is_permanent": 1,
    },
    # ── Berlin Outdoor ────────────────────────────────────────
    {
        "source_id": "waldhochseilgarten",
        "title": "Waldhochseilgarten Jungfernheide",
        "description": "Kletterpark mitten im Wald mit 10 Parcours, Seilbahnen und Bruecken. "
                       "Kinder-Parcours ab 1.10m Koerpergroesse.",
        "location_name": "Waldhochseilgarten Jungfernheide",
        "address": "Heckerdamm 260, 13627 Berlin",
        "lat": 52.5456, "lon": 13.2866,
        "tags": ["outdoor", "abenteuer", "sport", "natur"],
        "age_min": 6, "age_max": 99,
        "price_info": "ab 22 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "kinderbauernhof-pinke-panke",
        "title": "Kinderbauernhof Pinke-Panke",
        "description": "Kostenloser Bauernhof mitten in Pankow: Ziegen, Schafe, Kaninchen, "
                       "Gaerten, Lagerfeuer. Kinder koennen Tiere fuettern und pflegen.",
        "location_name": "Kinderbauernhof Pinke-Panke",
        "address": "Am Buergerpark 15, 13156 Berlin",
        "lat": 52.5717, "lon": 13.3961,
        "tags": ["outdoor", "tiere", "natur", "kostenlos"],
        "age_min": 0, "age_max": 14,
        "price_info": "Kostenlos (Spenden willkommen)",
        "is_permanent": 1,
    },
    {
        "source_id": "tempelhofer-feld",
        "title": "Tempelhofer Feld",
        "description": "Ehemaliger Flughafen — riesige Freiflaece zum Radfahren, Skaten, "
                       "Drachen steigen, Grillen. Einzigartige Berliner Atmosphaere.",
        "location_name": "Tempelhofer Feld",
        "address": "Tempelhofer Damm, 12101 Berlin",
        "lat": 52.4733, "lon": 13.4014,
        "tags": ["outdoor", "sport", "natur", "kostenlos", "spiel"],
        "age_min": 0, "age_max": 99,
        "price_info": "Kostenlos",
        "is_permanent": 1,
    },
    {
        "source_id": "bvg-faehre-f10",
        "title": "BVG Faehre F10 (Wannsee–Kladow)",
        "description": "Kostenlose Schifffahrt mit BVG-Ticket ueber den Wannsee. "
                       "20 Min. Ueberfahrt mit Blick auf Pfaueninsel. Geheimtipp!",
        "location_name": "BVG Faehre F10",
        "address": "Anlegestelle Wannsee, 14109 Berlin",
        "lat": 52.4172, "lon": 13.1648,
        "tags": ["outdoor", "wasser", "kostenlos", "natur"],
        "age_min": 0, "age_max": 99,
        "price_info": "Im BVG-Ticket enthalten",
        "is_permanent": 1,
        "is_special": 1,
    },
    {
        "source_id": "grunewald-teufelsberg",
        "title": "Teufelsberg + Drachenberg",
        "description": "Wanderung zum Teufelsberg mit Lost-Place-Abhoerstation oben drauf. "
                       "Drachenberg daneben: Perfekt zum Drachen steigen. Toller Blick ueber Berlin.",
        "location_name": "Teufelsberg",
        "address": "Teufelsseechaussee 10, 14193 Berlin",
        "lat": 52.4971, "lon": 13.2413,
        "tags": ["outdoor", "abenteuer", "natur", "sport"],
        "age_min": 5, "age_max": 99,
        "price_info": "Drachenberg kostenlos, Teufelsberg 8 EUR",
        "is_permanent": 1,
        "is_special": 1,
    },
    # ── Brandenburg Tagesausfluege ────────────────────────────
    {
        "source_id": "tropical-islands",
        "title": "Tropical Islands",
        "description": "Tropisches Paradies in einer ehemaligen Luftschiffhalle. "
                       "Regenwald, Suedseestrand, Rutschen, Ballonfahrt. Ganzjaehrig warm.",
        "location_name": "Tropical Islands",
        "address": "Tropical-Islands-Allee 1, 15910 Krausnick",
        "lat": 52.0380, "lon": 13.7569,
        "tags": ["indoor", "wasser", "abenteuer", "spiel"],
        "age_min": 0, "age_max": 99,
        "price_info": "ab 36 EUR Tagesticket",
        "is_permanent": 1,
    },
    {
        "source_id": "filmpark-babelsberg",
        "title": "Filmpark Babelsberg",
        "description": "Film-Erlebnispark: 4D-Kino, Stunt-Show, Vulkan, Horror-Labyrinth, "
                       "Filmkulissen. Saison April–Oktober.",
        "location_name": "Filmpark Babelsberg",
        "address": "Grossbeerenstr. 200, 14482 Potsdam",
        "lat": 52.3859, "lon": 13.1199,
        "tags": ["outdoor", "indoor", "abenteuer", "kultur"],
        "age_min": 4, "age_max": 99,
        "price_info": "ab 23 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "biosphaere-potsdam",
        "title": "Biosphaere Potsdam",
        "description": "Tropenhalle mit 20.000 Pflanzen, Schmetterlings-Haus, Unterwasserwelt, "
                       "Aquarium. Regenwald-Feeling mitten in Potsdam.",
        "location_name": "Biosphaere Potsdam",
        "address": "Georg-Hermann-Allee 99, 14469 Potsdam",
        "lat": 52.4188, "lon": 13.0445,
        "tags": ["indoor", "natur", "tiere", "wissenschaft"],
        "age_min": 2, "age_max": 99,
        "price_info": "11.50 EUR / erm. 8 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "schiffshebewerk-niederfinow",
        "title": "Schiffshebewerk Niederfinow",
        "description": "Spektakulaeres Schiffshebewerk — das aelteste noch arbeitende in Deutschland. "
                       "Neues Hebewerk 2022 eroeffnet. Beeindruckend fuer Technik-Fans!",
        "location_name": "Schiffshebewerk Niederfinow",
        "address": "Hebewerksstr. 52, 16248 Niederfinow",
        "lat": 52.8441, "lon": 13.8240,
        "tags": ["outdoor", "wissenschaft", "abenteuer"],
        "age_min": 4, "age_max": 99,
        "price_info": "5 EUR / erm. 3 EUR",
        "is_permanent": 1,
        "is_special": 1,
    },
    {
        "source_id": "barfusspark-beelitz",
        "title": "Barfusspark Beelitz-Heilstaetten",
        "description": "3.5 km Barfusspfad + Baumkronenpfad ueber den verlassenen Heilstaetten. "
                       "Lost Place + Natur-Erlebnis in einem. Absoluter Geheimtipp!",
        "location_name": "Barfusspark Beelitz",
        "address": "Str. nach Fichtenwalde 13, 14547 Beelitz",
        "lat": 52.2596, "lon": 12.9271,
        "tags": ["outdoor", "natur", "abenteuer"],
        "age_min": 4, "age_max": 99,
        "price_info": "ab 12.50 EUR",
        "is_permanent": 1,
        "is_special": 1,
    },
    {
        "source_id": "karls-erdbeerhof",
        "title": "Karls Erlebnis-Dorf Elstal",
        "description": "Erdbeer-Erlebnishof mit Achterbahnen, Manufakturen, Maislabyrinth (saisonal), "
                       "Tobeland, Kartoffelsackrutschen. Eintritt frei, Attraktionen einzeln.",
        "location_name": "Karls Erlebnis-Dorf",
        "address": "Doebertizer Heide, 14641 Wustermark",
        "lat": 52.5387, "lon": 13.0109,
        "tags": ["outdoor", "indoor", "spiel", "essen", "abenteuer"],
        "age_min": 0, "age_max": 14,
        "price_info": "Eintritt frei, Attraktionen ab 1 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "extavium-potsdam",
        "title": "Extavium Potsdam",
        "description": "Wissenschaftliches Mitmach-Museum: 80+ Exponate zum Anfassen, "
                       "Experimente-Workshops. Physik, Chemie, Biologie spielerisch erleben.",
        "location_name": "Extavium",
        "address": "Am Kanal 57, 14467 Potsdam",
        "lat": 52.3943, "lon": 13.0613,
        "tags": ["indoor", "wissenschaft", "handwerk", "kreativ"],
        "age_min": 3, "age_max": 14,
        "price_info": "9 EUR, Familien 30 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "spreewald-kahnfahrt",
        "title": "Spreewald Kahnfahrt",
        "description": "Traditionelle Kahnfahrt durch die Spreewaldkanaele. "
                       "2-4 Stunden, Gurken-Stopp inklusive. Maerchenhaft!",
        "location_name": "Spreewald (Luebbenau)",
        "address": "Grosser Hafen, 03222 Luebbenau",
        "lat": 51.8657, "lon": 13.9549,
        "tags": ["outdoor", "wasser", "natur", "kultur"],
        "age_min": 3, "age_max": 99,
        "price_info": "ab 12 EUR / Person",
        "is_permanent": 1,
    },
    {
        "source_id": "irrlandia",
        "title": "Irrlandia Storkow — Erlebnispark",
        "description": "Maislabyrinth, Wasser-Spielplatz, Irrgarten, Kletter-Parcours. "
                       "Komplett outdoor, April–Oktober. Wenig bekannt, super fuer Familien.",
        "location_name": "Irrlandia",
        "address": "Zum Wildgehege 1, 15859 Storkow",
        "lat": 52.2496, "lon": 13.9351,
        "tags": ["outdoor", "abenteuer", "spiel", "wasser", "natur"],
        "age_min": 2, "age_max": 14,
        "price_info": "8 EUR / erm. 6 EUR",
        "is_permanent": 1,
        "is_special": 1,
    },
    {
        "source_id": "modellpark-berlin-brandenburg",
        "title": "Modellpark Berlin-Brandenburg",
        "description": "80+ Miniatur-Modelle Berliner und Brandenburger Gebaeude im Massstab 1:25. "
                       "Brandenburger Tor, Reichstag, Schloss Sanssouci — alles in Klein.",
        "location_name": "Modellpark",
        "address": "An der Wuhlheide 81, 12459 Berlin",
        "lat": 52.4559, "lon": 13.5321,
        "tags": ["outdoor", "kultur", "spiel"],
        "age_min": 3, "age_max": 99,
        "price_info": "5 EUR / erm. 3 EUR",
        "is_permanent": 1,
    },
    {
        "source_id": "museumsdorf-dueppel",
        "title": "Museumsdorf Dueppel",
        "description": "Mittelalter-Dorf zum Mitmachen: Brot backen, Wolle spinnen, Schmieden. "
                       "Lebendige Geschichte fuer Kinder. Saison April–Oktober.",
        "location_name": "Museumsdorf Dueppel",
        "address": "Clauertstr. 11, 14163 Berlin",
        "lat": 52.4030, "lon": 13.2397,
        "tags": ["outdoor", "kultur", "handwerk", "kreativ"],
        "age_min": 4, "age_max": 14,
        "price_info": "4 EUR / erm. 2 EUR",
        "is_permanent": 1,
        "is_special": 1,
    },
]


class StaticPlacesScraper(BaseScraper):
    """Kuratierte permanente Attraktionen — kein Web-Scraping noetig."""

    name = "static_places"

    def scrape(self) -> list[dict]:
        return [dict(p) for p in _PLACES]
