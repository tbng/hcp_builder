#!/bin/bash

StudyFolder="$HOME/data/HCP_test"
Subject="100307"
TaskName="EMOTION"

LevelOneTasks="tfMRI_${TaskName}_RL@tfMRI_${TaskName}_LR"
LevelOneFSFs="tfMRI_${TaskName}_RL@tfMRI_${TaskName}_LR"
LevelTwoTask="tfMRI_${TaskName}"
LevelTwoFSF="tfMRI_${TaskName}"

FinalSmoothingFWHM="4" #Space delimited list for setting different final smoothings.  2mm is no more smoothing (above minimal preprocessing pipelines grayordinates smoothing).  Smoothing is added onto minimal preprocessing smoothing to reach desired amount
GrayOrdinatesResolution="2" #2mm if using HCP minimal preprocessing pipeline outputs
OriginalSmoothingFWHM="2" #2mm if using HCP minimal preprocessing pipeline outputes
Confound="NONE" #File located in ${SubjectID}/MNINonLinear/Results/${fMRIName} or NONE
TemporalFilter="200" #Use 2000 for linear detrend, 200 is default for HCP task fMRI
RegName="NONE" # Use NONE to use the default surface registration

bash ${HCPPIPEDIR}/TaskfMRIAnalysis/TaskfMRIAnalysis.v2.0.sh \
    --path=$StudyFolder \
    --subject=$Subject \
    --lvl1tasks=$LevelOneTasks \
    --lvl1fsfs=$LevelOneFSFs \
    --lvl2task=$LevelTwoTask \
    --lvl2fsf=$LevelTwoFSF \
    --grayordinatesres=$GrayOrdinatesResolution \
    --origsmoothingFWHM=$OriginalSmoothingFWHM \
    --confound=$Confound \
    --finalsmoothingFWHM=$FinalSmoothingFWHM \
    --temporalfilter=$TemporalFilter \
    --regname=$RegName