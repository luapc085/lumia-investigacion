#!/usr/bin/env python3
"""
Descarga datos diarios de MeteoGalicia para TODAS las estaciones de Galicia (2005-2022).

Diferencias con src/descargar_meteo.py (que baja solo las 20 de Ourense):
- La lista de estaciones se pide a la API (no está escrita a mano) + 3 estaciones que
  ya no figuran en la lista pero conservan histórico (comprobado en septiembre de 2026).
- Una peticion por estacion-año en vez de por mes: 18 peticiones por estacion en vez de 216.
  Verificado que devuelve exactamente los mismos datos que la descarga mensual.
- Guarda solo las 12 variables del modelo (el JSON completo pesa el doble).
- Reanudable: si el fichero de una estacion ya existe, la salta.

Uso: python3 scripts/descargar_meteo_galicia.py
Salida: data/raw/meteogalicia_galicia/estacion_<id>.json
"""

import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(HERE, "data", "raw", "meteogalicia_galicia")
API_URL = "https://servizos.meteogalicia.gal/mgrss/observacion/datosDiariosEstacionsMeteo.action"
API_LIST_URL = "https://servizos.meteogalicia.gal/mgrss/observacion/listaEstacionsMeteo.action"
PROVINCIAS = {"A Coruña", "Lugo", "Ourense", "Pontevedra"}

YEAR_START = 2005
YEAR_END = 2022          # Civio ya publico 2022 para Galicia
PAUSE = 1.0              # cortesía con el servidor
RETRIES = 5
BACKOFF = 15             # segundos; se duplica en cada reintento
PAUSA_LARGA = 300        # si falla una estación entera, espera 5 min antes de seguir

# Estaciones con histórico que no aparecen en listaEstacionsMeteo (sondeadas en sept. 2026)
STATIONS_UNLISTED = [10501, 10505, 10506]

VARIABLES = {
    "TA_AVG_1.5m", "TA_MAX_1.5m", "TA_MIN_1.5m",
    "HR_AVG_1.5m", "HR_MIN_1.5m", "PP_SUM_1.5m",
    "VV_AVG_10m", "VV_MAX_10m",
    "IRD_SUM_1.5m", "HSOL_SUM_1.5m", "TO_AVG_1.5m", "PR_AVG_1.5m",
}


def pedir_ano(est_id, year):
    """Un año de datos diarios de una estacion. Reintenta antes de rendirse."""
    params = {"idEst": est_id, "dataIni": f"01/01/{year}", "dataFin": f"31/12/{year}"}
    for intento in range(RETRIES):
        try:
            r = requests.get(API_URL, params=params, timeout=120)
            r.raise_for_status()
            return [d for d in r.json().get("listDatosDiarios", []) if d.get("listaEstacions")]
        except Exception as e:
            espera = BACKOFF * (2 ** intento)
            print(f"    reintento {intento + 1}/{RETRIES} — {est_id} {year} "
                  f"({type(e).__name__}), espera {espera}s", flush=True)
            time.sleep(espera)
    return None   # fallo: se anota y se sigue


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lista = requests.get(API_LIST_URL, timeout=60).json()["listaEstacionsMeteo"]
    activas = {e["idEstacion"]: e for e in lista if e.get("provincia") in PROVINCIAS}
    with open(os.path.join(os.path.dirname(OUTPUT_DIR), "estaciones_lista.json"), "w", encoding="utf-8") as f:
        json.dump(list(activas.values()), f, ensure_ascii=False)

    ids = sorted(activas) + [e for e in STATIONS_UNLISTED if e not in activas]
    print(f"Estaciones de Galicia: {len(activas)} activas + {len(ids) - len(activas)} sin listar = {len(ids)}")
    print(f"Rango: {YEAR_START}-{YEAR_END} | destino: {OUTPUT_DIR}")
    print("=" * 70, flush=True)

    fallos = []
    for i, est_id in enumerate(ids, 1):
        destino = os.path.join(OUTPUT_DIR, f"estacion_{est_id}.json")
        if os.path.exists(destino):
            print(f"[{i}/{len(ids)}] {est_id}: ya descargada, se salta", flush=True)
            continue

        info = activas.get(est_id, {})
        dias = []
        for year in range(YEAR_START, YEAR_END + 1):
            res = pedir_ano(est_id, year)
            if res is None:
                fallos.append((est_id, year))
            else:
                for d in res:
                    est = d["listaEstacions"][0]
                    est["listaMedidas"] = [
                        m for m in est.get("listaMedidas", [])
                        if m.get("codigoParametro") in VARIABLES
                    ]
                    dias.append(d)
            time.sleep(PAUSE)

        if not dias:
            # la estación entera falló: no escribimos fichero (para poder reintentarla)
            # y damos tregua al servidor antes de continuar
            print(f"[{i}/{len(ids)}] {est_id}: 0 días — se reintentará en otra pasada; "
                  f"pausa de {PAUSA_LARGA}s", flush=True)
            time.sleep(PAUSA_LARGA)
            continue

        with open(destino, "w", encoding="utf-8") as f:
            json.dump({
                "idEstacion": est_id,
                "nombre": info.get("estacion", f"sen_listar_{est_id}"),
                "concello": info.get("concello"),
                "provincia": info.get("provincia"),
                "altitude": info.get("altitude"),
                "lat": info.get("lat"),
                "lon": info.get("lon"),
                "utmx": info.get("utmx"),
                "utmy": info.get("utmy"),
                "rango": f"{YEAR_START}-{YEAR_END}",
                "total_dias": len(dias),
                "listDatosDiarios": dias,
            }, f, ensure_ascii=False)

        mb = os.path.getsize(destino) / (1024 * 1024)
        print(f"[{i}/{len(ids)}] {est_id} {info.get('estacion', '?')} "
              f"({info.get('provincia', '?')}): {len(dias)} días, {mb:.1f} MB", flush=True)

    print("=" * 70)
    print(f"FALLOS: {fallos if fallos else 'ninguno'}")
    print("FIN", flush=True)


if __name__ == "__main__":
    main()
