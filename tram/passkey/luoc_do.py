"""Kho riêng: không đổi su-kien.db, số phiên bản riêng qua cùng cơ chế migration."""
BUOC = {1: (
    'CREATE TABLE nguoi(id BLOB PRIMARY KEY, login TEXT UNIQUE NOT NULL, vai TEXT NOT NULL, bat INT NOT NULL)',
    'CREATE TABLE khoa(id BLOB PRIMARY KEY, nguoi BLOB NOT NULL, public BLOB NOT NULL, dem INT NOT NULL, '
    'ten TEXT NOT NULL, tao REAL NOT NULL, dung REAL, thu REAL)',
    'CREATE TABLE ma(bam TEXT PRIMARY KEY, nguoi BLOB NOT NULL, nguon BLOB, han REAL NOT NULL)',
    'CREATE TABLE phien(bam TEXT PRIMARY KEY, nguoi BLOB NOT NULL, khoa BLOB NOT NULL, '
    'login TEXT NOT NULL, han REAL NOT NULL)',
    'CREATE TABLE hoi(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, challenge BLOB NOT NULL, '
    'loai TEXT NOT NULL, rang TEXT NOT NULL, phien TEXT NOT NULL, ma TEXT NOT NULL, han REAL NOT NULL)',
    'CREATE TABLE quyen(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, phien TEXT NOT NULL, '
    'rang TEXT NOT NULL, han REAL NOT NULL, dung INT NOT NULL DEFAULT 0)',
    'CREATE TABLE tin(id INTEGER PRIMARY KEY, loai TEXT NOT NULL, luc REAL NOT NULL, gui INT NOT NULL DEFAULT 0)',
    'CREATE TABLE thao_tac(ma TEXT PRIMARY KEY, nguoi BLOB NOT NULL, bam TEXT NOT NULL)',
    'CREATE TABLE ket_qua(ma TEXT PRIMARY KEY, nguoi BLOB NOT NULL, rang TEXT NOT NULL, loai TEXT NOT NULL)',
    'CREATE TABLE sai(nguoi BLOB PRIMARY KEY, dem INT NOT NULL, han REAL NOT NULL)',
)}
