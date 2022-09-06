pipeline {
  agent any

  environment {
    
    //WORKSPACE           = '.'
    //DBRKS_BEARER_TOKEN  = "xyz"
    DBTOKEN             = "databricks-token"
    CLUSTERID           = "AWS-Glue Catalogue Cluster"
    DBURL               = "https://dbc-db420c65-4456.cloud.databricks.com"

    TESTRESULTPATH  ="./teste_results"
    LIBRARYPATH     = "./Libraries"
    OUTFILEPATH     = "./Validation/Output"
    NOTEBOOKPATH    = "./Notebooks"
    WORKSPACEPATH   = "/Demo-notebooks"               //"/Shared"
    DBFSPATH        = "dbfs:/FileStore/"
    BUILDPATH       = "${WORKSPACE}/Builds/${env.JOB_NAME}-${env.BUILD_NUMBER}"
    SCRIPTPATH      = "./Scripts"
    projectName = "${WORKSPACE}"  //var/lib/jenkins/workspace/Demopipeline/
    projectKey = "key"
 }

  stages {
    stage('Install Miniconda') {
        steps {

            sh '''#!/usr/bin/env bash
            echo "Inicianddo os trabalhos"  
            wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -nv -O miniconda.sh

            rm -r $WORKSPACE/miniconda
            bash miniconda.sh -b -p $WORKSPACE/miniconda
            
            export PATH="$WORKSPACE/miniconda/bin:$PATH"
            echo $PATH

            conda config --set always_yes yes --set changeps1 no
            conda update -q conda
            conda create --name mlops2
            
            echo ${BUILDPATH}
	    
            '''
        }

    }

    stage('Install Requirements') {
        steps {
            sh '''#!/usr/bin/env bash
            echo "Installing Requirements"  
            source $WORKSPACE/miniconda/etc/profile.d/conda.sh
            
	    conda activate mlops2
            export PATH="$HOME/.local/bin:$PATH"
            echo $PATH
	    
	    # pip install --user databricks-cli
            # pip install -U databricks-connect
	    
            pip install -r requirements.txt requirements-test.txt
            databricks --version

           '''
        }

    }
	  
stage('Databricks Setup') {
	steps{
		  withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) {
			sh """#!/bin/bash
			#Configure conda environment
			conda activate mlops2
			export PATH="$HOME/.local/bin:$PATH"
			echo $PATH
			# Configure Databricks CLI for deployment
			echo "${DBURL}
			$TOKEN" | databricks configure --token
			# Configure Databricks Connect for testing
			echo "${DBURL}
			$TOKEN
			${CLUSTERID}
			0
			15001" | databricks-connect configure
			"""
		  }	
	}
}

stage('Unit Tests') {
      steps {

        script {
            try {
		 withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) {   
		      sh """#!/bin/bash
			source $WORKSPACE/miniconda/etc/profile.d/conda.sh
			conda activate mlops2
			conda list
			DEBUG_IGNORE_VERSION_MISMATCH=1
			# Configure Databricks Connect for testing
			echo "${DBURL}
			$TOKEN
			${CLUSTERID}
			0
			15001" | databricks-connect configure
			# Python tests
			python3 -m pytest --junit-xml=${TESTRESULTPATH}/TEST-libout.xml ${LIBRARYPATH}/python/dbxdemo/test*.py || true
			"""
		 }
          } catch(err) {
            step([$class: 'JUnitResultArchiver', testResults: '--junit-xml=${TESTRESULTPATH}/TEST-*.xml'])
            if (currentBuild.result == 'UNSTABLE')
              currentBuild.result = 'FAILURE'
            throw err
          }
        }
      }
    }
	  
stage('Package') {
     steps{
	  sh """#!/bin/bash
	      # Enable Conda environment for tests
	      source $WORKSPACE/miniconda/etc/profile.d/conda.sh
	      conda activate mlops2
	      conda list

	      # Package Python library to wheel
	      cd ${LIBRARYPATH}/python/dbxdemo
	      pip install wheel
	      python3 setup.py sdist bdist_wheel
	     """
     }
}
	  
