'''Code file for baseball elimination lab created for Advanced Algorithms
Spring 2020 at Olin College. The code for this lab has been adapted from:
https://github.com/ananya77041/baseball-elimination/blob/master/src/BaseballElimination.java'''

import sys
import math
import picos as pic
import networkx as nx
import itertools
import cvxopt
import matplotlib.pyplot as plt

class Division:
    '''
    The Division class represents a baseball division. This includes all the
    teams that are a part of that division, their winning and losing history,
    and their remaining games for the season.

    filename: name of a file with an input matrix that has info on teams &
    their games
    '''

    def __init__(self, filename):
        self.teams = {}
        self.G = nx.DiGraph()
        self.readDivision(filename)

    def readDivision(self, filename):
        '''Reads the information from the given file and builds up a dictionary
        of the teams that are a part of this division.

        filename: name of text file representing tournament outcomes so far
        & remaining games for each team
        '''
        f = open(filename, "r")
        lines = [line.split() for line in f.readlines()]
        f.close()

        lines = lines[1:]
        for ID, teaminfo in enumerate(lines):
            team = Team(int(ID), teaminfo[0], int(teaminfo[1]), int(teaminfo[2]), int(teaminfo[3]), list(map(int, teaminfo[4:])))
            self.teams[ID] = team

    def get_team_IDs(self):
        '''Gets the list of IDs that are associated with each of the teams
        in this division.

        return: list of IDs that are associated with each of the teams in the
        division
        '''
        return self.teams.keys()

    def is_eliminated(self, teamID, solver):
        '''Uses the given solver (either Linear Programming or Network Flows)
        to determine if the team with the given ID is mathematically
        eliminated from winning the division (aka winning more games than any
        other team) this season.

        teamID: ID of team that we want to check if it is eliminated
        solver: string representing whether to use the network flows or linear
        programming solver
        return: True if eliminated, False otherwise
        '''
        flag1 = False
        team = self.teams[teamID]

        temp = dict(self.teams)
        del temp[teamID]

        for _, other_team in temp.items():
            if team.wins + team.remaining < other_team.wins:
                print("Easy out", " ", team.name)
                flag1 = True

        saturated_edges = self.create_network(teamID)
        if not flag1:
            if solver == "Network Flows":
                flag1 = self.network_flows(saturated_edges)
            elif solver == "Linear Programming":
                flag1 = self.linear_programming(saturated_edges)
        #print(self.teams[teamID].name,flag1)
        return flag1

    def draw_graph(self, graph, layout):
        """Draws a nice representation of a networkx graph object.
        Source: https://notebooks.azure.com/coells/projects/100days/html/day%2049%20-%20ford-fulkerson.ipynb"""

        plt.figure(figsize=(12, 4))
        plt.axis('off')

        nx.draw_networkx_nodes(graph, layout, node_color='steelblue', node_size=600)
        nx.draw_networkx_edges(graph, layout, edge_color='gray')
        nx.draw_networkx_labels(graph, layout, font_color='white')

        for u, v, e in graph.edges(data=True):
            label = '{}/{}'.format(e['flow'], e['capacity'])
            color = 'green' if e['flow'] < e['capacity'] else 'red'
            x = layout[u][0] * .6 + layout[v][0] * .4
            y = layout[u][1] * .6 + layout[v][1] * .4
            t = plt.text(x, y, label, size=16, color=color,
                         horizontalalignment='center', verticalalignment='center')

        plt.show()

    def create_network(self, THEteamID):
        '''Builds up the network needed for solving the baseball elimination
        problem as a network flows problem & stores it in self.G. Returns a
        dictionary of saturated edges that maps team pairs to the amount of
        additional games they have against each other.

        teamID: ID of team that we want to check if it is eliminated
        return: dictionary of saturated edges that maps team pairs to
        the amount of additional games they have against each other
        '''

        saturated_edges = {}
        self.G.clear()

        #print(self.teams[THEteamID].against)

        #TODO: implement this

        #The TeamId is the team that is NOT included in the graph (i.e. the team whose perspective the graph is in)
        #First make a dictionary with all the teams (but not for the teamId team) for how many games they have left

        #Make a graph with networkx
            # G = nx.DiGraph()
            # G.add_edge('x','a', capacity=3.0)
            # G.add_edge('x','b', capacity=1.0)

        #Code:
        #For x in self.teams:
        #   if x!= teamId:
        #       MAP ALL VALUES TO MAP WITH :
        #       Self.G.addEdge(self.teams[teamID].wins)

        # LIKE THIS

        self.G.add_node('S')

        CapValue = self.teams[THEteamID].wins+self.teams[THEteamID].remaining

        self.G.add_node('T')

        a = self.get_team_IDs()
        for teamID in a:
            if(teamID != THEteamID):
                team = self.teams[teamID]
                teamWins = team.wins
                self.G.add_node(team.ID)
                self.G.add_edge(team.ID, 'T', capacity=CapValue-teamWins, flow= 0 )


        matchUps = []

        for m in range(0, len(self.teams)):
            teamID1 = m
            for n in range(m, len(self.teams)):
                teamID2 = n
                if(teamID1 != teamID2 and teamID1 != THEteamID and teamID2 != THEteamID):
                    matchUps.append((teamID1, teamID2))

        #print(matchUps)
        #print(self.G.edges(data=True))

        for match in matchUps:
            team1, team2 = match
            gamesR = self.teams[team1].get_against(team2)
            #gamesR = self.teams[team1].against[team2]
            saturated_edges[match] = gamesR
            self.G.add_node(match)
            self.G.add_edge('S', match, capacity=gamesR, flow= 0 )
            #print(match)
            for matchedTeam in match:
                self.G.add_edge(match, matchedTeam, capacity=10000000, flow=0)

        #print(self.G.edges(data=True))
        #print(saturated_edges)
        return saturated_edges

    def find_path(self,graph, source, sink, path, visited):
      """Finds and returns an augmenting path from source to sink, if one exists"""
      #print(self.G.edges(data=True))
      # residual graph needs edges going in both directions - undirected representation
      residual_graph = graph.to_undirected()

      # if you have reached the sink already, return the path
      if source == sink:
        return path

      # go through edges in residual graph
      for edge in residual_graph.edges(source, data=True):
        edge_sink = edge[1]
        edge_data = edge[2]

        # determine if that edge was in the forward direction in the original graph
        # and compute the residual based on this information
        in_direction = graph.has_edge(source, edge_sink)
        if in_direction:
          residual = edge_data['capacity'] - edge_data['flow']
        else:
          residual = edge_data['flow']

        # check for positive residual value and make sure the node hasn't already been
        # visited as part of this path (no cycles)
        if residual > 0 and not edge_sink in visited:
          visited.add(edge_sink)
          # recursively call this function until we reach the sink
          result = self.find_path(graph, edge_sink, sink, path + [(edge,residual)], visited)

          if result != None:
            return result

      # if we can't reach the sink from the source, return None
      #print(self.G.edges(data=True))
      return None

    def network_flows(self, saturated_edges):
        '''Uses network flows to determine if the team with given team ID
        has been eliminated. You can feel free to use the built in networkx
        maximum flow function or the maximum flow function you implemented as
        part of the in class implementation activity.

        saturated_edges: dictionary of saturated edges that maps team pairs to
        the amount of additional games they have against each other
        return: True if team is eliminated, False otherwise
        '''
        # # print(len(self.G))
        # # print(self.G.number_of_edges())
        # graph = self.G
        # source = 'S'
        # sink = 'T'
        #
        # path = self.find_path(graph, source, sink, [], set(source))
        # #
        # #   # continue while a path exists from source to sink
        # while path != None:
        # #     # find the bottleneck/minimum residual value in the path
        #     flow = min(residual for edge,residual in path)
        # #
        #     for edge,residual in path:
        #       edge_data = edge[2]
        #       # check if the edge is a forward or backward edge in the original graph
        #       if graph.has_edge(edge[0], edge[1]):
        #         # add the flow for forward edge
        #         graph[edge[0]][edge[1]]['flow'] = edge_data['flow'] + flow
        #       else:
        #         # subtract the flow for backward edge
        #         graph[edge[1]][edge[0]]['flow'] = edge_data['flow'] - flow
        #
        #     path = self.find_path(graph, source, sink, [], set(source))
        #   # return the sum of the flow leaving the source node (which is total flow)
        # # print(sum(edge[2]['flow'] for edge in graph.edges(source, data=True)), "MAX FLOW")



        #######

        #layout = nx.bipartite_layout(self.G, ['S', 'T'])
        #self.draw_graph(self.G, layout)

        flow_val, flow_dict = nx.maximum_flow(self.G, 'S', 'T')


        for key in saturated_edges:
            currFlow=flow_dict['S'][key]
            # print(key,saturated_edges[key],flow_val)
            # print(saturated_edges[key], "CAP")
            # print(flow_val, "FLOW")
            # print(key, "TEAMS")
            if saturated_edges[key] != currFlow:
                return True

        return False
        #look at all first tier edges,
        # if cap > flow
        # return False
        # else return true

        #return sum(edge[2]['flow'] for edge in graph.edges(source, data=True))

    def linear_programming(self, saturated_edges):
        '''Uses linear programming to determine if the team with given team ID
        has been eliminated. We recommend using a picos solver to solve the
        linear programming problem once you have it set up.
        Do not use the flow_constraint method that Picos provides (it does all of the work for you)
        We want you to set up the constraint equations using picos (hint: add_constraint is the method you want)

        saturated_edges: dictionary of saturated edges that maps team pairs to
        the amount of additional games they have against each other
        returns True if team is eliminated, False otherwise
        '''

        maxflow=pic.Problem()

        c = {}

        for e in self.G.edges.data():
            cap = e[2]['capacity']
            node1 = e[0]
            node2 = e[1]
            c[(node1, node2)] = cap


        cc=pic.new_param('c', c)

        # Add the flow variables.
        f={}
        for e in self.G.edges():
          f[e]=maxflow.add_variable('f[{0}]'.format(e),1)

        # Add another variable for the total flow.
        F=maxflow.add_variable('F',1)

        # Enforce edge capacities.
        maxflow.add_list_of_constraints(
          [f[e]<cc[e] for e in self.G.edges()], # list of constraints
          [('e',2)],                       # e is a double index
          'edges')                         # set the index belongs to

        s = 'S'
        t = 'T'
        # Enforce flow conservation.
        maxflow.add_list_of_constraints(
          [pic.sum([f[p,i] for p in self.G.predecessors(i)],'p','pred(i)')
            == pic.sum([f[i,j] for j in self.G.successors(i)],'j','succ(i)')
            for i in self.G.nodes() if i not in (s,t)],
          'i','nodes-(s,t)')

        # Set source flow at s.
        maxflow.add_constraint(
          pic.sum([f[p,s] for p in self.G.predecessors(s)],'p','pred(s)') + F
          == pic.sum([f[s,j] for j in self.G.successors(s)],'j','succ(s)'))

        # Set sink flow at t.
        maxflow.add_constraint(
          pic.sum([f[p,t] for p in self.G.predecessors(t)],'p','pred(t)')
          == pic.sum([f[t,j] for j in self.G.successors(t)],'j','succ(t)') + F)

        # Enforce flow nonnegativity.
        maxflow.add_list_of_constraints(
          [f[e]>0 for e in self.G.edges()], # list of constraints
          [('e',2)],                   # e is a double index
          'edges')                     # set the index belongs to

        # Set the objective.
        maxflow.set_objective('max',F)

        # Solve the problem.
        maxflow.solve(verbose=0,solver='glpk')

        return False


    def checkTeam(self, team):
        '''Checks that the team actually exists in this division.
        '''
        if team.ID not in self.get_team_IDs():
            raise ValueError("Team does not exist in given input.")

    def __str__(self):
        '''Returns pretty string representation of a division object.
        '''
        temp = ''
        for key in self.teams:
            temp = temp + f'{key}: {str(self.teams[key])} \n'
        return temp

