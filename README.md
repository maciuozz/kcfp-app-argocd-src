<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Practica SRE Paolo Scotto Di Mase](#practica-sre-paolo-scotto-di-mase)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Practica SRE Paolo Scotto Di Mase
Se han agregado 2 endpoints, 3 contadores y 2 pruebas unitarias que están señalizados de manera visible en el codigo.
Observamos la ejecución de los 4 tests con el informe de cobertura de código:

    (venv) 21:33 @/Users/paoloscotto/desktop/sre ~ (git)-[main] $ pytest --cov
    =============================================================== test session starts ================================================================
    platform darwin -- Python 3.9.6, pytest-7.1.1, pluggy-1.0.0 -- /Users/paoloscotto/Desktop/SRE/venv/bin/python3
    cachedir: .pytest_cache
    rootdir: /Users/paoloscotto/Desktop/SRE, configfile: pytest.ini, testpaths: src/tests/
    plugins: asyncio-0.18.3, anyio-3.6.2, cov-3.0.0
    asyncio: mode=auto
    collected 4 items

    src/tests/app_test.py::TestSimpleServer::read_health_test PASSED                                                                             [ 25%]
    src/tests/app_test.py::TestSimpleServer::read_main_test PASSED                                                                               [ 50%]
    src/tests/app_test.py::TestSimpleServer::bye_bye_test PASSED                                                                                 [ 75%]
    src/tests/app_test.py::TestSimpleServer::joke_endpoint_test PASSED                                                                           [100%]

    ---------- coverage: platform darwin, python 3.9.6-final-0 -----------
    Name                          Stmts   Miss Branch BrPart     Cover   Missing
    ----------------------------------------------------------------------------
    src/application/__init__.py       0      0      0      0   100.00%
    src/application/app.py           44      5      4      1    87.50%   31, 35-37, 77
    src/tests/__init__.py             0      0      0      0   100.00%
    src/tests/app_test.py            32      0      2      0   100.00%
    ----------------------------------------------------------------------------
    TOTAL                            76      5      6      1    92.68%

    Required test coverage of 80.0% reached. Total coverage: 92.68%

    ================================================================ 4 passed in 1.69s =================================================================

<img width="1790" alt="Screenshot 2023-04-25 at 21 38 59" src="https://user-images.githubusercontent.com/118285718/234386277-b5564adc-950b-4157-a180-aebbb8e2f19d.png">

Se ha configurado una pipeline en GitHub Actions que incluye la funcionalidad de Semantic Release. Hace uso de 3 archivos, ***lint.yaml***, ***test.yaml*** y ***release.yaml***, los cuales representan 3 flujos de trabajo/workflow o fases distintas. La fase de ***Lint*** se activa en dos eventos, pull request (PR) y push, y define un job llamado ***lint-python-code*** que automatiza el proceso de linting (análisis de estilo y formato) del código Python en un repositorio de GitHub. La fase de ***Test*** se activa cuando se completa exitosamente ***Lint*** y se utiliza para ejecutar pruebas unitarias en el código fuente. La fase ***release-build*** se activa después de que se completa una ejecución exitosa de ***Test***. Automatiza el proceso de liberación y despliegue de software, generando automáticamente una nueva versión y publicando una imagen de Docker actualizada en dos registros diferentes: Docker Hub y GHCR.  He usado un repositorio privado en mi cuenta personal de GitHub en vez de usar un repositorio dentro de la organización ***keepcodingclouddevops7***.
El fichero ***release.yaml*** usa 3 ***repository secret***: ***GHCR_PAT***, ***DOCKERHUB_TOKEN*** y ***DOCKERHUB_USERNAME***.
Para definir ***GHCR_PAT*** generamos un token en ***Settings*** --> ***Developer settings*** con estos permisos:

<img width="1187" alt="Screenshot 2023-04-24 at 02 12 21" src="https://user-images.githubusercontent.com/118285718/233874655-ca1eb09a-7908-43d2-a032-f1ba8db3fbe3.png">

Dentro del repositorio generamos un secret, ***GHCR_PAT***, en ***Settings*** --> ***Secrets and variables*** --> ***Actions*** con el valor del PAT creado anteriormente. Para definir ***DOCKERHUB_TOKEN*** generamos un token en Docker Hub y usamos su valor para crear el secret. Para definir
***DOCKERHUB_USERNAME*** simplemente creamos un secret con el valor del nombre de usuario de Docker Hub. A continuación se muestran los 3 secret:

<img width="1224" alt="Screenshot 2023-04-24 at 02 24 56" src="https://user-images.githubusercontent.com/118285718/233875331-b1faa951-b2cb-40e8-a741-0ac7ccf365ff.png">

Para hacer pre-commit:

    pip3 install pre-commit
    pre-commit install
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r src/requirements.txt
    pre-commit run -a

El output:

    (venv) 3:44 @/Users/paoloscotto/desktop/sre ~ (git)-[main] $ pre-commit run -a
    Trim Trailing Whitespace.................................................Passed
    Fix End of Files.........................................................Passed
    Check for merge conflicts................................................Passed
    Mixed line ending........................................................Passed
    Add TOC for md files.....................................................Passed
    pylint...................................................................Passed

La sintaxis necesaria para realizar un commit es:

    git commit -m "fix(app): updated code"

A continuación hay algunas capturas de las varias fases de la pipeline:

<img width="1790" alt="Screenshot 2023-04-28 at 04 05 26" src="https://user-images.githubusercontent.com/118285718/235037266-75250ea4-4eeb-4b7a-bd5b-02625244a258.png">
<img width="1790" alt="Screenshot 2023-04-28 at 04 05 58" src="https://user-images.githubusercontent.com/118285718/235037372-1f2e2299-b3a6-4de5-8d75-ef6d947e2c62.png">
<img width="1789" alt="Screenshot 2023-04-28 at 04 06 27" src="https://user-images.githubusercontent.com/118285718/235037390-92dfa077-d7d1-4175-897b-c3cacbca88e2.png">
<img width="1791" alt="Screenshot 2023-04-28 at 04 07 13" src="https://user-images.githubusercontent.com/118285718/235037407-9fbfc09f-2bb7-4648-8853-ccaa224917ed.png">



Aqui se pueden observar las imagenes subidas a GitHub Container Registry y a Docker Hub:

<img width="1790" alt="Screenshot 2023-04-26 at 00 08 08" src="https://user-images.githubusercontent.com/118285718/234415976-4f122de1-ba2d-4951-87e1-6137d9e656c3.png">
<img width="1792" alt="Screenshot 2023-04-26 at 00 08 53" src="https://user-images.githubusercontent.com/118285718/234415987-b1940f14-07e9-42ab-875a-bc0de5f9ad15.png">

Para desplegar Prometheus creamos un cluster de Kubernetes que utilice la versión v1.21.1 utilizando minikube para ello a través de un nuevo perfil llamado monitoring-demo:

    minikube start --kubernetes-version='v1.21.1' --memory=4096 --addons="metrics-server" -p monitoring-demo

Añadir el repositorio de helm prometheus-community para poder desplegar el chart kube-prometheus-stack:

    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

Desplegar el chart kube-prometheus-stack del repositorio de helm añadido en el paso anterior con los valores configurados en el archivo kube-prometheus-stack/values.yaml en el namespace monitoring:

    helm -n monitoring upgrade --install prometheus prometheus-community/kube-prometheus-stack -f kube-prometheus-stack/values.yaml --create-namespace --wait --version 34.1.1

En el archivo ***values.yaml*** se establece la configuración para conectar Prometheus con Slack. Para ver los pod en el namespace monitoring utilizado para desplegar el stack de prometheus:

    kubectl -n monitoring get po -w

Añadir el repositorio de helm de bitnami para poder desplegar el chart de mongodb empaquetado por esta compañía:

    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update

Descargar las dependencias necesarias, siendo en este caso el chart de mongodb:

    helm dep up helm-chart-simple-server

Desplegamos en el mismo namespace nuestra aplicación que utiliza [FastAPI](https://fastapi.tiangolo.com/) para levantar un servidor en el puerto
8081, utilizando Helm:

    helm install my-release helm-chart-simple-server/ -n monitoring

Deberiamos obtener este output:

    NAME: my-release
    LAST DEPLOYED: Tue Apr 25 16:24:40 2023
    NAMESPACE: monitoring
    STATUS: deployed
    REVISION: 1
    NOTES:
    1. Get the application URL by running:
       - kubectl -n monitoring port-forward service/my-release-simple-server 8081:8081

Despues de ejecutar el ***port-forward*** mencionado en la sección ***NOTES*** del output anterior, comprobamos que la aplicación funcione correctamente accediendo a ***"/joke"***:

<img width="1382" alt="Screenshot 2023-04-25 at 23 41 36" src="https://user-images.githubusercontent.com/118285718/234411323-c20acfc6-c5b2-44e1-86fd-f99ff771f6c9.png">
<img width="1390" alt="Screenshot 2023-04-25 at 23 43 09" src="https://user-images.githubusercontent.com/118285718/234411385-83dab2a4-cdce-4ea9-b451-b12ef61b950b.png">
<img width="1347" alt="Screenshot 2023-04-25 at 23 43 31" src="https://user-images.githubusercontent.com/118285718/234411439-b9b3d80f-21d4-4c81-bd3f-cc101bc014a0.png">

Crear una nueva pestaña y obtener los logs del container ***wait-mongo*** del deployment ***my-release-simple-server*** en el namespace ***monitoring***, observar como está utilizando ese contenedor para esperar a que MongoDB esté listo:

    kubectl -n monitoring logs -f deployment/my-release-simple-server -c wait-mongo

Una vez se obtenga el mensaje de conexión exitosa a mongo, siendo algo como lo mostrado a continuación, indicará que empezará el contenedor:

    Connecting to my-app-mongodb:27017 (10.101.242.27:27017)
    HTTP/1.0 200 OK
    Connection: close
    Content-Type: text/plain
    Content-Length: 85

**Comprobación funcionamiento alerta**
Para forzar la alerta configurada es necesario realizar una prueba de estrés sobre el pod, para ello se deben seguir los siguientes pasos:

 - Para realizar esta prueba será necesario desactivar temporalmente el HPA configurado previamente mediante el helm de la aplicación, ya que sino nunca se lanzará la alarma ya que      empezará a paliarse este problema a través de la generación de nuevas réplicas:

       helm -n monitoring upgrade --install my-release --create-namespace --wait helm-chart-simple-server --set autoscaling.enabled=false

 - Obtener el POD que está ejecutando la aplicación. Es posible obtener el nombre del pod creado mediante el siguiente comando:

       export POD_NAME=$(kubectl get pods --namespace monitoring -l "app.kubernetes.io/name=simple-server,app.kubernetes.io/instance=my-release" -o jsonpath="{.items[0].metadata.name}")

 - Una vez obtenido el nombre del pod es necesario conectarse a él mediante una shell interactiva:

       kubectl -n monitoring exec -it $POD_NAME -- /bin/sh

 - Dentro del pod es necesario realizar una serie de pasos para la prueba de estrés:
   - Instalación de software necesario:

         apk update && apk add git go

   - Descargar las herramientas para realizar la prueba de estrés:

         git clone https://github.com/jaeg/NodeWrecker.git
         cd NodeWrecker
         go build -o estres main.go

   - Ejecutar el binario compilado en el paso anterior para realizar prueba de estrés:

         ./estres -abuse-memory -escalate -max-duration 10000000

Como que hemos configurado prometheus para que nos avise si el uso de CPU del contenedor ***simple-server*** supera la solicitud de recursos de CPU en un lapso de 1 minuto, despues de poco mas de 1 minuto deberíamos recibir notificaciones en Slack:

<img width="1792" alt="Screenshot 2023-04-25 at 20 54 20" src="https://user-images.githubusercontent.com/118285718/234376318-b246d27a-9941-4d87-85a5-52d077ac5dc2.png">

Para ver la salida de las métricas de Prometheus expuestas por la aplicación ejecutamos:

    kubectl -n monitoring port-forward service/my-release-simple-server 8000:8000

Abriendo http://localhost:8000/ vemos:

    # HELP main_requests_total Total number of requests to main endpoint
    # TYPE main_requests_total counter
    main_requests_total 172089.0
    # HELP bye_requests_total Total number of requests to bye endpoint
    # TYPE bye_requests_total counter
    bye_requests_total 7082.0
    # HELP joke_requests_total Total number of requests to joke endpoint
    # TYPE joke_requests_total counter
    joke_requests_total 15.0
    # HELP healthcheck_requests_total Total number of requests to healthcheck
    # TYPE healthcheck_requests_total counter
    healthcheck_requests_total 17.0
    # HELP app_start_count_total Number of times the application has started
    # TYPE app_start_count_total counter
    app_start_count_total 1.0

Abrir una nueva pestaña en la terminal y realizar un port-forward del puerto http-web del servicio de Grafana al puerto 3000 de la máquina:

    kubectl -n monitoring port-forward svc/prometheus-grafana 3000:http-web

Acceder a la dirección http://localhost:3000. Las credenciales de Grafana por defecto son ***admin*** para el usuario y ***prom-operator*** para la contraseña. Hacemos un import del fichero ***custom_dashboard.json***, seleccionamos el namespace ***monitoring*** y uno de los pods de la aplicación FastAPI. Se pueden observar 7 paneles:

* 4 paneles dedicados a los endpoints, los cuales registran el número de llamadas recibidas por cada uno de ellos.
* 1 panel que cuenta el número de veces que la aplicación ha sido iniciada.
* 1 panel que muestra el número total de llamadas realizadas.
* 1 panel que muestra el uso actual de CPU en comparación con la cantidad máxima solicitada.

<img width="1791" alt="Screenshot 2023-04-26 at 05 35 01" src="https://user-images.githubusercontent.com/118285718/234465574-b1c68ee6-dd07-4b64-a551-50a60ea0694d.png">
