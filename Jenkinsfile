pipeline {
    agent any

    environment {
        IMAGE_NAME = "aura-ai-app"
        CONTAINER_NAME = "aura-ai-container"
        DOCKER_BIN = "/usr/local/bin/docker"
        DOCKER_HOST = "unix:///var/run/docker.sock"
        // Bypass Docker Desktop's local password manager for public images
        DOCKER_CONFIG = "/tmp"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                echo 'Building the Aura AI Docker container...'
                sh '${DOCKER_BIN} build -t ${IMAGE_NAME} .'
            }
        }

        stage('Dry Run / Testing') {
            steps {
                echo 'Testing predictive engine inside the container...'
                sh '${DOCKER_BIN} run --rm ${IMAGE_NAME} python forecaster.py'
            }
        }

        stage('Deploy to Production (Local)') {
            steps {
                echo 'Deploying the new container...'
                sh '${DOCKER_BIN} stop ${CONTAINER_NAME} || true'
                sh '${DOCKER_BIN} rm ${CONTAINER_NAME} || true'
                sh '${DOCKER_BIN} run -d -p 8501:8501 --name ${CONTAINER_NAME} --add-host=host.docker.internal:host-gateway ${IMAGE_NAME}'
            }
        }
    }
}
