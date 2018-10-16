import os
import sqlite3

from dice import DiceRoller

DB_NAME = '%s%s%s' % (os.path.dirname(os.path.abspath(__file__)), os.path.sep, 'units.db')

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


def initialize_db():
    abspath = os.path.abspath('%s%s%s' % (os.path.dirname(os.path.abspath(__file__)), os.path.sep, '..'))
    files = ['%s%s%s' % (path, os.path.sep, file) for path, dirs, files, fd in os.fwalk(abspath) for file in files]
    schema_files = [_ for _ in filter(lambda file: '.sql' in file, files)]
    for schema in schema_files:
        read_schema(schema)


def read_schema(schema_file):
    with open(schema_file, 'rb+') as schema:
        conn.executescript(schema.read().decode('utf-8'))


def fetch_one(table, value, field='name', order_by='id'):
    sql = "SELECT * FROM %s WHERE %s=? ORDER BY %s" % (table, field, order_by)
    cursor.execute(sql, (value,))
    return cursor.fetchone()


def fetch_all(table, value, field='name'):
    sql = "SELECT * FROM %s WHERE %s=?" % (table, field)
    cursor.execute(sql, (value,))
    return cursor.fetchall()


def get_unit_by_name(unit_name):
    return fetch_one(table='units', value=unit_name)


def get_models_by_unit_id(unit_id):
    return fetch_all(table='models', field='unit_id', value=unit_id)


def get_weapon_profiles_by_model_id(model_id):
    return fetch_all(table='models_weapon_profiles', field='model_id', value=model_id)


def get_weapon_profile_by_id(profile_id):
    _, _, weapon_name, weapon_range, attacks, to_hit, to_wound, rend, damage = \
        fetch_one(table='weapon_profiles', field='id', value=profile_id)

    # Convert damage and attacks to integers or callbacks (random values e.g. d3 damage)
    try:
        damage = int(damage)
    except ValueError:
        damage = getattr(DiceRoller, damage)

    try:
        attacks = int(attacks)
    except ValueError:
        attacks = getattr(DiceRoller, attacks)

    return weapon_name, weapon_range, attacks, to_hit, to_wound, rend, damage


def close():
    cursor.close()
    conn.close()

# Run this file to reinitialize the database
if __name__ == '__main__':
    initialize_db()
    close()
