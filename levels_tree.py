import requests

import xmltodict
from treelib import Tree
from collections import defaultdict

import pandas as pd
from tabulate import tabulate


class YML:

    def __init__(self, url: str):
        self.url = url
        self.shop_name = None
        self.categories = None
        self.offers = None
        self.parent_and_children = defaultdict(list)
        self.category_trees = []
        self.category_trees_structure = []

    def print_report_table(self):
        """Print the report table on categories' offers."""
        catalog_report = self.get_report_table()
        print(f'\n{self.shop_name}:\n')
        table_to_print = catalog_report[['category', 'offers']]
        print(tabulate(table_to_print, headers='keys', showindex=False, tablefmt='psql'))
        print()

    def print_catalog_tree(self):
        """Print tree of categories of the catalog."""
        for category in self.category_trees_structure:
            category.show()
            print()

    def get_report_table(self) -> pd.DataFrame:
        """Prepare report table for the given catalog."""
        response = self.get_response()
        self.parse_xml(response)

        self.prepare_category_trees()
        category_levels = self.get_all_category_levels()

        catalog_report = pd.DataFrame(category_levels.items(), columns=['category_id', 'category'])
        catalog_report['offers'] = catalog_report['category_id'].apply(lambda category_id: self.offers.get(category_id, 0))

        return catalog_report

    def get_response(self) -> bytes:
        """Get and return yml response of the given url."""
        response = requests.get(self.url)
        response.raise_for_status()

        return response.content

    @staticmethod
    def count_offers(offers: list) -> dict:
        """Count number of offers by categories."""
        offers = pd.DataFrame(offers, columns=['categoryId'])
        offers_count = offers['categoryId'].value_counts().to_dict()

        return offers_count

    def parse_xml(self, response: bytes) -> None:
        """Parse Y(X)ML data to get categories and offers."""
        catalog = xmltodict.parse(response)
        assert 'yml_catalog' in catalog, 'The given url is not in Yandex Market Language format'

        shop = catalog['yml_catalog']['shop']
        self.shop_name = shop['name']
        categories = shop['categories']['category']
        offers = shop['offers']['offer']

        self.offers = self.count_offers(offers)
        self.categories = {
            category['@id']: {'parent_id': category.get('@parentId'), 'name': category['#text']}
            for category in categories
        }

    def construct_tree(self, root_category: str) -> Tree:
        """Construct full tree of the given root category."""
        tree = Tree()
        tree_structure = Tree()

        tree.create_node(root_category, root_category)
        tree_structure.create_node(self.categories[root_category]['name'], root_category)

        categories_list, seen = [root_category], {root_category}

        while categories_list:
            nxt = categories_list.pop()
            for child in self.parent_and_children[nxt]:
                tree.create_node(child, child, parent=nxt)
                tree_structure.create_node(self.categories[child]['name'], child, parent=nxt)
                if child not in seen:
                    categories_list.append(child)
                    seen.add(child)

        self.category_trees_structure.append(tree_structure)

        return tree

    def prepare_category_trees(self):
        """Get category trees for all root categories of the given catalog."""
        for child, child_info in self.categories.items():
            self.parent_and_children[child_info['parent_id']].append(child)

        root_categories = self.parent_and_children[None]
        for root_category in root_categories:
            tree = self.construct_tree(root_category)
            self.category_trees.append(tree)

    def get_all_category_levels(self):
        """Get category levels for all categories of the catalog."""
        category_levels = {}

        for category_tree in self.category_trees:
            root_category = category_tree.root
            category_levels[root_category] = self.categories[root_category]['name']
            final_categories = category_tree.paths_to_leaves()
            for category in final_categories:
                path = ' / '.join(self.categories[cat]['name'] for cat in category)
                category_levels[category[-1]] = path

        return category_levels
