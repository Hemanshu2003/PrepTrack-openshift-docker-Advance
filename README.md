## `Note:` This project is the successor to ![PrepTrack-openshift-docker](https://github.com/Hemanshu2003/PrepTrack-openshift-docker), and it requires completing all the necessary prerequisites.

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

### 🏗️ The Architectural Approach - Addition to the PREV architechture.

1. *Transport Protocol:* Swap standard HTTP polling for WebSockets (using Socket.IO) to enable bi-directional, real-time event pushing.

2. *Message Broker:* Deploy Redis in OpenShift. The backend Pods will publish incoming messages to Redis, which then broadcasts them to all other connected Pods.

3. *Data Persistence:* Update PostgreSQL with a new schema that supports self-referencing (replies) and JSONB fields (reactions).

 
![SS-Architecture-Daigram](https://github.com/Hemanshu2003/PrepTrack-openshift-docker/blob/main/arch.png)

 
## ⚙️ Prerequisites
 
To deploy this project, you will need:

* This project is the successor to ![PrepTrack-openshift-docker](https://github.com/Hemanshu2003/PrepTrack-openshift-docker)
* Assumming that ![PrepTrack-openshift-docker](https://github.com/Hemanshu2003/PrepTrack-openshift-docker) is `UP RUNNING`.
 
---
 
## 🚀 Deployment Guide
 
Open your terminal, log in to your OpenShift Sandbox, and follow these commands one by one. 
`USING SANDBOX CLI` for Deployment. (You can also use `CMD` make sure to install `oc.exe` from RedHat Offical -- then using `oc login --token=sha256~k4O5Wu45OyAX2xxxxx`).
 
1. Update the PostgreSQL Database Schema

```bash
oc get pods -l app=postgresql-persistent
# Replace the pod name below with your actual postgres pod name
oc rsh postgresql-1-slv25 
psql -U prepuser -d preptrackdb
```

Copy Schema from `database/init.sql`

```bash
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    parent_id INT REFERENCES messages(id), 
    reactions JSONB DEFAULT '{}', 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\q
```

```bash
exit
```

2. Deploy the Redis Message Broker

```bash
oc new-app docker.io/redis:alpine --name=redis-broker

```

3. Link Redis to the Backend API
   
```bash
oc set env deployment/api-backend REDIS_URL=redis://redis-broker:6379/0

```

4. Push Code Changes to GitHub
Ensure you have saved the updated `backend/app.py`, `backend/requirements.txt`, and `frontend/index.html` from the previous step. (Check Repo Content)
Commit the changes

```bash
git add .
git commit -m "Upgrade to real-time WebSockets chat with Redis"
git push origin main
```

5. Rebuild and Deploy
   
```bash
oc start-build api-backend
oc start-build web-frontend
```
 
 
### ✅ Final Step
 
Run `oc get route web-frontend`, click the link, and you should see your **PrepTrack** app live, connecting to the database, and displaying your study tasks!
 
## ✅ Verification
 
To view the live application, retrieve the frontend URL:
 
```bash
oc get route web-frontend
 
```
 
Copy the generated link add `http://<copied-link>` in browser. You should see the PrepTrack dashboard successfully fetching your study tasks from the PostgreSQL database via the Python API!

Thank You.

***

## ✨ Author

**Hemanshu Anil Waghmare (CG)**  
Feel free to reach out on **[LinkedIn](http://www.linkedin.com/in/hemanshu-anil-waghmare-50a7a3291)**!

***
