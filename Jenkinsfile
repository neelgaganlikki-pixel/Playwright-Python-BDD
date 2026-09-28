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

        /*
         * IMPORTANT:
         * Jenkins could not find Python through PATH.
         * Therefore we use the absolute Python executable path.
         */
        PYTHON_EXE = 'C:\\Users\\NEELGAGAN B R\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'

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


        stage('Setup Environment & Dependencies') {

            steps {

                echo '========================================'
                echo 'SETTING UP PYTHON ENVIRONMENT'
                echo '========================================'

                bat '''
                    if not exist venv (
                        echo Creating Python virtual environment...
                        "%PYTHON_EXE%" -m venv venv
                    )

                    echo Activating virtual environment...
                    call venv\\Scripts\\activate

                    echo.
                    echo Upgrading pip...
                    python -m pip install --upgrade pip

                    echo.
                    echo Installing project dependencies...
                    python -m pip install -r requirements.txt
                '''
            }
        }


        stage('Install Playwright Browsers') {

            steps {

                echo '========================================'
                echo 'INSTALLING PLAYWRIGHT BROWSERS'
                echo '========================================'

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

                echo "Browser    : ${params.BROWSER}"
                echo "Headless   : ${params.HEADLESS}"
                echo "Slow Mo    : ${params.SLOW_MO}"
                echo "Test Marker: ${params.TEST_MARKER}"

                bat '''
                    if not exist reports mkdir reports

                    if not exist screenshots mkdir screenshots

                    call venv\\Scripts\\activate

                    echo.
                    echo Starting Pytest...
                    echo.

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

Check:
1. Console Output
2. HTML Test Report
3. Failure Screenshots

========================================
'''
        }


        cleanup {

            echo 'Jenkins pipeline execution completed.'
        }
    }
}