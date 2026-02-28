CREATE SEQUENCE dyst_id_seq
start with 1
increment by 1;

create table Dystrybutor(
id integer primary key default nextval('dyst_id_seq'),
nazwa varchar(100) not null unique,
email varchar(100) not null unique,
constraint chk_email_format check(email ~* '^[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}$')
);

CREATE SEQUENCE klient_id_seq
START WITH 1
INCREMENT BY 1;

CREATE TABLE Klient(
id INTEGER PRIMARY KEY DEFAULT nextval('klient_id_seq'),
imie VARCHAR(50) NOT NULL,
nazwisko VARCHAR(50) NOT NULL,
mail VARCHAR(100) NOT NULL UNIQUE,
telefon VARCHAR(9) NOT NULL UNIQUE,
haslo VARCHAR(255) NOT NULL,
constraint chk_email_format CHECK (mail ~* '^[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}$'),
constraint chk_phone_format CHECK (telefon ~* '^[0-9]{9}$')
);

CREATE SEQUENCE rodzaj_id_seq
start with 1
increment by 1;

CREATE TABLE Rodzaj(
id INTEGER PRIMARY KEY DEFAULT nextval('rodzaj_id_seq'),
nazwa VARCHAR(50) NOT NULL UNIQUE
);

CREATE SEQUENCE gra_id_seq
start with 1
increment by 1;

CREATE TABLE Gra(
id INTEGER PRIMARY KEY DEFAULT nextval('gra_id_seq'),
nazwa VARCHAR(150) NOT NULL,
autor VARCHAR(100) NOT NULL,
cena NUMERIC(6, 2) NOT NULL CHECK (cena >=0),
dystrybutor INTEGER NOT NULL REFERENCES Dystrybutor(id) ON DELETE CASCADE
);

CREATE TABLE Gra_Rodzaj(
gra INTEGER NOT NULL REFERENCES Gra(id) ON DELETE CASCADE,
rodzaj INTEGER NOT NULL REFERENCES Rodzaj(id) ON DELETE CASCADE,
CONSTRAINT key PRIMARY KEY (gra, rodzaj)
);

CREATE SEQUENCE zam_id_seq
start with 1
increment by 1;

CREATE TABLE Zamowienie(
id INTEGER PRIMARY KEY DEFAULT nextval('zam_id_seq'),
data DATE DEFAULT current_date,
status VARCHAR(20) DEFAULT 'nieoplacone' CHECK (status IN ('nieoplacone', 'oplacone', 'zrealizowane', 'anulowane')),
klient INTEGER NOT NULL REFERENCES Klient(id) ON DELETE CASCADE
);

create function check_game()
returns trigger
language plpgsql
as $$
begin
if not exists (select 1 from Gra_Rodzaj where gra=new.id) then
raise exception 'Grze % musi odpowiadac co najmniej jeden rodzaj', new.nazwa;
end if;
return new;
end;
$$;

create constraint trigger trg_check_gra
after insert on Gra
deferrable initially deferred
for each row
execute function check_game();

CREATE SEQUENCE kopia_id_seq
start with 1
increment by 1;

CREATE TABLE Kopia_gry(
id INTEGER PRIMARY KEY DEFAULT nextval('kopia_id_seq'),
klucz_aktywacji VARCHAR(100) NOT NULL UNIQUE,
status VARCHAR(20) DEFAULT 'dostepna' CHECK(status IN ('dostepna', 'wyprzedana', 'zarezerwowana')),
gra INTEGER NOT NULL REFERENCES Gra(id) ON DELETE CASCADE,
klient INTEGER REFERENCES Klient(id) ON DELETE CASCADE
);

CREATE SEQUENCE poz_id_seq
start with 1
increment by 1;

