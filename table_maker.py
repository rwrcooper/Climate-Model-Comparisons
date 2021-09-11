"""
File: table_maker.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Creates tables of meta data and facet counts from a CORDEX seacrh from ESGF

Usage:
    table_maker update-search
    table_maker domain-table <domain>
    table_maker facet-table <facet> <specific>
    table_maker model-domain-table
    table_maker domain-model-table
    table_maker (-h | --help | --version)

Options:
    -h, --help          Show this screen and exit.
"""

from pyesgf.search import SearchConnection
import pandas as pd
from docopt import docopt


HTML_TPL = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Cordex data</title>
        <style>{css}</style>
    </head>
    <body>
        <h2>Facet count for {title_facet} from {title_search} CORDEX search.</h2>

        </div>

        {table}

        {script}

    </body>
</html>"""

HTML_TPL2 = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Cordex data</title>
        <style>{css}</style>
    </head>
    <body>
        <h2>test.</h2>

        </div>

        {table}

        {script}

    </body>
</html>"""

CSS = """
    h2 { text-align: center ;}
    #search { width: 100% ; text-align: center ; margin-bottom: 1em ; }
    #search input { margin: auto ; }
    table { width: 100% ; }
    td, th { padding: 0.1em 0.7em; }
    tr:nth-child(2n) { background: #eee; }
"""

SCRIPT = """<script>
            function searchTable() {
                var input, filter, table, tr, td, i, txtValue;
                input = document.getElementById("tableSearch");
                filter = input.value.toUpperCase();
                table = document.getElementById("AnaData");
                trs = table.getElementsByTagName("tr");
                [...trs].forEach(tr => {
                    let showRow = false;
                    tds = tr.getElementsByTagName("td");
                    if (tr.getElementsByTagName("th").length > 0) {
                        showRow = true;
                    } else {
                        [...tds].forEach(td => {
                            if (td) {
                                txtValue = td.textContent || td.innerText;
                                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                                    showRow = true;
                                    return(false);
                                };
                            }
                        })  // td
                    }
                    if (showRow) {
                        tr.style.display = "";
                    } else {
                        tr.style.display = "none";
                    }
                })  // tr
            }
        </script>"""

domains = {
    "aus": [
     'AUS-22',
     'AUS-44',
    ],
    "afr": [
        'AFR-22',
        'AFR-44',
    ],
    "ant": [
        'ANT-44',
    ],
    "arc": [
        'ARC-44',
    ],
    "cam": [
        'CAM-22',
        'CAM-44',
    ],
    "cas": [
        'CAS-22',
        'CAS-44',
    ],
    "eas": [
        'EAS-22',
        'EAS-44',
    ],
    "eur": [
        'EUR-11',
        'EUR-22',
        'EUR-44',
    ],
    "med": [
        'MED-11',
    ],
    "mna": [
        'MNA-22',
        'MNA-44',
    ],
    "nam": [
        'NAM-11',
        'NAM-22',
        'NAM-44',
    ],
    "sam": [
        'SAM-20',
        'SAM-22',
        'SAM-44',
    ],
    "sea": [
        'SEA-20',
    ],
    "was": [
        'WAS-22',
        'WAS-44',
    ],
}

domains_res = [
    'AUS-22',
    'AUS-44',
    'AFR-22',
    'AFR-44',
    'EAS-22',
    'EAS-44',
    'EUR-11',
    'EUR-22',
    'EUR-44',
    'NAM-11',
    'NAM-22',
    'NAM-44',
    'SAM-20',
    'SAM-22',
    'SAM-44',
    ]

time_frequencies = ['day', 'mon', 'sem']

variables = ['hurs', 'pr', 'prhmax', 'sfcwindmax', 'tas', 'tasmax', 'tasmin',
             'wsgsmax']

meta_data = ['domain', 'variable', 'time_frequency', 'ensemble', 'experiment',
             'rcm_name', 'rcm_version', 'id', 'institute', 'size',
             'number_of_files', 'driving_model']