stage('Build Artifact') {
        steps {
            sh """mkdir -p "${BUILDPATH}/Workspace"
	              mkdir -p "${BUILDPATH}/Workspace/Notebooks-tests"
                  mkdir -p "${BUILDPATH}/Libraries/python"
                  mkdir -p "${BUILDPATH}/Validation/Output"
              
                  cp ${WORKSPACE}/Notebooks/*.ipynb ${BUILDPATH}/Workspace
	          cp ${WORKSPACE}/Notebooks-tests/*.py ${BUILDPATH}/Workspace/Notebooks-tests
    
                  # Get packaged libs
                  find ${LIBRARYPATH} -name '*.whl' | xargs -I '{}' cp '{}' ${BUILDPATH}/Libraries/python/

                  # Generate artifact
                  #tar -czvf Builds/latest_build.tar.gz ${BUILDPATH}
                """
	        slackSend failOnError: true, color: "#439FE0", message: "Build Started: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }

    }
	  
stage('SonarQube analysis') {
          steps {
            //def scannerhome = tool name: 'SonarQubeScanner'

            withEnv(["PATH=/usr/bin:/usr/local/jdk-11.0.2/bin:/opt/sonarqube/sonar-scanner/bin/"]) {
            withSonarQubeEnv('sonar') {
                     sh "/opt/sonar-scanner/bin/sonar-scanner -Dsonar.projectKey=demo-project -Dsonar.projectVersion=0.0.3 -Dsonar.sources=${BUILDPATH} -Dsonar.host.url=http://107.20.71.233:9001 -Dsonar.login=ab9d8f9c15baff5428b9bf18b0ec198a5b35c6bb -Dsonar.python.coverage.reportPaths=coverage.xml -Dsonar.sonar.inclusions=**/*.ipynb -Dsonar.exclusions=**/*.ini,**/*.py,**./*.sh"
	   
	                 slackSend color: '#BADA55', message: 'Pipeline SonarQube analysis Done', timestamp :''
	      }
              }
		
        }
        }
   
stage('Databricks Deploy') {
          steps { 
            withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) {        
              sh """#!/bin/bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate mlops2
                export PATH="$HOME/.local/bin:$PATH"


                # Use Databricks CLI to deploy notebooks
		databricks workspace mkdirs ${WORKSPACEPATH}
                databricks workspace import_dir --overwrite ${BUILDPATH}/Workspace ${WORKSPACEPATH}
                dbfs cp -r ${BUILDPATH}/Libraries/python ${DBFSPATH}
                """
		      slackSend color: '#BADA55', message:'Pipeline Databricks Deploy Done'
		      slackSend color: '#FF0000', message:' Databricks Pipeline Deployment Finished', iconEmoji: ":white_check_mark:"
            }
          }
    }
  }
  post {
		success {
		  withAWS(credentials:'AWSCredentialsForSnsPublish') {
				snsPublish(
					topicArn:'arn:aws:sns:us-east-1:872161624847:mdlp-build-status-topic', 
					subject:"Job:${env.JOB_NAME}-Build Number:${env.BUILD_NUMBER} is a ${currentBuild.currentResult}", 
					message: "Please note that for Jenkins job:${env.JOB_NAME} of build number:${currentBuild.number} - ${currentBuild.currentResult} happened!"
				)
			}
		}
		failure {
		  withAWS(credentials:'AWSCredentialsForSnsPublish') {
				snsPublish(
					topicArn:'arn:aws:sns:us-east-1:872161624847:mdlp-build-status-topic', 
					subject:"Job:${env.JOB_NAME}-Build Number:${env.BUILD_NUMBER} is a ${currentBuild.currentResult}", 
					message: "Please note that for Jenkins job:${env.JOB_NAME} of build number:${currentBuild.number} - ${currentBuild.currentResult} happened! Details here: ${BUILD_URL}."
				)
			}
		}
  }
}


