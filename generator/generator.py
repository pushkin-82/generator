import yaml


class Generator:
    """Generate SQL-file with statements that create tables and add fields to tables"""

    def __init__(self, schema_path):
        """
        Initializer

        :param schema_path: path to .yaml file that contains schema
        :type schema_path: str
        """
        self.schema_path = schema_path
        self.tables = []
        self.additional_fields = []
        self.triggers = []
        self.data = None

    def read_schema(self):
        """Convert schema to dict as data"""

        with open(self.schema_path, 'r') as schema:
            self.data = yaml.load(schema.read())

    def create_table(self, name, data):
        """Create table named "name", according to data"""

        name = name.lower()
        new_table = (
            'DROP TABLE IF EXISTS {name} CASCADE;\n'
            'CREATE TABLE {name} (\n'
            '  {name}_id SERIAL,\n'
            '  {fields},\n'
            '  PRIMARY KEY (id)\n'
            ');\n'
        ).format(name=name, fields=',\n  '.join([f'{name}_{field} {field_type.upper()}'
                                      for field, field_type in data['fields'].items()])
        )
        self.tables.append(new_table)

    def add_field(self, table, new_field, new_field_type):
        """Add new field to table"""

        table = table.lower()
        self.additional_fields.append(f'ALTER TABLE {table} ADD COLUMN {table}_{new_field} {new_field_type.upper()};\n')

    def create_trigger_updated(self, table):
        func_name = 'update_{table}_timestamp()'.format(table=table.lower())
        trigger = (
            'CREATE FUNCTION {func_name}\n'
            'RETURNS TRIGGER AS $$\n'
            'BEGIN\n'
            '  NEW.{table}_updated = now()\n'
            '  RETURN NEW;\n'
            'END;\n'
            '$$ language \'plpgsql\';\n'
            'CREATE TRIGGER trig_{table}_updated AFTER UPDATE ON {table} FOR EACH ROW EXECUTE FUNCTION {func_name};\n'
        ).format(func_name=func_name, table=table.lower())

        self.triggers.append(trigger)

    def create_trigger_created(self, table):
        func_name = 'create_{table}_timestamp()'.format(table=table.lower())
        trigger = (
            'CREATE FUNCTION {func_name}\n'
            'RETURNS TRIGGER AS $$\n'
            'BEGIN\n'
            '  NEW.{table}_created = now()\n'
            '  RETURN NEW;\n'
            'END;\n'
            '$$ language \'plpgsql\';\n'
            'CREATE TRIGGER trig_{table}_updated AFTER INSERT ON {table} FOR EACH ROW EXECUTE FUNCTION {func_name};\n'
        ).format(func_name=func_name, table=table.lower())

        self.triggers.append(trigger)

    def timestamps(self):
        """Add fields "created" and "updated" to tables in data"""

        for table in self.data.keys():
            self.add_field(table, 'created', 'timestamp')
            self.add_field(table, 'updated', 'timestamp')

    def write_to_file(self):
        """Write statements to file"""

        with open('generated_db.sql', 'w') as f:
            f.write('\n'.join(self.tables))
            f.write('\n')
            f.write('\n'.join(self.additional_fields))
            f.write('\n')
            f.write('\n'.join(self.triggers))

    def generate(self):
        """Generate file with statements"""

        self.read_schema()

        for table, data in self.data.items():
            self.create_table(table, data)

        self.timestamps()

        for table in self.data.keys():
            self.create_trigger_updated(table)
            self.create_trigger_created(table)

        self.write_to_file()


if __name__ == '__main__':
    g = Generator('schema.yaml')
    g.generate()

# CREATE OR REPLACE FUNCTION update_user_timestamp()
# RETURNS TRIGGER AS $$
# BEGIN
#    NEW.user_updated = cast(extract(epoch from now()) as integer);
#    RETURN NEW;
# END;
# $$ language 'plpgsql';
# CREATE TRIGGER "tr_user_updated" BEFORE UPDATE ON "user" FOR EACH ROW EXECUTE PROCEDURE update_user_timestamp();
