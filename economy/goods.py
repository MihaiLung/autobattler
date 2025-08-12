import enum
from typing import Dict, List
from dataclasses import dataclass


class Good(enum.Enum):
    GRAIN = 'grain'
    MEAT = 'meat'
    WOOD = 'wood'


@dataclass
class GoodStats:
    image_loc: str
    price: int = 20
    weight: int = 10


GOOD_STATS = {
    Good.GRAIN.value: GoodStats("wood.png", 10, 10),
    Good.MEAT.value: GoodStats("wood.png", 10, 20),
    Good.WOOD.value: GoodStats("wood.png", 20, 40)
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
        self.supply = min(0, self.supply + additional_supply)

    def add_demand(self, additional_demand):
        self.demand = min(0, self.demand + additional_demand)

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
        self.good_markets: Dict[str, GoodMarket] = {
            good.value: GoodMarket(GOOD_STATS[good.value]) for good in Good
        }

    def add_demand(self, amount_of_goods: Dict[Good, float]):
        for good in amount_of_goods:
            self.good_markets[good.value].add_demand(amount_of_goods[good])

    def add_supply(self, amount_of_goods: Dict[Good, float]):
        for good in amount_of_goods:
            self.good_markets[good.value].add_supply(amount_of_goods[good])

    def value_goods_package(self, num_goods: Dict[Good, float]):
        """
        Evaluates the market price of a good package. Negative values expected & work as well.
        """
        value = 0
        for good in num_goods:
            value += self.good_markets[good.value].market_price * num_goods[good]
        return value


if __name__ == "__main__":
    d = {
            good: GoodMarket(good) for good in Good
        }
    print(d[Good.MEAT])

