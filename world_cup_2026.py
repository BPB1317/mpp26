import random
from collections import defaultdict

# ========================
# CONFIGURATION
# ========================
NUM_SIMULATIONS = 5000
RANDOM_SEED = None

# ========================
# INPUT DATA
# ========================

TEAMS_ELO = {
    "spain": 2000, "france": 2000, "england": 1900, "germany": 1875,
    "argentina": 1875, "portugal": 1850, "brazil": 1850, "netherlands": 1775,
    "belgium": 1775, "colombia": 1750, "croatia": 1750, "switzerland": 1750,
    "ecuador": 1720, "mexico": 1750, "morocco": 1720, "uruguay": 1725,
    "austria": 1720, "norway": 1720, "japan": 1700, "senegal": 1685,
    "turkey": 1685, "ivory-coast": 1660, "usa": 1660, "czechia": 1630,
    "sweden": 1630, "paraguay": 1615, "canada": 1615, "scotland": 1600,
    "south-korea": 1600, "egypt": 1570, "australia": 1535, "algeria": 1550,
    "tunisia": 1500, "bosnia": 1500, "congo": 1470, "south-africa": 1485,
    "saudi-arabia": 1450, "iran": 1450, "iraq": 1415, "jordania": 1415,
    "ghana": 1415, "cape-verde": 1370, "qatar": 1370, "new-zealand": 1350,
    "panama": 1350, "uzbekistan": 1330, "curacao": 1270, "haiti": 1350,
}

GROUPS = {
    "A": ["mexico", "czechia", "south-korea", "south-africa"],
    "B": ["switzerland", "canada", "bosnia", "qatar"],
    "C": ["brazil", "morocco", "haiti", "scotland"],
    "D": ["usa", "paraguay", "australia", "turkey"],
    "E": ["germany", "curacao", "ivory-coast", "ecuador"],
    "F": ["netherlands", "japan", "sweden", "tunisia"],
    "G": ["belgium", "egypt", "iran", "new-zealand"],
    "H": ["spain", "cape-verde", "saudi-arabia", "uruguay"],
    "I": ["france", "senegal", "iraq", "norway"],
    "J": ["argentina", "algeria", "austria", "jordania"],
    "K": ["portugal", "congo", "uzbekistan", "colombia"],
    "L": ["england", "croatia", "ghana", "panama"],
}

# ========================
# BRACKET R16
# ========================

BRACKET_R16 = [
    (("T1","E"), ("T3",["A","B","C","D","F"]),  74),
    (("T1","I"), ("T3",["C","D","F","G","H"]),  77),
    (("T2","A"), ("T2","B"),                     73),
    (("T1","F"), ("T2","C"),                     75),
    (("T2","K"), ("T2","L"),                     83),
    (("T1","H"), ("T2","J"),                     84),
    (("T1","D"), ("T3",["B","E","F","I","J"]),  81),
    (("T1","G"), ("T3",["A","E","H","I","J"]),  82),
    (("T1","C"), ("T2","F"),                     76),
    (("T2","E"), ("T2","I"),                     78),
    (("T1","A"), ("T3",["C","E","F","H","I"]),  79),
    (("T1","L"), ("T3",["E","H","I","J","K"]),  80),
    (("T1","J"), ("T2","H"),                     86),
    (("T2","D"), ("T2","G"),                     88),
    (("T1","B"), ("T3",["E","F","G","I","J"]),  85),
    (("T1","K"), ("T3",["D","E","I","J","L"]),  87),
]

QF_PAIRS = [(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15)]
SF_PAIRS = [(0,1),(2,3),(4,5),(6,7)]
FINAL_PAIRS = [(0,1),(2,3)]

# ========================
# MATCH SIMULATION
# ========================

def elo_win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def draw_probability(elo_a, elo_b):
    diff = abs(elo_a - elo_b)
    return max(0.15, min(0.35, 0.35 - (diff / 1000) * 0.20))

def simulate_match(team_a, team_b, elo_dict):
    elo_a = elo_dict[team_a]
    elo_b = elo_dict[team_b]
    p_win_a = elo_win_prob(elo_a, elo_b)
    p_draw  = draw_probability(elo_a, elo_b)
    p_win_a_adj = p_win_a * (1 - p_draw)
    roll = random.random()
    if roll < p_win_a_adj:
        return 3, 0
    elif roll < p_win_a_adj + p_draw:
        return 1, 1
    else:
        return 0, 3

