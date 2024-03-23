## Sistema para Ingestar datos a BigQuery y traerlos mediante una API.

### Parte 1 - Infraestructura e IaC

Para este proyecto, se implemento una arquitectura en GCP usando Terraform como herramienta de IaC. Los servicios utilizados para la ingesta de datos a Bigquery, son los siguientes:

- Data source. Para simular una fuente de datos ingestando a un topico PubSub, se utilizo Cloud Scheduler, con le objetivo de simular una fuente de datos ingestando cada 3 minutos.
- Sistema de Mensajeria Google Cloud Pub/Sub. Esta tendra como objetivo recibir los mensajes de la fuente( en este caso scheduler ) y tenerlos disponibles para ser consumidos mediante un suscriptor.
- Para el procesamiento de los archivos recibidos, se utilizo Google Cloud Dataflow, en modo Streaming, esto quiere decir que a medida que van llegando archivos al topico, son consumidos por el mismo.
- Como base de datos OLAP, se utilizo BigQuery para almacenar y luego recibir peticiones de la API.
- Estos datos, seran consumidos mediante una API desplegada en CloudRun y desarrollada con FastAPI.

Para la infraestructura, se incluye el codigo Terraform dentro de la carpeta terraform. En este proceso, no se incluyo CI/CD, pero hablare mas adelante sobre este tema, en el apartado de mejoras. El mismo, tiene la siguiente estructura de archivos:

- main.tf - Contiene el codigo que va a desplegar la infraestructura en GCP.
- outputs.tf - Contiene salidas que voy a querer para almacenar.
- variables.tf - Definicion de las variables a utilizar.
- remote_state.tf - Bucket remoto que va a almacenar el estado de terraform.
- terraform.tfvars - Definicion de valores para variables.

### Parte 2 - Aplicaciones y Flujo CICD

#### API

A continuacion se detalla el codigo desarrollado para el consumo de datos a BigQuery. Asi mismo tambien se incluyen las pipelines de Github Actions utilizadas para desplegar la API y para ejecutar los test de la misma. Esta API, fue desarrollada utilizando el patron MVC, en donde tenemos la siguiente estructura de carpetas/archivos:

- main.py - Inicializador de la API, en donde va a llamar al metodo que contiene todas las rutas.
- routes/bigquery_router.py - Aqui se incluiran todas las rutas disponibles para interactuar con BigQuery.
- controllers/bigquery_controller.py - Dentro de la arquitectura MVC, el controller es el encargado de realizar las consultas con el modelo y validar el tipo de dato de respuesta, para cumplir con el "contrato" que hemos realizado con el "frontend". Tambien se encargara de validar, de ser necesario, que si tenemos alguna consulta en donde venga informacion mediante el body de la consulta (usando el metodo POST), los datos sean validos y sean los requeridos por el endpoint. Este controller va a interactuar con el modelo.
- models/bigquery_models.py - Dentro de la arquitectura MVC, el archivo models es el encargado de interactuar con la base de datos. Este recibira las consultas validadas por el controller y hara las consultas a la base de datos. Luego devolvera la informacion requerida al controller en donde este se encargara de validar que esta es valida.
- serializers/bigquery_serializer.py - La utilizacion de serializadores, en este caso Pydantic, es muy necesaria para tener persistencia entre  las consultas y respuestas a la API. Con el uso de los mismos, haremos que todas las consultas que se hagan a la API, tengan solamente los campos requeridos, y en el caso de las respuestas, estan tengan siempre el mismo esquema.
- test.py - Script utilizado para testear la aplicacion. En este caso se utilizo la libreria pytest. En este caso, siempre es necesario testear y realizar mocks de las consultas externas a el funcionamiento interno de la API, en este caso, la consulta a BigQuery.

Cabe aclarar que el proceso de ingesta esta detallado en la Parte 1, por lo que esta simulado utilizando Cloud Scheduler. 

#### CI/CD

Las pipelines de Github Actions fueron creadas con la siguiente estructura:

