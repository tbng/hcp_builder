from os.path import join

from hcp_builder.system import get_data_dirs

tasks = [["WM", 1, "2BK_BODY"],
         ["WM", 2, "2BK_FACE"],
         ["WM", 3, "2BK_PLACE"],
         ["WM", 4, "2BK_TOOL"],
         ["WM", 5, "0BK_BODY"],
         ["WM", 6, "0BK_FACE"],
         ["WM", 7, "0BK_PLACE"],
         ["WM", 8, "0BK_TOOL"],
         ["WM", 9, "2BK"],
         ["WM", 10, "0BK"],
         ["WM", 11, "2BK-0BK"],
         ["WM", 12, "neg_2BK"],
         ["WM", 13, "neg_0BK"],
         ["WM", 14, "0BK-2BK"],
         ["WM", 15, "BODY"],
         ["WM", 16, "FACE"],
         ["WM", 17, "PLACE"],
         ["WM", 18, "TOOL"],
         ["WM", 19, "BODY-AVG"],
         ["WM", 20, "FACE-AVG"],
         ["WM", 21, "PLACE-AVG"],
         ["WM", 22, "TOOL-AVG"],
         ["WM", 23, "neg_BODY"],
         ["WM", 24, "neg_FACE"],
         ["WM", 25, "neg_PLACE"],
         ["WM", 26, "neg_TOOL"],
         ["WM", 27, "AVG-BODY"],
         ["WM", 28, "AVG-FACE"],
         ["WM", 29, "AVG-PLACE"],
         ["WM", 30, "AVG-TOOL"],
         ["GAMBLING", 1, "PUNISH"],
         ["GAMBLING", 2, "REWARD"],
         ["GAMBLING", 3, "PUNISH-REWARD"],
         ["GAMBLING", 4, "neg_PUNISH"],
         ["GAMBLING", 5, "neg_REWARD"],
         ["GAMBLING", 6, "REWARD-PUNISH"],
         ["MOTOR", 1, "CUE"],
         ["MOTOR", 2, "LF"],
         ["MOTOR", 3, "LH"],
         ["MOTOR", 4, "RF"],
         ["MOTOR", 5, "RH"],
         ["MOTOR", 6, "T"],
         ["MOTOR", 7, "AVG"],
         ["MOTOR", 8, "CUE-AVG"],
         ["MOTOR", 9, "LF-AVG"],
         ["MOTOR", 10, "LH-AVG"],
         ["MOTOR", 11, "RF-AVG"],
         ["MOTOR", 12, "RH-AVG"],
         ["MOTOR", 13, "T-AVG"],
         ["MOTOR", 14, "neg_CUE"],
         ["MOTOR", 15, "neg_LF"],
         ["MOTOR", 16, "neg_LH"],
         ["MOTOR", 17, "neg_RF"],
         ["MOTOR", 18, "neg_RH"],
         ["MOTOR", 19, "neg_T"],
         ["MOTOR", 20, "neg_AVG"],
         ["MOTOR", 21, "AVG-CUE"],
         ["MOTOR", 22, "AVG-LF"],
         ["MOTOR", 23, "AVG-LH"],
         ["MOTOR", 24, "AVG-RF"],
         ["MOTOR", 25, "AVG-RH"],
         ["MOTOR", 26, "AVG-T"],
         ["LANGUAGE", 1, "MATH"],
         ["LANGUAGE", 2, "STORY"],
         ["LANGUAGE", 3, "MATH-STORY"],
         ["LANGUAGE", 4, "STORY-MATH"],
         ["LANGUAGE", 5, "neg_MATH"],
         ["LANGUAGE", 6, "neg_STORY"],
         ["SOCIAL", 1, "RANDOM"],
         ["SOCIAL", 2, "TOM"],
         ["SOCIAL", 3, "RANDOM-TOM"],
         ["SOCIAL", 4, "neg_RANDOM"],
         ["SOCIAL", 5, "neg_TOM"],
         ["SOCIAL", 6, "TOM-RANDOM"],
         ["RELATIONAL", 1, "MATCH"],
         ["RELATIONAL", 2, "REL"],
         ["RELATIONAL", 3, "MATCH-REL"],
         ["RELATIONAL", 4, "REL-MATCH"],
         ["RELATIONAL", 5, "neg_MATCH"],
         ["RELATIONAL", 6, "neg_REL"],
         ["EMOTION", 1, "FACES"],
         ["EMOTION", 2, "SHAPES"],
         ["EMOTION", 3, "FACES-SHAPES"],
         ["EMOTION", 4, "neg_FACES"],
         ["EMOTION", 5, "neg_SHAPES"],
         ["EMOTION", 6, "SHAPES-FACES"]]