conn = SearchConnection('https://esgf-node.llnl.gov/esg-search', distrib=True)

ctx = conn.new_context(project='CORDEX', domain=','.join(domains_res),
                       time_frequency=','.join(time_frequencies),
                       variable=','.join(variables))

# full CORDEX search
ctx_full = conn.new_context(project='CORDEX')


def make_table(domain_list, time_frequency_list, variables_list,
               meta_data_list):
    '''function to make table, context (ctx), result set, hit count.'''
    # rs = ResultsSet
    # hc = hit count

    results_table = pd.DataFrame(columns=meta_data)
    ctx = conn.new_context(project='CORDEX',
                           domain=','.join(domain_list),
                           time_frequency=','.join(time_frequency_list),
                           variable=','.join(variables_list))
    hc = ctx.hit_count
    rs = ctx.search()
    results_table_len = 0

    for i in range(hc):
        to_append = []
        dataset = rs[i]
        dataset_json = dataset.json

        for data in meta_data:
            val = dataset_json[data]
            to_append.append(val[0] if isinstance(val, list) else val)

        results_table.loc[results_table_len] = to_append
        results_table_len = results_table_len+1

    return(ctx, rs, results_table, hc)


def main_facet_table(facet_chosen, specific):
    '''Makes full facet table'''
    if specific:
        ctx_local = ctx
        title_search = "specific"
        fn = ""

    else:
        ctx_local = ctx_full
        title_search = "full"
        fn = "_full"

    # function to make the table
    facet_count_table = ctx_local.facet_counts[facet_chosen]
    facet_count_table = pd.Series(facet_count_table, name='count').sort_values(
        ascending=False)

    # make facet count table to html appropriately formatted and titled
    counts_table_html = facet_count_table.to_frame().to_html()

    # save to html file
    with open(f'html_files/{facet_chosen}{fn}_table.html', 'w') as f:
        f.write(HTML_TPL.format(table=counts_table_html, css=CSS,
                                script=SCRIPT, title_search=title_search,
                                title_facet=title_facet))
    return


def main_update_search():
    ''''''
    ctx, rs, table, hc = make_table(domains_res, time_frequencies, variables,
                                    meta_data)
    ctx_full = conn.new_context(project='CORDEX')

    # add column parent domain
    table['parent_domain'] = table['domain'].apply(lambda x: x.split('-')[0])

    # save to html
    with open('html_files/cordex_search.html', 'w') as f:
        f.write(table.to_html())

    # save to csv
    with open('csv_files/cordex_search.csv', 'w') as f:
        f.write(table.to_csv())
    return(ctx, ctx_full, table)


def main_domain_table(domain_chosen):
    '''make table give a domain,
        makes html file for table with:
            domain, variables, driving_model, rcm_name'''

    domain_table = table[table['domain'] == domain_chosen].groupby(
        ['domain', 'variable', 'driving_model', 'rcm_name']).size()

    # save to html
    domain_table_html = domain_table.to_html()
    with open(f'html_files/{domain_chosen}_domain_table', 'w') as f:
        f.write(domain_table_html)
    return


