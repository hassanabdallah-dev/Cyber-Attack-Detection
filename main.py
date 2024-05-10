import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from Neo4j import Neo4j

root = tk.Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)
root.geometry('300x150')

listOfExistingNodes = list()
graph = Neo4j("bolt://localhost:7687", "neo4j", "123")
    print("We have started building your Graph")

    #graph = Neo4j("neo4j+s://17dbd888.databases.neo4j.io", "neo4j", "xb_ftqy2opPkEzatTU25ojUaOHEnZ7af97bwOpZ6w7E")
    graph.delete_all_nodes()

    newDictSource = dict()
    newDictDest = dict()
    newDictEdges = dict()

    for i in range(len(df)):

        if not listOfExistingNodes.__contains__(df.loc[i, sourceNodeAttributesColumns[nodePrimaryKey]]):
            for x in sourceNodeAttributesColumns:
                newDictSource[x] = df.loc[i, sourceNodeAttributesColumns[x]]
            graph.add_device_node(newDictSource)
            listOfExistingNodes.append(df.loc[i, sourceNodeAttributesColumns[nodePrimaryKey]])

        if not listOfExistingNodes.__contains__(df.loc[i, destinationNodeAttributesColumns[nodePrimaryKey]]):
            for x in destinationNodeAttributesColumns:
                newDictDest[x] = df.loc[i, destinationNodeAttributesColumns[x]]
            graph.add_device_node(newDictDest)
            listOfExistingNodes.append(df.loc[i, destinationNodeAttributesColumns[nodePrimaryKey]])

        for x in edgeAttributes:
            newDictEdges[x] = df.loc[i, edgeAttributes[x]]

        if aggregateBool == True:
            newDictEdges['CommunicationWeight'] = 0

        graph.add_edge(df.loc[i, sourceNodeAttributesColumns[nodePrimaryKey]], df.loc[i, destinationNodeAttributesColumns[nodePrimaryKey]], newDictEdges, nodePrimaryKey)


    print(listOfExistingNodes)

def constructGraphWithLoadCsv(filePath, sourceNodeAttributesColumns, destinationNodeAttributesColumns, edgeAttributes, aggregateBool):
    graph.construct_graph_with_load_csv(filePath, sourceNodeAttributesColumns, destinationNodeAttributesColumns, edgeAttributes, aggregateBool)

