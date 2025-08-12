import enum
from typing import Dict, List
from dataclasses import dataclass

from utils import diff_dicts


class Good(enum.Enum):
    GRAIN = 'grain'
    MEAT = 'meat'
    WOOD = 'wood'

# print("Initial check")
# print(type(Good.MEAT)==Good)

@dataclass
class GoodStats:
    image_loc: str
    price: int = 20
    weight: int = 10


GOOD_STATS = {
    Good.GRAIN: GoodStats("grain_icon.png", 10, 10),
    Good.MEAT: GoodStats("meat_icon.png", 10, 20),
    Good.WOOD: GoodStats("wood_icon.png", 20, 40)
}


@dataclass
class GoodMarket:
    good_stats: GoodStats
    supply: float = 0
    demand: float = 0

    @property
    def balance(self):
        return self.supply - self.demand

    def add_supply(self, additional_supply):
        self.supply = max(0, self.supply + additional_supply)

    def add_demand(self, additional_demand):
        self.demand = max(0, self.demand + additional_demand)

    @property
    def market_price_multiplier(self):
        if self.supply >0:
            return min(max(self.demand / self.supply, 0.1),10)
        else:
            return 10

    @property
    def market_price(self):
        return self.market_price_multiplier * self.good_stats.price

class Marketplace:
    def __init__(self):
        self.good_markets: Dict[Good, GoodMarket] = {
            good: GoodMarket(GOOD_STATS[good]) for good in Good
        }

    @property
    def supply(self) -> Dict[Good, float]:
        d_goods = {}
        for good in self.good_markets:
            market = self.good_markets[good]
            if market.supply > 0:
                d_goods[good] = market.supply

        return d_goods

    @property
    def demand(self) -> Dict[Good, float]:
        d_goods = {}
        for good in self.good_markets:
            market = self.good_markets[good]
            if market.demand > 0:
                d_goods[good] = market.demand
        return d_goods

    @property
    def balance(self) -> Dict[Good, float]:
        return diff_dicts(self.supply, self.demand)

    def add_demand(self, amount_of_goods: Dict[Good, float]):
        for good in amount_of_goods:
            self.good_markets[good].add_demand(amount_of_goods[good])

    def add_supply(self, amount_of_goods: Dict[Good, float]):
        for good in amount_of_goods:
            self.good_markets[good].add_supply(amount_of_goods[good])

    def value_goods_package(self, num_goods: Dict[Good, float]):
        """
        Evaluates the market price of a good package. Negative values expected & work as well.
        """
        value = 0
        for good in num_goods:
            value += self.good_markets[good].market_price * num_goods[good]
        return value


if __name__ == "__main__":
    d = {
            good: GoodMarket(GOOD_STATS[Good.MEAT]) for good in Good
        }
    # print(d[Good.MEAT])
    # print([good for good in Good])