```
.github
└── workflows
    ├── deployment.yml
    └── testing.yml
```

El objetivo de la Integracion y Despliegue Continuo, es lograr que automaticamente se hagan las siguientes tareas:

- testing.yml - Ejecutar los test para cada commit que haga en la API no afecten a la misma. Este se va a ejecutar con cada PUSH y cada PR solicitado.
- deployment.yml - Se encargara de desplegar el codigo al entorno de CloudRun. Cabe destacar para el caso de esta aplicacion, tenemos un solo entorno, que se el de desplegado por terraform. Este generara una nueva imagen Docker, la subira al Artifact Registry y luego actualizara la instancia de CloudRun con esta ultima imagen. Este tambien al momento del despliegue, usara una Service account para comunicarse con BigQuery.

#### Arquitectura

![alt text](diagrama_arquitectura.png)

### Parte 3 - Pruebas de Integracion y Puntos criticos de calidad

Para realizar los Test de la API, se utilizo la libreria PyTest de python, para simular dos escenarios posibles.
- Un caso exitoso, donde la consulta y respuesta son los esperados.
- Un caso fallido, donde la consulta no tiene un caso esperado, en este caso se le pasa un ID invalido.

Para esta API, se podrian agregar mas test, aqui detallo algunos ejemplos:
- Test de performance, para verificar que la API es robusta ante muchas solicitudes.
- Test de conexion a BigQuery, ya que dependemos del mismo para otorgar una respuesta. La latencia en la respuesta puede afectar a nuestra API.

Para plantear posibles mejoras, serian:
- Si vamos a tener una mayor carga, se consideraria utilizar explicitamente async/await (asyncio) para obtener un mayor rendimiento.
- Agregar mas manejo de errores ante error de consulta a BigQuery, como por ejemplo Value Error, Not Found error.

### Parte 4 - Metricas y Monitoreo

Ademas de las metricas convencionales, CPU, RAM y Disk Usage, al ser un proyecto de Ingesta de datos a BigQuery, propondria implementar las siguientes metricas:

- Metrica para entender el volumen ingestado a BigQuery, con el objetivo de saber si la cantidad ingestada es la esperada. (Suponiendo que conocemos el volumen de datos esperados).
- Metrica para conocer que cantidad y que tipo de trabajadores se estan utilizando en la herramienta de transformacion, en este caso Dataflow. Ya que esto, impacta en el costo de la Nube.
- Metrica para revision de entrada/salida en los topicos de PubSub, ya que esto puede impactar en la cantidad de datos ingestado a BigQuery.

Para la implementacion de estas metricas, se pueden utilizar herramientas como Cloud Monitoring, que es nativo de Google Cloud Platform, si se decide utilizar una herramienta de visualizacion externa, se puede utilizar Grafana.

En el caso que querramos escalar el sistema, en la arquitectura planteada, el que mayor va a sufrir esto es la API, ya que va a incrementar la cantidad de consultas recibidas. Para esto, lo que se puede realizar es un incremento en la cantidad de instancias de la misma y colocar un API Gateway para poder repartir el trafico. Con respecto a las metricas, una metrica interesante seria la de saber la cantidad de requests que llegan y la cantidad de instancias que se estan usando, ya que esto va a impactar en el costo. 
Cabe aclarar que para el caso de utilizar CloudRun esta respuesta no seria valido implementar un ApiGateway porque ya ofrece una opcion de autoescalado, pero  pero si nos basamos en una opcion menos serverless, podemos plantear el mismo y agregar la opcion de usar un ApiGateway para el manejo de las request y por consecuente la implementacion de las metricas.

### Parte 5 - Alertas y SRE.

Las alertas que plantearia para este sistema serian varias:

- Alertar ante una falla de un Job en Dataflow.
-  Definir umbrales en el monitoreo de BigQuery, ya que necesitamos conocer si la cantidad de datos recibidos difiere en gran cantidad de la cantidad esperada.

