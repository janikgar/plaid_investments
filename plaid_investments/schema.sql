DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS account;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE item (
  id TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL,
  access_token TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE account (
  id TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL,
  item_id TEXT NOT NULL,
  friendly_name TEXT NOT NULL,
  official_name TEXT NOT NULL,
  mask TEXT NOT NULL,
  account_type TEXT NOT NULL,
  account_subtype TEXT NOT NULL,
  persistent_account_id TEXT,
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(item_id) REFERENCES item(id)
);