CREATE TABLE Pozycja_zamowienia(
id INTEGER PRIMARY KEY DEFAULT nextval('poz_id_seq'),
ilosc INTEGER NOT NULL CHECK (ilosc > 0),
cena_historyczna NUMERIC(6, 2),
gra INTEGER NOT NULL REFERENCES Gra(id) ON DELETE CASCADE,
zamowienie INTEGER NOT NULL REFERENCES Zamowienie(id) ON DELETE CASCADE
);

CREATE FUNCTION check_gra_delete()
RETURNS TRIGGER
language plpgsql
AS $$
BEGIN
IF NOT EXISTS (SELECT 1 FROM gra_rodzaj WHERE gra = OLD.gra) THEN
        IF EXISTS (SELECT 1 FROM Gra WHERE id = OLD.gra) THEN
             raise exception 'Grze % musi odpowiadac co najmniej jeden rodzaj', OLD.gra;
        END IF;
    END IF;
RETURN OLD;
END;
$$;

CREATE CONSTRAINT TRIGGER trg_gra_del  
AFTER DELETE ON gra_rodzaj
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_gra_delete();

CREATE FUNCTION check_poz()
RETURNS TRIGGER
language plpgsql
AS $$
BEGIN
IF NOT EXISTS (SELECT 1 FROM pozycja_zamowienia WHERE zamowienie = NEW.id) THEN
raise exception 'Zamowienie musi miec pozycje';
END IF;
RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER trg_check_poz
AFTER INSERT ON zamowienie
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_poz();

CREATE FUNCTION set_price()
RETURNS TRIGGER
language plpgsql
AS $$
BEGIN
IF NEW.cena_historyczna IS NULL THEN
SELECT cena INTO NEW.cena_historyczna FROM gra WHERE id=NEW.gra;
END IF;
RETURN NEW;
END;
$$;

CREATE TRIGGER trg_set_price
BEFORE INSERT ON pozycja_zamowienia
FOR EACH ROW
EXECUTE FUNCTION set_price();

CREATE FUNCTION check_kop()
RETURNS TRIGGER
language plpgsql
AS $$
DECLARE
n_gra VARCHAR(150);
d_count INTEGER;
BEGIN
SELECT COUNT(*) INTO d_count FROM kopia_gry WHERE gra = new.gra and status = 'dostepna';
IF d_count < NEW.ilosc THEN
SELECT nazwa INTO n_gra FROM gra WHERE id = NEW.gra;
RAISE EXCEPTION 'Za mało dostępnych kopii gry %. Dostepne: %. Zamawiane: %', n_gra, d_count, NEW.ilosc;
END IF;
RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_kop
BEFORE INSERT ON pozycja_zamowienia
FOR EACH ROW
EXECUTE FUNCTION check_kop();

CREATE OR REPLACE FUNCTION check_num_kop()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_zakupiono BIGINT;   
    v_posiada BIGINT;     
BEGIN
    IF NEW.klient IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT COALESCE(SUM(ilosc), 0) INTO v_zakupiono
    FROM Pozycja_zamowienia pz
    JOIN Zamowienie z ON pz.zamowienie = z.id
    WHERE z.klient = NEW.klient
      AND pz.gra = NEW.gra
	AND z.status IN ('oplacone', 'zrealizowane');
    
    SELECT COUNT(*) INTO v_posiada
    FROM Kopia_gry
    WHERE klient = NEW.klient 
      AND gra = NEW.gra;

    IF v_posiada > v_zakupiono THEN
        RAISE EXCEPTION 'Limit kopii gry (id: %) ktore moga nalezec do klienta (id: %) zostal przekroczony', NEW.gra, NEW.klient;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_num_kop
AFTER UPDATE ON Kopia_gry
FOR EACH ROW
WHEN (OLD.klient IS DISTINCT FROM NEW.klient)
EXECUTE FUNCTION check_num_kop();

CREATE TRIGGER trg_num_kop_in
AFTER INSERT ON Kopia_gry
FOR EACH ROW
WHEN (NEW.klient IS NOT NULL)
EXECUTE FUNCTION check_num_kop();

