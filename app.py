import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pandas as pd


import json

cred_dict = st.secrets["FIREBASE"]
cred = credentials.Certificate(json.loads(json.dumps(cred_dict)))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://grupo10-b7d3b-default-rtdb.firebaseio.com/"
    })


def analizar_historial(moneda_id):
    now = datetime.datetime.now()
    hace_una_hora = now - datetime.timedelta(hours=1)

    base_ref = db.reference("crypto_prices").child(moneda_id)
    historial = base_ref.child("historial").get()
    actual = base_ref.child("actual").get()

    if historial is None or actual is None:
        return None

    precios_filtrados = []
    for timestamp, datos in historial.items():
        try:
            ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if ts >= hace_una_hora:
                precios_filtrados.append(datos["Price"])
        except:
            pass

    if not precios_filtrados:
        return None

    actual_price = actual.get("Price", 0)
    max_1h = max(precios_filtrados)
    min_1h = min(precios_filtrados)
    avg_1h = sum(precios_filtrados) / len(precios_filtrados)
    signal = "B" if actual_price > avg_1h else "S"

    return {
        "Crypto": moneda_id,
        "Actual Price": actual_price,
        "Highest 1H": round(max_1h, 6),
        "Lowest 1H": round(min_1h, 6),
        "AVG Price": round(avg_1h, 6),
        "Signal": signal
    }

cryptos = [
    'bitcoin', 'ethereum', 'binancecoin', 'usd-coin', 'ripple',
    'binance-peg-dogecoin', 'wrapped-solana', 'bridged-tether-fuse',
    'the-open-network', 'ada-the-dog'
]

st.set_page_config(page_title="Crypto Trading Signals", layout="wide")
st.title("📊 Plataforma de Señales de Trading con Criptomonedas")
st.write("Actualización en tiempo real basada en datos desde Firebase.")

resultados = []
for moneda in cryptos:
    r = analizar_historial(moneda)
    if r:
        resultados.append(r)

if resultados:
    df_resultados = pd.DataFrame(resultados)
    st.dataframe(df_resultados, use_container_width=True)
else:
    st.warning("No se pudo recuperar información desde Firebase o no hay datos recientes.")
