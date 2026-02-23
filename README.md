## Note: `This project is the successor to ![PrepTrack-openshift-docker](https://github.com/Hemanshu2003/PrepTrack-openshift-docker), and it requires completing all the necessary prerequisites.`

# 📚 PrepTrack Chat - (Advance): 3-Tier Microservices Study Portal
PrepTrack is a cloud-native, real-time community chat and study portal built. It utilizes an event-driven microservices architecture built with Python (Flask), WebSockets (Socket.IO), Redis for Pub/Sub message broadcasting, and PostgreSQL for stateful data storage. The application is containerized and deployed on Red Hat OpenShift using Source-to-Image (S2I) builds, dynamic networking, and Kubernetes health probes to demonstrate high availability and enterprise-grade deployment practices.

---
 
![OpenShift](https://img.shields.io/badge/OpenShift-EE0000?style=for-the-badge&logo=redhat&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

## 🎯 Project Overview
PrepTrack is a cloud-native, 3-tier web application built to manage intensive study schedules and track preparation progress for competitive technical exams.
 
This project serves as a practical demonstration of containerization, microservices architecture, and Kubernetes/OpenShift fundamentals. It showcases the deployment of a frontend UI, a stateless REST API, and a stateful database, all communicating securely within an OpenShift cluster.

### 📖 Core Concepts & Definitions
This project implements the following OpenShift/Kubernetes fundamentals:

1. *Project (Namespace):* A virtual cluster inside OpenShift that isolates our application environments (e.g., preptrack-dev).

2. *Pod:* The smallest deployable computing unit in Kubernetes. It encapsulates one or more Docker containers (e.g., our Python API runs inside a Pod).

3. *Deployment:* An object that manages the creation, scaling, and self-healing of Pods. If a backend Pod crashes, the Deployment spins up a new one.

4. *Service (Networking):* An internal load balancer that gives a stable internal IP address to a set of Pods. It allows the Frontend to always find the Backend, even if the Backend Pods are destroyed and recreated.

5. *Route:* An OpenShift-specific object (similar to a Kubernetes Ingress) that exposes a Service to the outside world with a public URL.

6. *Persistent Volume Claim (PVC):* A request for storage. Containers are ephemeral (data dies when the container dies). A PVC ensures our PostgreSQL database data survives Pod restarts.

7. *ConfigMap & Secret:* Objects used to inject configuration data (like database URLs) and sensitive data (like database passwords) into Pods without hardcoding them in the Docker image.
 
## 🏗️ Architecture
 
The application is broken down into three decoupled tiers:
 
1. **Frontend (Tier 1):** A lightweight HTML/JS web interface served by an Nginx container. It makes asynchronous REST calls to the backend.
2. **Backend API (Tier 2):** A Python (Flask) REST API that handles business logic and database connections.
3. **Database (Tier 3):** A PostgreSQL database utilizing a Persistent Volume Claim (PVC) to ensure study data survives pod restarts.

 
![SS-Architecture-Daigram](https://github.com/Hemanshu2003/PrepTrack-openshift-docker/blob/main/arch.png)

 
## ⚙️ Prerequisites
 
To deploy this project, you will need:

* Fork/Clone this *repo* to your repository _(IMP)_.
* Access to an OpenShift Cluster (e.g., Red Hat Developer Sandbox).
* The OpenShift CLI (`oc`) installed and logged in.
* Docker installed locally (if building images from scratch).
 
---
 
## 🚀 Deployment Guide
 
Since our code is on GitHub, we will use OpenShift's **"Source-to-Image" (S2I) / Build** capabilities. This means OpenShift will pull your code, read your Dockerfiles, build the images inside the cluster, and deploy them.
 
Here is your exact, step-by-step execution guide. Open your terminal, log in to your OpenShift Sandbox, and follow these commands one by one. 
`USING SANDBOX CLI` for Deployment. (You can also use `CMD` make sure to install `oc.exe` from RedHat Offical -- then using `oc login --token=sha256~k4O5Wu45OyAX2xxxxx`).
 
### 📋 Phase 1: Foundation (Project & Database)

**Step 1: Create the Project (Namespace) (SKIP if you are using _Red Hat Developer Sandbox_)**
*Note: Projects isolate your application resources.*
 
```bash
oc new-project preptrack-live

```
 
**Step 2: Create a Secret for Database Security**
*Note: Secrets store sensitive data (passwords) securely, separate from code.*
 
```bash
oc create secret generic db-secret --from-literal=DB_PASSWORD=SuperSecret123

```
 
**Step 3: Deploy the Database (Storage)**
*We are using a persistent database so data survives restart. This uses a standard PostgreSQL image.*
 
```bash
oc new-app postgresql-persistent \
    -p POSTGRESQL_USER=prepuser \
    -p POSTGRESQL_PASSWORD=SuperSecret123 \
    -p POSTGRESQL_DATABASE=preptrackdb \
    -p VOLUME_CAPACITY=1Gi \
    --name=postgres-db
 
```
 
*(Wait a moment for the database pod to start. You can check status with `oc get pods`)*
 
---
 
### 🐍 Phase 2: The Backend (Builds & Configuration)
 
**Step 4: Deploy Backend from GitHub**
*"Docker Build Strategy". OpenShift pulls your repo, goes into the `backend` folder, and builds the Dockerfile found there.*
 
* **Replace** `YOUR_GITHUB_USER` with your actual username. In my case i am using my repo.
 
```bash
oc new-app https://github.com/Hemanshu2003/PrepTrack-openshift-docker \
    --context-dir=backend \
    --name=api-backend \
    --strategy=docker

```
 
**Step 5: Inject Configuration (ConfigMaps)**
*ConfigMaps allow us to inject environment variables (like DB host) into the container without changing the code.*
 
```bash
# 1. Create the ConfigMap linking to our database service name 'postgres-db'
oc create configmap backend-config \
    --from-literal=DB_HOST=postgresql \
    --from-literal=DB_NAME=preptrackdb \
    --from-literal=DB_USER=prepuser
 
# 2. Add the ConfigMap to the deployment
oc set env deployment/api-backend --from=configmap/backend-config
 
# 3. Add the Secret (Password) to the deployment
oc set env deployment/api-backend --from=secret/db-secret
 
```
 
**Step 6: Expose the Backend (Routes)**
*Routes to create a public URL so the outside world (and your frontend) can reach the API.*
 
```bash
oc expose svc/api-backend
 
```
 
---
 
### 🔄 Phase 3: The Critical Connection (Development Lifecycle)
 
**Step 7: Get your Backend URL**
Run this command and **copy the URL** under the `HOST/PORT` column:
 
```bash
oc get route api-backend
 
```
 
*(It will look like: `api-backend-your-sandbox-name-live.apps.sandbox...`)*
 
**Step 8: Update your Frontend Code**
 
1. Go to your repo `PrepTrack-openshift-docker` folder.
2. Open `frontend/index.html`.
3. Find the line `const apiUrl = ...`.
4. **Replace** the placeholder with the URL you just copied. Ensure you keep the `/api/tasks` at the end.
* *Example:* `const apiUrl = 'http://api-backend-preptrack-live.apps.sandbox.../api/tasks';` -- make sure to add `http://`.  
 
 
5. **Save, Commit, and Push** this change to GitHub:
```bash
git add .
git commit -m "Update API URL"
git push origin main
 
```
 
---
 
### 🌐 Phase 4: The Frontend (Scaling & Services)
 
**Step 9: Deploy Frontend from GitHub**
Now that the code on GitHub has the correct API URL, we deploy the frontend.
 
```bash
oc new-app https://github.com/Hemanshu2003/PrepTrack-openshift-docker \
    --context-dir=frontend \
    --name=web-frontend \
    --strategy=docker
 
```
 
**Step 10: Scale the Frontend (Optional)**
*Scaling creates multiple copies (replicas) of your application to handle more traffic.*
 
```bash
oc scale deployment/web-frontend --replicas=2
 
```
 
**Step 11: Expose the Frontend**
This creates the final URL for you to view your app.
 
```bash
oc expose svc/web-frontend
 
```
 
---
 
### 🏗️ Phase 5: Advanced OpenShift (Templates, Users, Database Init)
 
**Step 12: Initialize the Database Tables**
*Remote Shelling (`rsh`). We need to run the SQL commands inside the running database pod.*
 
1. Find your database pod name:
```bash
oc get pods
 
```
 
 
*(Look for something like `postgres-db-1-xxxxx`)*
2. Remote into the pod (replace the pod name below):
```bash
oc rsh postgres-db-1-xxxxx
 
```
 
 
3. Once inside the prompt (`sh-4.2$`), log into Postgres and run your SQL:
```bash
psql -U prepuser -d preptrackdb
 
```
 
 
4. Paste the contents of your `database/init.sql` file here (CREATE TABLE, INSERT...).
5. Type `\q` to exit Postgres, and `exit` to leave the pod.
 
**Step 13: Export as a Template (Optional)**
*Templates allow you to "save" this entire complex setup as a reusable blueprint.*
 
```bash
oc get deployment,svc,route -l app=web-frontend -o yaml > my-frontend-template.yaml
 
```
 
**Step 14: Simulate User Management (Optional)**
*Concept: RBAC (Role Based Access Control). Simulating adding a teammate.*
 
```bash
# Give a fake user 'view' access to your project
oc adm policy add-role-to-user view fake-developer -n preptrack-live
 
```
 
### ✅ Final Step
 
Run `oc get route web-frontend`, click the link, and you should see your **PrepTrack** app live, connecting to the database, and displaying your study tasks!
 
## ✅ Verification
 
To view the live application, retrieve the frontend URL:
 
```bash
oc get route web-frontend
 
```
 
Copy the generated link add `http://<copied-link>` in browser. You should see the PrepTrack dashboard successfully fetching your study tasks from the PostgreSQL database via the Python API!

## Optional - **Health Probes in OpenShift (Liveness & Readiness)**

OpenShift uses health probes—just like Kubernetes—to monitor container health and control traffic flow to pods.

***

### **1. Liveness Probe**

*   Checks if the application **is still running properly**.
*   If the liveness probe fails, OpenShift will **restart the container**.
*   Helps recover from deadlocks, crashes, or hung processes.

**Meaning:** *“Is the app alive, or should I restart it?”*

```bash
oc set probe deployment/api-backend --liveness --get-url=http://:5000/health --initial-delay-seconds=15
```

***

### **2. Readiness Probe**

*   Checks if the application **is ready to accept traffic**.
*   If it fails, OpenShift **stops sending requests** to that pod until it becomes ready again.
*   Ensures only healthy pods serve users.
*   
```bash
oc set probe deployment/api-backend --readiness --get-url=http://:5000/health --initial-delay-seconds=5
```

**Meaning:** *“Can this pod handle requests right now?”*

***

### **In short (OpenShift):**

*   **Liveness Probe → Ensures the app stays alive (restart if needed).**
*   **Readiness Probe → Ensures traffic goes only to ready pods.**

***

## 🧹 Cleanup
 
To tear down the entire project and free up cluster resources (Note: This will delete everything):
 
```bash
oc delete all,secret,configmap,pvc,deployment --all
 
```

Thank You.

***

## ✨ Author

**Hemanshu Anil Waghmare (CG)**  
Feel free to reach out on **[LinkedIn](http://www.linkedin.com/in/hemanshu-anil-waghmare-50a7a3291)**!

***