CREATE OR REPLACE FUNCTION decl_zam()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$                          
DECLARE                     
rec pozycja_zamowienia%rowtype;
BEGIN
IF NEW.status = 'anulowane' THEN
 FOR rec IN (SELECT * FROM pozycja_zamowienia WHERE zamowienie = NEW.id) LOOP
  IF OLD.status = 'zrealizowane' THEN
   UPDATE Kopia_gry SET status = 'dostepna', klient = NULL WHERE id IN (SELECT id FROM Kopia_gry k WHERE k.gra = rec.gra AND klient = NEW.klient AND k.status = 'wyprzedana' LIMIT rec.ilosc FOR UPDATE SKIP LOCKED);
  ELSE
   UPDATE Kopia_gry SET status = 'dostepna' WHERE id IN (SELECT id FROM Kopia_gry k WHERE k.gra = rec.gra AND k.status = 'zarezerwowana' LIMIT rec.ilosc FOR UPDATE SKIP LOCKED);
  END IF;
 END LOOP;
END IF;
RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_decl_zam
AFTER UPDATE ON zamowienie
FOR EACH ROW
WHEN (NEW.status = 'anulowane')
EXECUTE FUNCTION decl_zam();


CREATE PROCEDURE zrealizuj_zamowienie(zam_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
kl INTEGER;
rec pozycja_zamowienia%rowtype;
BEGIN
 IF (SELECT status FROM zamowienie WHERE id=zam_id) != 'nieoplacone' THEN
  RAISE EXCEPTION 'Zamowienie zostalo opłacone lub ma zly status';
 END IF;
 
 UPDATE zamowienie SET status = 'oplacone' WHERE id = zam_id;
 
 SELECT klient INTO kl FROM zamowienie WHERE id = zam_id;
 
 FOR rec IN (SELECT * FROM pozycja_zamowienia WHERE zamowienie = zam_id) LOOP
  UPDATE kopia_gry SET klient = kl WHERE id IN (SELECT id FROM kopia_gry WHERE status = 'zarezerwowana' AND gra=rec.gra LIMIT rec.ilosc FOR UPDATE SKIP LOCKED);
  UPDATE kopia_gry SET status = 'wyprzedana' WHERE gra = rec.gra AND klient = kl AND status = 'zarezerwowana';
 END LOOP;
 
 UPDATE zamowienie SET status = 'zrealizowane' WHERE id = zam_id;

 RAISE NOTICE 'Zamowienie zostalo poprawnie zrealizowane';
END;
$$;

CREATE PROCEDURE zloz_zamowienie(
zm_klient INTEGER,
zm_gry INTEGER[],
zm_ilosci INTEGER[] 
)
LANGUAGE plpgsql
AS $$
DECLARE
zam_id INTEGER;
i INTEGER;
upd_num INTEGER;
BEGIN
IF array_length(zm_gry, 1) != array_length(zm_ilosci, 1) THEN
Raise Exception 'Dlugosci tablic musza byc rowne';
END IF;
INSERT INTO zamowienie(klient) values (zm_klient) RETURNING id INTO zam_id;
FOR i IN 1 .. array_length(zm_gry,1) LOOP
INSERT INTO pozycja_zamowienia(ilosc, gra, zamowienie) VALUES (zm_ilosci[i], zm_gry[i], zam_id);
UPDATE kopia_gry SET status = 'zarezerwowana' WHERE id IN (SELECT id FROM kopia_gry WHERE gra = zm_gry[i] AND status = 'dostepna' LIMIT zm_ilosci[i] FOR UPDATE SKIP LOCKED);
GET DIAGNOSTICS upd_num = ROW_COUNT;
IF upd_num < zm_ilosci[i] THEN
RAISE EXCEPTION 'W trakcie zlozenia zamowienia kopie zostaly sprzedane';
END IF;
END LOOP;
RAISE NOTICE 'Zamowienie zostalo poprawnie stworzone';
END;
$$;
