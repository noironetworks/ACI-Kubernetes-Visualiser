#!/usr/local/bin/python3
from flask import Flask, render_template, request, redirect
from  graph import VkaciTable, VkaciGraph, VkaciBuilTopology, VkaciEnvVariables, ApicMethodsResolve


app = Flask(__name__, template_folder='template',static_folder='template/assets')
env = VkaciEnvVariables()
topology = VkaciBuilTopology(env, ApicMethodsResolve())
graph = VkaciGraph(env,topology)
table = VkaciTable(topology)

f = open("version.txt", "r")
__build__ = f.read()

graph.update_database()

@app.route('/')
def index():
    return render_template('index.html', version=__build__, env=env, pod_names = topology.get_pods(), node_names = topology.get_nodes(), namespaces = topology.get_namespaces(), leaf_names = topology.get_leafs())


@app.route('/table_data')
def table_data():
    return table.get_leaf_table()

@app.route('/table_data_bgp')
def table_data_bgp():
    return table.get_bgp_table()

@app.route('/table_data_node')
def table_data_node():
    return table.get_node_table()

@app.route('/table_data_pod')
def table_data_pod():
    return table.get_pod_table()

@app.route('/re-generate',methods=['GET', 'POST'])
def regenerate():
    if request.method == 'POST':
        # Update neo4j with topology data using graph
        graph.update_database()
    return redirect("/", code=302)

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=8080)
    
