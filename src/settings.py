"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os

from utils import Utils

VERSION = "0.2"

WP_HOST = Utils.get_optional_env("WP_HOST", "localhost")
WP_PATH = Utils.get_optional_env("WP_PATH", "/")

WP_ADMIN_URL = Utils.get_optional_env("WP_ADMIN_URL", "wordpress.localhost")
WP_USER = 'admin'
WP_PASSWORD = 'passw0rd'

JAHIA_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(PROJECT_PATH, "jahia-data")

# by default the path for the export files is $PROJECT_ROOT/exports
# but it can be overridden by an environment variable
EXPORT_PATH_DEFAULT = os.path.join(PROJECT_PATH, "exports")
EXPORT_PATH = Utils.get_optional_env("EXPORT_PATH", EXPORT_PATH_DEFAULT)

LINE_LENGTH_ON_PPRINT = 150
LINE_LENGTH_ON_EXPORT = LINE_LENGTH_ON_PPRINT + 100

# this list cames from a cross-match of:
#  - all sites listed in Jahia administration (998), based on "site key"
#  - all sites liste in  Natalie's inventory (682), based on sudomain
# = 560 matches

JAHIA_SITES = [
    "3dahm2014",
    "3dcamp",
    "aaas",
    "ablasserlab",
    "acc",
    "acces",
    "accred-doc",
    "accueil",
    "achats",
    "achats-it",
    "acht",
    "acm",
    "adec",
    "adele",
    "adsv",
    "ae",
    "aegc",
    "aegel",
    "aesv",
    "afrotech",
    "alice",
    "amac",
    "anchp",
    "apc3",
    "apel",
    "aphys",
    "apml",
    "apprentis",
    "aprl",
    "aqua",
    "archizoom",
    "aro",
    "artlab",
    "asar",
    "asn",
    "aspg",
    "associations",
    "astie",
    "astrobots",
    "atelierweb2",
    "aumonerie",
    "auwerxlab",
    "bachelor2",
    "Baekkeskov",
    "benchmarking_achats",
    "bioem",
    "bioinspired",
    "biorob",
    "bios",
    "blokeschlab",
    "bluebrain",
    "boiling2012",
    "briskenlab",
    "bst",
    "bubbles",
    "bucherlab",
    "building2050",
    "cag",
    "cag2",
    "callista",
    "cama",
    "camipro",
    "cape",
    "carplat",
    "carriere",
    "cav2015",
    "cce",
    "cclab",
    "ccschool2016",
    "cdh",
    "cdm",
    "cdmit",
    "cds",
    "cdt",
    "ceat",
    "cemi",
    "cesb",
    "cfi",
    "cfi-sinergia",
    "cgd",
    "chili",
    "choros",
    "cibm",
    "cime2",
    "citation",
    "classes",
    "clic",
    "clickers",
    "clipair",
    "clse",
    "clubmontagne",
    "cmcs",
    "cms",
    "cnbi",
    "cnp",
    "cnpa",
    "cns",
    "colelab",
    "compbiol",
    "complexdesign",
    "constamlab",
    "controlegestion",
    "cooperation",
    "cosmo",
    "cosmograil",
    "courtine-lab",
    "cpex",
    "cqfd",
    "cream",
    "crem_ntr",
    "cri",
    "croq",
    "crpp",
    "cryos",
    "csag",
    "cse",
    "csea",
    "csft",
    "csi",
    "csp",
    "csqi",
    "cultures",
    "cvlab2",
    "dabs",
    "data",
    "dcg",
    "dcgprogram",
    "dcsl",
    "dedis",
    "depalma-lab",
    "demo-hd",
    "desl",
    "developpementdurable",
    "dhlab",
    "dias",
    "dii",
    "direction",
    "disal2",
    "discovery",
    "disopt",
    "dit-intra",
    "dln",
    "dualt",
    "duboulelab",
    "dynamic",
    "dynnet",
    "east",
    "echo",
    "ecol",
    "ecos",
    "ecotox",
    "ecps",
    "edlab",
    "eesd",
    "ekv",
    "elab",
    "electrip",
    "elemo",
    "emabm17",
    "emahp",
    "emc",
    "eml",
    "emploi",
    "enable",
    "enac",
    "enac-atelier",
    "enac-innoseed",
    "enac-it3",
    "enacco",
    "enacit2",
    "energy-center",
    "enigma",
    "entc",
    "entrepreneurship",
    "entreprises",
    "enz-group",
    "epsl",
    "equality",
    "esl",
    "eSpace",
    "esplab",
    "ethique",
    "euclid",
    "euler",
    "eurotech",
    "events",
    "exploitation-energies",
    "exploringedges",
    "extremes",
    "facs",
    "facultes-test.epfl.ch",
    "far",
    "fellay-lab",
    "festivaldessciences",
    "fifel",
    "fimap",
    "fix-the-leaky-pipeline",
    "fondationetudiants",
    "fondationrapin",
    "form",
    "formasciences",
    "formation",
    "fraeringlab",
    "fribourg",
    "fsb",
    "fsl",
    "fuelmat",
    "futureetudiant",
    "galatea",
    "gaz-naturel",
    "gbf",
    "gcb",
    "gcc",
    "gce",
    "gcee",
    "gcib",
    "gdp",
    "gecf",
    "gel",
    "gemini-e3",
    "geneva",
    "genomic-resources",
    "geom",
    "gerg",
    "gfo",
    "ggsd",
    "giving",
    "gmf",
    "gonczylab",
    "gpao",
    "gr-co",
    "gr-he",
    "gr-ost",
    "gr-yaz",
    "graefflab",
    "grcel",
    "groupware",
    "gscp",
    "gsf",
    "gtt",
    "gymnases",
    "habitat",
    "habitation",
    "hanahanlab",
    "hantschel-lab",
    "harrislab",
    "hcf",
    "help-gaspar",
    "help-infoscience",
    "help-memento",
    "help-people",
    "helpmy",
    "helpplan",
    "herus",
    "het",
    "hill-lab",
    "hl",
    "hsca",
    "huelsken-lab",
    "hummel-lab",
    "hydroptere",
    "iag",
    "iase",
    "iaus315",
    "ibi",
    "ibois2",
    "ic",
    "ic-aniversary-30-20",
    "ic-gsa",
    "icit",
    "idap",
    "ideas",
    "idevelop",
    "ieee",
    "ifl",
    "iig",
    "iipp",
    "imac",
    "iml",
    "infogest",
    "informationsystem",
    "informdoc",
    "instantlab",
    "integrcity",
    "international",
    "intranet-cms",
    "intranetic",
    "ipep",
    "ipese",
    "ipg",
    "iphys",
    "ipmc",
    "ipsb",
    "ipt",
    "irgc",
    "irrotationnels",
    "irsa",
    "isacademia",
    "iscb",
    "isic",
    "ivrg",
    "jahia6",
    "jensen-lab",
    "klab",
    "kobe-eth",
    "kuhn",
    "la",
    "lab-u",
    "labos",
    "lacal",
    "lacus",
    "lai",
    "lamd",
    "lammm",
    "lamp",
    "lamu",
    "lanes",
    "langues",
    "lap",
    "lapa",
    "lapd",
    "lapis",
    "las",
    "lasen",
    "lasig",
    "laspe",
    "last",
    "lastro",
    "lasur2",
    "lbe",
    "lben",
    "lbm",
    "lbni",
    "lbo",
    "lbp",
    "lbs",
    "lc",
    "lcav",
    "lcb",
    "lcbc",
    "lcbim",
    "lcbm",
    "lcc2",
    "lce",
    "lch",
    "lcmd",
    "lcn",
    "lcom",
    "lcpm",
    "lcpt",
    "lcr",
    "lcs",
    "lcsa",
    "lcsb",
    "lcso",
    "lcvmm",
    "ldcs",
    "ldm",
    "LDQM2016",
    "learning-vernacular",
    "leb",
    "lei",
    "lem2",
    "lemaitrelab",
    "lemr",
    "len",
    "lepa",
    "leso",
    "lfmi",
    "lfo2",
    "lgb",
    "lgc",
    "lhtc",
    "library3",
    "licp",
    "lifmet",
    "lightmatter2017",
    "limnc",
    "limno",
    "lingnerlab",
    "linuxline",
    "linx",
    "lions2",
    "lip",
    "lipid",
    "lis",
    "liv",
    "lmaf",
    "lmam",
    "lmc",
    "lmce",
    "lme",
    "lmer",
    "lmgn",
    "lmh",
    "lmif",
    "lmis1",
    "lmis2",
    "lmis4",
    "lmm",
    "lms",
    "lmsc",
    "lmtm",
    "lmts",
    "lnb",
    "lnce",
    "lnco",
    "lnd",
    "lndc",
    "lne",
    "lnmc",
    "lnnme",
    "lns2",
    "lo",
    "lob",
    "lp",
    "lpac",
    "lpap",
    "lpdc",
    "lpdi",
    "lpi",
    "lpm",
    "lpmat",
    "lpmn",
    "lpmv",
    "lpn",
    "lppc",
    "lppt",
    "lprx",
    "lps",
    "lpsc",
    "lptp",
    "lqg",
    "lqm",
    "lqno",
    "lrese",
    "lrm",
    "lrs",
    "lsbi",
    "lscb",
    "lsci",
    "lse",
    "lsen",
    "lsens",
    "lsi",
    "lsis",
    "lsm",
    "lsme",
    "lsmo",
    "lsms",
    "lsns",
    "lsp",
    "lspm",
    "lspn",
    "lsro",
    "lsu",
    "lsym",
    "ltc",
    "ltcm",
    "lte",
    "lth3",
    "lth5",
    "ltp",
    "ltpn",
    "ltqe",
    "lts3",
    "lts4",
    "lue",
    "luts",
    "lwe",
    "macline",
    "mag",
    "man",
    "manslab",
    "master",
    "master-architecture",
    "math",
    "mathcard",
    "mathgeom",
    "mathicse",
    "mccabelab",
    "mckinneylab",
    "mcs",
    "mcss",
    "mechanicalspectroscopy",
    "mediacom",
    "messaa",
    "metamedia",
    "meu",
    "meylan-lab",
    "mfca2016",
    "mhmc",
    "microbs",
    "microcity",
    "micromanufacturingcenter",
    "mir",
    "mmspl",
    "mns",
    "moocs",
    "mot",
    "mott-physics",
    "mowses",
    "mssql",
    "museephysique",
    "myprint",
    "mysql",
    "naeflab",
    "nal",
    "nanolab",
    "naveiras-lab",
    "nems",
    "network",
    "neuchatel",
    "nextgen",
    "nmnf",
    "nnbe",
    "nomad",
    "ntti2017",
    "nuitdelascience",
    "nutritioncenter",
    "oateslab",
    "oche",
    "octanis",
    "oes",
    "oet2016",
    "OFS-26",
    "ogif",
    "opt",
    "oricchiolab",
    "outilactuhelp",
    "parking",
    "pbl",
    "pcf-ptp",
    "pcrycf",
    "pde",
    "pecdemo",
    "pecf",
    "pel",
    "persat-lab",
    "phd",
    "phosl",
    "photonics",
    "piaget-award",
    "pixe",
    "polar",
    "polychinelle",
    "polycontrat",
    "polyjapan",
    "polylex",
    "poseidon",
    "postal-innovation",
    "postcarworld",
    "powerlab",
    "pps",
    "prix-etudiants",
    "professeurs",
    "professional",
    "prosense",
    "ptnn",
    "pvlabnew",
    "q-lab",
    "qed",
    "qred",
    "quartier-nord",
    "r4l",
    "radtkelab",
    "rdsg",
    "react",
    "recherche",
    "reme",
    "repro",
    "research-ideas",
    "research-office",
    "respect",
    "resslab",
    "restauration",
    "rfic",
    "risd",
    "roberta",
    "robopoly",
    "robot-competition",
    "rolexlearningcenter",
    "rrl",
    "sac",
    "sae",
    "salathelab",
    "save",
    "sber",
    "sbsst",
    "sccerfuries",
    "schoonjans-lab",
    "sd2016",
    "seances_vppl",
    "securite",
    "sesame",
    "sf",
    "sfbe",
    "sfi",
    "sfp",
    "shine",
    "si",
    "signatures",
    "simanislab",
    "simsen",
    "sjb-2017",
    "ska",
    "smal",
    "smb2017",
    "smlms",
    "socialmedialab",
    "sois",
    "sp",
    "space",
    "spmd",
    "sport",
    "sps",
    "sri",
    "ssmlms",
    "stages",
    "stat",
    "statapp",
    "sti",
    "sti-ateliers",
    "stil",
    "studevf",
    "studying",
    "sub",
    "sunmil",
    "suter-lab",
    "sv-in",
    "sv-postdoc",
    "sv-safety",
    "svit",
    "svnew2",
    "swartz-lab",
    "SwissCosmoDays2016",
    "sxl",
    "systems",
    "tan",
    "tang-lab",
    "tcf",
    "tcl",
    "tcs",
    "teaching",
    "teaching-bridge",
    "theos",
    "tic",
    "tip-test",
    "tis",
    "tne",
    "toastmasters",
    "tom",
    "topo",
    "tox",
    "tplaime",
    "transport",
    "travel",
    "tronolab",
    "tsam",
    "uasp",
    "uc",
    "unfold",
    "uniteccsap",
    "univalle",
    "UPJAGGI",
    "upramdya",
    "urbangene",
    "valais",
    "vdg",
    "venice",
    "vivapoly",
    "vlsc",
    "vnlausanne",
    "vpaa",
    "vpiv",
    "vtm",
    "web2010",
    "wio2017",
    "wire",
    "working",
    "yac",
    "yuva",
]
