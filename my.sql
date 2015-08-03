PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE currentusers(name TEXT);
CREATE TABLE chats(name TEXT, chat TEXT, time DATETIME);
CREATE TABLE users(name TEXT PRIMARY KEY, password TEXT);
COMMIT;
