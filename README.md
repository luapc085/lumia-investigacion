# LUMIA — investigación

Traballo de investigación detrás de **[LUMIA](https://lumia.cabanelas.info)**, a aplicación
web que predí o risco diario de incendio forestal en Galicia a partir de datos
meteorolóxicos.

Aquí vive a **continuación** do proxecto: a ampliación de Ourense a toda Galicia, as
medicións que sustentan cada decisión e os scripts que constrúen os datos.

> **De onde vén.** LUMIA naceu como proxecto STEMbach 2024-2026 no IES As Lagoas (Ourense),
> en colaboración coa Universidade de Vigo. Aquel traballo —a memoria, o pipeline orixinal e
> a comparativa co FWI canadense— está arquivado en
> **[stembach-incendios](https://github.com/luapc085/stembach-incendios)**, e este
> repositorio non o duplica: refírese a el.

## Que hai aquí

| | |
|---|---|
| [`docs/ampliacion_galicia.md`](docs/ampliacion_galicia.md) | As medicións: que mellora o modelo, que non, e por que. Con intervalos de confianza. |
| [`scripts/descargar_meteo_galicia.py`](scripts/descargar_meteo_galicia.py) | Descarga as observacións diarias das 155 estaciones de MeteoGalicia (2005-2022). |

Os **datos non están no repositorio** (centos de MB, e rexenerables): os scripts descárganos
das fontes públicas.

## A idea, en breve

Cada fila do dataset é un par **estación meteorolóxica × día**, etiquetado segundo se houbo
ou non incendio nesa zona ese día. As variables son 12 medidas meteorolóxicas e 10 derivadas
que capturan a seca e a tendencia (días sen choiva, precipitación acumulada, medias móbiles).
Sobre iso adéstrase un Random Forest.

O modelo **non predí incendios: predí condicións favorables a incendio**. Un risco alto non
significa que vaia haber lume, senón que se o hai, atopará condicións para arder.

## Fontes de datos (públicas)

| Fonte | Que achega |
|---|---|
| [Fundación Civio / EGIF](https://datos.civio.es/dataset/todos-los-incendios-forestales/) | Rexistro oficial de incendios: data, coordenadas, superficie |
| [API de MeteoGalicia](https://servizos.meteogalicia.gal/mgrss/observacion/datosDiariosEstacionsMeteo.action) | Observacións diarias das estacións |
| [MeteoSIX](https://www.meteogalicia.gal/web/modelos-numericos/meteosix) | Predición meteorolóxica (modelo WRF 4 km) para o risco a catro días |
| [EFFIS / Copernicus](https://forest-fire.emergency.copernicus.eu) | Perímetros de superficie queimada, para os anos que o rexistro oficial aínda non publicou |

## En que punto está

- Dataset de **toda Galicia** (155 estacións, 2005-2022) en construción.
- O modelo de Ourense **non se toca**: segue sendo o que se defendeu no STEMbach. O de
  Galicia é un modelo novo e aparte, cunha páxina propia na aplicación.
- Seguinte liña de traballo: **vexetación e estado do combustible** (NDVI, uso do solo), que
  é o teito que a memoria orixinal xa identificaba.

## Licenza

Código baixo licenza MIT (ver [`LICENSE`](LICENSE)).

Os **datos** teñen as súas propias condicións e non son deste proxecto: cita a Fundación
Civio (a partir da Estatística Xeral de Incendios Forestais do Ministerio), MeteoGalicia
(Xunta de Galicia) e Copernicus EFFIS se os reutilizas.
