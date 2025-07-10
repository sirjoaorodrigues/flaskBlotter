import requests
import pandas as pd

from io import BytesIO


class PNL:
    def __init__(self):
        self.funds = {
            'Multiestrategia': '111376',
            'Ibovespa': '189529',
            'ALOCACAO': '306274',
            'BDR': '1006215',
            'ELETROBRAS': '2200899',
            'TOP JUROS': '10553193',
            'DAYC ARBITRAGEM': '9735925',
            'IRFM1': '152196',
            'SOCJOV II': '8366977'
        }

    def get_pnl_closing(self, fund):
        fund = [self.funds.get(item, item) for item in fund]
        url = f'http://127.0.0.1:1000/api/data/pnl/{fund[0]}'
        data = requests.get(url)
        decoded = data.content.decode('latin1')
        df = pd.read_json(BytesIO(decoded.encode('utf-8')))

        if fund[0] == '9735925':
            df = df[['ativo', 'quantidade', 'P&L']]
            return df
        else:
            df = df[['Ticker', 'QtDm2', 'QtDm1', 'QtdBooks', 'PriceDm2', 'PriceDm1', 'PnLDm1', 'BPS_Closing']]
            bps = df['BPS_Closing'].sum()
            df = df.dropna()

            return df, bps

    def get_pnl_live(self, fund):
        fund = [self.funds.get(item, item) for item in fund]
        url = f'http://127.0.0.1:1000/api/data/pnl/{fund[0]}'
        data = requests.get(url)
        decoded = data.content.decode('latin1')
        df = pd.read_json(BytesIO(decoded.encode('utf-8')))

        if fund[0] == '9735925':
            df = df[['ativo', 'quantidade', 'P&L']]
        else:
            df = df[['Ticker', 'QtDm1', 'LastPrice', 'Ajuste_Dm1', 'AjusteLive', 'BPS']]

        equities_funds = ['1006215', '189529', '2200899']

        if fund[0] not in equities_funds:
            df = df.dropna()

        bps = df['BPS'].sum()

        return df, bps

    def update_prices(self):
        response = requests.get('http://10.11.6.51:1000/api/config/pnl')
        if response.status_code != 200:
            return False

        hour = pd.Timestamp.now().strftime('%H:%M:%S')

        return hour