def simulate_ko_match(team_a, team_b, elo_dict):
    p_win_a = elo_win_prob(elo_dict[team_a], elo_dict[team_b])
    return team_a if random.random() < p_win_a else team_b

# ========================
# GROUP SIMULATION
# ========================

def simulate_group(group_teams, elo_dict):
    stats = {t: {"points": 0} for t in group_teams}
    matchups = [(group_teams[i], group_teams[j])
                for i in range(len(group_teams))
                for j in range(i+1, len(group_teams))]
    for ta, tb in matchups:
        pa, pb = simulate_match(ta, tb, elo_dict)
        stats[ta]["points"] += pa
        stats[tb]["points"] += pb
    teams_list = list(group_teams)
    random.shuffle(teams_list)
    teams_sorted = sorted(teams_list, key=lambda t: stats[t]["points"], reverse=True)
    return [{"team": t, "rank": r+1, "points": stats[t]["points"]}
            for r, t in enumerate(teams_sorted)]

# ========================
# MEILLEURS 3EMES
# ========================

def get_best_third_place(all_thirds):
    shuffled = list(all_thirds)
    random.shuffle(shuffled)
    sorted_thirds = sorted(shuffled, key=lambda x: x["points"], reverse=True)
    return [e["team"] for e in sorted_thirds[:8]], [e["group"] for e in sorted_thirds[:8]]

# ========================
# SLOTS T3
# ========================

T3_SLOTS_GROUPS = [
    ["A","B","C","D","F"],   # slot 0 → M74
    ["C","D","F","G","H"],   # slot 1 → M77
    ["B","E","F","I","J"],   # slot 2 → M81
    ["A","E","H","I","J"],   # slot 3 → M82
    ["C","E","F","H","I"],   # slot 4 → M79
    ["E","H","I","J","K"],   # slot 5 → M80
    ["E","F","G","I","J"],   # slot 6 → M85
    ["D","E","I","J","L"],   # slot 7 → M87
]

def assign_t3_to_slots(best_thirds_groups, best_thirds_teams):
    thirds_pool = list(zip(best_thirds_groups, best_thirds_teams))
    random.shuffle(thirds_pool)

    slot_assignments = {}
    used_teams = set()

    for slot_idx, slot_groups in enumerate(T3_SLOTS_GROUPS):
        eligible = [(grp, team) for grp, team in thirds_pool
                    if grp in slot_groups and team not in used_teams]
        if eligible:
            _, team = random.choice(eligible)
        else:
            remaining = [(g, t) for g, t in thirds_pool if t not in used_teams]
            _, team = random.choice(remaining) if remaining else (None, None)

        slot_assignments[slot_idx] = team
        if team:
            used_teams.add(team)

    return slot_assignments

# ========================
# RESOLVE SLOT
# ========================

# Index des slots T3 dans BRACKET_R16 (position 0-based dans la liste)
T3_SLOT_INDEX = {
    0: 0,   # M74 → slot 0
    1: 1,   # M77 → slot 1
    6: 2,   # M81 → slot 2
    7: 3,   # M82 → slot 3
    10: 4,  # M79 → slot 4
    11: 5,  # M80 → slot 5
    14: 6,  # M85 → slot 6
    15: 7,  # M87 → slot 7
}

def resolve_slot(slot, bracket_idx, t1_map, t2_map, slot_assignments):
    kind, val = slot
    if kind == "T1":
        return t1_map.get(val)
    elif kind == "T2":
        return t2_map.get(val)
    elif kind == "T3":
        slot_idx = T3_SLOT_INDEX.get(bracket_idx)
        return slot_assignments.get(slot_idx)

# ========================
# SIMULATION KO COMPLET
# ========================

def simulate_knockout(t1_map, t2_map, slot_assignments, elo_dict,
                      count_r16, count_qf, count_sf, count_final):

    # R32 → R16
    r16_winners = []
    for idx, (slot1, slot2, mid) in enumerate(BRACKET_R16):
        ta = resolve_slot(slot1, idx, t1_map, t2_map, slot_assignments)
        tb = resolve_slot(slot2, idx, t1_map, t2_map, slot_assignments)
        if ta is None or tb is None:
            r16_winners.append(ta or tb)
            continue
        winner = simulate_ko_match(ta, tb, elo_dict)
        count_r16[winner] += 1
        r16_winners.append(winner)

    # R16 → QF
    qf_winners = []
    for i, j in QF_PAIRS:
        winner = simulate_ko_match(r16_winners[i], r16_winners[j], elo_dict)
        count_qf[winner] += 1
        qf_winners.append(winner)

    # QF → SF
    sf_winners = []
    for i, j in SF_PAIRS:
        winner = simulate_ko_match(qf_winners[i], qf_winners[j], elo_dict)
        count_sf[winner] += 1
        sf_winners.append(winner)

    # SF → Finale
    for i, j in FINAL_PAIRS:
        winner = simulate_ko_match(sf_winners[i], sf_winners[j], elo_dict)
        count_final[winner] += 1

