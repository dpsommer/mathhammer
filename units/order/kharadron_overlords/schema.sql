INSERT INTO units (name, movement, save, bravery, wounds) VALUES (
    "Arkanaut Company", 4, 5, 6, 1
);
INSERT INTO units (name, movement, save, bravery, wounds) VALUES (
    "Endrinriggers", 12, 4, 7, 2
);
INSERT INTO units (name, movement, save, bravery, wounds) VALUES (
    "Brokk Grungsson", 12, 3, 8, 8
);



INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Privateer Pistols", 12, "2", 4, 4, 0, "1"
);
INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Captain's Pistol", 12, "2", 4, 3, 0, "1"
);
INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Arkanaut Cutters", 1, "1", 4, 4, 0, "1"
);
INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Captain's Cutter", 1, "2", 4, 4, 0, "1"
);
INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Light Skyhooks", 24, "1", 4, 3, 2, "d3"
);
INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Gun Butts", 1, "1", 4, 5, 0, "1"
);



INSERT INTO models (unit_id, name) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Arkanaut"
);
INSERT INTO models (unit_id, name, type) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Arkanaut Captain",
    "Leader"
);
INSERT INTO models (unit_id, name, type) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    "Arkanaut with Light Skyhook",
    "Special"
);



INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Arkanaut"),
    (SELECT id FROM weapon_profiles WHERE name="Privateer Pistols")
);
INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Arkanaut"),
    (SELECT id FROM weapon_profiles WHERE name="Arkanaut Cutters")
);
INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Arkanaut Captain"),
    (SELECT id FROM weapon_profiles WHERE name="Captain's Pistol")
);
INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Arkanaut Captain"),
    (SELECT id FROM weapon_profiles WHERE name="Captain's Cutter")
);
INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Arkanaut with Light Skyhook"),
    (SELECT id FROM weapon_profiles WHERE name="Light Skyhooks")
);
INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Arkanaut with Light Skyhook"),
    (SELECT id FROM weapon_profiles WHERE name="Gun Butts")
);



INSERT INTO units_unit_types (unit_id, unit_type_id) VALUES (
    (SELECT id FROM units WHERE name="Arkanaut Company"),
    (SELECT id FROM unit_types WHERE name="Battleline")
);
INSERT INTO units_unit_types (unit_id, unit_type_id) VALUES (
    (SELECT id FROM units WHERE name="Brokk Grungsson"),
    (SELECT id FROM unit_types WHERE name="Leader")
);



INSERT INTO keywords (keyword) VALUES ("SKYFARERS");



INSERT INTO units_keywords (unit_id, keyword_id) VALUES (
    (SELECT id FROM units WHERE name="Brokk Grungsson"),
    (SELECT id FROM keywords WHERE keyword="HERO")
);
