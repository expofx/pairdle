import requests
import numpy as np
import json
import pandas as pd
from sklearn.manifold import TSNE

import matplotlib
import matplotlib.pyplot as plt
import os

api_key = os.environ.get('OPENAI_API_KEY')

def get_emb(word):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "input": word,
        "model": "text-embedding-ada-002"
    }
    response = requests.post("https://api.openai.com/v1/embeddings", json=data, headers=headers)
    return np.array(response.json()["data"][0]["embedding"])

def get_similarity(word1, word2):
    emb1 = get_word_embedding(word1)
    emb2 = get_word_embedding(word2)
    # cosine similarity
    similarity = np.dot(emb1, emb2) # / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity

def euclidean_dist(emb1, emb2):
    distance = np.linalg.norm(emb1 - emb2)
    return distance
  
if __name__ == "__main__":

  turns = 1
  embeddings = []
  words = []
  players = []

  while True:
      player1_word = input("Player 1, enter your word: ").strip()
      player2_word = input("Player 2, enter your word: ").strip()

      embeddings.append(get_emb(player1_word))
      words.append(player1_word)
      players.append('Player 1')
      embeddings.append(get_emb(player2_word))
      words.append(player2_word)
      players.append('Player 2')

      mat = np.array(embeddings)
      vis = TSNE(n_components=2, perplexity=min(5, turns), random_state=42).fit_transform(mat)

      # Highlight Movements for Player 1 and Player 2
      for player_idx, color in zip([0, 1], ['red', 'blue']):
          path = vis[player_idx::2]
          plt.plot(path[:, 0], path[:, 1], color=color, linestyle='-', marker='o')
          plt.text(path[-1, 0], path[-1, 1], turns, color=color)

      plt.title("Players' movements through embedding space with t-SNE")
      plt.show(block=False)
      plt.pause(1)  # Real-time update effect

      if player1_word == player2_word:
          print(f"Congratulations! You both chose {player1_word} in {turns} turn(s).")
          break

      ax.clear()
      similarity = get_similarity(player1_word, player2_word)
      print(similarity)
      turns += 1 