# ========================
# MONTE CARLO
# ========================

def run_monte_carlo(groups_dict, elo_dict, num_simulations=5000, seed=None):
    if seed is not None:
        random.seed(seed)

    all_teams = list(elo_dict.keys())
    count_t1     = defaultdict(int)
    count_t2     = defaultdict(int)
    count_t3     = defaultdict(int)
    count_qualif = defaultdict(int)
    count_r16    = defaultdict(int)
    count_qf     = defaultdict(int)
    count_sf     = defaultdict(int)
    count_final  = defaultdict(int)

    for sim in range(num_simulations):
        all_thirds = []
        t1_map = {}
        t2_map = {}

        # Phase de groupes
        for group_name, group_teams in groups_dict.items():
            result = simulate_group(group_teams, elo_dict)
            for entry in result:
                team = entry["team"]
                rank = entry["rank"]
                if rank == 1:
                    count_t1[team] += 1
                    t1_map[group_name] = team
                elif rank == 2:
                    count_t2[team] += 1
                    t2_map[group_name] = team
                elif rank == 3:
                    count_t3[team] += 1
                    all_thirds.append({
                        "team": team,
                        "points": entry["points"],
                        "group": group_name
                    })

        # Meilleurs 3èmes
        best_thirds_teams, best_thirds_groups = get_best_third_place(all_thirds)

        for team in best_thirds_teams:
            count_qualif[team] += 1
        for team in list(t1_map.values()) + list(t2_map.values()):
            count_qualif[team] += 1

        # Assignation des slots T3
        slot_assignments = assign_t3_to_slots(best_thirds_groups, best_thirds_teams)

        # Phase KO
        simulate_knockout(
            t1_map, t2_map, slot_assignments, elo_dict,
            count_r16, count_qf, count_sf, count_final
        )

    # Calcul des probabilités
    probabilities = {}
    for team in all_teams:
        probabilities[team] = {
            "T1":     count_t1[team]     / num_simulations,
            "T2":     count_t2[team]     / num_simulations,
            "T3":     count_t3[team]     / num_simulations,
            "QUALIF": count_qualif[team] / num_simulations,
            "R16":    count_r16[team]    / num_simulations,
            "QF":     count_qf[team]     / num_simulations,
            "SF":     count_sf[team]     / num_simulations,
            "F":      count_final[team]  / num_simulations,
        }

    return probabilities


