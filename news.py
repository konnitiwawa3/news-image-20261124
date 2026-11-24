"""Copy and reporting references for the 24 November Asia morning edition."""

from typing import NamedTuple


class Story(NamedTuple):
    place: str
    region: str
    headline: str
    source: str
    deck: str = ''


LEAD = Story(
    'Asia', 'East Asia', 'AI shares stage a comeback',
    'https://apnews.com/article/feec0e25b9994b1c86b16329cf770192',
    'Nvidia reinstates its chief executive. Seoul surges and Tokyo joins the rally.',
)

FEATURES = (
    Story(
        'South Korea', 'East Asia', 'Seoul scrambles fighter jets',
        'https://m-en.yna.co.kr/view/AEN20261124002251315',
        'Russian planes enter air defense zone.',
    ),
    Story(
        'COP31', 'Mediterranean', 'Climate divide could widen',
        'https://apnews.com/article/ae4c6b1fc5d6b6679947e01c9ff8f607',
        'Experts assess fallout from failed talks.',
    ),
    Story(
        'Nigeria', 'West Africa', 'Borno pupils return to class',
        'https://www.aljazeera.com/news/2026/11/24/borno-school-enrolment-nearly-doubles-after-years-of-conflict',
        'School enrollment has nearly doubled.',
    ),
    Story(
        'Australia', 'Oceania', 'New duty for tech giants',
        'https://www.abc.net.au/news/2026-11-24/federal-politics-live-blog-parliament-nov-24/107417818',
        'An online safety deal clears a hurdle.',
    ),
)

