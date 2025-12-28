#définition des règles de détection selon la loi


SEUIL_SMURFING_MONTANT = 10000      # < 10 000 €
#selon le code monétaire et financier : Article L561-15
SEUIL_SMURFING_NB_TX = 5            # nombre de transactions 
#seuil que j'ai choisi  et qui les cas les plus fréquent et très utilisé 
SEUIL_SMURFING_DUREE = "7D"         # sur 7 jours
#de meme ici 
SEUIL_PAYS_RISQUE_MONTANT = 5000    # ≥ 5 000 €
#seuil selon le code monétaire et financier : Article L561-10
SEUIL_CASH_IN_OUT_HEURES = 24       # max 24h entre IN et OUT

pays_risque = [
    "Afrique du Sud", "Algérie", "Angola", "Bulgarie", "Burkina Faso",
    "Cameroun", "Cote dIvoire", "Croatie", "Haiti", "Kenya",
    "Laos", "Liban", "Monaco", "Mozambique", "Namibie",
    "Nepal", "Nigeria", "Republique democratique du Congo",
    "Soudan du Sud", "Tanzanie", "Venezuela", "Vietnam",
    "Iles Vierges britanniques", "Yemen",
    "افغانستان", "Iles Caimans", "Luxembourg"
]

#ici les pays sur liste noire et grise du GAFI et la liste  les pays tiers à hauts
#  risques selon l'UE 

#on prépare les donnnées 
import pandas as pd


df = pd.read_csv("data/data_fraud.csv")
df["date_transaction"] = pd.to_datetime(df["date_transaction"])

# Normalisation des noms de pays en elève les accents et les caractères spéciaux 
df["pays_destination"] = (
    df["pays_destination"]
    .astype(str)
    .str.normalize("NFKD") #ici on sépare les acetns des lettres 
    .str.encode("ascii", errors="ignore") #ici on enlève les accents 
    .str.decode("utf-8") # et aisni on décode en utf-8
)

# Colonnes résultat , on rajoute les colonnes blanchiment d'agent (oui /non) et la raison "reason"
df["is_money_laundering"] = False
df["reason"] = ""

#smurfing detection
#on défini le smurfing en ne gardant que les transactions avec inférieur au seuil 
smurfing = (
    df[
        (df["type_transaction"] == "depot_cash") &
        (df["montant_eur"] < SEUIL_SMURFING_MONTANT)
    ]
    .set_index("date_transaction")
    .groupby("client_id")["transaction_id"]   # 👈 colonne explicite
    .rolling(SEUIL_SMURFING_DUREE)
    .count()                                  # 👈 au lieu de size()
    .reset_index(name="nb_tx")
)
#ensuite on utilise la date comme repère(l54) , et on travail client par client en travaillant sur leur transaction (l55) , sur une durée de 7 jours (L56), et on compte le nombre de transactions (L57), et pour finir on remet sous forme de tableau avec comme nouvelle colonnes nombre de transactions (l57)

clients_smurfing = smurfing[
    smurfing["nb_tx"] >= SEUIL_SMURFING_NB_TX
]["client_id"]

df.loc[df["client_id"].isin(clients_smurfing),
       ["is_money_laundering", "reason"]] = (
    True,
    "Smurfing (depots cash fractionnes)"
)
#pour finir on déclare les clients suspicieux qui ont un nombre de transactions superieur ou égal au seuil (L62-64)
# on localise les trasnactions supsicieuses en les étiquettant (L66-70)


#détection des transactions vers des pays à risques 

mask_pays_risque = (
    df["pays_destination"].isin(pays_risque) &
    (df["montant_eur"] >= SEUIL_PAYS_RISQUE_MONTANT)
)
#ici mask_pays_risque c'est une transaction vers un pays à risque avec un montant au dessus du seuil (L77-80)
df.loc[mask_pays_risque,
       ["is_money_laundering", "reason"]] = (
    True,
    "Transaction vers pays a risque"
)

#et pour finir on localise les trasnactions dans la base de données qui sont respectent les critères précédant pour leur implémenter les informations (L82-86)

#détection cash in / cash out

df = df.sort_values(["client_id", "date_transaction"])
#on classe les transactions par clients ensuite par date (plus ancien au plus récent )

for client_id, tx in df.groupby("client_id"):
    tx = tx.reset_index()
#pour chaque transaction par clients on leur attribue un numéro de ligne 
    for i in range(len(tx) - 1):
        t_in = tx.loc[i]
        t_out = tx.loc[i + 1]
#pour chaque transaction t_in = trasnaction i et out = transaction i+1 
        delai_heures = (
            t_out["date_transaction"] - t_in["date_transaction"]
        ).total_seconds() / 3600
#definition  de la variable delai_heure = le temps en heure entre in et out 
        if (
            t_in["sens"] == "IN" and
            t_out["sens"] == "OUT" and
            delai_heures <= SEUIL_CASH_IN_OUT_HEURES
#ici  le delai entre in/ou est inférieur au seuil alors .....
        ):
            df.loc[
                df["transaction_id"].isin(
                    [t_in["transaction_id"], t_out["transaction_id"]]
                ),
                ["is_money_laundering", "reason"]
            ] = (
                True,
                "Cash in / cash out rapide"
            )

#ducoup ici on localise toutes les transactions qui possèdent un delai inférieur au seuil et le insère vrai + cash in /cash out 
#résultat
suspects = df[df["is_money_laundering"]]
#permet de garder uniquement les transactions suspectent 
suspects = suspects.drop(columns=["is_money_laundering"])
#on supprime la colonne car elle ne donne aucune information utile à part true 
suspects.to_csv("transactions_suspectes.csv", index=False)
#j'exporte le resultat dans un csv , pour éviter une colonne inutile (index=false)
print("Le fichier 'transactions_suspectes.csv' a été créé avec succès")