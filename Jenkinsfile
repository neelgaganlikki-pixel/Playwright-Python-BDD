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
            description: 'Slow motion delay in milliseconds (e.g. 0 or 500)'
        )
        string(
            name: 'TEST_MARKER',
            defaultValue: 'smoke or regression',
            description: 'Pytest marker expression (e.g. smoke, regression, login, employee, leave, recruitment, buzz)'
        )
    }

    environment {
        BASE_URL = 'https://opensource-demo.orangehrmlive.com/'
        ORANGEHRM_USERNAME = 'Admin'
        HEADLESS = "${params.HEADLESS}"
        BROWSER = "${params.BROWSER}"
        SLOW_MO = "${params.SLOW_MO}"
        // Securely bind password credential from Jenkins Credential Store
        ORANGEHRM_PASSWORD = credentials('orangehrm-admin-password')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source repository...'
                checkout scm
            }
        }

        stage('Setup Environment & Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing packages...'
                // Windows batch / PowerShell support
                bat '''
                    if not exist venv (
                        python -m venv venv
                    )
                    call venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    python -m playwright install chromium
                '''
            }
        }

        stage('Execute Playwright BDD Tests') {
            steps {
                echo "Running pytest-bdd tests with marker: ${params.TEST_MARKER} on ${params.BROWSER}..."
                bat '''
                    call venv\\Scripts\\activate
                    pytest -m "%TEST_MARKER%" --html=reports/report.html --self-contained-html
                '''
            }
        }
    }

    post {
        always {
            echo 'Publishing test reports and archiving screenshots...'
            // Publish Pytest HTML report
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'OrangeHRM Automation Execution Report'
            ])

            // Archive failure screenshots and execution logs
            archiveArtifacts artifacts: 'screenshots/*.png, reports/*.log', allowEmptyArchive: true
        }
        success {
            echo 'All OrangeHRM Playwright BDD test scenarios passed successfully!'
        }
        failure {
            echo 'One or more test scenarios failed. Check the execution report and failure screenshots.'
        }
    }
}
