#!/bin/bash
# Modified by Arthur Mensch to recompute StandardCoordinates statistics

set -e
g_script_name=`basename ${0}`

source ${HCPPIPEDIR}/global/scripts/log.shlib # Logging related functions
log_SetToolName "${g_script_name}"

source ${HCPPIPEDIR}/global/scripts/fsl_version.shlib # Function for getting FSL version

show_tool_versions()
{
	# Show HCP pipelines version
	log_Msg "Showing HCP Pipelines version"
	cat ${HCPPIPEDIR}/version.txt

	# Show fsl version
	log_Msg "Showing FSL version"
	fsl_version_get fsl_ver
	log_Msg "FSL version: ${fsl_ver}"
}

Subject="$1"
log_Msg "Subject: ${Subject}"

ResultsFolder="$2"
log_Msg "ResultsFolder: ${ResultsFolder}"

LevelOnefMRINames="$3"
log_Msg "LevelOnefMRINames: ${LevelOnefMRINames}"

LevelOnefsfNames="$4"
log_Msg "LevelOnefsfNames: ${LevelOnefsfNames}"

LevelTwofMRIName="$5"
log_Msg "LevelTwofMRIName: ${LevelTwofMRIName}"

LevelTwofsfName="$6"
log_Msg "LevelTwofsfName: ${LevelTwofsfName}"

FinalSmoothingFWHM="$7"
log_Msg "FinalSmoothingFWHM: ${FinalSmoothingFWHM}"

TemporalFilter="$8"
log_Msg "TemporalFilter: ${TemporalFilter}"

RegName="$9"
log_Msg "RegName: ${RegName}"

show_tool_versions

#Set up some things
LevelOnefMRINames=`echo $LevelOnefMRINames | sed 's/@/ /g'`
LevelOnefsfNames=`echo $LevelOnefsfNames | sed 's/@/ /g'`

if [ ! ${RegName} = "NONE" ] ; then
  RegString="_${RegName}"
else
  RegString=""
fi

log_Msg "RegString: ${RegString}"

SmoothingString="_s${FinalSmoothingFWHM}"
log_Msg "SmoothingString: ${SmoothingString}"

TemporalFilterString="_hp""$TemporalFilter"
log_Msg "TemporalFilterString: ${TemporalFilterString}"

LevelOneFEATDirSTRING=""
i=1
for LevelOnefMRIName in $LevelOnefMRINames ; do
  LevelOnefsfName=`echo $LevelOnefsfNames | cut -d " " -f $i`
  LevelOneFEATDirSTRING="${LevelOneFEATDirSTRING}${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefsfName}${TemporalFilterString}${SmoothingString}_level1${RegString}.feat "
  i=$(($i+1))
done
NumFirstLevelFolders=$(($i-1))

FirstFolder=`echo $LevelOneFEATDirSTRING | cut -d " " -f 1`
ContrastNames=`cat ${FirstFolder}/design.con | grep "ContrastName" | cut -f 2`
NumContrasts=`echo ${ContrastNames} | wc -w`
LevelTwoFEATDir="${ResultsFolder}/${LevelTwofMRIName}/${LevelTwofsfName}${TemporalFilterString}${SmoothingString}_level2${RegString}.feat"
if [ -e ${LevelTwoFEATDir} ] ; then
  rm -r ${LevelTwoFEATDir}
  mkdir ${LevelTwoFEATDir}
else
  mkdir -p ${LevelTwoFEATDir}
fi

cat ${ResultsFolder}/${LevelTwofMRIName}/${LevelTwofsfName}_hp200_s4_level2.fsf | sed s/_hp200_s4/${TemporalFilterString}${SmoothingString}${RegString}/g > ${LevelTwoFEATDir}/design.fsf

#Make design files
log_Msg "Make design files"
DIR=`pwd`
cd ${LevelTwoFEATDir}
feat_model ${LevelTwoFEATDir}/design
cd $DIR

