CREATE TABLE IF NOT EXISTS Kontroll_diagram (
    id INT PRIMARY KEY,
    method_id INT NOT NULL,
    paramname TEXT NOT NULL,
    dimension TEXT,
    revision UNSIGNED INT,
    refmean REAL,
    refstd REAL,
    uncertainty REAL,
    creation_date TEXT NOT NULL,
    creator TEXT NOT NULL,
    comment TEXT,
    FOREIGN KEY(method_id) REFERENCES Modszer(id)
);
CREATE TABLE IF NOT EXISTS Kontroll_meres (
    id INT PRIMARY KEY,
    cc_id INT NOT NULL,
    date TEXT NOT NULL,
    value REAL NOT NULL,
    comment TEXT,
    FOREIGN KEY(cc_id) REFERENCES Kontroll_diagram(cc_id)
);
CREATE TABLE IF NOT EXISTS Referencia_meres (
    id INT PRIMARY KEY,
    cc_id INT NOT NULL,
    date TEXT NOT NULL,
    value REAL NOT NULL,
    comment TEXT,
    FOREIGN KEY(cc_id) REFERENCES Kontroll_diagram(cc_id)
);
CREATE TABLE IF NOT EXISTS Modszer (
    id UNSIGNED INT PRIMARY KEY,
    name TEXT NOT NULL,
    owner TEXT
);
CREATE TABLE IF NOT EXISTS Anyagminta (
    id INTEGER PRIMARY KEY,
    fancyid TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    category TEXT NOT NULL,
    reg_date TEXT NOT NULL,
    expiration TEXT NOT NULL,
    storage TEXT,
    grams DOUBLE,
    used DOUBLE,
    owner_id INT NOT NULL,
    creator_id INT,
    endorser_id INT,
    comment TEXT,
    FOREIGN KEY(owner_id) REFERENCES Allomany(id),
    FOREIGN KEY(creator_id) REFERENCES Allomany(id),
    FOREIGN KEY(endorser_id) REFERENCES Allomany(id)
);
CREATE TABLE IF NOT EXISTS Allomany (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tasz INTEGER NOT NULL,
    lvl INTEGER NOT NULL
);