from sklearn_extra.cluster import KMedoids
import numpy as np

class Clustering:
	def __init__(self, data):
		self.states = data.keys()
		self.kmeans = KMedoids(n_clusters=3)
		self.kmeans.fit(np.array(tuple(data.values())).reshape(-1, 1))

		self.mapping = list(np.argsort(np.squeeze(self.kmeans.cluster_centers_)))

	def cluster(self):
		result = [ [], [], [] ]
		for state, cluster in zip(self.states, self.kmeans.labels_):
			result[self.mapping.index(cluster)].append(state)
		return result

class Confirmed(Clustering):
	pass

class Active(Clustering):
	pass

class Deceased(Clustering):
	pass

class Recovered(Clustering):
	pass