COLUMNS = (
    ('SECURITY & DIPLOMACY', (
        Story(
            'Ukraine / Libya', 'North Africa', 'Libya protests strike on Russian warship',
            'https://www.independent.co.uk/news/world/europe/b3089568.html',
        ),
        Story(
            'European Union', 'Europe', 'EU eyes sanctions on Russian banks',
            'https://apnews.com/article/ecad86868390f6602b346c70d1fa5757',
        ),
        Story(
            'Iran', 'Middle East', 'Tehran vows to resist US blockade',
            'https://www.aljazeera.com/news/2026/11/23/iran-says-it-will-use-all-available-means-to-counter-us-blockade',
        ),
        Story(
            'US / Israel', 'Middle East', 'US and Israel hold talks with Iran in focus',
            'https://apnews.com/article/16e0c2cb05347cfcac068ec4aebb363f',
        ),
        Story(
            'Yemen', 'Middle East', 'Houthi media put port strike toll at 10',
            'https://www.ahmedabadmirror.com/saudi-airstrike-kills-10-people-in-yemen/81926628.html',
        ),
        Story(
            'Poland / NATO', 'Europe', 'NATO meets after missiles land in Poland',
            'https://www.washingtonpost.com/world/2026/11/23/nato-calls-urgent-meeting-string-incidents-escalates-russia-tensions/',
        ),
        Story(
            'Armenia', 'Caucasus', 'Armenia drafts charter to advance peace',
            'https://apnews.com/article/f912a60316e544dbabfba9a1aef4e887',
        ),
        Story(
            'United Kingdom', 'Europe', 'London police seize 500 knives in sweep',
            'https://news.met.police.uk/news/met-arrest-more-than-260-suspects-and-seize-500-knives-in-crime-crackdown-515394',
        ),
    )),
    ('ECONOMY & TRANSPORT', (
        Story(
            'Japan', 'East Asia', 'Factory activity returns to growth',
            'https://malaysia.news.yahoo.com/japans-factory-activity-expands-november-003524309.html',
        ),
        Story(
            'US / Singapore', 'Southeast Asia', 'US moves to blacklist Singapore AI firm',
            'https://www.antaranews.com/berita/5873923',
        ),
        Story(
            'Philippines', 'Southeast Asia', 'Jeepney drivers extend their strike',
            'https://www.gmanetwork.com/news/topstories/nation/1010564/manibela-extends-transport-strike-until-wednesday-november-25-2026/story/',
        ),
        Story(
            'Brazil', 'Latin America', 'Lower house backs main fiscal bill text',
            'https://agenciabrasil.ebc.com.br/politica/noticia/2026-11/camara-aprova-texto-base-do-projeto-de-ajuste-fiscal',
        ),
        Story(
            'East Africa', 'East Africa', 'Oil and conflict squeeze African economies',
            'https://www.standardmedia.co.ke/business/article/2001562873/oil-prices-conflicts-put-pressure-on-africa-s-economic-stability',
        ),
        Story(
            'United States', 'North America', 'Storms threaten holiday travel',
            'https://apnews.com/article/c26a27fd648f766252b54724d8a897a3',
        ),
        Story(
            'Kenya', 'East Africa', 'Midsize firms report pressure to pay bribes',
            'https://www.standardmedia.co.ke/business/article/2001562885/corruption-haven-how-mid-sized-companies-are-forced-into-informal-payments-to-get-things-done',
        ),
        Story(
            'Singapore / Australia', 'Oceania', 'New Sydney airport gets Singapore flights',
            'https://www.abc.net.au/news/2026-11-24/federal-politics-live-blog-parliament-nov-24/107417818',
        ),
    )),
    ('POWER & PUBLIC LIFE', (
        Story(
            'Nigeria', 'West Africa', 'Election body queries 54 officials',
            'https://punchng.com/inec-queries-54-officials-over-voter-registration-breaches/',
        ),
        Story(
            'Paraguay', 'Latin America', 'Two detained in money laundering probe',
            'https://www.ambito.com/politica/detenciones-en-paraguay-n6348438',
        ),
        Story(
            'Gaza', 'Middle East', 'Flooded shelters spur UK call for aid',
            'https://commonsbusiness.parliament.uk/Document/109261/Pdf',
        ),
        Story(
            'South Africa', 'Southern Africa', 'Cartel case widens over police leaks',
            'https://www.sowetan.co.za/news/2026-11-24-how-jmpd-cop-shared-police-intel-with-big-five-cartel/',
        ),
        Story(
            'United States', 'North America', 'FAA examines delivery drone crash',
            'https://www.michiganpublic.org/transportation-infrastructure/2026-11-23/after-drone-crash-lands-on-metro-detroit-rooftop-federal-regulators-are-gathering-information',
        ),
        Story(
            'Hungary', 'Europe', 'Hungarian premier plans trip to Ukraine',
            'https://apnews.com/article/564457bace8a9053b948d3182235cc1f',
        ),
        Story(
            'Australia / Singapore', 'Oceania', 'Canberra weighs safeguards for chip trade',
            'https://www.abc.net.au/news/2026-11-24/federal-politics-live-blog-parliament-nov-24/107417818',
        ),
        Story(
            'Laos / Malaysia', 'Southeast Asia', 'Laos and Malaysia mark 60 years of ties',
            'https://www.kln.gov.my/uploads/post/01M81AFJ6V7859DVPN3MCPH2XS/pdf',
        ),
    )),
    ('CLIMATE & COMMUNITIES', (
        Story(
            'India / Nepal', 'South Asia', 'India pledges $1.6bn for Nepal flood recovery',
            'https://apnews.com/article/6a1b8fa471745cf043480671d066f01e',
        ),
        Story(
            'Indonesia', 'Southeast Asia', 'ASEAN opens disaster response talks',
            'https://thekabarnews.com/indonesia-hosts-asean-disaster-management-meetings/',
        ),
        Story(
            'Thailand', 'Southeast Asia', 'Flooding reaches six southern districts',
            'https://www.thebangkokguide.org/news/2026-11-24/',
        ),
        Story(
            'South Korea', 'East Asia', 'Electric wildfire truck heads for trials',
            'https://www.yna.co.kr/view/AKR20261124034200003',
        ),
        Story(
            'Mexico', 'Latin America', 'Arctic air brings lows near -10 C',
            'https://elpais.com/mexico/2026-11-23/la-masa-de-aire-artico-dejara-temperaturas-de-hasta-10-grados-en-mexico-estos-son-los-estados-afectados.html',
        ),
        Story(
            'Argentina', 'Latin America', 'Storm alerts cover several provinces',
            'https://www.ambito.com/informacion-general/alerta-amarilla-tormentas-y-fuertes-vientos-que-provincias-seran-afectadas-y-como-estara-el-clima-buenos-aires-n6348454',
        ),
        Story(
            'Australia', 'Oceania', 'Existing drugs offer more cancer options',
            'https://thewest.com.au/news/health/missed-chances-to-give-people-existing-cancer-drugs-c-23204658',
        ),
        Story(
            'Mekong region', 'Southeast Asia', 'Three nations meet on arsenic in rivers',
            'https://www.nationthailand.com/news/40073750',
        ),
    )),
)
