CREATE database PhenixMarket;

DROP TABLE IF EXISTS users
CREATE TABLE users(
     id_users int PRIMARY key IDENTITY(1,1),
	 roles varchar(50) not null,
	 email varchar(50) not null,
	 motdepasse varchar(15) not null
	 );

DROP TABLE IF EXISTS superviseur
CREATE TABLE superviseur(
     id_superviseur int PRIMARY key IDENTITY(1,1),
	 nom varchar(50) not null,
	 prenoms varchar(50) not null,
	 genre varchar(6) not null,
	 telephone varchar(50) not null,
	 id_users int,
	 FOREIGN key (id_users) REFERENCES users(id_users)
	 );

DROP TABLE IF EXISTS gestionnaire_stock
CREATE TABLE gestionnaire_stock(
     id_gestionnaire_stock int PRIMARY key IDENTITY(1,1),
	 nom varchar(50) not null,
	 prenoms varchar(50) not null,
	 genre varchar(10) not null,
	 telephone varchar(50) not null,
	 id_users int,
	 FOREIGN key (id_users) REFERENCES users(id_users)
	 );

	 ALTER TABLE users add  nom varchar(225) not null;
	 ALTER TABLE users add column nom varchar(225) not null,
	 add column prenom varchar(225) not null,
	 add column tel varchar(225) not null,
	 add column genre varchar(225) not null;

	 ALTER TABLE users
ADD prenoms varchar(225) NOT NULL,
    telephone varchar(225) NOT NULL,
    genre varchar(225) NOT NULL;


DROP TABLE IF EXISTS vendeur
CREATE TABLE vendeur(
     id_vendeur int PRIMARY key IDENTITY(1,1),
	 nom varchar(50) not null,
	 prenoms varchar(50) not null,
	 genre varchar(10) not null,
	 telephone varchar(50) not null,
	 id_users int,
	 FOREIGN key (id_users) REFERENCES users(id_users)
	 );

DROP TABLE IF EXISTS client
CREATE TABLE client(
     id_client int PRIMARY key IDENTITY(1,1),
	 nom varchar(50) not null,
	 prenoms varchar(50) not null,
	 genre varchar(10) not null,
	 telephone varchar(50),
	 adresse varchar(50)
	 );

DROP TABLE IF EXISTS categorie
CREATE TABLE categorie(
     id_categorie int PRIMARY key IDENTITY(1,1),
	 nom varchar(50) not null
	 );

DROP TABLE IF EXISTS produit
CREATE TABLE produit(
     id_produit int PRIMARY key IDENTITY(1,1),
	 nom varchar(100) not null,
	 descriptions varchar(100),
	 prixunitaire float not null,
	 id_categorie int,
	 FOREIGN key (id_categorie) REFERENCES categorie(id_categorie)
	 );

DROP TABLE IF EXISTS stock
CREATE TABLE stock(
     id_stock int PRIMARY key IDENTITY(1,1),
	 quantité int not null,
	 datelivraison varchar(20) not null,
	 id_produit int,
	 FOREIGN key (id_produit) REFERENCES produit(id_produit)
	 );

DROP TABLE IF EXISTS vente
CREATE TABLE vente(
     id_vente int PRIMARY key IDENTITY(1,1),
	 id_vendeur int,
	 id_client int,
	 id_produit int,
	 quantite int,
	 montant float,
	 FOREIGN key (id_vendeur) REFERENCES vendeur(id_vendeur),
	 FOREIGN key (id_client) REFERENCES client(id_client),
	 FOREIGN key (id_produit) REFERENCES produit(id_produit),
	 );

	 ALTER TABLE vente
DROP CONSTRAINT id_vendeur;

	 select @@SERVERNAME


	 SELECT TOP (1000) [id_vente]
      ,[id_vendeur]
      ,[id_client]
      ,[id_produit]
      ,[quantite]
      ,[montant]
  FROM [PhenixMarket].[dbo].[vente]


ALTER TABLE users
DROP COLUMN motdepasse;

ALTER TABLE vente
DROP CONSTRAINT FK__vente__id_vendeu__5DCAEF64;

ALTER TABLE vente
ADD CONSTRAINT FK_user_vente

ALTER TABLE users
ADD password varchar(225) NOT NULL;


ALTER TABLE nom_table
ADD nom_colonne1 varchar(225) NOT NULL,
    nom_colonne2 varchar(225) NOT NULL,
    nom_colonne3 varchar(225) NOT NULL,
    nom_colonne4 varchar(225) NOT NULL;


FOREIGN KEY (id_vendeur) REFERENCES users(id_users);
