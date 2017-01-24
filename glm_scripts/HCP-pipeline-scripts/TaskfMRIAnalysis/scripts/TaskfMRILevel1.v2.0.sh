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

LevelOnefMRIName="$3"
log_Msg "LevelOnefMRIName: ${LevelOnefMRIName}"

LevelOnefsfName="$4"
log_Msg "LevelOnefsfName: ${LevelOnefsfName}"

OriginalSmoothingFWHM="$5"
log_Msg "OriginalSmoothingFWHM: ${OriginalSmoothingFWHM}"

Confound="$6"
log_Msg "Confound: ${Confound}"

FinalSmoothingFWHM="$7"
log_Msg "FinalSmoothingFWHM: ${FinalSmoothingFWHM}"

TemporalFilter="$8"
log_Msg "TemporalFilter: ${TemporalFilter}"

RegName="$9"
log_Msg "RegName: ${RegName}"

show_tool_versions

if [ ! ${RegName} = "NONE" ] ; then
  RegString="_${RegName}"
else
  RegString=""
fi
log_Msg "RegString: ${RegString}"

TR_vol=`fslinfo ${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefMRIName}.nii.gz | grep pixdim4 | awk '{print $2}'`
log_Msg "TR_vol: ${TR_vol}"

#Only do the additional smoothing required to hit the target final smoothing for CIFTI.  Additional smoothing is not recommended, if looking for area-sized effects use parcellation for greater sensitivity and satistical power
AdditionalSmoothingFWHM=`echo "sqrt(( $FinalSmoothingFWHM ^ 2 ) - ( $OriginalSmoothingFWHM ^ 2 ))" | bc -l`
log_Msg "AdditionalSmoothingFWHM: ${AdditionalSmoothingFWHM}"

SmoothingString="_s${FinalSmoothingFWHM}"
TemporalFilterString="_hp""$TemporalFilter"
log_Msg "SmoothingString: ${SmoothingString}"
log_Msg "TemporalFilterString: ${TemporalFilterString}"

FEATDir="${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefsfName}${TemporalFilterString}${SmoothingString}_level1${RegString}.feat"
log_Msg "FEATDir: ${FEATDir}"
if [ -e ${FEATDir} ] ; then
  rm -r ${FEATDir}
  mkdir ${FEATDir}
else
  mkdir -p ${FEATDir}
fi

if [ $TemporalFilter = "200" ] ; then
  #Don't edit the fsf file if the temporal filter is the same
  log_Msg "Don't edit the fsf file if the temporal filter is the same"
  cp ${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefsfName}_hp200_s4_level1.fsf ${FEATDir}/temp.fsf
else
  #Change the highpass filter string to the desired highpass filter
  log_Msg "Change the highpass filter string to the desired highpass filter"
  cat ${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefsfName}_hp200_s4_level1.fsf | sed s/"set fmri(paradigm_hp) \"200\""/"set fmri(paradigm_hp) \"${TemporalFilter}\""/g > ${FEATDir}/temp.fsf
fi

#Change smoothing to be equal to additional smoothing in FSF file and change output directory to match total smoothing and highpass
log_Msg "Change smoothing to be equal to additional smoothing in FSF file and change output directory to match total smoothing and highpass"
cat ${FEATDir}/temp.fsf | sed s/"set fmri(smooth) \"4\""/"set fmri(smooth) \"${AdditionalSmoothingFWHM}\""/g | sed s/_hp200_s4/${TemporalFilterString}${SmoothingString}${RegString}/g > ${FEATDir}/design.fsf
rm ${FEATDir}/temp.fsf

#Change number of timepoints to match timeseries so that template fsf files can be used
log_Msg "Change number of timepoints to match timeseries so that template fsf files can be used"
fsfnpts=`cat ${FEATDir}/design.fsf | grep "set fmri(npts)" | cut -d " " -f 3 | sed 's/"//g'`
log_Msg "fsfnpts: ${fsfnpts}"
CIFTInpts=`fslinfo ${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefMRIName}.nii.gz | grep '^dim4' | awk '{print $2}'`
log_Msg "CIFTInpts: ${CIFTInpts}"
if [ "$fsfnpts" != "$CIFTInpts" ] ; then
  cat ${FEATDir}/design.fsf | sed s/"set fmri(npts) \"\?${fsfnpts}\"\?"/"set fmri(npts) ${CIFTInpts}"/g > ${FEATDir}/temp.fsf
  mv ${FEATDir}/temp.fsf ${FEATDir}/design.fsf
  log_Msg "Short Run! Reseting FSF Number of Timepoints (""${fsfnpts}"") to Match CIFTI (""${CIFTInpts}"")"
fi

#Create design files, model confounds if desired
log_Msg "Create design files, model confounds if desired"
DIR=`pwd`
cd ${FEATDir}
if [ $Confound = "NONE" ] ; then
  feat_model ${FEATDir}/design
else
  feat_model ${FEATDir}/design ${ResultsFolder}/${LevelOnefMRIName}/${Confound}
fi
cd $DIR

#Prepare files and folders
log_Msg "Prepare files and folders"
DesignMatrix=${FEATDir}/design.mat
DesignContrasts=${FEATDir}/design.con
DesignfContrasts=${FEATDir}/design.fts

