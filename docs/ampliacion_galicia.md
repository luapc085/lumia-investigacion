# Ampliación de Ourense a toda Galicia — medicións

Todas as cifras deste documento saen de experimentos sobre datos reais (outubro de 2026).
O que non está medido dise que non está medido.

## Punto de partida

O modelo do proxecto académico usa **20 estacións de Ourense** e 22 variables
meteorolóxicas, e obtén **PR-AUC 0,1485** no seu test (2019-2021), o que son **8,5 veces
mellor que o azar** (só o 1,74 % dos pares estación-día teñen incendio).

Galicia ten **155 estacións meteorolóxicas activas** e, no rexistro oficial de incendios
(Civio/EGIF), **16.581 incendios con coordenadas entre 2005 e 2022** (438.752 ha):

| Provincia | Incendios |
|---|---:|
| Ourense | 7.886 |
| A Coruña | 3.644 |
| Pontevedra | 2.734 |
| Lugo | 2.317 |

## Como se mide (e por que o PR-AUC non se compara entre territorios)

**PR-AUC depende da proporción de positivos.** En Galicia só o 0,48 % dos pares estación-día
teñen incendio, fronte ao 1,74 % de Ourense: o mesmo modelo dá un número máis baixo en
Galicia sen ser peor. Por iso aquí todo se expresa tamén en **"veces mellor que o azar"**
(PR-AUC dividido pola proporción de positivos), e os modelos compáranse sempre **sobre o
mesmo exame**.

Control de reprodutibilidade: reentrenar co dataset orixinal devolve **exactamente 0,14845**,
a cifra publicada. Sobre esa base constrúense as comparacións.

## Que mellora e que non

Exame: **2022 real** (un ano que ningún modelo viu), nas 20 estacións orixinais, etiquetas
oficiais. Cada fila engade **un só cambio** sobre a anterior. Diferenzas validadas con
bootstrap emparellado (2.000 remostras).

| | Cambio | PR-AUC | Veces mellor que o azar |
|---|---|---:|---:|
| A | O modelo académico, tal cal | 0,140 | 6,1× |
| B | Reentrenado con datos máis recentes | 0,128 | 5,5× |
| C | Descartar incendios a máis de 30 km da súa estación | 0,122 | 5,3× |
| D | Ampliar a 34 estacións (sen dicirlle onde están) | **0,090** | 3,9× |
| E | Engadir a localización (coordenadas e altitude) | 0,164 | 7,1× |
| F | Hiperparámetros novos (150 árbores, follas de 50) | 0,192 | 8,3× |
| G | Ponderar por superficie queimada | 0,195 | 8,4× |

Resultados do bootstrap emparellado:

| Comparación | Mellora | Intervalo 95 % | Demostrado |
|---|---:|---|---|
| Paquete completo fronte ao modelo académico | +0,056 | +0,016 a +0,103 | **Si** |
| Efecto da localización | +0,078 | +0,044 a +0,117 | **Si, o maior** |
| Efecto dos hiperparámetros | +0,028 | +0,008 a +0,052 | **Si** |
| Efecto da magnitude (ponderar por superficie) | +0,003 | −0,011 a +0,018 | Non |
| **Máis estacións sen indicar a localización** | **−0,034** | −0,054 a −0,018 | **Si, empeora** |

**Conclusión práctica:** ampliar o número de estacións e darlle ao modelo a localización son
**un só paso**, non dous. Ampliar sen localización empeora o modelo de forma demostrada,
porque mestura estacións cuxo comportamento é moi distinto e non ten como distinguilas.

## Que significa fisicamente a localización (e por que non é a variable correcta)

As 22 variables describen **o aire a 1,5 m sobre a estación**, non o que hai debaixo. Dous
experimentos:

1. **Mesmo día meteorolóxico, distinta estación.** Fixando as 22 variables e cambiando só a
   localización, a predición vai do **17 % ao 88 %**, e esa orde correlaciona 0,68 co
   histórico de cada estación. Nun día húmido, en cambio, dá **0 % en todas**: a localización
   só modula cando as condicións xa son malas; non é unha fonte de risco independente.
2. **Só os días nos que houbo incendio** (pregunta: fíxose grande, de máis de 20 ha?). Aquí a
   localización **non achega nada** (+0,010, intervalo cruzando o cero), e as variables que
   soben ao top son a humidade e o **refacho máximo de vento**, que é física de propagación.

Interpretación: a localización codifica **canto arde nesa zona**, que mestura dúas cousas
inseparables con estes datos — cantos lumes se prenden (o 83 % dos incendios en Galicia son
intencionados) e canto combustible hai. A **altitude** tampouco é unha variable de
propagación: os seus efectos (temperatura, humidade, presión, exposición ao vento) xa se
miden na propia estación, e como indicador de vexetación é malo (correlación −0,20 coa
frecuencia de incendios; dúas estacións á mesma altura, Manzaneda e Xares, teñen taxas do
9,2 % e do 0,8 %).

Por iso as coordenadas son un **apaño**: funcionan, pero non explican nada e non xeneralizan
a estacións novas. A variable correcta é a **vexetación e o estado do combustible** (NDVI,
cubertura do solo), que é precisamente a limitación que a memoria do proxecto académico xa
identificaba como o teito do modelo.

## Fontes para manter os datos actualizados

O rexistro oficial (EGIF, vía Civio) é o bo, pero chega **con arredor de dous anos de
atraso**. Alternativas probadas para os anos recentes:

| Fonte | Que dá | Atraso | Detección (fronte ao rexistro oficial) |
|---|---|---|---|
| [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov) (VIIRS, 375 m) | Focos de calor: punto, data, intensidade | Horas | 29 % dos incendios ≥1 ha; 60 % dos de 20-100 ha. **40 % dos focos agrupados non casan con ningún incendio oficial** |
| [EFFIS / Copernicus](https://forest-fire.emergency.copernicus.eu) | Perímetros de superficie queimada: data, concello, hectáreas | ~4 días (mediana) | 83-90 % dos incendios oficiais ≥20 ha; só o 4-8 % dos seus polígonos non casan con ningún |

A nivel de **par estación-día**, EFFIS restrinxido a ≥20 ha acerta o 76 % dos días con
incendio grande oficial, e o 83 % dos que sinala teñen un detrás.

**Medido:** rellenar os dous últimos anos con etiquetas de satélite en lugar das oficiais
**non degrada o modelo de forma apreciable** (EFFIS −0,008; NASA +0,008, ambos cos intervalos
cruzando o cero). Pero substituír **todas** as etiquetas polas da NASA si o degrada (de 0,097
a 0,033): o satélite non ve os incendios pequenos, e un modelo adestrado só con el aprende
que o mesmo tempo dá menos lumes dos que dá en realidade.

## Estado

En marcha. Decisións tomadas:

- **Dous modelos separados**: o de Ourense queda como está (é o que se defendeu) e o de
  Galicia é novo e aparte, cunha páxina e un mapa propios.
- O modelo de Galicia, **só coas 22 variables meteorolóxicas**: as coordenadas quedan fóra
  por ser un indicador opaco da vexetación. Rendemento esperable: arredor de 14 veces mellor
  que o azar (o modelo actual aplicado a Galicia dá 9,2×).
- Datos **2005-2022**, cun tope de 30 km entre incendio e estación (corrixe 2.587 etiquetas
  mal asignadas de 2005, cando só había 16 estacións con datos).
- Seguinte paso coñecido: **vexetación e estado do combustible**.
