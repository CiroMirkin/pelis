.pragma library

// Nombre de país tal como lo da OMDb → código ISO 3166-1 alfa-2 (el nombre del SVG en banderas/).
// OMDb usa nombres en inglés y a veces históricos; los que ya no existen van al país que los sucedió.
const CODIGOS = {
    "afghanistan": "af", "albania": "al", "algeria": "dz", "andorra": "ad", "angola": "ao",
    "antigua and barbuda": "ag", "argentina": "ar", "armenia": "am", "aruba": "aw", "australia": "au",
    "austria": "at", "azerbaijan": "az", "bahamas": "bs", "bahrain": "bh", "bangladesh": "bd",
    "barbados": "bb", "belarus": "by", "belgium": "be", "belize": "bz", "benin": "bj", "bermuda": "bm",
    "bhutan": "bt", "bolivia": "bo", "bosnia and herzegovina": "ba", "botswana": "bw", "brazil": "br",
    "brunei": "bn", "brunei darussalam": "bn", "bulgaria": "bg", "burkina faso": "bf", "burma": "mm",
    "burundi": "bi", "cambodia": "kh", "cameroon": "cm", "canada": "ca", "cape verde": "cv",
    "cabo verde": "cv", "cayman islands": "ky", "central african republic": "cf", "chad": "td",
    "chile": "cl", "china": "cn", "colombia": "co", "comoros": "km", "congo": "cg",
    "republic of the congo": "cg", "democratic republic of the congo": "cd", "costa rica": "cr",
    "côte d'ivoire": "ci", "cote d'ivoire": "ci", "ivory coast": "ci", "croatia": "hr", "cuba": "cu",
    "curaçao": "cw", "cyprus": "cy", "czech republic": "cz", "czechia": "cz", "czechoslovakia": "cz",
    "denmark": "dk", "djibouti": "dj", "dominica": "dm", "dominican republic": "do",
    "east timor": "tl", "timor-leste": "tl", "ecuador": "ec", "egypt": "eg", "el salvador": "sv",
    "equatorial guinea": "gq", "eritrea": "er", "estonia": "ee", "eswatini": "sz", "swaziland": "sz",
    "ethiopia": "et", "faroe islands": "fo", "fiji": "fj", "finland": "fi", "france": "fr",
    "french polynesia": "pf", "gabon": "ga", "gambia": "gm", "georgia": "ge", "germany": "de",
    "west germany": "de", "east germany": "de", "ghana": "gh", "gibraltar": "gi", "greece": "gr",
    "greenland": "gl", "grenada": "gd", "guadeloupe": "gp", "guam": "gu", "guatemala": "gt",
    "guinea": "gn", "guinea-bissau": "gw", "guyana": "gy", "haiti": "ht", "honduras": "hn",
    "hong kong": "hk", "hungary": "hu", "iceland": "is", "india": "in", "indonesia": "id",
    "iran": "ir", "iraq": "iq", "ireland": "ie", "republic of ireland": "ie", "isle of man": "im",
    "israel": "il", "italy": "it", "jamaica": "jm", "japan": "jp", "jordan": "jo",
    "kazakhstan": "kz", "kenya": "ke", "kiribati": "ki", "korea": "kr", "south korea": "kr",
    "north korea": "kp", "kosovo": "xk", "kuwait": "kw", "kyrgyzstan": "kg", "laos": "la",
    "latvia": "lv", "lebanon": "lb", "lesotho": "ls", "liberia": "lr", "libya": "ly",
    "liechtenstein": "li", "lithuania": "lt", "luxembourg": "lu", "macao": "mo", "macau": "mo",
    "madagascar": "mg", "malawi": "mw", "malaysia": "my", "maldives": "mv", "mali": "ml",
    "malta": "mt", "marshall islands": "mh", "martinique": "mq", "mauritania": "mr",
    "mauritius": "mu", "mexico": "mx", "micronesia": "fm", "moldova": "md", "republic of moldova": "md",
    "monaco": "mc", "mongolia": "mn", "montenegro": "me", "morocco": "ma", "mozambique": "mz",
    "myanmar": "mm", "namibia": "na", "nauru": "nr", "nepal": "np", "netherlands": "nl",
    "netherlands antilles": "cw", "new caledonia": "nc", "new zealand": "nz", "nicaragua": "ni",
    "niger": "ne", "nigeria": "ng", "north macedonia": "mk", "republic of north macedonia": "mk",
    "macedonia": "mk", "norway": "no", "oman": "om", "pakistan": "pk", "palau": "pw",
    "palestine": "ps", "state of palestine": "ps", "occupied palestinian territory": "ps",
    "panama": "pa", "papua new guinea": "pg", "paraguay": "py", "peru": "pe", "philippines": "ph",
    "poland": "pl", "portugal": "pt", "puerto rico": "pr", "qatar": "qa", "réunion": "re",
    "reunion": "re", "romania": "ro", "russia": "ru", "russian federation": "ru", "soviet union": "ru",
    "rwanda": "rw", "saint kitts and nevis": "kn", "saint lucia": "lc",
    "saint vincent and the grenadines": "vc", "samoa": "ws", "san marino": "sm",
    "sao tome and principe": "st", "saudi arabia": "sa", "senegal": "sn", "serbia": "rs",
    "serbia and montenegro": "rs", "yugoslavia": "rs", "federal republic of yugoslavia": "rs",
    "seychelles": "sc", "sierra leone": "sl", "singapore": "sg", "slovakia": "sk",
    "slovenia": "si", "solomon islands": "sb", "somalia": "so", "south africa": "za",
    "south sudan": "ss", "spain": "es", "sri lanka": "lk", "sudan": "sd", "suriname": "sr",
    "sweden": "se", "switzerland": "ch", "syria": "sy", "taiwan": "tw", "tajikistan": "tj",
    "tanzania": "tz", "thailand": "th", "togo": "tg", "tonga": "to", "trinidad and tobago": "tt",
    "tunisia": "tn", "turkey": "tr", "türkiye": "tr", "turkmenistan": "tm", "tuvalu": "tv",
    "uganda": "ug", "ukraine": "ua", "united arab emirates": "ae", "united kingdom": "gb",
    "uk": "gb", "great britain": "gb", "united states": "us", "usa": "us",
    "united states of america": "us", "uruguay": "uy", "uzbekistan": "uz", "vanuatu": "vu",
    "vatican": "va", "holy see (vatican city state)": "va", "venezuela": "ve", "vietnam": "vn",
    "viet nam": "vn", "yemen": "ye", "zambia": "zm", "zimbabwe": "zw"
}

// "Italy, France" → [{nombre: "Italy", codigo: "it"}, {nombre: "France", codigo: "fr"}].
// Sin mapear, codigo queda "" y el país se muestra solo como texto.
function separar(pais) {
    return (pais || "").split(",").map(x => x.trim()).filter(x => x)
        .map(x => ({ nombre: x, codigo: CODIGOS[x.toLowerCase()] || "" }))
}
