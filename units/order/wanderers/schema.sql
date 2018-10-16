INSERT INTO units (name, movement, save, bravery, wounds) VALUES (
    "Wildwood Rangers", 6, 5, 7, 1
);
INSERT INTO units (name, movement, save, bravery, wounds) VALUES (
    "Glade Guard", 6, 6, 6, 1
);



INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Wildwood Rangers"),
    "Ranger's Draich", 2, "2", 3, 4, 1, "1"
);
INSERT INTO weapon_profiles (unit_id, name, range, attacks, to_hit, to_wound, rend, damage) VALUES (
    (SELECT id FROM units WHERE name="Wildwood Rangers"),
    "Warden's Draich", 2, "3", 3, 4, 1, "1"
);



INSERT INTO models (unit_id, name) VALUES (
    (SELECT id FROM units WHERE name="Wildwood Rangers"),
    "Ranger"
);
INSERT INTO models (unit_id, name, type) VALUES (
    (SELECT id FROM units WHERE name="Wildwood Rangers"),
    "Warden",
    "Leader"
);



INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Ranger"),
    (SELECT id FROM weapon_profiles WHERE name="Ranger's Draich")
);
INSERT INTO models_weapon_profiles (model_id, weapon_profile_id) VALUES (
    (SELECT id FROM models WHERE name="Warden"),
    (SELECT id FROM weapon_profiles WHERE name="Warden's Draich")
);
