#
# Usage
# $ python  TestLogging.py --log-level=debug
#
import argparse
import logging
import sys



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log-level')

    args = parser.parse_args()

    if args.log_level:
        log_level_num = getattr(logging, args.log_level.upper(), None)
        if type(log_level_num) is not int:
            raise ValueError('Invalid log level: {}'.format(args.log_level))
        print('-- Log Level Num = ' + str(log_level_num))
        logging.basicConfig(level=log_level_num)

    logging.info('-- Information Message')
    logging.debug('-- Debug Message')
    another_task()
    logging.info('-- Information End')
    logging.debug('-- Debug End')


def another_task():
    logging.info('-- Information Message from another_task')
    logging.debug('-- Information Message from another_task')


if __name__ == "__main__":
    sys.exit(main())
