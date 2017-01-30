#!/bin/bash

set -e

StudyFolder="$1"
Subject="$2"
TaskName="$3"

DirectionList=""
DirectionList="${DirectionList} RL"
DirectionList="${DirectionList} LR"


for direction in ${DirectionList}
do

    # Prepare for Level 1

    ${HCPPIPEDIR}/PrepareTaskfMRI/scripts/generate_level1_fsf.sh \
        --studyfolder=${StudyFolder} \
        --subject=${Subject} \
        --taskname=tfMRI_${TaskName}_${direction} \
        --templatedir=${HCPPIPEDIR}/PrepareTaskfMRI/fsf_templates \
        --outdir=${StudyFolder}/${Subject}/MNINonLinear/Results/tfMRI_${TaskName}_${direction}

done

# Prepare for Level 2

mkdir -p ${StudyFolder}/${Subject}/MNINonLinear/Results/tfMRI_${TaskName}
cp -v ${HCPPIPEDIR}/PrepareTaskfMRI/fsf_templates/tfMRI_${TaskName}_hp200_s4_level2.fsf ${StudyFolder}/${Subject}/MNINonLinear/Results/tfMRI_${TaskName}

exit 0