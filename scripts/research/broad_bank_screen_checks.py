#!/usr/bin/env python3
"""Bounded source-screen calculations, not Harbor or model trials.

Run with Python 3.12 from the repository root. Optional --sheets-archive uses
SpreadsheetBench's pinned archive (URL/hash in the screening source manifest).
No network, package installation, generated workbook or upstream code execution.
Prints JSON; callers may save raw output under runs/.
"""
from __future__ import annotations

import argparse
import calendar
from collections import defaultdict
import io
import itertools
import json
import math
from pathlib import Path
import random
import sqlite3
import tarfile
import time
import xml.etree.ElementTree as ET
import zipfile


def paired_facet_check():
    # Independent instances of the inspected paired-facet generator family.
    # For full row rank A, solve A*x = (b_plus-b_minus)/2. The radius equals
    # min((b_plus+b_minus)/(2*norm(A_i))), the paired-inequality upper bound.
    rng = random.Random(20260912)
    worst = 0.0
    for _ in range(100):
        a = [[rng.gauss(0, 1) for _ in range(8)] for _ in range(4)]
        p = [rng.gauss(0, 1) for _ in range(8)]
        bp = [sum(u*v for u, v in zip(row, p)) + rng.random() for row in a]
        bm = [-sum(u*v for u, v in zip(row, p)) + rng.random() for row in a]
        c = [(u-v)/2 for u, v in zip(bp, bm)]
        gram = [[sum(u*v for u, v in zip(row, col)) for col in a] + [c[i]] for i, row in enumerate(a)]
        for k in range(4):
            j = max(range(k, 4), key=lambda j: abs(gram[j][k]))
            gram[k], gram[j] = gram[j], gram[k]
            scale = gram[k][k]
            assert abs(scale) > 1e-12
            gram[k] = [v/scale for v in gram[k]]
            for j in range(4):
                if j != k:
                    f = gram[j][k]
                    gram[j] = [x-f*y for x, y in zip(gram[j], gram[k])]
        x = [sum(a[i][j]*gram[i][-1] for i in range(4)) for j in range(8)]
        norms = [math.sqrt(sum(v*v for v in row)) for row in a]
        bound = min((u+v)/(2*n) for u, v, n in zip(bp, bm, norms))
        ax = [sum(u*v for u, v in zip(row, x)) for row in a]
        actual = min([(u-v)/n for u, v, n in zip(bp, ax, norms)] + [(u+v)/n for u, v, n in zip(bm, ax, norms)])
        worst = max(worst, abs(actual-bound))
    assert worst < 1e-10
    return {'instances': 100, 'dimensions': [4, 8], 'max_radius_gap_to_analytic_upper_bound': worst,
            'limit': 'Independent family instances; no CVXPY or upstream timed harness replay.'}


def fifo_check():
    # Direct recurrence of verified_asyn_fifo.v nonblocking assignments.
    # Reset complete, no reads, winc always true. rptr_syn stays zero.
    b = g = 0
    accepted = []
    for edge in range(1, 20):
        full = g == 0b11000  # invert top two bits of synchronized read Gray 0
        old_b = b
        if not full:
            accepted.append({'edge': edge, 'address': b & 15})
            b = (b + 1) & 31
        g = old_b ^ (old_b >> 1)
    assert len(accepted) == 18 and accepted[16] == {'edge': 17, 'address': 0}
    return {'depth': 16, 'accepted_through_edge_19_without_reads': len(accepted), 'first_overwrite': accepted[16],
            'limit': 'Source-derived clock recurrence, not a Verilog simulator run.'}


def trunc_div(x, y):
    q = abs(x)//abs(y)
    return -q if (x < 0) != (y < 0) else q


def signed_division_check():
    count = 0
    for x in range(-128, 128):
        for y in range(-128, 128):
            if y == 0 or (x == -128 and y == -1):
                continue
            q = trunc_div(x, y)
            for z in range(-128, 128):
                p = y*z
                if z == 0 or (q == -128 and z == -1):
                    continue
                if -128 <= p <= 127 and not (x == -128 and p == -1):
                    assert trunc_div(q, z) == trunc_div(x, p)
                    count += 1
    x, y, z = -128, -128, -127
    wrapped = (y*z+128) % 256-128
    source, target = trunc_div(trunc_div(x, y), z), trunc_div(x, wrapped)
    assert source != target
    return {'defined_i8_cases_with_representable_product': count, 'mismatches': 0,
            'wrapped_product_counterexample': {'x': x, 'y': y, 'z': z, 'product_i8': wrapped, 'source': source, 'target': target},
            'limit': 'Finite arithmetic check of sufficient conditions; not Alive2 or a target-profit measurement.'}


