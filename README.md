## System to Ingest data to BigQuery and Get it using Cloud Run

La idea de este sistema, es Ingestar informacion a BigQuery, usando un proceso PubSub.

Mi idea para resolver esto, es utilizar la siguiente arquitectura:

cloud pub/sub
cloud dataflow
cloud bigquery

Para ingestar los datos, voy a usar Cloud Scheduler como simulador de un mensaje que llega cada 5 min.
Para consumir los datos, voy a hacer una API que va a estar desplegada en Cloud Run, que expone un endpoint para consumir esos datos.


## Carpeta Terraform

Para esta carpeta, decidi separar entre diferentes servicios, en donde, cada execucion va a tener:

- main.tf - codigo principal
- outputs.tf - Lo que voy a querer a la salida de la ejecucion, es lo que se va a ser visible para el resto de los modulos.
- variables.tf - Definicion de variables
- remote_state.tf - Donde voy a guardar los archivos de estado.
- data.tf - Data que voy a encesitar traerme de otros estados.
- terraform.tfvars - Definicion de valores para variables.

#### Mejoras:

Infraestructura
- Si voy a tener varios ambientes (dev/test/prod), puedo tener la siguiente estructura para poder escalar el sistema:
  terraform:
    - production
    - testing
    - development
    - modules - Pueden ser usados en comun por los otros entornos, cada uno le va a setear las variables correspondientes.
- Incluir reglas de IAM para evitar otorgar accesos indevidos.
- Utilizar CICD para automatizar cada vez que hagamos un cambio y que nosotros (devops) no tengamos permisos para modificar la infrastructura, lo ideal es que CICD tenga la service account para que solamente esa pueda modificar la infra.

API
- Si vamos a tener una mayor carga, se consideraria utilizar explicitamente async/await (asyncio) para obtener un mayor rendimiento.
- 

#### Requerimientos

- Terraform
- gcloud configurado
- Tener Dataflow, containerregistry, bigquery y compute engine API activados.


#### Pasos para ejecutar terraform

#### Pasos para correr la API
- Setear la variable GOOGLE_APPLICATION_CREDENTIALS para que tu aplicacion pueda usar la API de GCP con esa SA.
- export GOOGLE_APPLICATION_CREDENTIALS="path_to_sa"