def show_team_detail(team_name, groups, teams_elo, num_simulations=5000, seed=None):
    team_name = team_name.lower().strip()
    if team_name not in teams_elo:
        print(f"\n✗ Équipe '{team_name}' non trouvée.")
        print(f"  Équipes disponibles : {', '.join(sorted(teams_elo.keys()))}")
        return

    team_group = None
    for g, teams in groups.items():
        if team_name in teams:
            team_group = g
            break

    print(f"\n{'='*65}")
    print(f"  DÉTAIL : {team_name.upper()}  |  Groupe {team_group}  |  Elo {teams_elo[team_name]}")
    print(f"{'='*65}")

    group_teams = groups[team_group]
    opponents = [t for t in group_teams if t != team_name]
    print(f"\n📋 PHASE DE GROUPES — Groupe {team_group}")
    print(f"  {'Adversaire':<22} {'Victoire':>9}  {'Nul':>9}  {'Défaite':>9}")
    print(f"  {'-'*52}")
    for opp in opponents:
        pw  = elo_win_prob(teams_elo[team_name], teams_elo[opp]) * 100
        pd_ = draw_probability(teams_elo[team_name], teams_elo[opp]) * 100
        pl  = 100 - pw - pd_
        print(f"  {opp:<22} {pw:>8.1f}%  {pd_:>8.1f}%  {pl:>8.1f}%")

    if seed is not None:
        random.seed(seed)

    count_t1 = count_t2 = count_t3 = count_qualif = 0
    count_r16 = count_qf = count_sf = count_final = count_win = 0

    # Adversaires par round : round -> {opp -> [rencontres, victoires]}
    ROUNDS = ["R32", "R16", "QF", "SF", "Finale"]
    ko_by_round = {r: defaultdict(lambda: [0, 0]) for r in ROUNDS}

    for sim in range(num_simulations):
        all_thirds = []
        t1_map, t2_map = {}, {}

        for group_name, group_teams_list in groups.items():
            result = simulate_group(group_teams_list, teams_elo)
            for entry in result:
                t, r = entry["team"], entry["rank"]
                if r == 1:   t1_map[group_name] = t
                elif r == 2: t2_map[group_name] = t
                elif r == 3: all_thirds.append({"team": t, "points": entry["points"], "group": group_name})
                if t == team_name:
                    if r == 1:   count_t1 += 1
                    elif r == 2: count_t2 += 1
                    elif r == 3: count_t3 += 1

        best_thirds_teams, best_thirds_groups = get_best_third_place(all_thirds)
        slot_assignments = assign_t3_to_slots(best_thirds_groups, best_thirds_teams)

        qualified = (team_name in t1_map.values() or
                     team_name in t2_map.values() or
                     team_name in best_thirds_teams)
        if not qualified:
            continue
        count_qualif += 1

        team_alive = True

        # R32
        r16_winners = []
        for idx, (slot1, slot2, mid) in enumerate(BRACKET_R16):
            ta = resolve_slot(slot1, idx, t1_map, t2_map, slot_assignments)
            tb = resolve_slot(slot2, idx, t1_map, t2_map, slot_assignments)
            if ta is None or tb is None:
                r16_winners.append(ta or tb)
                continue
            winner = simulate_ko_match(ta, tb, teams_elo)
            r16_winners.append(winner)
            if team_name in (ta, tb):
                opp = tb if ta == team_name else ta
                ko_by_round["R32"][opp][0] += 1
                if winner == team_name:
                    ko_by_round["R32"][opp][1] += 1
                    count_r16 += 1
                else:
                    team_alive = False

        if not team_alive: continue

        # R16
        qf_winners = []
        for i, j in QF_PAIRS:
            ta, tb = r16_winners[i], r16_winners[j]
            winner = simulate_ko_match(ta, tb, teams_elo)
            qf_winners.append(winner)
            if team_name in (ta, tb):
                opp = tb if ta == team_name else ta
                ko_by_round["R16"][opp][0] += 1
                if winner == team_name:
                    ko_by_round["R16"][opp][1] += 1
                    count_qf += 1
                else:
                    team_alive = False

        if not team_alive: continue

        # QF
        sf_winners = []
        for i, j in SF_PAIRS:
            ta, tb = qf_winners[i], qf_winners[j]
            winner = simulate_ko_match(ta, tb, teams_elo)
            sf_winners.append(winner)
            if team_name in (ta, tb):
                opp = tb if ta == team_name else ta
                ko_by_round["QF"][opp][0] += 1
                if winner == team_name:
                    ko_by_round["QF"][opp][1] += 1
                    count_sf += 1
                else:
                    team_alive = False

        if not team_alive: continue

        # SF + Finale
        for i, j in FINAL_PAIRS:
            ta, tb = sf_winners[i], sf_winners[j]
            winner = simulate_ko_match(ta, tb, teams_elo)
            if team_name in (ta, tb):
                opp = tb if ta == team_name else ta
                ko_by_round["SF"][opp][0] += 1
                if winner == team_name:
                    ko_by_round["SF"][opp][1] += 1
                else:
                    team_alive = False

        if not team_alive: continue
        count_final += 1

        # Finale (2 finales dans ce format)
        # On repart des sf_winners pour la 2ème finale
        # À adapter si ta structure finale est différente
        count_win += 1  # simplifié ici, à affiner selon ton bracket

    n = num_simulations
    print(f"\n📊 PROBABILITÉS GLOBALES")
    print(f"  {'-'*38}")
    print(f"  {'1er groupe':<22} {count_t1/n*100:>6.1f}%")
    print(f"  {'2ème groupe':<22} {count_t2/n*100:>6.1f}%")
    print(f"  {'3ème qualifié':<22} {count_t3/n*100:>6.1f}%")
    print(f"  {'Qualifié R32':<22} {count_qualif/n*100:>6.1f}%")
    print(f"  {'-'*38}")
    print(f"  {'Passe R32 → R16':<22} {count_r16/n*100:>6.1f}%")
    print(f"  {'Passe R16 → QF':<22} {count_qf/n*100:>6.1f}%")
    print(f"  {'Passe QF → SF':<22} {count_sf/n*100:>6.1f}%")
    print(f"  {'Atteint Finale':<22} {count_final/n*100:>6.1f}%")
    print(f"  {'🏆 Vainqueur':<22} {count_win/n*100:>6.1f}%")

    print(f"\n⚔️  ADVERSAIRES PAR TOUR")
    for round_name in ROUNDS:
        data = ko_by_round[round_name]
        if not data:
            continue
        print(f"\n  ── {round_name} " + "─" * (45))
        print(f"  {'Adversaire':<22} {'Fréquence':>10}  {'Victoire':>10}  {'Défaite':>10}")
        print(f"  {'-'*54}")
        sorted_opps = sorted(data.items(), key=lambda x: x[1][0], reverse=True)
        for opp, (meetings, wins) in sorted_opps[:8]:
            freq    = meetings / n * 100
            win_pct = wins / meetings * 100 if meetings else 0
            los_pct = 100 - win_pct
            print(f"  {opp:<22} {freq:>9.1f}%  {win_pct:>9.1f}%  {los_pct:>9.1f}%")
    print()



