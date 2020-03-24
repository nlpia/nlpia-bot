# dialgo-graph-representation-options.md

## 1. Actions/Statements as Nodes

- Human statements are one kind of node
- Bot statemetns are another kind of node
- Edges are probabilities (Markhov Chain)

## 2. Bot Actions as Nodes

- Bot context or state is a node, which immediately triggers a deterministic action.
- Human actions/statements are edges

Can't easily model multiple possible responses by the bot.

## All Actions as Edges

- Humans have states of mind, including context, which are the nodes
- Bots have states which are just the context and personality and current dialog goal
- Bot actions (edges) change the world state
- Human actions (edges) change the bot state

Actions by both humans and bots modeled probabilistically, analogously to one another.
Theory of mind can model both self and human states (who, personality, demographics, knowledge), which can be used to explore the graph and do A* Search to try to find a goal state for both the human and the bot:
- bot to have some piece of knowlege
- human to have some piece of knowledge
- human to be happy with the outcome.

## Human and Bot graphs have same structure

- edges are experiences (sensing)
- nodes are states (knowledge, context, personality, emotional state)
- statements can be chosen from those experiences expected to trigger partner's state of mind transition


# State of Mind Representation

- individual identity (ID, name)
- group identity (bot/not, personality, demographics)
- individual vocabulary
- group vocabulary (shared vocabulary or vocabulary diff from the common English vocab)
- individual knowledge
- group knowledge
- group capabilities
