"""
Static data for name verification app.
Includes nickname mappings, name components, and normalization rules.
"""

# NICKNAME_MAP: bidirectional nickname dictionary
# Maps canonical names to their nicknames/variants
NICKNAME_MAP = {
    "Robert": ["Bob", "Rob", "Bobby", "Robbie"],
    "Elizabeth": ["Liz", "Lisa", "Beth", "Eliza", "Ellie", "Betty", "Bette", "Libby"],
    "William": ["Bill", "Will", "Billy", "Willie"],
    "James": ["Jim", "Jimmy", "Jamie"],
    "John": ["Jack", "Johnny", "Jon"],
    "Margaret": ["Meg", "Peg", "Peggy", "Maggie", "Marge"],
    "Katherine": ["Kate", "Kathy", "Kat", "Kit", "Kay"],
    "Catherine": ["Kate", "Kathy", "Cathy", "Kat", "Kit", "Kay"],
    "Michael": ["Mike", "Mick", "Mickey"],
    "Thomas": ["Tom", "Tommy"],
    "Richard": ["Rich", "Rick", "Dick", "Richie"],
    "Charles": ["Charlie", "Chuck", "Chaz"],
    "Edward": ["Ed", "Eddie", "Ted", "Ned"],
    "George": ["Georgie"],
    "Henry": ["Harry", "Hal"],
    "Joseph": ["Joe", "Joey"],
    "David": ["Dave", "Davy"],
    "Peter": ["Pete"],
    "Andrew": ["Andy", "Drew"],
    "Alexander": ["Alex", "Alec", "Sandy", "Xander"],
    "Christopher": ["Chris"],
    "Daniel": ["Dan", "Danny"],
    "Patrick": ["Pat", "Paddy"],
    "Matthew": ["Matt", "Matty"],
    "Anthony": ["Tony"],
    "Stephen": ["Steve"],
    "Steven": ["Steve"],
    "Sean": ["Shawn", "Shaun"],
    "Sara": ["Sarah"],
    "Ann": ["Anne", "Annie", "Anna"],
    "Susan": ["Sue", "Suzy", "Susie"],
    "Patricia": ["Pat", "Patty", "Trish", "Tricia"],
    "Jennifer": ["Jen", "Jenny"],
    "Barbara": ["Barb", "Barbie"],
    "Dorothy": ["Dot", "Dottie"],
    "Helen": ["Nell", "Nellie"],
    "Nancy": ["Nan"],
    "Mary": ["Molly", "Polly", "Mae", "Maria"],
    "Caroline": ["Carol", "Carrie"],
    "Christine": ["Chris", "Christie", "Tina"],
    "Deborah": ["Deb", "Debbie"],
    "Linda": ["Lindy"],
    "Laura": ["Laurie"],
    "Sandra": ["Sandy"],
    "Janet": ["Jan"],
    "Frances": ["Fran", "Frankie"],
    "Ahmad": ["Ahmed"],
    "Muhammad": ["Mohammed", "Mohamed", "Muhammed"],
    "Abdullah": ["Abdallah"],
    "Abdul": [],
}

# Build NICKNAME_LOOKUP: flat lookup dict where any name maps to its full group
# This enables fast verification of name equivalence
NICKNAME_LOOKUP = {}

for canonical_name, nicknames in NICKNAME_MAP.items():
    # Create the full group including the canonical name and all nicknames
    full_group = {canonical_name.lower()}
    for nickname in nicknames:
        full_group.add(nickname.lower())

    # Map canonical name (lowercase) to the group
    NICKNAME_LOOKUP[canonical_name.lower()] = full_group

    # Map each nickname (lowercase) to the same group
    for nickname in nicknames:
        NICKNAME_LOOKUP[nickname.lower()] = full_group


# NAME_PARTS: dictionary with cultural name components
NAME_PARTS = {
    "arabic_first": [
        "Muhammad", "Ahmad", "Ali", "Fatima", "Aisha", "Mohammed",
        "Abdullah", "Ibrahim", "Hassan", "Hussain", "Omar", "Karim",
        "Layla", "Noor", "Zahra", "Amina", "Leila", "Samira",
        "Tariq", "Jamal", "Rashid", "Hamza", "Khalid", "Samir",
        "Nadia", "Rania", "Hana", "Dina", "Sara", "Yasmin",
        "Zainab", "Maryam", "Amira", "Huda"
    ],
    "arabic_prefix": [
        "al", "abu", "ibn", "bin", "bint", "abd"
    ],
    "arabic_middle": [
        "Rahman", "Rahim", "Hakim", "Karim", "Aziz", "Malik",
        "Salim", "Nasir", "Wahab", "Latif", "Majid", "Qadir",
        "Hamid", "Halim", "Kareem", "Baraka", "Noor", "Sakina",
        "Jawed", "Salam"
    ],
    "western_first": [
        "John", "James", "Robert", "Michael", "William", "David",
        "Richard", "Joseph", "Thomas", "Charles", "Christopher",
        "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
        "Paul", "Andrew", "Kenneth", "George", "Edward", "Brian",
        "Ronald", "Kevin", "Jason", "Matthew", "Gary", "Nicholas",
        "Larry", "Justin", "Scott", "Eric"
    ],
    "western_last": [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
        "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor",
        "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis",
        "Robinson", "Young", "Chavez", "Castillo"
    ],
    "slavic_first": [
        "Ivan", "Vladimir", "Sergei", "Dmitri", "Alexander", "Nikolai",
        "Pavel", "Viktor", "Andrei", "Mikhail", "Alexei", "Yuri",
        "Elena", "Natasha", "Olga", "Irina", "Svetlana", "Anastasia",
        "Marina", "Valentina", "Tatiana", "Lydia"
    ],
    "slavic_last": [
        "Popov", "Sokolov", "Volkov", "Orlov", "Lebedev", "Smirnov",
        "Frolov", "Kuznetsov", "Novikov", "Pavlov", "Ivanov", "Petrov",
        "Antonov", "Stepanov", "Aleksandrov", "Gregorov", "Maksimov",
        "Fedorov", "Mitrofanov", "Zhukov"
    ],
}


# PREFIX_NORMALIZATIONS: dict for prefix equivalence
PREFIX_NORMALIZATIONS = {
    "mc": "mac",
    "mac": "mac",
    "al-": "al",
    "al ": "al",
}


# COMPOUND_SPLITS: dict for known compound name splits
COMPOUND_SPLITS = {
    "abdulrahman": ["abdul", "rahman"],
    "abdulaziz": ["abdul", "aziz"],
    "abdulkarim": ["abdul", "karim"],
    "abdulhamid": ["abdul", "hamid"],
    "abdulwahab": ["abdul", "wahab"],
    "abdullatif": ["abdul", "latif"],
    "abdulmajid": ["abdul", "majid"],
    "abdulqadir": ["abdul", "qadir"],
}
