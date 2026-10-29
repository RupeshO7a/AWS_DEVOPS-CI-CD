# CI/CD Pipeline for a FastAPI Application on AWS

A beginner-friendly DevOps project that automates the build and
deployment of a FastAPI application using **GitHub, Jenkins, Docker,
Amazon ECR, Amazon EC2, Docker Compose, and PostgreSQL**.

> **Project status:** The project has successfully completed a Jenkins
> deployment pipeline. The deployed API's health endpoint returned
> `{"status":"ok","database":"connected"}`, and the application returned
> records from PostgreSQL. Screenshots should be added to the repository
> to document the actual deployment.

------------------------------------------------------------------------

## Table of Contents

-   [Overview](#overview)
-   [Project Objectives](#project-objectives)
-   [Architecture](#architecture)
-   [End-to-End Workflow](#end-to-end-workflow)
-   [Technology Stack](#technology-stack)
-   [Repository Structure](#repository-structure)
-   [Prerequisites](#prerequisites)
-   [AWS Infrastructure](#aws-infrastructure)
-   [Configuration and Secrets](#configuration-and-secrets)
-   [How the Pipeline Works](#how-the-pipeline-works)
-   [Run the Application](#run-the-application)
-   [API Endpoints](#api-endpoints)
-   [Verification and Testing](#verification-and-testing)
-   [Screenshots](#screenshots)
-   [Security Considerations](#security-considerations)
-   [Troubleshooting](#troubleshooting)
-   [Known Limitations](#known-limitations)
-   [Future Improvements](#future-improvements)
-   [Learning Outcomes](#learning-outcomes)

------------------------------------------------------------------------

## Overview

Deploying an application manually can require repeating several steps:
retrieving source code, building an application image, publishing the
image, connecting to a server, updating containers, and checking whether
the application works.

This project uses a **Continuous Integration / Continuous Delivery
(CI/CD) pipeline** to organize and automate these tasks.

The FastAPI source code is maintained in GitHub. Jenkins runs the
pipeline steps defined in the `Jenkinsfile`. Docker builds an image for
the application, and Amazon Elastic Container Registry (Amazon ECR)
stores that image. The application server on Amazon EC2 retrieves and
runs the image. Docker Compose runs the FastAPI application and
PostgreSQL database as separate containers.

The final deployment is verified using the API health endpoint and by
checking that the API can return stored database records.

## Project Objectives

-   Automate repeatable application build and deployment tasks.
-   Package the FastAPI application and its dependencies in a Docker
    image.
-   Store Docker images in Amazon ECR.
-   Deploy the application to an AWS EC2 application server.
-   Run FastAPI and PostgreSQL with Docker Compose.
-   Verify application health and database connectivity.
-   Demonstrate a practical DevOps workflow using commonly used tools.

## Architecture

### Architecture flow

``` text
Developer
   |
   v
GitHub Repository
   |
   | Jenkins job trigger / webhook, if configured
   v
Jenkins Server (AWS EC2)
   |
   | 1. Checkout source code
   | 2. Execute Jenkinsfile stages
   | 3. Build Docker image
   v
Docker Image
   |
   | Authenticate and push image
   v
Amazon ECR
   |
   | Jenkins connects to app server over SSH
   | App server pulls the selected image
   v
Application Server (AWS EC2)
   |
   v
Docker Compose
   |
   +-----------------------+
   |                       |
   v                       v
FastAPI Container      PostgreSQL Container
   |                       ^
   +---- database queries--+
   |
   v
Health Check and API Responses
```

### In one line

**Developer → GitHub → Jenkins → Docker Build → Amazon ECR → Application
EC2 → Docker Compose → FastAPI ↔ PostgreSQL → Health Check**

The Jenkins server and application server are separate EC2 instances in
the current setup.

## End-to-End Workflow

1.  **Code development:** A developer updates the FastAPI application or
    deployment files.
2.  **Push to GitHub:** The source code is committed and pushed to the
    repository.
3.  **Pipeline trigger:** Jenkins starts when the configured job is run
    or when an enabled webhook/job trigger starts it.
4.  **Checkout:** Jenkins retrieves the repository contents.
5.  **Build:** Jenkins uses the Dockerfile to build an application
    image.
6.  **Publish:** Jenkins authenticates to Amazon ECR and pushes the
    image with a tag.
7.  **Prepare deployment:** Jenkins connects to the application EC2
    server and transfers or uses deployment files such as the Compose
    configuration and deployment script.
8.  **Pull and deploy:** The application server pulls the selected image
    and runs the deployment script.
9.  **Start containers:** Docker Compose starts or updates the FastAPI
    and PostgreSQL services.
10. **Verify:** The pipeline checks the health endpoint and reports
    whether deployment verification succeeded.
11. **Access:** Users or reviewers can access the API through the
    application server's public address if the relevant network rules
    allow it.

> Automatic deployment on every GitHub push depends on the Jenkins
> webhook or job trigger being configured and enabled. Verify this by
> making a controlled test commit and checking that Jenkins starts a new
> build.

## Technology Stack

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  GitHub                              Source-code hosting and version
                                      history

  Jenkins                             Pipeline orchestration and
                                      deployment automation

  Docker                              Packages the application and its
                                      dependencies into an image

  Amazon ECR                          Private registry for Docker images

  Amazon EC2                          Cloud virtual machines for Jenkins
                                      and the application

  FastAPI                             Python framework for the REST API

  PostgreSQL                          Relational database for persistent
                                      application data

  Docker Compose                      Defines and runs the application
                                      and database containers

  SSH                                 Secure connection from Jenkins to
                                      the application server

  Linux / Ubuntu                      Operating system used on the EC2
                                      servers
  -----------------------------------------------------------------------

## Repository Structure

A typical structure for this project is:

``` text
AWS_DEVOPS-CI-CD/
├── main.py                  # FastAPI application (if named this way)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Instructions to build the app image
├── Jenkinsfile              # CI/CD pipeline definition
├── docker-compose.prod.yml  # Production services configuration
├── deploy.sh                # Deployment commands on the app server
├── .gitignore               # Files Git should ignore
└── README.md                # Project documentation
```


## Prerequisites

Before reproducing the deployment, prepare:

-   A GitHub repository containing the application and pipeline files.
-   An AWS account with permission to manage EC2 and ECR.
-   A Jenkins server with the required plugins and tools.
-   Docker installed on the machine that builds the image.
-   An EC2 application server with Docker and Docker Compose installed.
-   An ECR repository for the application image.
-   SSH connectivity from Jenkins to the application server.
-   AWS permissions that allow the pipeline to push and pull ECR images.
-   A PostgreSQL configuration and credentials supplied securely through
    environment variables or a secret-management system.

Exact package versions and Jenkins plugins should be documented after
checking the actual server configuration.

## AWS Infrastructure

The project uses two EC2 instances:

### 1. Jenkins server

Responsibilities:

-   Hosts Jenkins.
-   Retrieves source code from GitHub.
-   Executes the configured pipeline.
-   Builds and publishes the Docker image.
-   Connects to the application server to initiate deployment.

### 2. Application server

Responsibilities:

-   Pulls the application image from ECR.
-   Runs the FastAPI container.
-   Runs the PostgreSQL container through Docker Compose.
-   Exposes the application API on port `8000`, subject to EC2
    security-group and host firewall rules.

### Amazon ECR

The configured image repository is:

``` text
010603499783.dkr.ecr.ap-southeast-2.amazonaws.com/fastapi-app
```

The AWS region used in the current setup is **Asia Pacific (Sydney),
`ap-southeast-2`**.

Image tags can change with each build. The previously deployed image
included tag `3`; confirm the current tag in ECR and on the application
server before documenting a new deployment.

**Do not publish SSH private keys, AWS credentials, database passwords,
access tokens, or `.env` files in the repository.**

## Configuration and Secrets

Configure sensitive values in Jenkins Credentials, environment
variables, or an appropriate AWS secrets service. Do not hard-code
secrets in the source code or commit them to GitHub.

Typical configuration values may include:

  Setting                  Purpose
  ------------------------ -----------------------------------------------------
  AWS region               Region containing ECR and EC2 resources
  ECR repository URI       Location of the Docker image
  Image tag                Version of the image to deploy
  Database name            PostgreSQL database name
  Database user/password   Database authentication
  Database host/port       Database connection settings
  SSH credential           Allows Jenkins to connect to the application server

Use placeholders in examples. Never include real secret values in this
README.

A `.gitignore` should exclude private keys, environment files, local
virtual environments, caches, and other sensitive or generated files.
For example:

``` gitignore
.env
.env.*
!.env.example
*.pem
*.key
id_rsa
id_ed25519
__pycache__/
.venv/
venv/
*.py[cod]
```

Review the existing `.gitignore` before changing it. If a secret was
committed in the past, deleting it from the latest commit is not enough;
rotate the exposed credential and clean the repository history if
appropriate.

## How the Pipeline Works

### Jenkins

Jenkins runs the stages defined in `Jenkinsfile`. The actual stages
depend on the file in this repository. A typical pipeline can include:

1.  Checkout code.
2.  Build the Docker image.
3.  Authenticate to ECR.
4.  Push the image to ECR.
5.  Copy deployment files or connect to the application server.
6.  Deploy the selected image.
7.  Run a health check.

Only claim that automated tests run if a test stage is present and has
actually passed.

### Docker and Amazon ECR

Docker builds a versioned image from the application source and
Dockerfile. Jenkins then pushes the image to the configured ECR
repository. The application server can pull that image during
deployment.

### Application EC2 and Docker Compose

The deployment process uses the Compose configuration and deployment
script to start the services. The application service uses the selected
image, while the database service uses PostgreSQL. The database should
use a persistent volume if data must survive container replacement.

**Database safety:** Do not use `docker compose down -v` on a database
that contains data you need to preserve. The `-v` option can remove
Compose-managed volumes.

## Run the Application

The commands below are examples for an environment where Docker and
Docker Compose are installed and the configuration files are present.
Adapt file names and environment settings to match the repository.

### 1. Clone the repository

``` bash
git clone https://github.com/RupeshO7a/AWS_DEVOPS-CI-CD.git
cd AWS_DEVOPS-CI-CD
```

### 2. Review configuration

Check the Dockerfile, Compose file, application settings, and
environment-variable names. Configure the required values securely. Do
not put real passwords or private keys in the repository.

### 3. Build the image locally (optional)

``` bash
docker build -t fastapi-app:local .
```

### 4. Start services with Docker Compose

If the Compose file expects an `IMAGE` variable, set it to the image you
intend to run. For example, after building the local image:

``` bash
IMAGE=fastapi-app:local docker compose -f docker-compose.prod.yml up -d
```

If your Compose file has a different name or uses different environment
variables, adjust the command accordingly. Production deployment should
use the intended ECR image and secure configuration.

### 5. Check container status and logs

``` bash
docker compose ps
docker compose logs --tail=100
```

Run these commands in the directory containing the Compose file and
ensure any required environment variables are loaded.

## API Endpoints

The deployed application was verified using the following endpoints:

  Endpoint        Purpose
  --------------- ----------------------------------------------------
  `GET /docs`     Interactive Swagger API documentation
  `GET /health`   Health check, including database connectivity
  `GET /items`    Returns application records stored in the database

Replace `<APP_PUBLIC_IP>` with the current public IP or DNS name of the
application EC2 instance.

``` text
http://<APP_PUBLIC_IP>:8000/docs
http://<APP_PUBLIC_IP>:8000/health
http://<APP_PUBLIC_IP>:8000/items
```

Do not assume a public address is permanent; an EC2 public IP can change
after stopping and starting an instance unless an Elastic IP is
assigned.

## Verification and Testing

The following results were observed during the successful deployment:

-   Jenkins Build #3 finished with `SUCCESS`.
-   The deployment output reported that the application was deployed
    successfully.
-   The `fastapi-app` container was running.
-   The `fastapi-db` PostgreSQL container was reported healthy.
-   The health endpoint returned:

``` json
{
  "status": "ok",
  "database": "connected"
}
```

-   The `/items` endpoint returned saved records from the database.

These results demonstrate a successful deployment and database
connectivity at the time of the check. Re-run the checks before
presenting the project to confirm the current environment is still
available.

### Useful server-side checks

On the application server:

``` bash
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/items
```

## Security Considerations

-   Never commit private SSH keys such as `.pem`, `id_rsa`, or
    `id_ed25519` files.
-   Never commit AWS access keys, database passwords, or production
    `.env` files.
-   Restrict SSH access to trusted sources and use least-privilege
    permissions.
-   Limit public inbound traffic to only the ports required for the
    demonstration.
-   Avoid exposing Jenkins publicly without appropriate access controls.
-   Use secure secret storage for credentials used by Jenkins.
-   Use persistent storage and backups for PostgreSQL data.
-   Rotate credentials immediately if they are exposed.
-   Review screenshots and logs before uploading them to GitHub.

## Troubleshooting

### Jenkins cannot connect to the application server

-   Verify the application server is running.
-   Confirm Jenkins has the correct SSH private key in its credential
    store or configured key path.
-   Confirm the matching public key is authorized for the target
    account.
-   Check the EC2 security group and network connectivity for SSH.
-   Verify the target username and private IP address.

### Docker image push to ECR fails

-   Confirm the AWS region and ECR repository URI.
-   Check that Jenkins has permission to authenticate and push images.
-   Verify the image tag and ECR login command.
-   Review Jenkins console output for the first error.

### Application container does not start

-   Check `docker compose ps` and `docker compose logs`.
-   Verify the selected image tag exists in ECR.
-   Check the application environment variables and dependencies.
-   Confirm the port mapping and application bind address.

### Health endpoint cannot connect to PostgreSQL

-   Confirm the PostgreSQL container is running and healthy.
-   Check database credentials, database name, and connection settings.
-   When using Docker Compose, the database hostname is normally the
    Compose service name, not `localhost` inside the app container.
-   Review application and database logs.

### API cannot be reached from a browser

-   Confirm the application container is running and listening on port
    `8000`.
-   Check the EC2 security group and host firewall.
-   Confirm you are using the current public IP or DNS name.
-   Avoid opening ports broadly to the internet when a narrower rule is
    sufficient.

## Known Limitations

-   Exact Jenkins stages and test coverage depend on the committed
    `Jenkinsfile`.
-   Automatic deployment on each push requires a working webhook or
    configured Jenkins trigger.
-   Public IP addresses may change unless a stable address is
    configured.
-   AWS resources can incur charges while running.
-   Production use would require additional hardening, monitoring,
    backup, and access-control practices.

## Future Improvements

-   Add automated unit and integration tests to the Jenkins pipeline.
-   Configure and verify a GitHub webhook for automatic builds.
-   Use IAM roles and least-privilege permissions for AWS access.
-   Store secrets in Jenkins Credentials or AWS Secrets Manager.
-   Add deployment rollback and image-version retention.
-   Add HTTPS using a domain name and TLS certificate.
-   Add monitoring, centralized logs, and alerts.
-   Configure database backups and test restoration.
-   Add vulnerability scanning for Docker images.
-   Add health checks and deployment gates before promoting a release.

## Learning Outcomes

Through this project, the team gains practical experience with:

-   Source control and version history using GitHub.
-   CI/CD pipeline concepts and Jenkins.
-   Docker image creation and container management.
-   Publishing images to Amazon ECR.
-   Deploying to EC2 over SSH.
-   Running multiple services with Docker Compose.
-   Connecting a FastAPI application to PostgreSQL.
-   Verifying deployments through health checks and API responses.
-   Applying basic secret-management and cloud-security practices.

## Author / Project Repository

**Repository:**
[AWS_DEVOPS-CI-CD](https://github.com/RupeshO7a/AWS_DEVOPS-CI-CD)

------------------------------------------------------------------------

*This README documents the project workflow and the results observed
during the successful deployment. Before final submission, confirm that
filenames, commands, screenshots, Jenkins stages, and configuration
details match the current contents of your repository.*
