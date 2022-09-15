import sys
from levels_tree import YML


def run_example():
    nnetwork = YML('https://nnetwork.ru/yandex-market.xml')
    tbmarlet = YML('https://saratov.tbmmarket.ru/tbmmarket/service/yandex-market.xml')
    nnetwork.print_report_table()
    nnetwork.print_catalog_tree()
    tbmarlet.print_report_table()
    tbmarlet.print_catalog_tree()


def main():

    if len(sys.argv) == 2:
        url = sys.argv[1]
        if url == 'example':
            run_example()
            exit()
    else:
        url = input('Enter url of catalog: ')

    catalog_report = YML(url)
    catalog_report.print_report_table()


if __name__ == '__main__':
    main()
