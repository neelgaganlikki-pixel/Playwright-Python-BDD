pipeline {

    agent any

    parameters {

        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit'],
            description: 'Browser engine for test execution'
        )

        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Execute tests in headless mode'
        )

        string(
            name: 'SLOW_MO',
            defaultValue: '0',
            description: 'Slow motion delay in milliseconds'
        )

        string(
            name: 'TEST_MARKER',
            defaultValue: '',
            description: 'Pytest marker expression. Leave empty to run all tests.'
        )
    }

    environment {

        BASE_URL = 'https://opensource-demo.orangehrmlive.com/'

        ORANGEHRM_USERNAME = 'Admin'

        HEADLESS = "${params.HEADLESS}"

        BROWSER = "${params.BROWSER}"

        SLOW_MO = "${params.SLOW_MO}"

        ORANGEHRM_PASSWORD = credentials(
            'orangehrm-admin-password'
        )
    }

    stages {

        stage('Checkout') {

            steps {

                echo '========================================'
                echo 'CHECKOUT'
                echo '========================================'

                checkout scm
            }
        }


        stage('Environment Check') {

            steps {

                echo 'Checking environment...'

                bat '''
                    python --version
                    python -m pip --version
                    git --version
                '''
            }
        }


        stage('Setup Environment & Dependencies') {

            steps {

                echo '========================================'
                echo 'SETTING UP PYTHON ENVIRONMENT'
                echo '========================================'

                bat '''
                    if not exist venv (
                        python -m venv venv
                    )

                    call venv\\Scripts\\activate

                    python -m pip install --upgrade pip

                    python -m pip install -r requirements.txt
                '''
            }
        }


        stage('Install Playwright Browsers') {

            steps {

                echo 'Installing Playwright browsers...'

                bat '''
                    call venv\\Scripts\\activate

                    python -m playwright install chromium firefox webkit
                '''
            }
        }


        stage('Execute Playwright BDD Tests') {

            steps {

                echo '========================================'
                echo 'RUNNING PLAYWRIGHT BDD TESTS'
                echo '========================================'

                echo "Browser: ${params.BROWSER}"
                echo "Headless: ${params.HEADLESS}"
                echo "Slow Mo: ${params.SLOW_MO}"
                echo "Marker: ${params.TEST_MARKER}"

                bat '''
                    if not exist reports mkdir reports
                    if not exist screenshots mkdir screenshots

                    call venv\\Scripts\\activate

                    if "%TEST_MARKER%"=="" (
                        pytest -v -s ^
                            --html=reports/report.html ^
                            --self-contained-html
                    ) else (
                        pytest -m "%TEST_MARKER%" -v -s ^
                            --html=reports/report.html ^
                            --self-contained-html
                    )
                '''
            }
        }
    }


    post {

        always {

            echo '========================================'
            echo 'PUBLISHING TEST REPORTS'
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
ORANGEHRM TEST EXECUTION SUCCESSFUL
========================================
All selected Playwright BDD tests passed.
========================================
'''
        }


        failure {

            echo '''
========================================
ORANGEHRM TEST EXECUTION FAILED
========================================
Check the Console Output,
HTML report and screenshots.
========================================
'''
        }


        cleanup {

            echo 'Jenkins pipeline execution completed.'
        }
    }
}