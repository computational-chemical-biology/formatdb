import json
import sys
from api.NPClassifier.Classifier import fingerprint_handler
from api.NPClassifier.Classifier import prediction_voting
import tensorflow as tf
import numpy as np
from multiprocessing import Pool
from joblib import Parallel, delayed
from tqdm import tqdm

ontology_dictionary = json.loads(open("api/NPClassifier/Classifier/dict/index_v1.json").read())

sup_model = tf.keras.models.load_model('api/NPClassifier/Classifier/models_folder/models/SUPERCLASS/000001/')
class_model = tf.keras.models.load_model('api/NPClassifier/Classifier/models_folder/models/CLASS/000001/')
path_model = tf.keras.models.load_model('api/NPClassifier/Classifier/models_folder/models/PATHWAY/000001/')

def predict_class(smiles_list):
    fps = [fingerprint_handler.calculate_fingerprint(x, 2) for x in smi]
    fp1 = [fp[0][0] for fp in fps]
    fp2 = [fp[1][0] for fp in fps]
    inp = [np.array(fp1), np.array(fp2)]
    init = tf.global_variables_initializer()
    sess = tf.Session()
    sess.run(init)
    a = pred.eval(session=sess)
    pred_super = sup_model.predict(inp)
    pred_class = class_model.predict(inp)
    pred_path = path_model.predict(inp)

def handle_supeclass(pred_super):
    n_super = list(np.where(pred_super>=0.3)[0])
    path_from_superclass = []
    for j in n_super:
        path_from_superclass += ontology_dictionary['Super_hierarchy'][str(j)]['Pathway']
    path_from_superclass = list(set(path_from_superclass))
    return path_from_superclass

def handle_class(pred_class):
    n_class = list(np.where(pred_class>=0.1)[0])
    path_from_class = []
    for j in n_class:
        path_from_class += ontology_dictionary['Class_hierarchy'][str(j)]['Pathway']
    path_from_class = list(set(path_from_class))
    return path_from_class


def handle_path(pred_path):
    n_path = list(np.where(pred_path>=0.5)[0])
    return n_path

def classify_structure(smiles):
    isglycoside = fingerprint_handler._isglycoside(smiles)
    fp = fingerprint_handler.calculate_fingerprint(smiles, 2)
    fp1 = fp[0].tolist()[0]
    fp2 = fp[1].tolist()[0]
    inp = [np.array(fp1).reshape(1,-1), np.array(fp2).reshape(1,-1)]
    # Handling SUPERCLASS
    pred_super = sup_model.predict(inp).squeeze()
    n_super = list(np.where(pred_super>=0.3)[0])
    path_from_superclass = []
    for j in n_super:
        path_from_superclass += ontology_dictionary['Super_hierarchy'][str(j)]['Pathway']
    path_from_superclass = list(set(path_from_superclass))
    # Handling CLASS
    pred_class = class_model.predict(inp).squeeze()
    n_class = list(np.where(pred_class>=0.1)[0])
    path_from_class = []
    for j in n_class:
        path_from_class += ontology_dictionary['Class_hierarchy'][str(j)]['Pathway']
    path_from_class = list(set(path_from_class))
    # Handling PATHWAY
    pred_path = path_model.predict(inp).squeeze()
    n_path = list(np.where(pred_path>=0.5)[0])
    class_result = []
    superclass_result = []
    pathway_result = []
    # Voting on Answer
    pathway_result, superclass_result, class_result, isglycoside = prediction_voting.vote_classification(n_path,
                                                                                                        n_class,
                                                                                                        n_super,
                                                                                                        pred_class,
                                                                                                        pred_super,
                                                                                                        path_from_class,
                                                                                                        path_from_superclass,
                                                                                                        isglycoside,
                                                                                                        ontology_dictionary)
    return isglycoside, class_result, superclass_result, pathway_result, path_from_class, path_from_superclass, n_path, fp1, fp2

def update_dict(d):
    if not len(d):
        return {}
    isglycoside, class_results, superclass_results, pathway_results, path_from_class, path_from_superclass, n_path, fp1, fp2 = classify_structure(d['PUBCHEM_OPENEYE_CAN_SMILES'])
    d["class_results"] = class_results
    d["superclass_results"] = superclass_results
    d["pathway_results"] = pathway_results
    d["isglycoside"] = isglycoside
    #d["fp1"] = fp1
    #d["fp2"] = fp2
    return d

if __name__=='__main__':
    fname = sys.argv[1]
    with open(fname) as f:
        dlist = json.load(f)

    #with Pool() as p:
    #    res_dlist = p.map(update_dict, dlist[:10])

    #inputs = tqdm(dlist[:10])
    #res_dlist = Parallel(n_jobs=5, prefer="threads")(delayed(update_dict)(i) for i in inputs)
    res_dlist = [update_dict(i) for i in dlist]

    with open(sys.argv[2], 'w') as f:
        json.dump(res_dlist, f)
