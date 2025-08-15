import networkx as nx

from battle_logic.character_settings.minion_stats import orc_stats
from map_logic.encounter_icon import CircularImageSprite




class CampaignMapConfig:
    def __init__(self, edges):
        self.edges = edges
        self.d_neighbors = {}
        self.d_node_to_id = {}

        node_id = 0
        for edge in edges:
            for node in edge:
                if node not in self.d_neighbors:
                    self.d_neighbors[node] = []
                    self.d_node_to_id[node] = node_id
                    node_id += 1
            self.d_neighbors[edge[0]].append(edge[1])
            self.d_neighbors[edge[1]].append(edge[0])

        self.d_id_to_node = {self.d_node_to_id[node]: node for node in self.d_node_to_id}

        self.G = nx.Graph()
        for edge in edges:
            self.G.add_edge(self.d_node_to_id[edge[0]], self.d_node_to_id[edge[1]])

    def get_shortest_path(self, source, target):
        path_in_ids = nx.shortest_path(self.G, source=self.d_node_to_id[source], target=self.d_node_to_id[target])[1:]
        path_in_nodes = [self.d_id_to_node[id] for id in path_in_ids]
        return path_in_nodes


# Define Nodes
home_node = CircularImageSprite(
    "elf_settlement.png",
    (0.9, 0.3)
)
wolf_node = CircularImageSprite("goodboy.png", (0.5, 0.5), [(orc_stats, 5)])
wolf_node_2 = CircularImageSprite("goodboy.png", (0.6, 0.7), [(orc_stats, 15)])
wolf_node_3 = CircularImageSprite("goodboy.png", (0.6, 0.9), [(orc_stats, 29)])

# Define edges
edges = [
    (home_node, wolf_node),
    (wolf_node, wolf_node_2),
    (wolf_node_2, wolf_node_3),
]

forest_campaign_config = CampaignMapConfig(edges)