###Standard NIFTI Volume-based Processsing###
log_Msg "Standard NIFTI Volume-based Processsing"
#Add edge-constrained volume smoothing
log_Msg "Add edge-constrained volume smoothing"
FinalSmoothingSigma=`echo "$FinalSmoothingFWHM / ( 2 * ( sqrt ( 2 * l ( 2 ) ) ) )" | bc -l`
InputfMRI=${ResultsFolder}/${LevelOnefMRIName}/${LevelOnefMRIName}
InputSBRef=${InputfMRI}_SBRef
OrigMask="mask_orig"
fslmaths ${InputSBRef} -bin ${FEATDir}/${OrigMask}
fslmaths ${FEATDir}/${OrigMask} -kernel gauss ${FinalSmoothingSigma} -fmean ${FEATDir}/mask_weight -odt float
fslmaths ${InputfMRI} -kernel gauss ${FinalSmoothingSigma} -fmean \
-div ${FEATDir}/mask_weight -mas ${FEATDir}/${OrigMask} \
${FEATDir}/${LevelOnefMRIName}"$SmoothingString" -odt float

#Add volume dilation
#
# For some subjects, FreeSurfer-derived brain masks (applied to the time
# series data in IntensityNormalization.sh as part of
# GenericfMRIVolumeProcessingPipeline.sh) do not extend to the edge of brain
# in the MNI152 space template. This is due to the limitations of volume-based
# registration. So, to avoid a lack of coverage in a group analysis around the
# penumbra of cortex, we will add a single dilation step to the input prior to
# creating the Level1 maps.
#
# Ideally, we would condition this dilation on the resolution of the fMRI
# data.  Empirically, a single round of dilation gives very good group
# coverage of MNI brain for the 2 mm resolution of HCP fMRI data. So a single
# dilation is what we use below.
#
# Note that for many subjects, this dilation will result in signal extending
# BEYOND the limits of brain in the MNI152 template.  However, that is easily
# fixed by masking with the MNI space brain template mask if so desired.
#
# The specific implementation involves:
# a) Edge-constrained spatial smoothing on the input fMRI time series (and masking
#    that back to the original mask).  This step was completed above.
# b) Spatial dilation of the input fMRI time series, followed by edge constrained smoothing
# c) Adding the voxels from (b) that are NOT part of (a) into (a).
#
# The motivation for this implementation is that:
# 1) Identical voxel-wise results are obtained within the original mask.  So, users
#    that desire the original ("tight") FreeSurfer-defined brain mask (which is
#    implicitly represented as the non-zero voxels in the InputSBRef volume) can
#    mask back to that if they chose, with NO impact on the voxel-wise results.
# 2) A simpler possible approach of just dilating the result of step (a) results in
#    an unnatural pattern of dark/light/dark intensities at the edge of brain,
#    whereas the combination of steps (b) and (c) yields a more natural looking
#    transition of intensities in the added voxels.
log_Msg "Add volume dilation"

DilationString="_dilM"

# Dilate the original BOLD time series, then do (edge-constrained) smoothing
fslmaths ${FEATDir}/${OrigMask} -dilM -bin ${FEATDir}/mask${DilationString}
fslmaths ${FEATDir}/mask${DilationString} \
-kernel gauss ${FinalSmoothingSigma} -fmean ${FEATDir}/mask${DilationString}_weight -odt float
fslmaths ${InputfMRI} -dilM -kernel gauss ${FinalSmoothingSigma} -fmean \
-div ${FEATDir}/mask${DilationString}_weight -mas ${FEATDir}/mask${DilationString} \
${FEATDir}/${LevelOnefMRIName}${DilationString}"$SmoothingString".nii.gz -odt float

# Take just the additional "rim" voxels from the dilated then smoothed time series, and add them
# into the smoothed time series (that didn't have any dilation)
DilationString2="${DilationString}rim"
SmoothedDilatedResultFile=${FEATDir}/${LevelOnefMRIName}"$SmoothingString"${DilationString2}
fslmaths ${FEATDir}/${OrigMask} -binv ${FEATDir}/${OrigMask}_inv
fslmaths ${FEATDir}/${LevelOnefMRIName}${DilationString}"$SmoothingString" \
-mas ${FEATDir}/${OrigMask}_inv \
-add ${FEATDir}/${LevelOnefMRIName}"$SmoothingString" \
${SmoothedDilatedResultFile}

#Add temporal filtering to the output from above
# (Here, we drop the "DilationString" from the output file name, so as to avoid breaking
# any downstream scripts).
log_Msg "Add temporal filtering"
fslmaths ${SmoothedDilatedResultFile} -bptf `echo "0.5 * $TemporalFilter / $TR_vol" | bc -l` -1 \
${FEATDir}/${LevelOnefMRIName}"$TemporalFilterString""$SmoothingString".nii.gz

#Run film_gls on subcortical volume data
log_Msg "Run film_gls on subcortical volume data"
film_gls --rn=${FEATDir}/StandardVolumeStats --sa --ms=5 --in=${FEATDir}/${LevelOnefMRIName}"$TemporalFilterString""$SmoothingString".nii.gz \
--pd="$DesignMatrix" --con=${DesignContrasts} --fcon=${DesignfContrasts} --thr=-100000000000

exit 0