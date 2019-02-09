import yaml


class Generator:
    def __init__(self, schema_path):
        self.schema_path = schema_path
        self.tables = []
        self.data = None

    def read_schema(self):
        with open(self.schema_path, 'r') as schema:
            self.data = yaml.load(schema.read())

    def create_table(self, name, data):
        new_table = (
            'DROP TABLE IF EXISTS {name} CASCADE;\n'
            'CREATE TABLE {name} (\n'
            '  id SERIAL,\n'
            '  {fields}\n'
            '  PRIMARY KEY (id)'
            ');\n'
        ).format(
            name=name.lower(),
            fields=',\n  '.join([f'{field} {field_type.upper()}' for field, field_type in data['fields'].items()])
        )
        self.tables.append(new_table)

    def write_to_file(self):
        with open('generated_db.sql', 'w') as f:
            f.write('\n'.join(self.tables))
            f.write('\n')

    def generate(self):
        self.read_schema()

        for table, data in self.data.items():
            self.create_table(table, data)

        self.write_to_file()


if __name__ == '__main__':
    g = Generator('schema.yaml')
    g.generate()
