from datetime import datetime
from time import time, sleep
from requests import Session
from loguru import logger
from sys import stderr
import os


def create_subacc_subaddress(session: Session):
    payload = {
        "currencyId": 2,
        "subCurrencyId": CHAIN_ID,
        "isIsolationAddress": False
    }
    for i in range(20):
        url = f'https://www.okx.com/v2/asset/deposit/address?t={int(time() * 1000)}'
        r = session.post(url, json=payload)
        if r.json().get('code') == 0 and r.json().get('error_code') == '0':
            logger.info(f'Created {i+1} subaddress')
        else:
            if r.json().get('error_message') in ['The number of deposit addresses has reached the maximum limit', 'Maximum number of deposit addresses reached']:
                logger.warning(f'Sub Addresses limit')
                break
            else:
                logger.error(f'Create {i+1} subaddress ERROR: {r.json()}')


def get_subaddresses(session: Session, filename: str):
    addresses = []
    r = session.get(f'https://www.okx.com/v2/asset/deposit/address/list?t={int(time() * 1000)}&currencyId=2&subCurrencyId={CHAIN_ID}&all=true')

    if r.json().get('code') == 0 and r.json().get('error_code') == '0':
        for subaddress_data in r.json()['data']:
            addresses.append(subaddress_data['address'])

        with open(filename, 'a') as f:
            f.write('\n'.join([str(addr) for addr in addresses])+'\n')
        logger.debug(f'{len(addresses)} added to {filename}')

    else:
        logger.error(f'Cant get subaddresses: {r.json()}')


def manager(tokens: list):
    file_name = f'results/addresses_{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.txt'

    for index, token in enumerate(tokens):
        logger.info(f'Creating sub addresses for {index + 1} subacc...')

        session = Session()
        session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3',
            'authorization': token,
        })

        create_subacc_subaddress(session=session)

        get_subaddresses(session=session, filename=file_name)


if __name__ == '__main__':
    logger.remove()
    logger.add(stderr, format="<white>{time:HH:mm:ss:SSS}</white> | <level>{level: <8}</level> | <level>{message}</level>")
    if not os.path.isdir('results'): os.mkdir('results')

    while True:
        logger.info(f'What chain you want?\n1. Starknet\n2. EVM')
        chain_ = input()
        if chain_ == '1':
            CHAIN_ID = 2131
            break
        elif chain_ == '2':
            CHAIN_ID = 1917
            break
        else:
            logger.warning(f'No option :{chain_}"')


    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    while tokens.count(''): tokens.remove('')

    if len(tokens) > 6: raise ValueError('Может быть максимум 6 токенов')

    try:
        manager(tokens)
    except Exception as err:
        logger.error(f'Globally error: {err}')

    sleep(0.1)
    input('\n\t> Enter')
