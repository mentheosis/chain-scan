import os, json, traceback
from os.path import dirname, join, realpath
from sqlite3 import connect

class SqlLiteClient:
    def __init__(self, db_file_path, emitterFn=None):
        self.db_file_path = db_file_path
        self.emitterFn = emitterFn

    def __enter__(self):
        try:
            db_path = self.db_file_path
            self.conn = connect(db_path)
            self.c = self.conn.cursor()
            return self
        except:
            self.printOrLog("SqlLiteClient: Could not open db")

    def __exit__(self, exc_type, exc_value, traceback):
            self.conn.close()

    def printOrLog(self, message):
            if self.emitterFn != None:
                self.emitterFn(message)
            else:
                print(message)

    '''
    ################ below this point are kinda silly dev debug functions

    # sql lite schema for reference
    CREATE TABLE sqlite_master (
      type TEXT,
      name TEXT,
      tbl_name TEXT,
      rootpage INTEGER,
      sql TEXT
    );
    '''

    ## just an easy method to explore db file
    def query_and_print(self, query):
        c = self.c

        #input_query = self.transform_query_convenience_shortcuts(query)
        input_query = query.strip()
        self.printOrLog(f"\n query {query}")

        try:
            c.execute(input_query)
            rowct = 1
            for row in c:
                if input_query == 'select * from sqlite_master':
                    self.printOrLog(f"row {rowct}\n {row[0]}, {row[1]}, {row[2]}, {row[3]}")
                    sub_row = row[4].split("\n")
                    for sub in sub_row:
                        self.printOrLog(sub)

                elif query == 'models':
                    j = json.loads(row[0])
                    for item in j:
                        self.printOrLog(f"\n\nNote model: {item}")
                        self.printOrLog(f"Name: {j[item]['name']}\nfields:")
                        for field in j[item]['flds']:
                            self.printOrLog(f"    {field['name']}")
                        self.printOrLog(f"cards:")
                        for card in j[item]['tmpls']:
                            self.printOrLog(f"    {card['name']}")

                elif type(row) is tuple:
                    self.printOrLog(f"\nrow {rowct}")
                    for field in row:
                        if type(field) == str and len(field) > 100:
                            try:
                                j = json.loads(field)
                                self.printOrLog(json.dumps(j,indent=2))
                            except:
                                self.printOrLog(field)
                        else:
                            self.printOrLog(f"{field}")

                else:
                    self.printOrLog(f"\nrow {rowct}\n {row}")
                rowct += 1
        except:
            e = traceback.format_exc()
            self.printOrLog(f"\nError: {e}")
