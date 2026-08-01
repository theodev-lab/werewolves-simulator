# 🐺 werewolves-simulator

This project simulates Werewolves games without requiring human input. Each player receives a role and a randomly generated personality. During the game, players build suspicions, influence one another, vote during the day, and use their role-specific abilities at night.

The simulator can run either a single detailed game or many games in order to estimate each faction's win rate.

## 🧰 Requirements

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Run the simulator

Start the simulation from the repository root:

```bash
python3 main.py
```

The output depends on `N_GAMES` in `config.py`:

- With `N_GAMES = 1`, the simulator prints the history of a single game.
- With `N_GAMES > 1`, it prints a table containing the number of victories and win rate for each faction.

## ⚙️ Configuration

Simulation settings are defined in [`config.py`](config.py).

### 🃏 Role distribution

`ROLE_COUNTS` controls how many cards of each role are included in a game:

```python
ROLE_COUNTS = {
    "thief": 1,
    "cupid": 1,
    "seer": 1,
    "wolf": 3,
    "little_girl": 1,
    "witch": 1,
    "villager": 4,
    "hunter": 1
}
```

Set a role count to `0` to disable that role. When the Thief is enabled, two extra Villager cards are added to the deck before roles are dealt. After the role distribution, the Thief may choose their role from the two undealt cards.

### 🎛️ Simulation parameters

| Parameter | Description |
| --- | --- |
| `N_GAMES` | Number of games to simulate. Use `1` for a detailed game log and a larger value for aggregate statistics. |
| `SEED` | Seed used to initialize the simulator RNG. With the same seed, repeated simulation runs are reproducible. |
| `DEBATE_ACTIONS_LAMBDA` | Mean number of debate actions sampled from a Poisson distribution before each daytime vote. |
| `HUNTER_SHOT_THRESHOLD` | Minimum suspicion score required for the Hunter to shoot another player when dying. |
| `WITCH_KILL_THRESHOLD` | Minimum suspicion score required for the Witch to use her death potion. |
| `USE_SHERIFF` | Enables the sheriff election mechanic. Set to `0` to disable it, or `1` to elect a sheriff on the first day. |

## 🎭 Roles

| Player card | Faction | Role |
| --- | --- | --- |
| <img src="assets/cards/villager.jpg" alt="Villager card" width="100"> | Villagers | **Villager**: Their objective is to eliminate every Werewolf. They have no special power and must rely solely on their insight and powers of persuasion. |
| <img src="assets/cards/wolf.jpg" alt="Werewolf card" width="100"> | Werewolves | **Werewolf**: Their objective is to eliminate every innocent player, meaning anyone who is not a Werewolf. Each night, the Werewolves choose a victim to eliminate. |
| <img src="assets/cards/seer.jpg" alt="Seer card" width="100"> | Villagers | **Seer**: Her objective is to eliminate every Werewolf. Each night, she may inspect a player and discover their true identity. |
| <img src="assets/cards/little_girl.jpg" alt="Little Girl card" width="100"> | Villagers | **Little Girl**: Her objective is to eliminate every Werewolf. Each night, she may spy on the Werewolves. |
| <img src="assets/cards/witch.jpg" alt="Witch card" width="100"> | Villagers | **Witch**: Her objective is to eliminate every Werewolf. She has two potions: a life potion that can save the Werewolves' victim and a death potion that can eliminate another player. |
| <img src="assets/cards/hunter.jpg" alt="Hunter card" width="100"> | Villagers | **Hunter**: Their objective is to eliminate every Werewolf. When they die, they may eliminate another player with their final bullet. |
| <img src="assets/cards/cupid.jpg" alt="Cupid card" width="100"> | Villagers | **Cupid**: Their objective is to eliminate every Werewolf. At the beginning of the game, they create a couple. The two lovers must survive together: if one dies, the other dies of grief. |
| <img src="assets/cards/thief.jpg" alt="Thief card" width="100"> | Variable | **Thief**: Their objective is not fixed. At the beginning of the game, they may choose their role from the two cards that were not dealt. |
| <img src="assets/cards/sheriff.jpg" alt="Sheriff card" width="100"> | Special mechanic | **Sheriff**: If enabled, the village elects a sheriff on the first day before the first elimination vote. The sheriff keeps their original role, and their vote counts double during each elimination vote. In case of a tie, the sheriff decides which tied player is eliminated. |

## 🗳️ Voting and behavior model

The simulator focuses mainly on voting dynamics. Each player has two behavioral parameters generated at the beginning of the game:

$$\beta_i \sim \Gamma(4, 0.5)$$

where $\beta_i > 0$ controls how sharply player $i$ follows their suspicion scores :
* low $\beta_i$ makes votes close to random ;
* high $\beta_i$ makes player $i$ vote almost always against their most suspicious target.

Each player also has a participation parameter:

$$\eta_i \sim \Gamma(4, 0.5)$$

During debate, $\eta_i$ controls how likely player $i$ is to participate in the discussion.

The suspicion matrix $S(t)$ contains every player's suspicions at time $t$. Each coefficients $S_{ij}(t)$ represents player $i$'s subjective estimated probability that player $j$ is a Werewolf.

$$
S_{ij}(t)=P\left(W_j \mid \mathcal I_i(t)\right)
$$

where:

* $i$ is the observing player ;
* $j$ is the player whose role is being evaluated ;
* $W_j$ is the event "player $j$ is a Werewolf" ;
* $\mathcal I_i(t)$ is the set of information observed by player $i$ up to time $t$.

