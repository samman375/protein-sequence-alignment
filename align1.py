from Bio import SeqIO
import pandas as pd
import sys

# Uses Biopython v.1.79, Pandas v.1.4.1
# Developed on MacOS v.12.5.1

# Example of how to run:
# $ python3 evolve.py < s001.fasta | python3 align1.py > a501

gapPenalty = 8

AASubstitutionMatrix = [["A","B","C","D","E","F","G","H","I","K","L","M","N","P","Q","R","S","T","V","W","X","Y","Z"],
["A","4","-2","0","-2","-1","-2","0","-2","-1","-1","-1","-1","-2","-1","-1","-1","1","0","0","-3","-1","-2","-1"],
["B","-2","6","-3","6","2","-3","-1","-1","-3","-1","-4","-3","1","-1","0","-2","0","-1","-3","-4","-1","-3","2"],
["C","0","-3","9","-3","-4","-2","-3","-3","-1","-3","-1","-1","-3","-3","-3","-3","-1","-1","-1","-2","-1","-2","-4"],
["D","-2","6","-3","6","2","-3","-1","-1","-3","-1","-4","-3","1","-1","0","-2","0","-1","-3","-4","-1","-3","2"],
["E","-1","2","-4","2","5","-3","-2","0","-3","1","-3","-2","0","-1","2","0","0","-1","-2","-3","-1","-2","5"],
["F","-2","-3","-2","-3","-3","6","-3","-1","0","-3","0","0","-3","-4","-3","-3","-2","-2","-1","1","-1","3","-3"],
["G","0","-1","-3","-1","-2","-3","6","-2","-4","-2","-4","-3","0","-2","-2","-2","0","-2","-3","-2","-1","-3","-2"],
["H","-2","-1","-3","-1","0","-1","-2","8","-3","-1","-3","-2","1","-2","0","0","-1","-2","-3","-2","-1","2","0"],
["I","-1","-3","-1","-3","-3","0","-4","-3","4","-3","2","1","-3","-3","-3","-3","-2","-1","3","-3","-1","-1","-3"],
["K","-1","-1","-3","-1","1","-3","-2","-1","-3","5","-2","-1","0","-1","1","2","0","-1","-2","-3","-1","-2","1"],
["L","-1","-4","-1","-4","-3","0","-4","-3","2","-2","4","2","-3","-3","-2","-2","-2","-1","1","-2","-1","-1","-3"],
["M","-1","-3","-1","-3","-2","0","-3","-2","1","-1","2","5","-2","-2","0","-1","-1","-1","1","-1","-1","-1","-2"],
["N","-2","1","-3","1","0","-3","0","1","-3","0","-3","-2","6","-2","0","0","1","0","-3","-4","-1","-2","0"],
["P","-1","-1","-3","-1","-1","-4","-2","-2","-3","-1","-3","-2","-2","7","-1","-2","-1","-1","-2","-4","-1","-3","-1"],
["Q","-1","0","-3","0","2","-3","-2","0","-3","1","-2","0","0","-1","5","1","0","-1","-2","-2","-1","-1","2"],
["R","-1","-2","-3","-2","0","-3","-2","0","-3","2","-2","-1","0","-2","1","5","-1","-1","-3","-3","-1","-2","0"],
["S","1","0","-1","0","0","-2","0","-1","-2","0","-2","-1","1","-1","0","-1","4","1","-2","-3","-1","-2","0"],
["T","0","-1","-1","-1","-1","-2","-2","-2","-1","-1","-1","-1","0","-1","-1","-1","1","5","0","-2","-1","-2","-1"],
["V","0","-3","-1","-3","-2","-1","-3","-3","3","-2","1","1","-3","-2","-2","-3","-2","0","4","-3","-1","-1","-2"],
["W","-3","-4","-2","-4","-3","1","-2","-2","-3","-3","-2","-1","-4","-4","-2","-3","-3","-2","-3","11","-1","2","-3"],
["X","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1"],
["Y","-2","-3","-2","-3","-2","3","-3","2","-1","-2","-1","-1","-2","-3","-1","-2","-2","-2","-1","2","-1","7","-2"],
["Z","-1","2","-4","2","5","-3","-2","0","-3","1","-3","-2","0","-1","2","0","0","-1","-2","-3","-1","-2","5"]]

columns = AASubstitutionMatrix[0]
rows = [row[1:] for row in AASubstitutionMatrix[1:]]
index = [row[0] for row in AASubstitutionMatrix[1:]]

df = pd.DataFrame(rows, columns=columns, index=index)

# Given 2 seqeunces, returns optimal alignment score and identity percentage
def align(seq1, seq2):
    n = len(seq1)
    m = len(seq2)

    # Initialise 2D matrix
    a = [[0] * (n + 1) for i in range(m + 1)]

    # Initialise top row
    for i in range(0, n + 1):
        a[0][i] = -1 * i * gapPenalty
    
    # Initialise left column
    for j in range(0, m + 1):
        a[j][0] = -1 * j * gapPenalty

    # Initialise pointer 2D matrix
    ps = [[0] * (n + 1) for i in range(m + 1)]

    # Recurrence rules
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate matrix value
            xi = seq1[i-1]
            yj = seq2[j-1]

            if xi not in columns:
                sys.exit(f"Error: Unknown amino acid supplied: \"{xi}\". Exiting")
            elif yj not in columns:
                sys.exit(f"Error: Unknown amino acid supplied: \"{yj}\". Exiting")

            a[j][i] = max(a[j-1][i-1] + int(df[yj][xi]), a[j-1][i] - gapPenalty, a[j][i-1] - gapPenalty)
            
            # Set pointer
            if a[j][i] == a[j-1][i-1] + int(df[yj][xi]):
                # diagonal
                ps[j][i] = 1
            elif a[j][i] == a[j][i-1] - gapPenalty:
                # left
                ps[j][i] = 3
            else:
                # up
                ps[j][i] = 2
    
    # Traceback
    k = 0
    ids = 0
    i = n
    j = m

    while i > 0 or j > 0:
        if ps[j][i] == 3:
            # Left gap
            i -= 1
        elif ps[j][i] == 2:
            # Up gap
            j -= 1
        else:
            # Diagonal match
            if seq1[i-1] == seq2[j-1]:
                ids += 1
            i -= 1
            j -= 1
        
        k += 1

    score = a[m][n]
    percIds = 100 * (ids / k)

    return score, percIds

# Extract input sequences into list
records = SeqIO.parse(sys.stdin, "fasta")
seqs = []
for record in records:
    seqs.append(record.seq)

# Print values for each sequence
for i in range(0, len(seqs)):
    score, perc = align(seqs[0], seqs[i])
    print(f"{i}\t {score}\t {perc:.2f}")
