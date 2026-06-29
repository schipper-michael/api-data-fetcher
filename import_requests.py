import requests
import pandas as pd
import csv


indicators_url1 = {
    "NY.GDP.PCAP.CD":   "bip_pro_kopf",
    "SP.DYN.IMRT.IN":   "saeuglingssterblichkeit",
    "SH.XPD.CHEX.GD.ZS": "gesundheitsausgaben_pct_bip",
    "SH.H2O.BASW.ZS":   "zugang_sauberes_wasser",
    "SP.DYN.CBRT.IN":   "geburtenrate",
    "EN.GHG.CO2.PC.CE.AR5":   "co2_pro_kopf",
    "AG.LND.TOTL.K2":   "landflaeche_km2"
}
def url1_request (code, spaltenname):  #depending on database, viarble "dimension" may be necessary to add
    
    url = (
        f"https://api.worldbank.org/v2/country/all"
        f"/indicator/{code}"
        f"?format=json&date=2000:2021&per_page=5000"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Fehler bei url2 {code}: Status {response.status_code}")
        return None

    data_url1 = response.json() # weltbank gibt Liste zurück 

    """
    print(type(data_url1))
    print(len(data_url1))
    print(data_url1)
    """
    # data_url1[0] = Metadaten, data_url1[1] = Messwerte
    if not data_url1[1]:
        print(f"Keine Daten für url1 {code}")
        return None

    df_url1 = pd.DataFrame(data_url1[1])

    df_url1 = (
        df_url1[["countryiso3code", "date", "value"]]
        .rename(columns={
            "countryiso3code": "country_code",
            "date": "year",
            "value": spaltenname
        })
    )

    df_url1["year"] = df_url1["year"].astype(int)

    # Leere Ländercodes entfernen (ohne ISO-3-Code)
    df_url1 = df_url1[df_url1["country_code"] != ""]

    return df_url1


df_url1 = None

for code, spaltenname in indicators_url1.items():
    print(f"Abruf: {spaltenname} ...")
    df_url1_new = url1_request(code, spaltenname)

    if df_url1_new is None:
        continue

    if df_url1 is None:
        df_url1 = df_url1_new
    else:
        df_url1 = df_url1.merge(
            df_url1_new,
            on=["country_code", "year"],
            how="outer"
        )

print(f"\nurl1-Datensatz: {df_url1.shape}")
print(df_url1.head())

###---------------------------------------------------

indicators_url2 = {
    "WHOSIS_000001":"life_expectancy_at_birth"}


def url2_request (code, spaltenname): #depending on database, viarble "dimension" may be necessary to add

    url = (f"https://ghoapi.azureedge.net/api/{code}"
           f"?$filter=TimeDim ge 2000 and TimeDim le 2021") #kann sein das code für zeitspanne anders geschrieben werden muss

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Fehler bei {code}: Status {response.status_code}")
        return None

    data_url2 = response.json() #WHO gibt Dictionary zurück

    # data_url2[0] = Metadaten, data_url2[1] = Messwerte
    if not data_url2["value"]:
        print(f"Keine Daten für {code}")
        return None

    df_url2 = pd.DataFrame(data_url2["value"])

    df_url2 = (
        df_url2[["SpatialDim", "TimeDim", "NumericValue"]]
        .rename(columns={
            "SpatialDim":   "country_code",
            "TimeDim":      "year",
            "NumericValue": spaltenname
        })
    )

    df_url2["year"] = df_url2["year"].astype(int)

    # Leere Ländercodes entfernen (ohne ISO-3-Code)
    df_url2 = df_url2[df_url2["country_code"] != ""]

    return df_url2


df_url2 = None

for code, spaltenname in indicators_url2.items():
    print(f"Abruf: {spaltenname} ...")
    df_url2_new = url2_request(code, spaltenname)

    if df_url2_new is None:
        continue

    if df_url2 is None:
        df_url2 = df_url2_new
    else:
        df_url2 = df_url2.merge(
            df_url2_new,
            on=["country_code", "year"],
            how="outer"
        )

print(f"\nurl2-Datensatz: {df_url2.shape}")
print(df_url2.head())


#---------------------------------------------------
# merge und export in csv



# WHO + Weltbank 
df_merged = df_url2.merge(
    df_url1,
    on=["country_code", "year"],
    how="left"
)

print(f"\nFinaler Datensatz: {df_merged.shape}")
print(df_merged.head())


# Fehlende Werte pro Spalte 
print("\nFehlende Werte pro Feature:")
print(
    df_merged.isnull()
    .sum()
    .sort_values(ascending=False)
    .to_string()
)

df_merged.to_csv("output.csv", index="false")