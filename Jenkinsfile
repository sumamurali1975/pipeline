pipeline {
  agent any

  environment {
    
    WORKSPACE           = '.'
    DBRKS_BEARER_TOKEN  = "xyz"
    DBTOKEN             ="DBTOKEN"
    CLUSTERID           ="1228-220746-bqqkddxs"
    DBURL               ="https://adb-6840195589605290.10.azuredatabricks.net"

    TESTRESULTPATH  ="./teste_results"
    LIBRARYPATH     = "./Libraries"
    OUTFILEPATH     = "./Validation/Output"
    NOTEBOOKPATH    = "./Notebooks"
    WORKSPACEPATH   = "/Shared"
    DBFSPATH        = "dbfs:/FileStore/"
    BUILDPATH       = "${WORKSPACE}/Builds/${env.JOB_NAME}-${env.BUILD_NUMBER}"
    SCRIPTPATH      = "./Scripts"
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

            pip install --user databricks-cli
            pip install -U databricks-connect
            pip install pytest
            databricks --version

           '''
        }

    }
    
      stage('Configure Databricks') {
        steps {
           withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) { 
            sh """#!/bin/bash
                
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate mlops2

                #pip install -r requirements.txt
                export PATH="$HOME/.local/bin:$PATH"
                echo $PATH
          
                # Configure Databricks CLI for deployment
                echo "${DBURL}
                $TOKEN" | databricks configure --token

                # Configure Databricks Connect
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
              sh """#!/bin/bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate mlops2

                # Python tests for libs
                python -m pytest --junit-xml=${TESTRESULTPATH}/TEST-libout.xml ${LIBRARYPATH}/python/dbxdemo/test*.py || true
                """
          } catch(err) {
            step([$class: 'JUnitResultArchiver', testResults: '--junit-xml=${TESTRESULTPATH}/TEST-*.xml'])
            if (currentBuild.result == 'UNSTABLE')
              currentBuild.result = 'FAILURE'
            throw err
          }
        }
      }
    }

    stage('Build Artifact') {
        steps {
            sh """mkdir -p "${BUILDPATH}/Workspace"
              mkdir -p "${BUILDPATH}/Libraries/python"
              mkdir -p "${BUILDPATH}/Validation/Output"
              
              cp ${WORKSPACE}/Workspace/*.ipynb ${BUILDPATH}/Workspace
    
              # Get packaged libs
              find ${LIBRARYPATH} -name '*.whl' | xargs -I '{}' cp '{}' ${BUILDPATH}/Libraries/python/

              # Generate artifact
              #tar -czvf Builds/latest_build.tar.gz ${BUILDPATH}
           """
        }

    }

    stage('Deploy') {
          steps { 
            withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) {        
              sh """#!/bin/bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate mlops2
                export PATH="$HOME/.local/bin:$PATH"


                # Use Databricks CLI to deploy notebooks
                databricks workspace import_dir --overwrite ${BUILDPATH}/Workspace ${WORKSPACEPATH}
                dbfs cp -r ${BUILDPATH}/Libraries/python ${DBFSPATH}
                """
            }
          }
    }

    stage('Run Integration Tests') {
      steps {   
          withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) {
          
          sh """#!/bin/bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate mlops2
                export PATH="$HOME/.local/bin:$PATH"

                python3 ${SCRIPTPATH}/executenotebook.py --workspace=${DBURL}\
                          --token=$TOKEN\
                          --clusterid=${CLUSTERID}\
                          --localpath=${NOTEBOOKPATH}/VALIDATION\
                          --workspacepath=${WORKSPACEPATH}/VALIDATION\
                          --outfilepath=${OUTFILEPATH}
             """
          }
        sh """sed -i -e 's #ENV# ${OUTFILEPATH} g' ${SCRIPTPATH}/evaluatenotebookruns.py
              python3 -m pytest --junit-xml=${TESTRESULTPATH}/TEST-notebookout.xml ${SCRIPTPATH}/evaluatenotebookruns.py || true
           """
      }
    }

    stage('Execute Notebook') {
      steps {
           withCredentials([string(credentialsId: DBTOKEN, variable: 'TOKEN')]) { 
            sh """#!/bin/bash
                
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate mlops2

                #pip install -r requirements.txt
                export PATH="$HOME/.local/bin:$PATH"
                echo $PATH

                

                # Configure Databricks Connect for testing
                echo "${DBURL}
                $TOKEN
                ${CLUSTERID}
                0
                15001" | databricks-connect configure

                python ${SCRIPTPATH}/executenotebook.py --workspace=${DBURL}\
                      --token=$TOKEN\
                      --clusterid=${CLUSTERID}\
                      --localpath=${NOTEBOOKPATH}\
                      --workspacepath=${WORKSPACEPATH}\
                      --outfilepath=${OUTFILEPATH}
                """
                
           }
      }
    }
  } 
}