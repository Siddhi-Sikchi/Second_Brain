
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {

        stage('Verify Tools') {
            steps {
                echo 'Checking installed development tools...'

                bat 'python --version'
                bat 'node --version'
                bat 'npm --version'
                bat 'git --version'
            }
        }

        stage('Backend Dependencies') {
            steps {
                dir('backend') {
                    echo 'Installing Python dependencies...'

                    bat 'python -m venv .venv-ci'

                    bat '.venv-ci\\Scripts\\python.exe -m pip install --upgrade pip'

                    bat '.venv-ci\\Scripts\\python.exe -m pip install -r requirements.txt'
                }
            }
        }

        stage('Backend Testing') {
            steps {
                dir('backend') {
                    echo 'Running backend Pytest cases...'

                    bat '.venv-ci\\Scripts\\python.exe -m pytest tests -v'
                }
            }
        }

        stage('Frontend Dependencies') {
            steps {
                dir('frontend') {
                    echo 'Installing frontend dependencies...'

                    bat 'npm ci'
                }
            }
        }

        stage('Frontend Build') {
            steps {
                dir('frontend') {
                    echo 'Building React application...'

                    bat 'npm run build'
                }
            }
        }

        stage('Continuous Delivery') {
            steps {
                echo 'Preparing application delivery artifacts...'

                archiveArtifacts(
                    artifacts: 'frontend/dist/**',
                    fingerprint: true
                )
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Second Brain CI/CD pipeline completed!'
        }

        failure {
            echo 'FAILURE: Check the Jenkins console output for errors.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}
