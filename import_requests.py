import requests
import pandas as pd


indicators_url1 = {
    "NY.GDP.PCAP.CD":   "bip_pro_kopf",
    "SP.DYN.IMRT.IN":   "saeulingssterblichkeit",
    "SH.XPD.CHEX.GD.ZS": "gesundheitsausgaben_pct_bip",
    "SH.H2O.BASW.ZS":   "zugang_sauberes_wasser",
    "SP.DYN.CBRT.IN":   "geburtenrate",
    "EN.ATM.CO2E.PC":   "co2_pro_kopf",
    "AG.LND.TOTL.K2":   "landflaeche_km2",
}
def url1_request (code, spaltenname, dim): #depending on database, dim may be not necessary
    
    url = (
        f"https://api.worldbank.org/v2/country/all"
        f"/indicator/{code}"
        f"?format=json&date=2000:2021&per_page=5000"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Fehler bei url2 {code}: Status {response.status_code}")
        return None

    data_url1 = response.json()

    # data_url1[0] = Metadaten, data_url1[1] = Messwerte
    if not data_url1[1]:
        print(f"Keine Daten für url1 {code}")
        return None

    df = pd.DataFrame(data_url1[1])

    df_url1 = (
        df_url1[["countryiso3code", "date", "value"]]
        .rename(columns={
            "countryiso3code": "country_code",
            "date": "year",
            "value": spaltenname,
        })
    )

    df_url1["year"] = df_url1["year"].astype(int)

    # Leere Ländercodes entfernen (ohne ISO-3-Code)
    df_url1 = df_url1[df_url1["country_code"] != ""]

    return df_url1


df_worldb = None

for code, spaltenname in indicators_url1.items():
    print(f"Abruf: {spaltenname} ...")
    df_neu = url1_request(code, spaltenname)

    if df_neu is None:
        continue

    if df_worldb is None:
        df_worldb = df_neu
    else:
        df_worldb = df_worldb.merge(
            df_neu,
            on=["country_code", "year"],
            how="outer"
        )

print(f"\nurl1-Datensatz: {df_worldb.shape}")
print(df_worldb.head())

#---------------------------------------------------

indicators_url2 = {
    "WHOSIS_000001":"life_expectancy_at_birth"}





def url2_request (code, spaltenname, dim): #depending on database, dim may be not necessary

   url = (f"https://ghoapi.azureedge.net/api/{code}"
          f"?$filter=date(TimeDimensionBegin) ge 2000-01-01" 
          f"and date(TimeDimensionBegin) lt 2022-01-01") #kann sein das code für zeitspanne anders geschrieben werden muss

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Fehler bei {code}: Status {response.status_code}")
        return None

    data_url1 = response.json()

    # data_url1[0] = Metadaten, data_url1[1] = Messwerte
    if not data_url1[1]:
        print(f"Keine Daten für {code}")
        return None

    df = pd.DataFrame(data_url1[1])

    df_url1 = (
        df_url1[["countryiso3code", "date", "value"]]
        .rename(columns={
            "countryiso3code": "country_code",
            "date":            "year",
            "value":           spaltenname,
        })
    )

    df_url1["year"] = df_url1["year"].astype(int)

    # Leere Ländercodes entfernen (ohne ISO-3-Code)
    df_url1 = df_url1[df_url1["country_code"] != ""]

    return df_url1

# API WHO  WHOSIS_000002 

df_worldb = None

for code, spaltenname in indicators_url2.items():
    print(f"Abruf: {spaltenname} ...")
    df_neu = url2_request(code, spaltenname)

    if df_neu is None:
        continue

    if df_worldb is None:
        df_worldb = df_neu
    else:
        df_worldb = df_worldb.merge(
            df_neu,
            on=["country_code", "year"],
            how="outer"
        )

print(f"\nurl2-Datensatz: {df_worldb.shape}")
print(df_worldb.head())


#---------------------------------------------------


"""
df_who = pd.read_csv("data_life-expectancy-at-birth.csv")

# Nur Gesamtwert (beide Geschlechter)
df_who = df_who[df_who["Dim1"] == "Both sexes"]

# Relevante Spalten auswählen und umbenennen
df_who = (
    df_who[["SpatialDimValueCode", "Period", "Value"]]
    .rename(columns={
        "SpatialDimValueCode": "country_code",
        "Period":              "year",
        "Value":               "lebenserwartung",
    })
)

df_who["year"] = df_who["year"].astype(int)

print(f"\nWHO-Datensatz: {df_who.shape}")
print(df_who.head())"""


# WHO + Weltbank 
df = df_who.merge(
    df_wb,
    on=["country_code", "year"],
    how="left"
)

print(f"\nFinaler Datensatz: {df.shape}")
print(df.head())


# Fehlende Werte pro Spalte 
print("\nFehlende Werte pro Feature:")
print(
    df.isnull()
    .sum()
    .sort_values(ascending=False)
    .to_string()
)