# Could be simplfied
evs = ['tfMRI_EMOTION_LR/EVs/EMOTION_Stats.csv',
       'tfMRI_EMOTION_LR/EVs/Sync.txt',
       'tfMRI_EMOTION_LR/EVs/fear.txt',
       'tfMRI_EMOTION_LR/EVs/neut.txt',
       'tfMRI_EMOTION_RL/EVs/EMOTION_Stats.csv',
       'tfMRI_EMOTION_RL/EVs/Sync.txt',
       'tfMRI_EMOTION_RL/EVs/fear.txt',
       'tfMRI_EMOTION_RL/EVs/neut.txt',
       'tfMRI_GAMBLING_LR/EVs/GAMBLING_Stats.csv',
       'tfMRI_GAMBLING_LR/EVs/Sync.txt',
       'tfMRI_GAMBLING_LR/EVs/loss.txt',
       'tfMRI_GAMBLING_LR/EVs/loss_event.txt',
       'tfMRI_GAMBLING_LR/EVs/neut_event.txt',
       'tfMRI_GAMBLING_LR/EVs/win.txt',
       'tfMRI_GAMBLING_LR/EVs/win_event.txt',
       'tfMRI_GAMBLING_RL/EVs/GAMBLING_Stats.csv',
       'tfMRI_GAMBLING_RL/EVs/Sync.txt',
       'tfMRI_GAMBLING_RL/EVs/loss.txt',
       'tfMRI_GAMBLING_RL/EVs/loss_event.txt',
       'tfMRI_GAMBLING_RL/EVs/neut_event.txt',
       'tfMRI_GAMBLING_RL/EVs/win.txt',
       'tfMRI_GAMBLING_RL/EVs/win_event.txt',
       'tfMRI_LANGUAGE_LR/EVs/LANGUAGE_Stats.csv',
       'tfMRI_LANGUAGE_LR/EVs/Sync.txt',
       'tfMRI_LANGUAGE_LR/EVs/cue.txt',
       'tfMRI_LANGUAGE_LR/EVs/math.txt',
       'tfMRI_LANGUAGE_LR/EVs/present_math.txt',
       'tfMRI_LANGUAGE_LR/EVs/present_story.txt',
       'tfMRI_LANGUAGE_LR/EVs/question_math.txt',
       'tfMRI_LANGUAGE_LR/EVs/question_story.txt',
       'tfMRI_LANGUAGE_LR/EVs/response_math.txt',
       'tfMRI_LANGUAGE_LR/EVs/response_story.txt',
       'tfMRI_LANGUAGE_LR/EVs/story.txt',
       'tfMRI_LANGUAGE_RL/EVs/LANGUAGE_Stats.csv',
       'tfMRI_LANGUAGE_RL/EVs/Sync.txt',
       'tfMRI_LANGUAGE_RL/EVs/cue.txt',
       'tfMRI_LANGUAGE_RL/EVs/math.txt',
       'tfMRI_LANGUAGE_RL/EVs/present_math.txt',
       'tfMRI_LANGUAGE_RL/EVs/present_story.txt',
       'tfMRI_LANGUAGE_RL/EVs/question_math.txt',
       'tfMRI_LANGUAGE_RL/EVs/question_story.txt',
       'tfMRI_LANGUAGE_RL/EVs/response_math.txt',
       'tfMRI_LANGUAGE_RL/EVs/response_story.txt',
       'tfMRI_LANGUAGE_RL/EVs/story.txt',
       'tfMRI_MOTOR_LR/EVs/Sync.txt',
       'tfMRI_MOTOR_LR/EVs/cue.txt',
       'tfMRI_MOTOR_LR/EVs/lf.txt',
       'tfMRI_MOTOR_LR/EVs/lh.txt',
       'tfMRI_MOTOR_LR/EVs/rf.txt',
       'tfMRI_MOTOR_LR/EVs/rh.txt',
       'tfMRI_MOTOR_LR/EVs/t.txt',
       'tfMRI_MOTOR_RL/EVs/Sync.txt',
       'tfMRI_MOTOR_RL/EVs/cue.txt',
       'tfMRI_MOTOR_RL/EVs/lf.txt',
       'tfMRI_MOTOR_RL/EVs/lh.txt',
       'tfMRI_MOTOR_RL/EVs/rf.txt',
       'tfMRI_MOTOR_RL/EVs/rh.txt',
       'tfMRI_MOTOR_RL/EVs/t.txt',
       'tfMRI_RELATIONAL_LR/EVs/RELATIONAL_Stats.csv',
       'tfMRI_RELATIONAL_LR/EVs/Sync.txt',
       'tfMRI_RELATIONAL_LR/EVs/error.txt',
       'tfMRI_RELATIONAL_LR/EVs/match.txt',
       'tfMRI_RELATIONAL_LR/EVs/relation.txt',
       'tfMRI_RELATIONAL_RL/EVs/RELATIONAL_Stats.csv',
       'tfMRI_RELATIONAL_RL/EVs/Sync.txt',
       'tfMRI_RELATIONAL_RL/EVs/error.txt',
       'tfMRI_RELATIONAL_RL/EVs/match.txt',
       'tfMRI_RELATIONAL_RL/EVs/relation.txt',
       'tfMRI_SOCIAL_LR/EVs/SOCIAL_Stats.csv',
       'tfMRI_SOCIAL_LR/EVs/Sync.txt',
       'tfMRI_SOCIAL_LR/EVs/mental.txt',
       'tfMRI_SOCIAL_LR/EVs/mental_resp.txt',
       'tfMRI_SOCIAL_LR/EVs/other_resp.txt',
       'tfMRI_SOCIAL_LR/EVs/rnd.txt',
       'tfMRI_SOCIAL_RL/EVs/SOCIAL_Stats.csv',
       'tfMRI_SOCIAL_RL/EVs/Sync.txt',
       'tfMRI_SOCIAL_RL/EVs/mental.txt',
       'tfMRI_SOCIAL_RL/EVs/mental_resp.txt',
       'tfMRI_SOCIAL_RL/EVs/other_resp.txt',
       'tfMRI_SOCIAL_RL/EVs/rnd.txt',
       'tfMRI_WM_LR/EVs/0bk_body.txt',
       'tfMRI_WM_LR/EVs/0bk_cor.txt',
       'tfMRI_WM_LR/EVs/0bk_err.txt',
       'tfMRI_WM_LR/EVs/0bk_faces.txt',
       'tfMRI_WM_LR/EVs/0bk_nlr.txt',
       'tfMRI_WM_LR/EVs/0bk_places.txt',
       'tfMRI_WM_LR/EVs/0bk_tools.txt',
       'tfMRI_WM_LR/EVs/2bk_body.txt',
       'tfMRI_WM_LR/EVs/2bk_cor.txt',
       'tfMRI_WM_LR/EVs/2bk_err.txt',
       'tfMRI_WM_LR/EVs/2bk_faces.txt',
       'tfMRI_WM_LR/EVs/2bk_nlr.txt',
       'tfMRI_WM_LR/EVs/2bk_places.txt',
       'tfMRI_WM_LR/EVs/2bk_tools.txt',
       'tfMRI_WM_LR/EVs/Sync.txt',
       'tfMRI_WM_LR/EVs/WM_Stats.csv',
       'tfMRI_WM_LR/EVs/all_bk_cor.txt',
       'tfMRI_WM_LR/EVs/all_bk_err.txt',
       'tfMRI_WM_RL/EVs/0bk_body.txt',
       'tfMRI_WM_RL/EVs/0bk_cor.txt',
       'tfMRI_WM_RL/EVs/0bk_err.txt',
       'tfMRI_WM_RL/EVs/0bk_faces.txt',
       'tfMRI_WM_RL/EVs/0bk_nlr.txt',
       'tfMRI_WM_RL/EVs/0bk_places.txt',
       'tfMRI_WM_RL/EVs/0bk_tools.txt',
       'tfMRI_WM_RL/EVs/2bk_body.txt',
       'tfMRI_WM_RL/EVs/2bk_cor.txt',
       'tfMRI_WM_RL/EVs/2bk_err.txt',
       'tfMRI_WM_RL/EVs/2bk_faces.txt',
       'tfMRI_WM_RL/EVs/2bk_nlr.txt',
       'tfMRI_WM_RL/EVs/2bk_places.txt',
       'tfMRI_WM_RL/EVs/2bk_tools.txt',
       'tfMRI_WM_RL/EVs/Sync.txt',
       'tfMRI_WM_RL/EVs/WM_Stats.csv',
       'tfMRI_WM_RL/EVs/all_bk_cor.txt',
       'tfMRI_WM_RL/EVs/all_bk_err.txt']


