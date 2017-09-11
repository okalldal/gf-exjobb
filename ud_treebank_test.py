import nltk
import numpy as np


def extract_features(graph, node, feature_vector):
    return [extract_feature(graph, node, feature) for feature in feature_vector]


def extract_feature(graph, node, feature):
    feature = feature.split('_')
    if feature[0] == 'head':
        if node['head'] == 0:
            return '#ROOT'
        else:
            head = graph.get_by_address(node['head'])
            return head[feature[1]]
    else:
        return node[feature[0]]


def parse_connlu_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        current = []
        for line in f:
            if line == "\n":
                connlu_string = ''.join(current)
                yield nltk.parse.DependencyGraph(
                    tree_str=connlu_string, top_relation_label='root')
                current = []
            elif not line.startswith('#'):
                current.append(line)


def compile_feature_lists(tag_keys, feature_keys, graphs, wanted_tags=None):
    feature_lists = dict()
    for dg in graphs:
        for node in dg.nodes:
            features = extract_features(dg, node, tag_keys+feature_keys)
            tag = '_'.join(features[:len(tag_keys)])
            features = dict(zip(feature_keys, features[len(tag_keys):]))
            if wanted_tags is None or tag in wanted_tags:
                if tag not in feature_lists.keys():
                    feature_lists[tag] = []
                feature_lists[tag].append(features)
    return feature_lists


class ParameterSet:
    def __init__(self, feature_vector_list, sense_list):

        self.sense_map = dict()  # [sense] -> id
        self.feature_type_map = dict()  # [feature_type] -> id
        self.feature_val_map = dict()  # [feature_type][feature_val] -> id

        current_id = 0
        for sense in sense_list:
            self.sense_map[sense] = current_id
            current_id = current_id + 1

        feature_types = feature_vector_list[0].keys()
        max_feature_vals = 0
        for feature_type in feature_types:
            self.feature_val_map[feature_type] = dict()
            current_id = 0
            for feature_vector in feature_vector_list:
                feature_val = feature_vector[feature_type]
                if feature_val not in self.feature_val_map[feature_type]:
                    self.feature_val_map[feature_type][feature_val] = current_id
                    current_id = current_id + 1
                pass
            max_feature_vals = max(max_feature_vals, current_id)

        self.params = np.zeros(
            [len(sense_list), len(feature_types), max_feature_vals])

    def get_parameter(self, sense, feature_type, feature):
        return self.params[
            self.sense_map[sense],
            self.feature_type_map[feature_type,
            self.feature_val_map[feature]]
        ]


def estimate_sense_probabilities(feature_vector, parameter_set):
    feature_parameters = np.stack([parameter_set.params[:, f_type, f_val]
                                   for f_type, f_val in feature_vector.items()], axis=1)
    likelihoods = np.prod(feature_parameters, axis=1)
    probabilities = likelihoods / sum(likelihoods)
    return probabilities


def update_parameter_set(feature_vector_list, sense_probabilities_list, parameter_set):
    new_parameters = np.zeros(np.shape(parameter_set.params))
    for feature_vector, sense_probabilities in zip(feature_vector_list, sense_probabilities_list):
        for feature_type, feature_val in feature_vector.items():
            feature_type_id = new_parameters.feature_type_map[feature_type]
            feature_val_id = new_parameters.feature_val_map[feature_val]
            new_parameters[:, feature_type_id, feature_val_id] =\
                new_parameters[:, feature_type_id, feature_val_id] + sense_probabilities
    parameter_set.params = new_parameters / np.sum(new_parameters, axis=2)

def randomize_parameter_set(parameter_set):
    for feature_type in parameter_set.feature_type_map.keys():
        feature_type_id = parameter_set.feature_type_map[feature_type]
        feature_val_length = len(parameter_set.feature_val_map[feature_type])
        sense_length = len(parameter_set.sense_map)
        random_probabilities = np.random.rand([sense_length, feature_val_length])
        random_probabilities = random_probabilities / sum(random_probabilities, axis=1)
        parameter_set.params[:, feature_type_id, :feature_val_length] = random_probabilities