The diagonal coefficients $S_{ii}(t)$ are not defined, since a player does not estimate the probability of their own role. In practice, they are ignored in calculations and voting mechanics.


### Initial suspicion

A game has $n$ total players and $w$ Werewolves. Before any other information is observed, every player $j\ne i$ is symmetric from player $i$'s point of view. The initial suspicion is therefore:

$$
S_{ij}(0)=\frac{w}{n-1}
$$

### Bayesian suspicion update

The informative effect of observation $I$ is represented by its likelihood ratio:

$$
\Lambda_I=
\frac{P(I\mid W_j)}
{P(I\mid \overline{W_j})}
$$

The likelihood ratio measures how strongly observation $I$ favors the hypothesis that $j$ is a Werewolf over the hypothesis that $j$ is not a Werewolf:

* if $\Lambda_I>1$, the observation increases suspicion toward $j$ ;
* if $\Lambda_I<1$, the observation decreases suspicion toward $j$ ;
* if $\Lambda_I=1$, the observation provides no information about $j$'s role.

> [!NOTE]
> When player $i$ observes a new piece of information $I$ about player $j$, the current suspicion value $S_{ij}(t)$ is the prior probability that $j$ is a Werewolf.

The suspicion is updated as:

$$
S_{ij}(t+1)=
\frac{\Lambda_I S_{ij}(t)}
{1-S_{ij}(t)+\Lambda_I S_{ij}(t)}
$$

This update is equivalent to classic Bayes' rule:

$$
S_{ij}(t+1)=
\frac{P(I\mid W_j)S_{ij}(t)}
{P(I\mid W_j)S_{ij}(t)+P(I\mid \overline{W_j})(1-S_{ij}(t))}
$$

Dividing the numerator and denominator by $P(I\mid \overline{W_j})$ gives the likelihood-ratio form used by the simulator.

### Debate phase

The debate phase allows players to exchange information and influence one another's beliefs before the daytime vote.

Each debate phase consists of a variable number of actions, following a Poisson distribution:

$$
N_{\text{actions}}
\sim
\mathcal{P}(\lambda),
$$

where $\lambda>0$ is the expected number of actions during one debate phase.

At each action, the next speaker $a$ is sampled from the set of alive players $\mathcal{V}(t)$, with probability proportional to their participation parameter $\eta_a>0$:

$$
P(a\text{ speaks})
=
\frac{\eta_a}
{\sum_{k \in \mathcal{V}(t)} \eta_k}
$$

The parameter $\eta_a$ represents player $a$'s tendency to participate in the debate. The larger it is relative to the other alive players' participation parameters, the more likely player $a$ is to speak.

Once selected as the speaker, player $a$ performs a random action from the following action set:

$$
A_a \in \left\{
\text{accuse},
\text{defend},
\text{follow},
\text{stay silent}
\right\}.
$$

The probability distribution of $A_a$ depends on the speaker's role. These probabilities are behavioral parameters of the model. They do not necessarily describe optimal play; instead, they encode different tendencies depending on the player's role. They can be adjusted to simulate different Villager profiles or different Werewolf strategies.

### Information propagation

Each observable action is treated as new public information. When player $a$ performs an action $A_a$, possibly directed at player $k$, each observer $i$ may update their beliefs about:

* the role of the acting player $a$;
* the role of the target $k$.

The suspicion toward the acting player $a$ is updated directly using Bayes’ rule.

For the target $k$, however, the informational value of the action depends on how much observer $i$ trusts player $a$. We define this trust as the probability that $a$ is not a werewolf:

$$
T_{ia}(t) = P(\overline{W}_a \mid \mathcal I_i(t)) = 1 - S_{ia}(t)
$$

We denote by $\Lambda_{A_a \to k}$ the effect of action $A_a$ on the suspicion toward player $k$. This effect is adjusted according to the level of trust placed in player $a$:

$$
\widetilde{\Lambda}_{A_a \to k} = \Lambda_{A_a \to k}^{T_{ia}(t)}
$$

This transformation preserves the direction of the information while scaling its strength according to the credibility of its source:

* if $T_{ia}(t)=1$, then $\widetilde{\Lambda}_{A_a \to k}=\Lambda_{A_a \to k}$: the information is fully trusted;
* if $0<T_{ia}(t)<1$, the effect of the information is attenuated;
* if $T_{ia}(t)=0$, then $\widetilde{\Lambda}_{A_a \to k}=1$: the action has no effect on the belief about $k$.

The suspicion toward the target is then updated as:

$$
S_{ik}(t+1) = \frac{
\widetilde{\Lambda}_{A_a \to k} S_{ik}(t)
}{
1 - S_{ik}(t)
+
\widetilde{\Lambda}_{A_a \to k} S_{ik}(t)
}
$$

### Vote

At the end of the debate phase, each player $i$ chooses a target among the other players who are still alive. The probability that player $i$ votes against player $j$ is determined by the suspicion score $S_{ij}(t)$:

$$
P(i \to j)
=
\frac{S_{ij}^{\beta_i}}
{\displaystyle\sum_{\substack{k \in \mathcal{V}{(t)}\\ k \ne i}} S_{ik}^{\beta_i}}
$$

The player with the most votes is eliminated.

## 📄 License

This project is licensed under the terms of the [`LICENSE`](LICENSE) file.