def get_fmri_path(subject, data_type='all'):
    """Utility to download from s3"""
    subject = str(subject)
    out = []
    subject_dir = join('HCP_900', subject, 'MNINonLinear', 'Results')

    if data_type not in ['all', 'rest', 'task']:
        raise ValueError("Wrong data type. Expected ['rest', 'type'], got"
                         "%s" % data_type)

    if data_type in ['all', 'rest']:
        for run_index in [1, 2]:
            for run_direction in ['LR', 'RL']:
                filename = 'rfMRI_REST%i_%s' % (run_index, run_direction)
                rest_dir = join(subject_dir, filename)
                rest_func = join(rest_dir, filename + '.nii.gz')
                mask_func = join(rest_dir, filename + '_SBRef.nii.gz')
                rest_confounds = ['Movement_AbsoluteRMS_mean.txt',
                                  'Movement_AbsoluteRMS.txt',
                                  'Movement_Regressors_dt.txt',
                                  'Movement_Regressors.txt',
                                  'Movement_RelativeRMS_mean.txt',
                                  'Movement_RelativeRMS.txt']
                rest_confounds = [join(rest_dir, confound)
                                  for confound in rest_confounds]
                out.append(rest_func)
                out.append(mask_func)
                out += rest_confounds
    # Tasks
    if data_type in ['all', 'task']:
        for task in ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL', 'GAMBLING',
                     'SOCIAL', 'LANGUAGE']:
            for run_direction in ['LR', 'RL']:
                filename = 'tfMRI_%s_%s' % (task, run_direction)
                task_dir = join(subject_dir, filename)
                task_func = join(task_dir, filename + '.nii.gz')
                mask_func = join(task_dir, filename + '_SBRef.nii.gz')
                task_confounds = ['Movement_AbsoluteRMS_mean.txt',
                                  'Movement_AbsoluteRMS.txt',
                                  'Movement_Regressors_dt.txt',
                                  'Movement_Regressors.txt',
                                  'Movement_RelativeRMS_mean.txt',
                                  'Movement_RelativeRMS.txt']
                task_confounds = [join(task_dir, confound)
                                  for confound in task_confounds]
                out.append(task_func)
                out.append(mask_func)
                out += task_confounds
        # EVs
        subject_evs = [join(subject_dir, ev) for ev in evs]
        out += subject_evs
    return out


def get_subject_list(data_dir=None):
    import pandas as pd
    import numpy as np
    data_dir = get_data_dirs(data_dir)[0]
    df = pd.read_csv(join(data_dir, 'parietal_extra', 'hcp_unrestricted_data.csv'))

    indices = np.logical_and(df['3T_RS-fMRI_PctCompl'] == 100,
                             df['3T_tMRI_PctCompl'] == 100)
    return df.Subject[indices].tolist()