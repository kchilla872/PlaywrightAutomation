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
                bat 'python -m pip install --upgrade pip'
                bat 'pip install -r requirements.txt'
                bat 'playwright install'
            }
        }
        stage('Run Tests') {
            steps {
                bat 'pytest homePage.py -v'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