#Loop over Grayordinates and Standard Volume (if requested) Level 2 Analyses
Analysis="StandardVolumeStats"
log_Msg "Analysis: ${Analysis}"
mkdir -p ${LevelTwoFEATDir}/${Analysis}
#Copy over level one folders and convert CIFTI to NIFTI if required
log_Msg "Copy over level one folders and convert CIFTI to NIFTI if required"
log_Msg "${FirstFolder}/${Analysis}/cope1.nii.gz"
if [ -e ${FirstFolder}/${Analysis}/cope1.nii.gz ] ; then
  Grayordinates="NO"
  i=1
  for LevelOneFEATDir in ${LevelOneFEATDirSTRING} ; do
    mkdir -p ${LevelTwoFEATDir}/${Analysis}/${i}
    cp ${LevelOneFEATDir}/${Analysis}/* ${LevelTwoFEATDir}/${Analysis}/${i}
    i=$(($i+1))
  done
else
  echo "Level One Folder Not Found"
fi
#Create dof and Mask
log_Msg "Create dof and Mask"
MERGESTRING=""
i=1
while [ $i -le ${NumFirstLevelFolders} ] ; do
  dof=`cat ${LevelTwoFEATDir}/${Analysis}/${i}/dof`
  fslmaths ${LevelTwoFEATDir}/${Analysis}/${i}/res4d.nii.gz -Tstd -bin -mul $dof ${LevelTwoFEATDir}/${Analysis}/${i}/dofmask.nii.gz
  MERGESTRING=`echo "${MERGESTRING}${LevelTwoFEATDir}/${Analysis}/${i}/dofmask.nii.gz "`
  i=$(($i+1))
done
fslmerge -t ${LevelTwoFEATDir}/${Analysis}/dof.nii.gz $MERGESTRING
fslmaths ${LevelTwoFEATDir}/${Analysis}/dof.nii.gz -Tmin -bin ${LevelTwoFEATDir}/${Analysis}/mask.nii.gz
#Merge COPES and VARCOPES and run 2nd level analysis
log_Msg "Merge COPES and VARCOPES and run 2nd level analysis"
log_Msg "NumContrasts: ${NumContrasts}"
i=1
while [ $i -le ${NumContrasts} ] ; do
  log_Msg "i: ${i}"
  COPEMERGE=""
  VARCOPEMERGE=""
  j=1
  while [ $j -le ${NumFirstLevelFolders} ] ; do
    COPEMERGE="${COPEMERGE}${LevelTwoFEATDir}/${Analysis}/${j}/cope${i}.nii.gz "
    VARCOPEMERGE="${VARCOPEMERGE}${LevelTwoFEATDir}/${Analysis}/${j}/varcope${i}.nii.gz "
    j=$(($j+1))
  done
  fslmerge -t ${LevelTwoFEATDir}/${Analysis}/cope${i}.nii.gz $COPEMERGE
  fslmerge -t ${LevelTwoFEATDir}/${Analysis}/varcope${i}.nii.gz $VARCOPEMERGE
  flameo --cope=${LevelTwoFEATDir}/${Analysis}/cope${i}.nii.gz --vc=${LevelTwoFEATDir}/${Analysis}/varcope${i}.nii.gz --dvc=${LevelTwoFEATDir}/${Analysis}/dof.nii.gz --mask=${LevelTwoFEATDir}/${Analysis}/mask.nii.gz --ld=${LevelTwoFEATDir}/${Analysis}/cope${i}.feat --dm=${LevelTwoFEATDir}/design.mat --cs=${LevelTwoFEATDir}/design.grp --tc=${LevelTwoFEATDir}/design.con --runmode=fe
  i=$(($i+1))
done
#Cleanup Temporary Files
log_Msg "Cleanup Temporary Files"
j=1
while [ $j -le ${NumFirstLevelFolders} ] ; do
  rm -r ${LevelTwoFEATDir}/${Analysis}/${j}
  j=$(($j+1))
done
