import pandas as pd
from datetime import datetime
import yfinance as yf

class DataLoader:
    """ Rôle : récupérer et préparer les prix.
        Elle isole la logique d’accès aux données 
        (remplacer par une API plus tard)
    """

    def __init__(self, symbol :str, start_date :datetime, end_date :datetime):
        """ Initialisation de la classe DataLoader """
        self.symbol : str = symbol
        self.start_date : datetime = start_date
        self.end_date : datetime = end_date
        self.data : pd.DataFrame = None
        self.clean_data : pd.DataFrame = None

    def fetch_yfinance(self) -> None:
        """ Rôle : récupérer les données de Yahoo Finance """
        if self.data is not None:
            raise ValueError("Data already loaded.")
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date, progress=False)
        
    def load_from_csv(self, file_path :str) -> None:
        """ Rôle : charger les données depuis un fichier CSV """
        if self.data is not None:
            raise ValueError("Data already loaded.")
        self.data = pd.read_csv(file_path)
    
    def get_close(self) -> pd.Series:
        """ Rôle : récupérer les prix de clôture """
        if self.data is None:
            raise ValueError("Data not loaded yet.")
        return self.data["Close"].squeeze() # Met au format Series

    def get_open(self) -> pd.Series:
        """ Rôle : récupérer les prix d'ouverture """
        if self.data is None:
            raise ValueError("Data not loaded yet.")
        return self.data["Open"].squeeze() # Met au format Series

    def get_daily_returns(self) -> pd.Series:
        """ Rôle : récupérer les retours quotidiens """
        if self.data is None:
            raise ValueError("Data not loaded yet.")
        return self.data["Close"].pct_change().dropna() # Met au format Series

if __name__ == "__main__":
    loader = DataLoader("AAPL", "2025-01-01", "2025-10-24")
    loader.fetch_yfinance()

    print(loader.get_daily_returns())