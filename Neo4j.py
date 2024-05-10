from neo4j import GraphDatabase


class Neo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node_tx(self, tx, attributesValuesDict):
        query = "CREATE (a:Device {"
        length = len(attributesValuesDict)
        i = 0
        for value in attributesValuesDict:
            query += str(value) + ": '" + str(attributesValuesDict[value]) + "'"
            i += 1
            if not i == length:
                query += ","
        query += "}) return a"
        result = tx.run(query)
        node = [record["a"] for record in result]
        return node

    def add_device_node(self, attributesValuesDict):
        with self.driver.session() as session:
            result = session.write_transaction(self.create_node_tx, attributesValuesDict)
            print(result)
            session.close()
            self.close()

    def check_existing_tx(self, tx, Ipp):
        exist = False
        result = tx.run("MATCH (a:Device { Ip : '" + Ipp + "'}) return a")
        node = [record for record in result.data()]
        if len(node) != 0:
            print(node[0]['a']['Ip'])
            exist = True

        return exist

    def check_existing_devices(self, Ipp):
        with self.driver.session() as session:
            exist = session.write_transaction(self.check_existing_tx, Ipp)
            session.close()
            self.close()
            return exist

    def add_edge_txn(self, txn, primarySValue, primaryDValue, edgeAttributes, nodePrimaryKey):

        if 'CommunicationWeight' not in edgeAttributes.keys():
            query = "MATCH (a:Device { " + str(nodePrimaryKey) + " : '" + str(primarySValue) + "'}),(b:Device { " + str(
                nodePrimaryKey) + " : '" + str(primaryDValue) + "'}) CREATE (a)-[r:Connection]->(b) SET r ={"

            length = len(edgeAttributes)
            i = 0
            for x in edgeAttributes:
                query += x + " : " + str(edgeAttributes[x])
                i += 1
                if not i == length:
                    query += ","
            query += "} return r"
            result = txn.run(query)
            return result
        else:
            checkExist = "MATCH (a:Device { " + str(nodePrimaryKey) + " : '" + str(
                primarySValue) + "'}),(b:Device { " + str(nodePrimaryKey) + " : '" + str(
                primaryDValue) + "'}) MATCH (a)-[r:Connection]->(b) return PROPERTIES(r)"
            checkResult = txn.run(checkExist)
            listresult = list(checkResult)
            if len(listresult) != 0:
                weight = listresult[0][0]['CommunicationWeight']
                weightInt = int(weight)
                weightInt += 1
                query = "MATCH (a:Device { " + str(nodePrimaryKey) + " : '" + str(
                    primarySValue) + "'}),(b:Device { " + str(nodePrimaryKey) + " : '" + str(
                    primaryDValue) + "'}) MATCH (a)-[r:Connection]->(b) SET r ={CommunicationWeight: " + str(
                    weightInt) + "} return r.CommunicationWeight as weight"
                result = txn.run(query)
            else:
                query = "MATCH (a:Device { " + str(nodePrimaryKey) + " : '" + str(
                    primarySValue) + "'}),(b:Device { " + str(nodePrimaryKey) + " : '" + str(
                    primaryDValue) + "'}) CREATE (a)-[r:Connection]->(b) SET r ={CommunicationWeight: " + str(
                    1) + "} return r.CommunicationWeight as weight"
                result = txn.run(query)

            return result

    def add_edge(self, primarySValue, primaryDValue, edgeAttributes, nodePrimaryKey):
        with self.driver.session() as session:
            result = session.write_transaction(self.add_edge_txn, primarySValue, primaryDValue, edgeAttributes,
                                               nodePrimaryKey)
            # print(result)
            session.close()
            self.close()

    def delete_all_nodes_txn(self, txn):
        result = txn.run("MATCH ()-[r:Connection]-() DELETE r")
        result = txn.run("MATCH (n) DELETE n")

    def delete_all_nodes(self):
        with self.driver.session() as session:
            exist = session.write_transaction(self.delete_all_nodes_txn)
            session.close()
            self.close()

    def set_relationship_weight_txn(self, txn):
        query = "MATCH (n)-[r:Connection]->(m) Set r.relationShipWeight= 0"
        queryResult = txn.run(query)
        query = "MATCH (n)-[r:Connection]->(m) return Properties(r) limit 1"
        queryResult = txn.run(query)
        listresult = list(queryResult)
        listOfProperties = list()
        if len(listresult) != 0 and len(listresult[0]) != 0:
            for property in listresult[0][0].keys():
                listOfProperties.append(property)
            query = "MATCH (n)-[r:Connection]->(m) Set " \
                    "r.relationShipWeight=(0+"
            length = len(listOfProperties)
            j = 0
            for i in range(len(listOfProperties)):
                if listOfProperties[i] != "starttime":
                    #query += "toInteger(r." + listOfProperties[i] + ")/100000000"
                    query += "toFloat(r." + listOfProperties[i] + ")"


                j += 1
                if not j == length:
                    query += "+"
            query += ")"
            queryResult1 = txn.run(query)
            return queryResult1
        else:
            return None

    def set_relationship_weight(self):
        with self.driver.session() as session:
            result = session.write_transaction(self.set_relationship_weight_txn)
            # print(result)
            session.close()
            self.close()

    def project_graph_txn(self, txn, time1, time2, timeStampAttribute):

        query = "CALL gds.graph.exists('cyberSecGraphProjectedGraph') YIELD graphName, exists RETURN graphName, exists"
        queryResult = txn.run(query)
        exist = queryResult.data()[0]['exists']

        if exist == True:
            query = "CALL gds.graph.drop('cyberSecGraphProjectedGraph') YIELD graphName;"
            queryResult = txn.run(query)

        query = "MATCH (n)-[r:Connection]->(m) return Properties(r) limit 1"
        queryResult = txn.run(query)
        listresult = list(queryResult)
        listOfProperties = list()
        if len(listresult) != 0 and len(listresult[0]) != 0:
            for property in listresult[0][0].keys():
                listOfProperties.append(property)

        query = "CALL gds.graph.project.cypher('cyberSecGraphProjectedGraph','MATCH (n:Device) where n.degree > 0 RETURN id(n) AS id, " \
                "labels(n) AS labels, n.degree AS degree'" \
                ", 'MATCH (n)-[r:Connection]->(m)  WHERE r."+timeStampAttribute+" >= "+str(time1)+" And r."+timeStampAttribute+" <= "+str(time2)+" And n.degree > 0 And m.degree > 0 " \
                "RETURN id(n) AS source, id(m) AS target, type(r) AS type, "
        length = len(listOfProperties)
        j = 0
        for i in range(len(listOfProperties)):
            query += "r."+listOfProperties[i]+" AS "+listOfProperties[i]
            j+=1
            if not j == length:
                query += ", "
        query += "') YIELD graphName, nodeCount AS nodes, " \
                "relationshipCount AS rels RETURN graphName, nodes, rels"
        queryResult = txn.run(query)

        data = queryResult.data()[0]

        #print(data['graphName'])
        #print(data['nodes'])
        #print(data['rels'])

        return data

    def project_graph(self, time1, time2, timeStampAttribute):
        with self.driver.session() as session:
            result = session.write_transaction(self.project_graph_txn,time1,time2, timeStampAttribute)
            # print(result)
            session.close()
            self.close()

    def add_degree_attribute_txn(self, txn):
        #query = "CALL gds.degree.mutate('cyberSecGraphProjectedGraph',{mutateProperty: 'degree'}) YIELD nodePropertiesWritten Return nodePropertiesWritten"
        #queryResult = txn.run(query)
        #data = queryResult.data()[0]
        #return data['nodePropertiesWritten']
        query = "Match (n) set n.degree=0 return n.degree"
        queryResult = txn.run(query)
        query = "MATCH (p)-[r]->(x) " \
                "with x, count(r) as degree" \
                " set x.degree = degree return degree as degree"
        queryResult = txn.run(query)
        data = queryResult.data()[0]
        return data['degree']

    def add_degree_attribute(self):
        with self.driver.session() as session:
            result = session.write_transaction(self.add_degree_attribute_txn)
            #print(result)
            session.close()
            self.close()

    def train_graph_sage_model_txn(self, txn, aggregator, activationFunction, embeddingDimension, epochs, learningRate):

        query = "CALL gds.beta.model.exists('cyberSecGraphModel') YIELD exists RETURN exists"
        queryResult = txn.run(query)
        alldata = queryResult.data()[0]
        exist = alldata['exists']

        if exist == True:
            query = "CALL gds.beta.model.drop('cyberSecGraphModel') YIELD modelInfo, loaded, shared, stored " \
                    "RETURN modelInfo.modelName AS modelName, loaded, shared, stored;"
            queryResult = txn.run(query)
        #, relationshipWeightProperty: 'relationShipWeight'
        query = "CALL gds.beta.graphSage.train('cyberSecGraphProjectedGraph',{modelName: 'cyberSecGraphModel'," \
                "featureProperties: ['degree'], aggregator: '"+aggregator+"', " \
                "activationFunction: '"+activationFunction+"', randomSeed: 1337, embeddingDimension: "+str(embeddingDimension)+", epochs: "+str(epochs)+", " \
                "learningRate: "+str(learningRate)+"}) YIELD modelInfo as info RETURN info.modelName as modelName, " \
                "info.metrics.didConverge as didConverge, info.metrics.ranEpochs as ranEpochs, " \
                "info.metrics.epochLosses as epochLosses"
        queryResult = txn.run(query)
        data = queryResult.data()[0]

        #print(data)

        return data

    def train_graph_sage_model(self, aggregator, activationFunction, embeddingDimension, epochs, learningRate):
        with self.driver.session() as session:
            result = session.write_transaction(self.train_graph_sage_model_txn, aggregator, activationFunction, embeddingDimension, epochs, learningRate)
            #print(result)
            session.close()
            self.close()

    def get_embedding_vectors_txn(self, txn):
        query = "CALL gds.beta.graphSage.stream('cyberSecGraphProjectedGraph',{modelName: 'cyberSecGraphModel'}) " \
                "YIELD nodeId, embedding return nodeId, embedding"
        queryResult = txn.run(query)
        allData = queryResult.data()
        #print(allData)
        return allData

    def get_embedding_vectors(self, dimension):
        with self.driver.session() as session:
            result = session.write_transaction(self.get_embedding_vectors_txn)
            #print(result)
            session.close()
            self.close()
            vector = list()

            for i in range(dimension):
                sum=0
                for j in range(len(result)):
                  sum += result[j]['embedding'][i]
                vector.append(sum)

            return vector

    def construct_graph_with_load_csv_txn(self, txn, filePath, sourceNodeAttributeValue, destinationNodeAttributeValue, edgeAttributeValue, aggregateBool):

        result = txn.run("MATCH ()-[r:Connection]-() DELETE r")
        result = txn.run("MATCH (n) DELETE n")

        newFilePath = "file:///"+filePath
        newFilePath.replace("\\", "/")
        query = "LOAD CSV WITH HEADERS FROM '"+newFilePath+"' AS line " \
                "MERGE (a:Device { "

        length = len(sourceNodeAttributeValue)
        i = 0
        for attribute in sourceNodeAttributeValue:
            query += attribute + ": line." + sourceNodeAttributeValue[attribute]
            i += 1
            if not i == length:
                query += ","

        query += "})"

        query += "MERGE (b:Device { "

        length = len(destinationNodeAttributeValue)
        i = 0
        for attribute in destinationNodeAttributeValue:
            query += attribute + ": line." + destinationNodeAttributeValue[attribute]
            i += 1
            if not i == length:
                query += ","

        query += "})"

        if aggregateBool is False:
            query += "CREATE (a)-[r:Connection]->(b) SET r ={"

            length = len(edgeAttributeValue)
            i = 0
            for attribute in edgeAttributeValue:
                query += attribute + ": toFloat(line." + edgeAttributeValue[attribute]+")"
                i += 1
                if not i == length:
                    query += ","

            query += "}"
        else:
            query += "MERGE (a)-[r:Connection]->(b) ON CREATE SET r.communicationWeight = 1" \
                     " ON MATCH SET r.communicationWeight = r.communicationWeight + 1"

        _ = txn.run(query)
        return 1

    def construct_graph_with_load_csv(self, filePath, sourceNodeAttributeValue, destinationNodeAttributeValue, edgeAttributeValue, aggregateBool):
        with self.driver.session() as session:
            result = session.write_transaction(self.construct_graph_with_load_csv_txn, filePath, sourceNodeAttributeValue, destinationNodeAttributeValue, edgeAttributeValue, aggregateBool)
            #print(result)
            session.close()
            self.close()