class Team:
    '''
    The Team class represents one team within a baseball division for use in
    solving the baseball elimination problem. This class includes information
    on how many games the team has won and lost so far this season as well as
    information on what games they have left for the season.

    ID: ID to keep track of the given team
    teamname: human readable name associated with the team
    wins: number of games they have won so far
    losses: number of games they have lost so far
    remaining: number of games they have left this season
    against: dictionary that can tell us how many games they have left against
    each of the other teams
    '''

    def __init__(self, ID, teamname, wins, losses, remaining, against):
        self.ID = ID
        self.name = teamname
        self.wins = wins
        self.losses = losses
        self.remaining = remaining
        self.against = against

    def get_against(self, other_team=None):
        '''Returns number of games this team has against this other team.
        Raises an error if these teams don't play each other.
        '''
        try:
            num_games = self.against[other_team]
        except:
            raise ValueError("Team does not exist in given input.")

        return num_games

    def __str__(self):
        '''Returns pretty string representation of a team object.
        '''
        return f'{self.name} \t {self.wins} wins \t {self.losses} losses \t {self.remaining} remaining'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        division = Division(filename)
        for (ID, team) in division.teams.items():
            print(f'{team.name}: Eliminated? {division.is_eliminated(team.ID, "Linear Programming")}')
    else:
        print("To run this code, please specify an input file name. Example: python baseball_elimination.py teams2.txt.")
