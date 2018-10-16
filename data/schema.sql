DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS unit_types;
DROP TABLE IF EXISTS units_unit_types;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS units_keywords;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS models_weapon_profiles;
DROP TABLE IF EXISTS weapon_profiles;

CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    movement INTEGER NOT NULL,
    save INTEGER NOT NULL,
    bravery INTEGER NOT NULL,
    wounds INTEGER NOT NULL
);

CREATE TABLE unit_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO unit_types (name) VALUES ('Battleline');
INSERT INTO unit_types (name) VALUES ('Leader');
INSERT INTO unit_types (name) VALUES ('Behemoth');
INSERT INTO unit_types (name) VALUES ('War Machine');

CREATE TABLE units_unit_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    unit_type_id INTEGER NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units (id),
    FOREIGN KEY (unit_type_id) REFERENCES unit_types (id)
);

CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL
);

INSERT INTO keywords (keyword) VALUES ('HERO');
INSERT INTO keywords (keyword) VALUES ('MONSTER');
INSERT INTO keywords (keyword) VALUES ('WIZARD');
INSERT INTO keywords (keyword) VALUES ('ORDER');
INSERT INTO keywords (keyword) VALUES ('CHAOS');
INSERT INTO keywords (keyword) VALUES ('DESTRUCTION');
INSERT INTO keywords (keyword) VALUES ('DEATH');

CREATE TABLE units_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units (id),
    FOREIGN KEY (keyword_id) REFERENCES keywords (id)
);

CREATE TABLE weapon_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    range INTEGER NOT NULL,
    attacks TEXT NOT NULL,
    to_hit INTEGER NOT NULL,
    to_wound INTEGER NOT NULL,
    rend INTEGER NOT NULL,
    damage TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units (id)
);

CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'Base',
    FOREIGN KEY (unit_id) REFERENCES units (id)
);

CREATE TABLE models_weapon_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    weapon_profile_id INTEGER NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models (id),
    FOREIGN KEY (weapon_profile_id) REFERENCES weapon_profiles (id)
);
