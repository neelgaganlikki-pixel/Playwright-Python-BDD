pipeline {

    agent any

    environment {

        // Explicit Python installation used by Jenkins
        PYTHON_EXE = 'C:\\Users\\NEELGAGAN B R\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'

        // OrangeHRM configuration
        BASE_URL = 'https://opensource-demo.orangehrmlive.com/'

        ORANGEHRM_USERNAME = 'Admin'

        // CI settings
        HEADLESS = 'true'
        BROWSER = 'chromium'
        SLOW_MO = '0'

        // Jenkins Credential
        ORANGEHRM_PASSWORD = credentials(
            'orangehrm-admin-password'
        )
    }


    stages {

        stage('Environment Check') {

            steps {

                echo '========================================'
                echo 'ENVIRONMENT CHECK'
                echo '========================================'

                bat '''
                    echo Checking Python...
                    "%PYTHON_EXE%" --version

                    echo.
                    echo Checking pip...
                    "%PYTHON_EXE%" -m pip --version

                    echo.
                    echo Checking Git...
                    git --version
                '''
            }
        }


        stage('Setup Python Environment') {

            steps {

                echo '========================================'
                echo 'SETTING UP PYTHON ENVIRONMENT'
                echo '========================================'

                bat '''
                    if not exist venv (
                        echo Creating virtual environment...
                        "%PYTHON_EXE%" -m venv venv
                    )

                    echo Activating virtual environment...
                    call venv\\Scripts\\activate

                    echo.
                    echo Upgrading pip...
                    python -m pip install --upgrade pip

                    echo.
                    echo Installing dependencies...
                    python -m pip install -r requirements.txt
                '''
            }
        }


        stage('Install Playwright') {

            steps {

                echo '========================================'
                echo 'INSTALLING PLAYWRIGHT BROWSER'
                echo '========================================'

                bat '''
                    call venv\\Scripts\\activate

                    python -m playwright install chromium
                '''
            }
        }


        stage('Run Tests') {

            steps {

                echo '========================================'
                echo 'RUNNING PLAYWRIGHT BDD TESTS'
                echo '========================================'

                bat '''
                    if not exist reports mkdir reports

                    if not exist screenshots mkdir screenshots

                    call venv\\Scripts\\activate

                    echo.
                    echo Running complete test suite...
                    echo.

                    pytest -v -s ^
                        --html=reports/report.html ^
                        --self-contained-html
                '''
            }
        }
    }


    post {

        always {

            echo '========================================'
            echo 'PUBLISHING TEST REPORT'
            echo '========================================'

            publishHTML(
                target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'OrangeHRM Automation Execution Report'
                ]
            )


            archiveArtifacts(
                artifacts: 'screenshots/*.png, reports/*.log',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }


        success {

            echo '''
========================================
ORANGEHRM CI BUILD SUCCESSFUL
========================================

All Playwright BDD tests passed.

========================================
'''
        }


        failure {

            echo '''
========================================
ORANGEHRM CI BUILD FAILED
========================================

Check:
1. Console Output
2. HTML Test Report
3. Failure Screenshots

========================================
'''
        }


        cleanup {

            echo 'Jenkins pipeline completed.'
        }
    }
}
