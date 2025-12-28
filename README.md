Détection de transactions suspectes LCB-FT – Script Python

Description
-----------
Ce programme permet de détecter automatiquement des transactions potentiellement suspectes
en matière de Lutte contre le Blanchiment de Capitaux et le Financement du Terrorisme (LCB-FT).

Il applique des règles simples basées sur des seuils réglementaires et des typologies courantes
(smurfing, pays à risque, cash in / cash out rapide) afin d’identifier des opérations à analyser
par un analyste conformité.

Le script est à visée pédagogique et ne remplace pas une analyse humaine.

---

Prérequis
---------
- Python 3.8 ou supérieur
- Bibliothèque pandas

Installation de pandas :
pip install pandas

---

Structure attendue du projet
-----------------------------
.
├── data/
│   └── data_fraud.csv
├── script_detection.py
└── README.md (ou README.txt)

---

Données d’entrée
----------------
Le fichier data/data_fraud.csv doit contenir au minimum les colonnes suivantes :

- transaction_id : identifiant unique de la transaction
- client_id : identifiant du client
- date_transaction : date et heure de la transaction
- montant_eur : montant de la transaction en euros
- type_transaction : type d’opération (ex : depot_cash)
- sens : sens de la transaction (IN ou OUT)
- pays_destination : pays de destination des fonds

Les données utilisées dans ce projet sont artificielles et générées à des fins pédagogiques.

---

Règles de détection appliquées
------------------------------
Le script applique trois règles principales :

1. Smurfing
   - Dépôts cash inférieurs à 10 000 €
   - Au moins 5 transactions
   - Sur une période de 7 jours

2. Transactions vers des pays à risque
   - Pays figurant sur des listes à risque (GAFI / UE)
   - Montant supérieur ou égal à 5 000 €

3. Cash in / cash out rapide
   - Transaction entrante suivie d’une transaction sortante
   - Délai maximal de 24 heures entre les deux

Les seuils sont définis directement dans le script et peuvent être modifiés.

---

Exécution du script
-------------------
Depuis la racine du projet, exécuter la commande suivante :

python script_detection.py

---

Résultat attendu
----------------
Le script génère un fichier de sortie nommé :

transactions_suspectes.csv

Ce fichier contient uniquement :
- les transactions détectées comme suspectes
- le motif de détection associé à chaque transaction

La colonne technique indiquant True / False est supprimée avant l’export,
car toutes les lignes du fichier final sont suspectes par définition.

---

Remarques
---------
- Le script repose sur des règles statiques et peut générer des faux positifs ou des faux négatifs.
- Il constitue une base simple pour comprendre la logique de la surveillance transactionnelle LCB-FT.
- Toute décision finale doit être prise par un analyste conformité après analyse du contexte client.