def read_data(filePath):
    nRowsRead = None
    mainDf = pd.read_csv(filePath, delimiter=',', nrows=nRowsRead, low_memory=False, header=0)
    mainDf.dataframeName = 'forTraining.csv'

    columnsList = mainDf.columns.values.tolist()

    if len(columnsList) < 2:
        print("The selected file contains less than two columns, we can't construct the graph. \n")
        return
    else:
        print('The following are all the columns of your file: \n')
        print(columnsList)
        print('-------------------------------------------------------------------------------------------')

        sourceNodeAttributesColumns = dict()
        destinationNodeAttributesColumns = dict()
        edgeAttributes = dict()

        stop = False

        print('-------------------------------------------------------------------------------------------')
        while not stop:
            attributeName = input('Please write the names of an attribute for the nodes:')
            while not stop:
                columnName = input("Please write the names of the column you want to associate with the written "
                                   "source node attribute:")
                if columnsList.__contains__(columnName):
                    sourceNodeAttributesColumns[attributeName.lower()] = columnName.lower()
                    print("The pair " + attributeName + " => " + columnName + " is added for the source nodes")
                    break
                else:
                    print("The column name you written is not in the list of columns in your file, "
                          "the column: " + columnName + " is not added")
            cont = input("Do you want to add more attributes for the nodes? (Y/N)")
            if cont == "N" or cont == "n":
                break

        print('-------------------------------------------------------------------------------------------')
        for x in sourceNodeAttributesColumns:
            while not stop:
                columnName = input("Please write the names of the column you want to associate with the '" + x +
                                   "' attribute for the destination node:")
                if columnsList.__contains__(columnName):
                    if columnName not in sourceNodeAttributesColumns.values():
                        destinationNodeAttributesColumns[x.lower()] = columnName.lower()
                        print("The pair " + x + " => " + columnName + " is added for the destination nodes")
                        break
                    else:
                        print("You have already chosen " + columnName + " for one of the source "
                                                                        "nodes attributes, please choose another")
                else:
                    print("The column name you written is not in the list of columns in your file, "
                          "the column: " + columnName + " is not added")


        print('-------------------------------------------------------------------------------------------')
        while not stop:
            attributeName = input('Please write the names of the edge attribute that represent the TIMESTAMP of the connection:')
            while not stop:
                columnName = input("Please write the names of the column you want to associate with the written "
                                   "TIMESTAMP attribute:")
                if columnsList.__contains__(columnName):
                    if columnName not in destinationNodeAttributesColumns.values() and columnName not in sourceNodeAttributesColumns.values():
                        timeStampAttribute = attributeName.lower()
                        timeStampColumn = columnName
                        edgeAttributes[attributeName.lower()] = columnName.lower()
                        print("The pair " + attributeName + " => " + columnName + " is added for the edges")
                        break
                    else:
                        print("You have already chosen " + columnName + " for one of the source or destination "
                                                                        "nodes attributes, please choose another")
                else:
                    print("The column name you written is not in the list of columns in your file, "
                          "the column: " + columnName + " is not added")
            break

        print('-------------------------------------------------------------------------------------------')
        while not stop:
            attributeName = input('Please write the names of an attribute for the edges:')
            while not stop:
                columnName = input("Please write the names of the column you want to associate with the written "
                                   "edges attribute:")
                if columnsList.__contains__(columnName):
                    if columnName not in destinationNodeAttributesColumns.values() and columnName not in sourceNodeAttributesColumns.values():
                        edgeAttributes[attributeName.lower()] = columnName.lower()
                        print("The pair " + attributeName + " => " + columnName + " is added for the edges")
                        break
                    else:
                        print("You have already chosen " + columnName + " for one of the source or destination "
                                                                        "nodes attributes, please choose another")
                else:
                    print("The column name you written is not in the list of columns in your file, "
                          "the column: " + columnName + " is not added")
            cont = input("Do you want to add more attributes for the edges? (Y/N)")
            if cont == "N" or cont == "n":
                break

        print('-------------------------------------------------------------------------------------------')


        listOfCommonAttributes = list()
        for key1 in sourceNodeAttributesColumns.keys():
            for key2 in destinationNodeAttributesColumns.keys():
                if key1.lower().__eq__(key2.lower()):
                    if not listOfCommonAttributes.__contains__(key1.lower()):
                        listOfCommonAttributes.append(key1.lower())
        if len(listOfCommonAttributes) > 0:
            nodePrimaryKey = None
            aggregate = input("Do you want to aggregate edges and add a weight attribute? (If you accept, each edge will\n hold only one attribute named 'weight' and describe the number of your communication) (Y/N)")
            aggregateBool = False
            if aggregate == "N" or aggregate == "n":
                aggregateBool = False
            elif aggregate == "Y" or aggregate == "y":
                aggregateBool = True
            else:
                print("We have consider that no aggregation\n")

            print("----------------Start Graph constuction----------------")
            constructGraphWithLoadCsv(filePath, sourceNodeAttributesColumns, destinationNodeAttributesColumns, edgeAttributes, aggregateBool)
        else:
            print("You haven't any common attributes between the list of source node attributes and the list"
                  " of destination nodes attributes, we can't build the graph")
        return timeStampAttribute, timeStampColumn

def select_file_and_construct_graph():
    FILE_PATH = os.getcwd() + '/dataset/Train_generalization.csv'
    timeStampAttribute, timeStampColumn = read_data(FILE_PATH)
    return FILE_PATH, timeStampAttribute, timeStampColumn