# make tables
# table 1: model -> domain (name this table_model_domain)
def main_model_domain_table():
    '''makes table with first heirarchy model, then domain.'''

    # make the model_domain_table
    table_model_domain = table.groupby(
        ['driving_model', 'rcm_name', 'parent_domain',
            'domain']).size().to_frame()

    # make tables to use for totals within different categories
    rcm_total_table = table_model_domain.groupby(
        ['driving_model', 'rcm_name']).sum()

    driving_model_total_table = table_model_domain.groupby(
        ['driving_model']).sum()

    parent_domain_total_table = table_model_domain.groupby(
        ['driving_model', 'rcm_name', 'parent_domain']).sum()

    # join to get rcm_total
    table_model_domain['rcm_total'] = table_model_domain.join(
        rcm_total_table, rsuffix='_join1').iloc[:, -1]

    # join to get driving_model_total
    table_model_domain['driving_model_total'] = table_model_domain.join(
        driving_model_total_table, rsuffix='_join2').iloc[:, -1]

    # join to get parent_domain_total
    table_model_domain['parent_domain_total'] = table_model_domain.join(
        parent_domain_total_table, rsuffix='_join3').iloc[:, -1]

    # save domain total
    table_model_domain['domain_total'] = table_model_domain.iloc[:, -4]

    # group by
    table_model_domain_grouped = table_model_domain.groupby(
        ['driving_model', 'driving_model_total', 'rcm_name', 'rcm_total',
            'parent_domain', 'parent_domain_total', 'domain',
            'domain_total']).size().to_frame()

    # sort
    table_model_domain_sorted = table_model_domain_grouped.sort_values(
        ['driving_model_total', 'rcm_total', 'parent_domain_total',
            'domain_total'], ascending=[False, False, False, False])

    # save to html file
    with open('html_files/table_model_domain_sorted.html', 'w') as f:
        f.write(table_model_domain_sorted.to_html())

    # save to csv
    table_model_domain_sorted.to_csv("csv_files/table_model_domain_sorted.csv")
    return


def main_domain_model_table():
    '''makes table with first heirarchy domain, then model.'''

    table_domain_model = table.groupby(
        ['parent_domain', 'domain', 'driving_model', 'rcm_name']).size(
        ).to_frame()

    # make tables to use for totals within different categories
    parent_domain_total_table = table_domain_model.groupby(
        'parent_domain').sum()

    domain_total_table = table_domain_model.groupby(
        ['parent_domain', 'domain']).sum()

    driving_model_total_table = table_domain_model.groupby(
        ['parent_domain', 'domain', 'driving_model']).sum()

    # joins

    # join for parent_domain_total
    table_domain_model['parent_domain_total'] = table_domain_model.join(
        parent_domain_total_table, rsuffix='_join').iloc[:, -1]

    # save rcm totals
    table_domain_model['rcm_total'] = table_domain_model.iloc[:, -2]

    # join for domain_total
    table_domain_model = table_domain_model.join(
        domain_total_table, rsuffix='_test')
    table_domain_model = table_domain_model.rename(
        columns={'0_test': 'domain_total'})

    # join for driving_model_total
    table_domain_model['driving_model_total'] = table_domain_model.join(
        driving_model_total_table, rsuffix='_test',
        on=('parent_domain', 'domain', 'driving_model')).iloc[:, -1]

    # group by
    table_domain_model_grouped = table_domain_model.groupby(
        ['parent_domain', 'parent_domain_total', 'domain', 'domain_total',
         'driving_model', 'driving_model_total', 'rcm_name',
         'rcm_total']).size().to_frame()

    # sort
    table_domain_model_sorted = table_domain_model_grouped.sort_values(
        ['parent_domain_total', 'domain_total', 'driving_model_total',
            'rcm_total'], ascending=[False, False, False, False])

    # save to html file
    with open('html_files/table_domain_model_sorted.html', 'w') as f:
        f.write(HTML_TPL2.format(table=table_domain_model_sorted.to_html(),
                css=CSS, script=SCRIPT))

    # save to csv file
    table_domain_model_sorted.git to_csv("csv_files/table_domain_model_sorted.csv")
    return


def main(args):

    return

    domain_chosen = args['<domain>']
    facet_chosen = args['<facet>']
    specific = args['<specific>']

    if args['update-search']:
        main_update_search()

    elif args['domain-table']:
        main_domain_table(domain_chosen)

    elif args['facet-table']:
        main_facet_table(facet_chosen, specific)

    elif args['model-domain-table']:
        main_model_domain_table()

    elif args['domain-model-table']:
        main_domain_model_table()


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
