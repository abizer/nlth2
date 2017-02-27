CREATE TABLE items ("name" TEXT NOT NULL, "group" TEXT NOT NULL, "price" REAL NOT NULL, "cost" REAL NOT NULL, "disabled" INTEGER, "attr" TEXT);
CREATE TABLE transactions ("iid" INTEGER NOT NULL, "name" TEXT NOT NULL, "date" date default current_date, "price" REAL NOT NULL, "open" BOOLEAN, FOREIGN KEY(iid) REFERENCES items(ROWID));