SLI's (Service Level Indicators) y SLO's (Service Level Objetives) 
- El primer indicador de servicio planteado es la disponibilidad que tiene la API para ser consumida. El objetivo de servicio seria mayor a un 99.9% ya que esto seria 8 horas y 45 minutos de downtime al año.
- Otro indicador de servicio podria ser la cantidad de datos procesados en Dataflow, en donde el objetivo de servicio deberia ser un porcentaje superior a un 99% para no tener distorciones en los datos ingestados a BigQuery, es decir, el 99% de los archivos procesdos por Dataflow seran procesados correctamente. Este valor dependera de la exactitud que necesitemos en BigQuery.

### Inicializacion del Proyecto.

#### Requisitos para el ejecutar el proyecto.

Se deben cumplir los siguientes requisitos para ejecutar el proyecto.

- Python 3 version 3.8
- Terraform instalado
- gcloud instalado y configurado
- Dentro del proyecto de GCP, tener habilitado la API de Dataflow, Container Registry, BigQuery Api, Compute Engine API y CloudRun.
- Docker (Para pruebas locales)
- Docker Compose (Para pruebas locales)
- Tener una service account en formato Json, para que pueda ser utilizada por la API y por Terraform. Esta se debera llamar service_account.json
- Crear un bucket en el proyecto GCP para que terraform guarde los estados. Luego modificar el archivo remote_state.tf con el nombre indicado.
- Setear la variable de entorno GOOGLE_APPLICATION_CREDENTIALS con la ubicacion de esta SA.
- Setear en los secretos de GitHub Actions, la variables:
  - GCP_PROJECT_ID = Indicando el ID del proyecto de GCP
  - GCP_SA_KEY = Esta variable tiene que contener la Service Account que va a usar Github Actions para desplegar a CloudRun la API. La misma, debera tener los permisos suficientes para realizarlo.
  - GCP_SA_EMAIL = Email usado en la Service Account.

#### Pasos para desplegar la infraestructura en GCP.

Para ejecutar terraform, se deberan seguir los siguientes pasos:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

#### Pasos para ejecutar la aplicacion localmente.

Para ejecutar la API local, se deberan seguir los siguientes pasos:
```bash
cd api
docker-compose up -d
```

Para realizar una prueba, se puede ejecutar un CURL indicando el ID.
```bash
curl --location '0.0.0.0:8000/api/v1/{id}'
```
Como respuesta obtendremos la data que se ingesto en BigQuery con el ID solicitado.

#### Pasos para utilizar CI/CD para ejecutar la aplicacion usando CloudRun

Se debera hacer un commit y solicitar el respectivo PR a rama main (en este caso porque no tenemos un entorno de desarrollo). Una vez realizado este, si los test se ejecutan correctamente, este se desplegara en CloudRun y obtendremos un Endpoint para poder realizar las consultas.

### Mejoras realizables al proyecto

#### Infraestructura
- Con el objetivo de tener diferentes ambientes, se podria mejorar el IaC para que se desplieguen diferentes ambientes usando los mismo archivos. Este desplegaria los siguientes ambientes:
  - Desarrollo
  - Testing
  - Produccion
- Realizar el despliegue de la Aplicacion de CloudRun utilizando terraform y dos service account, una encargada de realizar las consultas a BigQuery, que tendra los respectivos permisos, y otra que sera dada al servicio que consultar a la API, con permisos de invoker, para que solamente usando esta cuenta de servicio se pueda realizar consultas a la API y no afecte a otro servicio de GCP.
- Utilizar CICD con sus respectivos secretos, para automatizar los cambios en infraestructura cada vez que se necesiten y que nosotros (DevOps) no tengamos permisos para modificar la infrastructura, lo ideal es que CICD tenga la service account para que solamente esa pueda modificar la infra.

#### CI/CD
- Para tener una pipeline que se adapte a cada environment creado, una mejora seria modificar la pipeline, para que dependiendo de la branch adonde estemos pusheando codigo, esta despliegue en ese entorno en la nube, por ejemplo si pusheamos a staging, la pipeline debera actualiar la instancia de CloudRun de Staging, asi mismo con main (produccion).