# ========================
# EXPORT EXCEL
# ========================

def export_to_excel(probabilities, groups, teams_elo, output_path="resultats_cdm2026.xlsx"):
    import pandas as pd
    rows = []
    for group_name, teams in groups.items():
        for team in teams:
            p = probabilities[team]
            rows.append({
                "Groupe":       group_name,
                "Équipe":       team,
                "Elo":          teams_elo[team],
                "1er (%)":      round(p["T1"]     * 100, 1),
                "2ème (%)":     round(p["T2"]     * 100, 1),
                "3ème (%)":     round(p["T3"]     * 100, 1),
                "Qualifié (%)": round(p["QUALIF"] * 100, 1),
                "R16 (%)":      round(p["R16"]    * 100, 1),
                "QF (%)":       round(p["QF"]     * 100, 1),
                "SF (%)":       round(p["SF"]     * 100, 1),
                "Finale (%)":   round(p["F"]      * 100, 1),
            })
    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)
    print(f"\n✓ Résultats exportés dans : {output_path}")

# ========================
# VALIDATION
# ========================

def validate_inputs(groups_dict, elo_dict):
    errors = []
    all_group_teams = []
    for group_name, teams in groups_dict.items():
        if len(teams) != 4:
            errors.append(f"Groupe {group_name} : {len(teams)} équipes (attendu : 4)")
        for team in teams:
            if team not in elo_dict:
                errors.append(f"Equipe '{team}' (Groupe {group_name}) : Elo manquant")
            all_group_teams.append(team)
    if len(all_group_teams) != len(set(all_group_teams)):
        errors.append("Des équipes apparaissent en double dans les groupes")
    if len(groups_dict) != 12:
        errors.append(f"Attendu 12 groupes, trouvé : {len(groups_dict)}")
    if errors:
        print("\nERREURS DE VALIDATION :")
        for e in errors: print(f"  ✗ {e}")
        return False
    print(f"  ✓ Validation OK : {len(groups_dict)} groupes, {len(all_group_teams)} équipes")
    return True

# ========================
# MAIN
# ========================

def main():
    print("\n" + "=" * 75)
    print("  COUPE DU MONDE 2026 - SIMULATEUR MONTE CARLO")
    print("=" * 75)

    teams_elo = TEAMS_ELO
    groups    = GROUPS

    print("\n[1/3] Validation des données...")
    if not validate_inputs(groups, teams_elo):
        print("\nArrêt du script.")
        return

    print(f"\n[2/3] Lancement de {NUM_SIMULATIONS} simulations...")
    probabilities = run_monte_carlo(
        groups_dict=groups,
        elo_dict=teams_elo,
        num_simulations=NUM_SIMULATIONS,
        seed=RANDOM_SEED
    )
    print("  ✓ Simulations terminées")

    print("\n[3/3] Export des résultats...")
    export_to_excel(
        probabilities, groups, teams_elo,
        output_path=r"C:\Users\nodet\OneDrive\Desktop\resultats_cdm2026.xlsx"
    )

        # --- Détail par équipe ---
    while True:
        print("\n" + "-"*40)
        team_input = input("  Équipe à détailler (ou 'q' pour quitter) : ").strip()
        if team_input.lower() == 'q':
            break
        show_team_detail(team_input, groups, teams_elo, num_simulations=NUM_SIMULATIONS, seed=RANDOM_SEED)


if __name__ == "__main__":
    main()
