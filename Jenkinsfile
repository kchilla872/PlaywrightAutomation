pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/kchilla872/Playwright.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                bat 'python -m venv venv'
                bat 'python -m pip install --upgrade pip'
                bat 'call venv\\Scripts\\activate && pip install -r requirements.txt'
                bat 'call venv\\Scripts\\activate && playwright install'
            }
        }
        stage('Run Tests') {
            steps {
                bat 'call venv\\Scripts\\activate && pytest homePage.py -v'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
