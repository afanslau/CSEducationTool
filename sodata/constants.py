# w_watson_rank = 400
# w_text_similarity = 400

# w_total_relations = 55
# w_child_role = 90
# w_user_total_relations = 70

# w_total_starred = 85
# w_user_starred = 200

# w_total_relations = 0
# w_path_confidence = 0.3
# w_watson_rank = 0.1
# w_text_similarity = 0.5
# w_total_views     = 0.1
# w_child_role      = 0.3


# weights = {
# 	'w_watson_rank'     : 10
# 	'w_text_similarity' : 70
# 	'w_total_views'     : 10
# 	'w_child_role'      : 30
# 	'w_user_created'    : 30
# }

# def normalize_weights(weights):
# 	total = sum(weights)
# 	if total==0:
# 		return weights
# 	return [w/total for w in weights]




# w_all = w_total_views + w_text_similarity + w_path_confidence + w_total_relations
# print 'recommender - weights: ', w_all
# print 'recommender - weights: ', round(w_all, 5)==1
# assert , "Recommendation feature weights must sum to 1"



USER_WEIGHT = 0.8
NUM_MOST_VIEWED_CANDIDATES = 100
SEARCH_PATH_LENGTH = 2

N_IMPORTANT_TERMS = 10
TITLE_WEIGHT = 5

N_RECOMMENDATIONS_PER_TERM = 20
N_RECOMMENDATIONS = N_IMPORTANT_TERMS * N_RECOMMENDATIONS_PER_TERM