def intervals_check():
    db = sqlite3.connect(':memory:')
    db.execute('create table intervals(start integer, finish integer)')
    query = '''WITH frontier AS (
 SELECT *, max(finish) OVER (ORDER BY start, finish
 ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prior_end FROM intervals
), groups AS (
 SELECT *, sum(CASE WHEN prior_end IS NULL OR start > prior_end THEN 1 ELSE 0 END)
 OVER (ORDER BY start, finish ROWS UNBOUNDED PRECEDING) AS grp FROM frontier
) SELECT min(start), max(finish) FROM groups GROUP BY grp ORDER BY min(start)'''
    def oracle(rows):
        result = []
        for start, finish in sorted(rows):
            if not result or start > result[-1][1]:
                result.append([start, finish])
            else:
                result[-1][1] = max(result[-1][1], finish)
        return [tuple(r) for r in result]
    possible = list(itertools.combinations(range(6), 2))
    cases = list(itertools.combinations_with_replacement(possible, 3)) + [[(0, 10), (1, 2), (3, 4)]]
    for rows in cases:
        db.execute('delete from intervals')
        db.executemany('insert into intervals values(?,?)', rows)
        assert db.execute(query).fetchall() == oracle(rows)
    db.close()
    return {'cases': len(cases), 'matches': len(cases), 'nested_counterexample_output': [[0, 10]],
            'semantics': 'Closed intervals; touching merges; positive lengths; one group.',
            'limit': 'Authored variant inputs, not BIRD database or upstream evaluator.'}


