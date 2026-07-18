# Job Board Data Pipeline — dbt + Snowflake + Airflow

Pipeline de données permettant de centraliser les offres d'emploi d'un job board dans un data warehouse Snowflake, de les transformer via dbt selon une modélisation en étoile, puis (à venir) d'automatiser l'ensemble avec Airflow.

## Objectif du projet

Ce projet a été construit dans un but d'apprentissage et de démonstration de compétences en **analytics engineering** : extraction de données, chargement dans un data warehouse cloud, transformation avec dbt, tests de qualité de données, documentation, et orchestration.

## Architecture

```
Adzuna API  -->  Script Python  -->  Snowflake (RAW)  -->  dbt (TRANSFORM)  -->  Airflow (orchestration)
```

- **Extraction** : un script Python interroge l'API Adzuna (offres d'emploi) avec pagination, et charge les résultats bruts (JSON) dans Snowflake.
- **Chargement** : les données brutes sont stockées telles quelles dans une table `VARIANT`, pattern ELT classique — aucune transformation n'est faite côté Python.
- **Transformation (dbt)** : les données brutes sont nettoyées, typées, puis modélisées en schéma en étoile.
- **Orchestration (Airflow)** : *(à venir)* automatisation de l'extraction et des runs dbt.

## Modélisation des données

Le projet suit une modélisation en couches, standard en analytics engineering :

| Couche | Modèle | Rôle |
|---|---|---|
| Source | `raw.job_offers` | Données brutes (JSON) chargées depuis l'API Adzuna |
| Staging | `stg_job_offers` | Parsing du JSON, typage des colonnes, une ligne par offre |
| Dimension | `dim_company` | Entreprises uniques, avec clé de substitution (`company_id`) |
| Dimension | `dim_location` | Localisations uniques, avec clé de substitution (`location_id`) |
| Fait | `fct_job_offers` | Une ligne par offre, enrichie des clés étrangères vers les dimensions, avec salaire moyen calculé |

## Data Lineage

![dbt lineage graph](docs/Lineage_job_board_pipeline_dbt.png)

Isoler les entreprises et localisations dans des tables de dimension évite la redondance de texte à chaque ligne d'offre, et permet des jointures propres et réutilisables. La table de faits `fct_job_offers` centralise les métriques (salaires) et les clés étrangères, dans la logique d'un schéma en étoile classique.

## Qualité des données

Des tests dbt sont appliqués sur les modèles clés :
- `unique` et `not_null` sur les identifiants (`job_id`, `company_id`, `location_id`)
- `dbt_utils.accepted_range` sur les salaires, pour détecter des valeurs aberrantes (négatives)

## Stack technique

- **Extraction** : Python (`requests`, `snowflake-connector-python`, `python-dotenv`)
- **Data Warehouse** : Snowflake
- **Transformation** : dbt (dbt-core + dbt-snowflake)
- **Tests de données** : dbt natif + package `dbt_utils`
- **Orchestration** : Airflow

## Structure du projet

```
job-board-pipeline/
├── extraction/
│   └── adzuna_extractor.py       # extraction API Adzuna + chargement Snowflake RAW
├── job_board_dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   └── stg_job_offers.sql
│   │   └── marts/
│   │       ├── dim_company.sql
│   │       ├── dim_location.sql
│   │       ├── fct_job_offers.sql
│   │       └── schema.yml         # tests dbt
│   ├── dbt_project.yml
│   ├── packages.yml
│   └── profiles.yml               # connexion Snowflake via variables d'environnement
├── docs/
│   └── lineage.png
├── requirements.txt
└── .gitignore
```
