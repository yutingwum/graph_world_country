import csv
from collections import defaultdict

def year_from_date(date):
    year = str.split(date, '/')[2]
    return(year)

def output_formatted_float_string(f):
  return "{0:0.2f}".format(f)

# numeric_string_to_float: take a string representing a number as input (which may include commas or quotation marks)
# and convert it to float type so that it can be used in numerical calculations.
def strip_numeric_formatting(s):
    # remove commas and quotation marks from the number
    return s.replace(',', '').replace('\"', '')

def read_region_file(filename):
    region_mapping = dict()

    with open(filename, 'r', newline='') as input_file:
        region_file_reader = csv.DictReader(input_file, delimiter='\t', quotechar ='"')

        for row in region_file_reader:
            region  = row['Region']
            country = row['Country']
            region_mapping[country] = region

    return region_mapping

def read_original_year2000_rows(filename):
    year200_rows = []
    with open(filename, 'rt') as input_file:
        country_data_reader = csv.DictReader(input_file, delimiter='\t', quotechar='"')
        for row in country_data_reader:
            year200_rows.append(row)
    return year200_rows


def read_directed_graph_from_csv(filename, source_column, dest_column, weight_column):
    graph = defaultdict(list)
    with open(filename, 'r', newline='') as input_file:
        graph_file_reader = csv.DictReader(input_file, delimiter=',', quotechar = '"' )
        for row in graph_file_reader:
            #graph.setdefault(row[source_column], []).append((row[dest_column], row[weight_column]))
            if row[weight_column] == '..' or row[weight_column] == '':
                graph[row[source_column]].append((row[dest_column], str(0)))
            else:
                graph[row[source_column]].append((row[dest_column], row[weight_column]))
            graph[row[source_column]] = sorted(graph[row[source_column]], key=lambda x:float(x[1]), reverse = True)

    return graph

def write_country_data_to_file(filename, country_data_list, destination_graph, source_graph):
    region_mapping = read_region_file("world_bank_regions.txt")

    with open(filename, 'w', newline = '') as output_file:
        # Prepare to write out rows to the output file using csv package's DictWriter routines
        # We are going to write out a subset of the original input file's columns, namely, these three:
        country_data_writer = csv.DictWriter(output_file,
                                                 fieldnames = ['Region', 'Country Name', 'Mobile users per capita', 'Population', 'Year', 'Migration: Top 3 destinations', 'Migration: Top 3 sources'],
                                                 extrasaction = 'ignore',
                                                 delimiter = ',', quotechar = '"')
        country_data_writer.writeheader()
        row_count = 0
        for row in country_data_list:
            year = year_from_date(row['Date'])
            # filter for year condition
            if (year != "2000"):
                continue
            row['Year'] = year

            total_mobile_users_string = strip_numeric_formatting(row["Business: Mobile phone subscribers"])
            total_population_string = strip_numeric_formatting(row["Population: Total (count)"])

            if total_population_string == "":
                row["Population"] = "NA"
            else:
                row['Population'] = int(total_population_string)

            if total_mobile_users_string == "" or total_population_string == "":
                row["Mobile users per capita"] = "NA"
            else:
                mobile_users_per_capita = float(total_mobile_users_string) / float(total_population_string)
                row["Mobile users per capita"] = output_formatted_float_string(mobile_users_per_capita)

            country_name = row['Country Name']
            row['Region'] = region_mapping.get(country_name, "NA")

            row['Migration: Top 3 destinations'] = destination_graph[row['Country Name']][0:3]
            row['Migration: Top 3 sources'] = source_graph[row['Country Name']][0:3]

            country_data_writer.writerow(row)
            row_count = row_count + 1

    print("Done! Wrote a total of %d rows" % row_count)


def get_nodes_edges_csv(input_filename, node_filename, edge_filename, destination_graph):
    nodes = {}
    with open(input_filename, 'r', newline='') as input_file:
        location_data_reader = csv.DictReader(input_file, delimiter=',', quotechar = '"' )
        with open(node_filename, 'w', newline='') as output_file:
            nodes_data_writer = csv.DictWriter(output_file,
                                             fieldnames=['country', 'latitude', 'longitude'],
                                             extrasaction='ignore',
                                             delimiter=',', quotechar='"')
            nodes_data_writer.writeheader()
            for row in location_data_reader:
                if row['Country Name'] not in nodes:
                    nodes[row['Country Name']] = (row['Latitude'], row['Longitude'])
                    nodes_data_writer.writerow({'country': row['Country Name'], 'latitude': row['Latitude'], 'longitude': row['Longitude']})

    countries = []
    with open(edge_filename, 'w', newline='') as output_file:
        edges_data_writer = csv.DictWriter(output_file, fieldnames=['start_country', 'end_country', 'start_lat', 'start_long', 'end_lat', 'end_long', 'count'],
                                             extrasaction='ignore',
                                             delimiter=',', quotechar='"')
        edges_data_writer.writeheader()
        for country in destination_graph:
            for edge in destination_graph[country]:
                try:
                    countries.append({'start_country': country, 'end_country': edge[0], 'start_lat': nodes[country][0],
                                            'start_long': nodes[country][1], 'end_lat': nodes[edge[0]][0],
                                            'end_long': nodes[edge[0]][1], 'count': edge[1]})
                except (KeyError,ValueError):
                    pass
        countries = sorted(countries, key = lambda x:float(x['count']), reverse = True)[0:1000]
        for i in countries:
            edges_data_writer.writerow(i)
    return countries


def main():
    year2000_rows = read_original_year2000_rows('world_bank_country_data.txt')
    destination_graph = read_directed_graph_from_csv('world_bank_migration.csv', 'Country Origin Name', 'Country Dest Name', '2000 [2000]')
    source_graph = read_directed_graph_from_csv('world_bank_migration.csv', 'Country Dest Name', 'Country Origin Name', '2000 [2000]')
    write_country_data_to_file('world-bank-output-hw2-WYUTING.csv', year2000_rows, destination_graph, source_graph)
    countries = get_nodes_edges_csv('locations.csv', 'nodes.csv', 'edges.csv', destination_graph)






# This is boilerplate python code: it tells the interpreter to execute main() only
# if this module is being run as the main script by the interpreter, and
# not being imported as a module.
if __name__ == '__main__':
    main()