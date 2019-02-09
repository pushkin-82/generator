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

    def generate(self):
        """Generate file with statements"""

        self.read_schema()

        for table, data in self.data.items():
            self.create_table(table, data)

        self.timestamps()

        self.write_to_file()


if __name__ == '__main__':
    g = Generator('schema.yaml')
    g.generate()