def read_xlsx(data):
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rel = {x.attrib['Id']: x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        out = {}
        for s in ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets', ns):
            target = rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target = target.lstrip('/') if target.startswith('/') else 'xl/'+target
            cells = {}
            for c in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row/s:c', ns):
                value = c.find('s:v', ns)
                value = value.text if value is not None else None
                if c.attrib.get('t') == 's' and value is not None:
                    value = strings[int(value)]
                elif c.attrib.get('t') == 'inlineStr':
                    value = ''.join(c.find('s:is', ns).itertext())
                elif value is not None:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                if value is not None:
                    cells[c.attrib['r']] = value
            out[s.attrib['name']] = cells
        return out


def workbook_checks(archive):
    ids = ['39432', '2768', '61-4', '55468', '46646', '82-38', '254-34']
    books = {}
    with tarfile.open(archive) as tar:
        for m in tar.getmembers():
            if m.name.endswith('.xlsx') and any('/'+i+'/' in m.name for i in ids):
                books[m.name.rsplit('/', 1)[-1]] = read_xlsx(tar.extractfile(m).read())
    def sheet(i, tag='init', name='Sheet1'):
        return books[f'1_{i}_{tag}.xlsx'][name]
    src = sheet('39432')
    gold = sheet('39432', 'golden')
    fifo = []
    for row in range(2, 6):
        remaining = src[f'L{row}']
        total = 0
        for qty, cost in [('J','K'),('H','I'),('F','G'),('D','E'),('B','C')]:
            use = min(remaining, src.get(f'{qty}{row}', 0))
            total += use*src.get(f'{cost}{row}', 0)
            remaining -= use
        value = total/src[f'L{row}']
        assert math.isclose(value, gold[f'M{row}'], abs_tol=1e-10)
        fifo.append(value)
    src, supply = sheet('2768'), sheet('2768', name='Sheet2')
    gold = sheet('2768', 'golden')
    available = defaultdict(float)
    for r in range(2, 8):
        available[supply[f'A{r}'], supply[f'B{r}']] += supply[f'D{r}']
    used = defaultdict(float)
    allocation = []
    for r in range(2, 19):
        key = src[f'A{r}'], src[f'D{r}']
        value = min(src[f'G{r}'], max(0, available[key]-used[key]))
        used[key] += value
        assert value == gold[f'H{r}']
        allocation.append(value)
    assert src['C12'] == src['C13'] and src['F13'] < src['F12']
    src, gold_ohlc = sheet('61-4', name='input'), sheet('61-4', 'golden', name='output')
    groups = []
    for row in range(2, 22):
        negative = src[f'H{row}'] < 0
        if groups and negative and src[f'H{groups[-1][-1]}'] < 0 and src[f'B{row}'] == src[f'B{groups[-1][-1]}']:
            groups[-1].append(row)
        else:
            groups.append([row])
    for out_row, group in enumerate(groups, 2):
        newest, oldest = group[0], group[-1]
        values = [src[f'A{newest}'], src[f'B{newest}'], src[f'C{oldest}'],
                  max(src[f'D{r}'] for r in group), min(src[f'E{r}'] for r in group),
                  src[f'F{newest}'], sum(src[f'G{r}'] for r in group)]
        assert values == [gold_ohlc[f'{c}{out_row}'] for c in 'ABCDEFG']
    assert all(gold_ohlc.get(f'{c}{r}') is None for c in 'ABCDEFG' for r in range(len(groups)+2, 16))
    src, gold = sheet('55468'), sheet('55468', 'golden')
    rows = [r for r in range(5, 11) if src.get(f'A{r}') == src['AE4'] and src.get(f'B{r}') == src['AD4']]
    cols = [chr(c) for c in range(ord('C'), ord('Z')+1) if src.get(chr(c)+'3') == src['AB4'] and src.get(chr(c)+'4') == src['AC4']]
    assert len(rows) == len(cols) == 1
    lookup = src[f'{cols[0]}{rows[0]}']
    assert lookup == gold['AE5'] == 228
    src, gold = sheet('46646'), sheet('46646', 'golden')
    shifts = [src[f'{chr(66+m)}9']/calendar.monthrange(int(src['B3']), m+1)[1] for m in range(12)]
    assert all(math.isclose(v, gold[f'{chr(66+m)}11'], abs_tol=1e-12) for m, v in enumerate(shifts))
    src, gold = sheet('82-38', name='FAKE'), sheet('82-38', 'golden', name='DATA')
    equal = [src.get(f'D{r}') == gold.get(f'D{r}') for r in range(2, 21)]
    assert all(equal)
    src = sheet('254-34', name='Before')
    vals = [src[f'A{i}'] for i in range(1, 17)]
    witnesses = []
    for mask in range(1 << 16):
        total = math.fsum(v for i, v in enumerate(vals) if mask & (1 << i))
        if 994108 <= total <= 994112:
            witnesses.append({'rows': [i+1 for i in range(16) if mask & (1 << i)], 'sum': total})
    assert witnesses
    return {'archive': str(archive), 'workbooks_read': len(books), 'fifo_values_4_of_4': fifo,
            'allocation_row_order_17_of_17': allocation,
            'allocation_order_observation': 'Rows 12 and 13 tie on issued date; row 13 has an earlier requested date. Golden follows line order, which is not evidence of an incorrect issued-date policy.',
            'ohlc_grouped_rows': len(groups), 'ohlc_golden_cells_including_blanks_matched': 98, 'composite_lookup': lookup, 'monthly_count_division_12_of_12': shifts,
            'invoice_input_FAKE_matches_gold_D2_D20': len(equal),
            'subset_masks_examined': 1 << 16, 'valid_subset_witnesses': witnesses,
            'limit': 'Actual archived init/golden cached values; no Excel recalculation, formula authoring or full benchmark run.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheets-archive', type=Path)
    args = parser.parse_args()
    start = time.perf_counter()
    y, reference, example = [1., 1.2], [.4, .6], [.25, .75]
    objective = lambda x: sum((a-b)**2 for a, b in zip(x, y))/2
    assert objective(reference) < objective(example)
    mask_table = [(((x-1) & 255) & 253) == 0 for x in range(4)]
    assert mask_table == [bool(x & 1) for x in range(4)]
    # Brake source: reference hub is on opposite side of disk; candidate overlaps.
    ref_volume = math.pi*((140**2-70**2)*30+(80**2-30**2)*50-5*7.5**2*50-20*3**2*30)
    overlap = math.pi*(80**2-70**2)*30
    out = {'schema_version': 1, 'kind': 'source_screen_calculations', 'model_trials': 0,
           'simplex': {'reference': reference, 'example': example, 'reference_objective': objective(reference), 'example_objective': objective(example)},
           'chebyshev_paired_facets': paired_facet_check(), 'fifo_reference': fifo_check(),
           'division': signed_division_check(), 'range_mask': {'inputs': [0, 1, 2, 3], 'output': mask_table, 'rewrite': '(arg & 1) != 0'},
           'interval_sql': intervals_check(),
           'brake_analytic': {'reference_volume': ref_volume, 'candidate_volume': ref_volume-overlap, 'relative_volume_difference_percent': 100*overlap/ref_volume,
                              'mean_bbox_dimension_difference_percent': 100*(80-50)/80/3,
                              'limit': 'Analytic primitives inferred from source/FCStd XML; no FreeCAD replay.'}}
    if args.sheets_archive:
        out['spreadsheets'] = workbook_checks(args.sheets_archive)
    out['elapsed_seconds'] = time.perf_counter()-start
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
