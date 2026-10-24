pipeline {
    agent any
 
    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }
 
    // Start this pipeline automatically when GitHub sends a "push" webhook
    triggers {
        githubPush()
    }
 
    environment {
        // ======== EDIT THESE 4 VALUES ========
        AWS_ACCOUNT_ID = '010603499783'      // your 12-digit AWS account ID
        AWS_REGION     = 'ap-southeast-2'        // region where you created ECR
        ECR_REPO       = 'fastapi-app'       // ECR repository name
        APP_HOST       = '172.31.36.119'      // PRIVATE IP of the App server
        // =====================================
 
        APP_USER     = 'ubuntu'
        APP_DIR      = '/home/ubuntu/app'
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_URI    = "${ECR_REGISTRY}/${ECR_REPO}"
        IMAGE_TAG    = "${env.BUILD_NUMBER}"
    }
 
    stages {
 
        stage('1. Checkout code from GitHub') {
            steps {
                checkout scm
                sh 'git log -1 --pretty=format:"Commit: %h | Author: %an | Message: %s"'
            }
        }
 
        stage('2. Build Docker image') {
            steps {
                sh 'docker build -t ${IMAGE_URI}:${IMAGE_TAG} -t ${IMAGE_URI}:latest .'
            }
        }
 
        stage('3. Push image to Amazon ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | \
                      docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    docker push ${IMAGE_URI}:${IMAGE_TAG}
                    docker push ${IMAGE_URI}:latest
                '''
            }
        }
 
        stage('4. Deploy on the EC2 app server') {
            steps {
                sh '''
                    SSH_OPTS="-o StrictHostKeyChecking=accept-new -o BatchMode=yes -o ConnectTimeout=15"
                    TARGET=${APP_USER}@${APP_HOST}
 
                    scp $SSH_OPTS docker-compose.prod.yml ${TARGET}:${APP_DIR}/docker-compose.yml
                    scp $SSH_OPTS deploy.sh ${TARGET}:${APP_DIR}/deploy.sh
                    ssh $SSH_OPTS ${TARGET} \
                      "bash ${APP_DIR}/deploy.sh ${IMAGE_URI}:${IMAGE_TAG} ${AWS_REGION} ${ECR_REGISTRY}"
                '''
            }
        }
 
        stage('5. Health check') {
            steps {
                sh '''
                    for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
                        if curl -fsS http://${APP_HOST}:8000/health; then
                            echo ""
                            echo "SUCCESS: the app is running and connected to PostgreSQL"
                            exit 0
                        fi
                        echo "App not ready yet (try $i of 12) - waiting 5 seconds..."
                        sleep 5
                    done
                    echo "FAILED: the app did not become healthy"
                    exit 1
                '''
            }
        }
    }
 
    post {
        always {
            // Free disk space on the Jenkins server
            sh 'docker rmi ${IMAGE_URI}:${IMAGE_TAG} ${IMAGE_URI}:latest || true'
            sh 'docker image prune -f || true'
        }
        success {
            echo "Build #${env.BUILD_NUMBER} deployed successfully."
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} FAILED - open Console Output and read the first red error."
        }
    }
}
