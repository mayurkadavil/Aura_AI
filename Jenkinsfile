pipeline {
    agent any

    environment {
        IMAGE_NAME = "aura-ai-app"
        CONTAINER_NAME = "aura-ai-container"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                echo 'Building the Aura AI Docker container...'
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Dry Run / Testing') {
            steps {
                echo 'Testing predictive engine inside the container...'
                sh 'docker run --rm ${IMAGE_NAME} python forecaster.py'
            }
        }

        stage('Deploy to Production (Local)') {
            steps {
                echo 'Deploying the new container...'
                sh 'docker stop ${CONTAINER_NAME} || true'
                sh 'docker rm ${CONTAINER_NAME} || true'
                sh 'docker run -d -p 8501:8501 --name ${CONTAINER_NAME} --add-host=host.docker.internal:host-gateway ${IMAGE_NAME}'
            }
        }
    }
}
