# landmodo.com-scrapper (uses playwright, json & re modules)

This script scraps landmodo realestate website ("https://www.landmodo.com").

- Script takes search term as input e.g. "Mohave County, AZ" and search for this term on https://www.landmodo.com
- It then gets data of all the property listing on results page. It also handles the paging elegantly and get information of all properties till last page
- Script also calculates following information 
-- Term Price of property
-- Price per Acre
-- WS Price

- Script prepares all the information in JSON.. example response is

```json
[
    {
    "acerage": "2.07",
    "apn": "207-03-124",
    "link": "https://www.landmodo.com/properties/282478/yucca-elementary-district-az-usa/2-07-acres-in-mohave-county-just-100-down",
    "month_listed": "05",
    "no": 1,
    "price_per_acre": 3671.49758454106,
    "seller": "La Vie Style ",
    "term_price": 7600.0,
    "ws_price": 0
    },
    {
    "acerage": "2.35",
    "apn": "245-24-084",
    "link": "https://www.landmodo.com/properties/282463/red-rock-rd-between-knox-dr-mary-dr-yucca-az-86438/159-mo-mohave-county-az-2-35-acres-power-next-door",
    "month_listed": "05",
    "no": 2,
    "price_per_acre": 4144.68085106383,
    "seller": "Tate Land Company ",
    "term_price": 9740.0,
    "ws_price": 0
    },
    {
    "acerage": "1.20",
    "apn": "336-07-498",
    "link": "https://www.landmodo.com/properties/282452/palo-christi-rd-meadview-az-86444/enjoy-summer-weather-private-mohave-getaway-165-mo",
    "month_listed": "05",
    "no": 3,
    "price_per_acre": 8333.33333333333,
    "seller": "Crossed Arrows Land ",
    "term_price": 10000.0,
    "ws_price": 0
    },
    {
    "acerage": "1.24",
    "apn": "122-06-020",
    "link": "https://www.landmodo.com/properties/282427/lake-havasu-city-az-86406/off-road-enthusiast%E2%80%99s-dream-%E2%80%93-desert-land-with-a-view",
    "month_listed": "05",
    "no": 4,
    "price_per_acre": 2834.67741935484,
    "seller": "Bear Fruit Properties ",
    "term_price": 3515.0,
    "ws_price": 0
    },
    {
    "acerage": "2.35",
    "apn": "312-14-002A",
    "link": "https://www.landmodo.com/properties/282420/kingman-arizona-86411/2-35-acres-lot-with-dirt-road-mountain-views-near-kingman",
    "month_listed": "05",
    "no": 5,
    "price_per_acre": 2454.89361702128,
    "seller": "JAME Properties LLC ",
    "term_price": 5769.0,
    "ws_price": 0
    },
    {
    "acerage": "3.75",
    "apn": "338-04-254, 338-04-196, and 338-04-195",
    "link": "https://www.landmodo.com/properties/282416/mohave-county-az/secluded-serenity-3-75-acres-arizona-s-hidden-treasure",
    "month_listed": "05",
    "no": 6,
    "price_per_acre": 2666.4,
    "seller": "Blue Moose Land LLC ",
    "term_price": 9999.0,
    "ws_price": 0
    },
    {
    "acerage": "1.02",
    "apn": "342-06-195",
    "link": "https://www.landmodo.com/properties/282414/mohave-county-az/your-ticket-to-relaxation-1-02-acres-in-arizona-spa-country",
    "month_listed": "05",
    "no": 7,
    "price_per_acre": 3920.58823529412,
    "seller": "Blue Moose Land LLC ",
    "term_price": 3999.0,
    "ws_price": 0
    },
    {
    "acerage": "2.35",
    "apn": "217-06-069",
    "link": "https://www.landmodo.com/properties/282412/3693-s-epidote-rd-mohave-county-az/raw-land-opportunity-off-grid-enthusiasts-dream-219-mo",
    "month_listed": "05",
    "no": 8,
    "price_per_acre": 6879.57446808511,
    "seller": "Milk and Honey Land Co. ",
    "term_price": 16167.0,
    "ws_price": 0
    },
    {
    "acerage": "1.25",
    "apn": "215-11-257",
    "link": "https://www.landmodo.com/properties/282410/w-safari-dr-golden-valley-az/seize-the-opportunity-off-grid-living-investment-189-mo",
    "month_listed": "05",
    "no": 9,
    "price_per_acre": 9391.2,
    "seller": "Milk and Honey Land Co. ",
    "term_price": 11739.0,
    "ws_price": 0
    },
    {
    "acerage": "1.07",
    "apn": "319-17-080 ",
    "link": "https://www.landmodo.com/properties/282407/lake-mohave-ranchos-unit-5-a-1st-amend-lot-88/invest-wisely-off-grid-haven-for-entrepreneurs-149-mo",
    "month_listed": "05",
    "no": 10,
    "price_per_acre": 8541.1214953271,
    "seller": "Milk and Honey Land Co. ",
    "term_price": 9139.0,
    "ws_price": 0
    },
    {
    "acerage": "2.35",
    "apn": "208-24-201",
    "link": "https://www.landmodo.com/properties/282408/yucca-arizona/escape-the-city-embrace-nature-s-embrace-in-golden-valley",
    "month_listed": "05",
    "no": 11,
    "price_per_acre": 4776.17021276596,
    "seller": "TerraVest Land ",
    "term_price": 11224.0,
    "ws_price": 0
    },
    {
    "acerage": "0.21",
    "apn": "333-21-090",
    "link": "https://www.landmodo.com/properties/282406/valle-vista-unit-4-a-tr-1207-b-lot-4650-e2e2-mohave-county-az-86401/unlock-potential-raw-land-for-eco-investors-69-mo",
    "month_listed": "05",
    "no": 12,
    "price_per_acre": 13761.9047619048,
    "seller": "Milk and Honey Land Co. ",
    "term_price": 2890.0,
    "ws_price": 0
    },
    {
    "acerage": "1.21",
    "apn": "308-12-111",
    "link": "https://www.landmodo.com/properties/282405/w-chloride-rd-golden-valley-az/invest-in-the-future-eco-entrepreneurs-paradise-225-mo",
    "month_listed": "05",
    "no": 13,
    "price_per_acre": 13552.8925619835,
    "seller": "Milk and Honey Land Co. ",
    "term_price": 16399.0,
    "ws_price": 0
    },
    {
    "acerage": "1.00",
    "apn": "343-07-509",
    "link": "https://www.landmodo.com/properties/282397/1825-cormorant-dr-meadview-az-86444-usa/discover-freedom-in-mohave-county-own-your-dream-acre-today",
    "month_listed": "05",
    "no": 14,
    "price_per_acre": 9361.0,
    "seller": "TerraVest Land ",
    "term_price": 9361.0,
    "ws_price": 0
    },
    {
    "acerage": "1.00",
    "apn": "329-06-467",
    "link": "https://www.landmodo.com/properties/282392/white-hills-mohave-county-az-86445/prime-1-acre-lot-in-white-hills-az",
    "month_listed": "05",
    "no": 15,
    "price_per_acre": 24639.0,
    "seller": "ZeteoLand.com ",
    "term_price": 24639.0,
    "ws_price": 0
    },
    {
    "acerage": "4.56",
    "apn": "208-26-172",
    "link": "https://www.landmodo.com/properties/282390/ruby-rd-yucca-mohave-county-arizona-86438/4-56-acre-outdoor-enthusiast-playground",
    "month_listed": "05",
    "no": 16,
    "price_per_acre": 4548.02631578947,
    "seller": "ZeteoLand.com ",
    "term_price": 20739.0,
    "ws_price": 0
    },
    {
    "acerage": "5.71",
    "apn": "353-36-160",
    "link": "https://www.landmodo.com/properties/282389/kingman-mohave-county-az-86401/your-5-71-acre-dream-home-treed-lot",
    "month_listed": "05",
    "no": 17,
    "price_per_acre": 10240.8056042032,
    "seller": "ZeteoLand.com ",
    "term_price": 58475.0,
    "ws_price": 0
    },
    {
    "acerage": "1.00",
    "apn": "327-05-186",
    "link": "https://www.landmodo.com/properties/282387/dolan-springs-mohave-county-az-86441/conveniency-meets-views-only-159-month",
    "month_listed": "05",
    "no": 18,
    "price_per_acre": 10389.0,
    "seller": "ZeteoLand.com ",
    "term_price": 10389.0,
    "ws_price": 0
    },
    {
    "acerage": "5.00",
    "apn": "317-08-077",
    "link": "https://www.landmodo.com/properties/282355/n-mabel-dr-dolan-springs-az-86441/5-acre-rv-land-in-dolan-springs-az-just-239-month",
    "month_listed": "05",
    "no": 19,
    "price_per_acre": 3741.4,
    "seller": "ZeteoLand.com ",
    "term_price": 18707.0,
    "ws_price": 0
    },
    {
    "acerage": "1.00",
    "apn": "328-02-175",
    "link": "https://www.landmodo.com/properties/282344/dolan-springs-arizona-86441/1-perfect-for-new-home-rv-dolan-springs-az",
    "month_listed": "05",
    "no": 20,
    "price_per_acre": 5323.0,
    "seller": "JAME Properties LLC ",
    "term_price": 5323.0,
    "ws_price": 0
    },
    {
    "acerage": "1.24",
    "apn": "122-06-243",
    "link": "https://www.landmodo.com/properties/282309/yucca-az-86438/discover-your-desert-oasis-1-24-acres-mohave-county-az",
    "month_listed": "05",
    "no": 21,
    "price_per_acre": 3729.83870967742,
    "seller": "Bear Fruit Properties ",
    "term_price": 4625.0,
    "ws_price": 0
    },
    {
    "acerage": "1.88",
    "apn": "245-02-054",
    "link": "https://www.landmodo.com/properties/282307/yucca-az-86438/serene-desert-land-%E2%80%93-perfect-for-recreation-or-retirement",
    "month_listed": "05",
    "no": 22,
    "price_per_acre": 11555.8510638298,
    "seller": "Bear Fruit Properties ",
    "term_price": 21725.0,
    "ws_price": 0
    },
    {
    "acerage": "2.35",
    "apn": "217-05-223",
    "link": "https://www.landmodo.com/properties/282305/chemehuevi-dr-golden-valley-az/this-week-s-hot-deal-is-a-2-35-acre-lot-for-only-250-down",
    "month_listed": "05",
    "no": 23,
    "price_per_acre": 6170.21276595745,
    "seller": "Bear Fruit Properties ",
    "term_price": 14500.0,
    "ws_price": 0
    },
    {
    "acerage": "5.00",
    "apn": "340-20-088",
    "link": "https://www.landmodo.com/properties/282304/golden-valley-az-86413/your-rv-sanctuary-in-chloride-az-5-acres-of-freedom",
    "month_listed": "05",
    "no": 24,
    "price_per_acre": 4119.0,
    "seller": "Bear Fruit Properties ",
    "term_price": 20595.0,
    "ws_price": 0
    },
    {
    "acerage": "1.07",
    "apn": "316-09-219B",
    "link": "https://www.landmodo.com/properties/282272/dolan-springs-mohave-county-az-86441/1-acre-w-power-great-access-in-dolan-springs-az",
    "month_listed": "05",
    "no": 25,
    "price_per_acre": 20361.6822429907,
    "seller": "ZeteoLand.com ",
    "term_price": 21787.0,
    "ws_price": 0
    }
]