def graph_sage(FILE_PATH, timeStampAttribute, timeStampColumn):

    mainDf = pd.read_csv(FILE_PATH, delimiter=',', nrows=None, low_memory=False, header=0)
    print("hello, graph sage has started")
    time1 = int(mainDf.loc[mainDf.index[0], timeStampColumn])
    time2 = time1 + 30
    lastTimeStamp = int(mainDf.loc[len(mainDf)-1, timeStampColumn])
    df = pd.DataFrame(columns=["value1", "value2", "value3", "value4", "value5", "class"])
    k = 1

    while time2 <= lastTimeStamp and time1 < lastTimeStamp: #and k < 10:
        try:
            graph.project_graph(time1, time2, timeStampAttribute)
            #graph.add_degree_attribute()
            graph.train_graph_sage_model('mean', 'sigmoid', 5, 1000, 0.1)
            result = graph.get_embedding_vectors(5)

            dfFromCsv = mainDf.loc[(mainDf[timeStampColumn] >= time1) & (mainDf[timeStampColumn] <= time2) & (mainDf['label'] == 1)]
            if len(dfFromCsv) == 0:
                result.append(0)
            else:
                result.append(1)

            print("result vector:"+str(k))
            print(result)

            k+=1

            df.loc[len(df)] = result

            time1 = time2
            time2 = time2 + 30

            print(time2)
        except:
            if 1554322617 <= time2 < 1556021410:
                time1 = 1556021410
                time2 = time1 + 30
            else:
                time1 = time2
                time2 = time2 + 30

            print("No relationships founds: ")
            print(time1)
            print(time2)
            pass

    print("final df:")
    print(df)
    df.to_csv('newOutput3.csv', index=False)




    mainDf = pd.read_csv(FILE_PATH, delimiter=',', nrows=None, low_memory=False, header=0)
    print("hello, graph sage has started")

    time1 = int(mainDf.loc[mainDf.index[0], timeStampColumn])
    time2 = time1 + 30
    k=1
    lastTimeStamp = int(mainDf.loc[len(mainDf)-1, timeStampColumn])

    df = pd.DataFrame(columns=["value1", "value2", "value3", "value4", "value5", "class"])

    print("start projecting")
    graph.project_graph_new_version()
    print("start training")
    graph.train_graph_sage_model_new_version('mean', 'sigmoid', 5, 1000, 0.1)

    while time2 <= lastTimeStamp and time1 < lastTimeStamp:
        try:
            graph.project_graph(time1, time2, timeStampAttribute)

            result = graph.get_embedding_vectors_new_version(5)

            dfFromCsv = mainDf.loc[(mainDf[timeStampColumn] >= time1) & (mainDf[timeStampColumn] <= time2) & (mainDf['label'] == 1)]
            if len(dfFromCsv) == 0:
                result.append(0)
            else:
                result.append(1)

            print("result vector:"+str(k))
            print(result)

            k+=1

            df.loc[len(df)] = result

            #if 1554322617 <= time2 < 1556021410:
            #    time1 = 1556021410
            #    time2 = time1 + 30
            #else:
            #    time1 = time2
            #    time2 = time2 + 30
            time1 = time2
            time2 = time2 + 30

            print(time2)
        except:
            #if 1554322617 <= time2 < 1556021410:
            #    time1 = 1556021410
            #    time2 = time1 + 30
            #else:
            #    time1 = time2
            #    time2 = time2 + 30
            time1 = time2
            time2 = time2 + 30
            print("No relationships founds: ")
            print(time1)
            print(time2)
            pass

    print("final df:")
    print(df)
    df.to_csv('newOutput2.csv', index=False)

if __name__ == '__main__':
    #construct graph from csv file
    FILE_PATH, timeStampAttribute, timeStampColumn = select_file_and_construct_graph()
    graph.set_relationship_weight()
    graph.add_degree_attribute()

    #apply GraphSAGE
    print("---------GraphSAGE has started----------")
    graph_sage(FILE_PATH, timeStampAttribute, timeStampColumn)
    print("---------finish----------")
