#!/usr/local/bin/python3
from flask import Flask, render_template, request, redirect
from  graph import VkaciTable, VkaciGraph, VkaciBuilTopology, VkaciEnvVariables, ApicMethodsResolve, KubernetesApi
import vkaci_mocks
import argparse


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s",
        description="Running vkaci"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument('--test', action="store_true")
    parser.add_argument('--neo4jp')
    return parser

parser = init_argparse()
args = parser.parse_args()

app = Flask(__name__, template_folder='template',static_folder='template/assets')

if args.test:
    vars = vkaci_mocks.mock_vars
    vars["NEO4J_URL"] = "neo4j://localhost:7687"
    vars["NEO4J_PASSWORD"] = args.neo4jp
    env = VkaciEnvVariables(vars)
    topology = VkaciBuilTopology(env, vkaci_mocks.ApicMethodsMock(),  vkaci_mocks.KubernetesApiMock())
else:
    env = VkaciEnvVariables()
    topology = VkaciBuilTopology(env, ApicMethodsResolve(), KubernetesApi())
graph = VkaciGraph(env,topology)
table = VkaciTable(topology)

f = open("version.txt", "r")
__build__ = f.read()

graph.update_database()

@app.route('/')
def index():
    return render_template('index.html', version=__build__, env=env, pod_names=topology.get_pods(), 
    node_names=topology.get_nodes(), namespaces=topology.get_namespaces(), 
    leaf_names=topology.get_leafs(), label_names=topology.get_labels())

@app.route('/pod_names')
def pod_names():
    ns = request.args.get("ns")
    if ns == "!":
        ns = None
    return {"pods":topology.get_pods(ns=ns)}

@app.route('/label_values')
def label_values():
    label = request.args.get("label")
    return {"values":topology.get_label_values(label)}

@app.route('/table_data')
def table_data():
    return table.get_leaf_table()

@app.route('/table_data_bgp')
def table_data_bgp():
    return table.get_bgp_table()

#Corresponding service names with namespaces 
@app.route('/service_names')
def service_names():
    ns = request.args.get("ns")
    if ns == "":
        ns = None
    return {"svc":topology.get_svc(ns=ns)}

@app.route('/table_data_node')
def table_data_node():
    return table.get_node_table()

@app.route('/table_data_pod')
def table_data_pod():
    return table.get_pod_table()

@app.route('/table_data_services')
def table_data_services():
    return table.get_services_table()

@app.route('/re-generate',methods=['GET', 'POST'])
def regenerate():
    if request.method == 'POST':
        # Update neo4j with topology data using graph
        graph.update_database()
    return redirect("/", code=302)

if __name__ == '__main__':
	app.run(debug=False, host="0.0.0.0", port=8080)