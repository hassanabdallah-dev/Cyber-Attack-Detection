# Automated Attack Detection in IoT Networks

This project aims to automatically detect attacks in IoT networks using a graph-based approach, leveraging the GraphSAGE algorithm in conjunction with machine learning and deep learning techniques.

## Abstract
An IoT system is made up of smart devices that are linked together to collect and send
data as well as act on it, due to resource constraints, IoT systems are vulnerable to a
variety of vulnerabilities. Despite the effectiveness of the existing Intrusion Detection
Systems, IoT environments restrict the use of some security features and systems. In this
work we made two contributions, the first contribution was state-of-the-art, where we
discussed various studies containing several techniques to detect attacks and anomalies
in order to improve security in IoT networks, highlighted the challenges when building an
intrusion detection approach in IoT, then we focused on the graph-based techniques which
in general gave good results. The second contribution was an approach to detecting cyberattacks
in IoT networks in real-time, our approach has achieved 99% accuracy. After
comparing with three existing approaches, we noticed that ours outperformed them.

## Overview

The repository contains the implementation of an automated attack detection system for IoT networks. The approach employs a graph-based methodology, utilizing the GraphSAGE algorithm along with machine learning and deep learning techniques.

## Project Components

- **Report**: The 'report.pdf' file provides a comprehensive overview of the approach, including the state of the art, explanation of the dataset used, evaluation protocol, and results obtained. It serves as a detailed documentation of the methodology and findings.

- **Presentation**: The 'Presentation.pptx' file contains a PowerPoint presentation outlining the key aspects of the approach. It offers a visual summary of the methodology and its results.

- **Source Code**: The source code consists of two main files:
  - `main.py`: This file represents the main implementation of the method, covering tasks from dataset loading to attack detection.
  - `Neo4J.py`: This file serves as a middleware to communicate with the Neo4j API, facilitating interactions with the graph database.

## Prerequisites

To test and run the approach, ensure you have the following prerequisites installed:

- Neo4j: [Download Neo4j](https://neo4j.com/download/)
- IDE (e.g., PyCharm): [Download PyCharm](https://www.jetbrains.com/pycharm/download/)


