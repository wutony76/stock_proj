#!/usr/bin/python
# -*- coding: UTF-8 -*-

TWSE_EXPONENT = {
  "twse01":u"發行量加權股價指數",
  "twse02":u"未含金融保險股指數",
  "twse03":u"未含電子股指數",
  "twse04":u"未含金融電子股指數",
  "twse05":u"水泥類指數",
  "twse06":u"食品類指數",
  "twse07":u"塑膠類指數",
  "twse08":u"紡織纖維類指數",
  "twse09":u"電機機械類指數",
  "twse10":u"電器電纜類指數",
  "twse11":u"化學生技醫療類指數",
  "twse12":u"化學類指數",
  "twse13":u"生技醫療類指數",
  "twse14":u"玻璃陶瓷類指數",
  "twse15":u"造紙類指數",
  "twse16":u"鋼鐵類指數",
  "twse17":u"橡膠類指數",
  "twse18":u"汽車類指數",
  "twse19":u"電子類指數",
  "twse20":u"半導體類指數",
  "twse21":u"電腦及週邊設備類指數",
  "twse22":u"光電類指數",
  "twse23":u"通信網路類指數",
  "twse24":u"電子零組件類指數",
  "twse25":u"電子通路類指數",
  "twse26":u"資訊服務類指數",
  "twse27":u"其他電子類指數",
  "twse28":u"建材營造類指數",
  "twse29":u"航運類指數",
  "twse30":u"觀光類指數",
  "twse31":u"金融保險類指數",
  "twse32":u"貿易百貨類指數",
  "twse33":u"油電燃氣類指數",
  "twse34":u"其他類指數",
}

EFTRI_EXPONENT = {
  "eftri01":u"電子類指數",
  "eftri02":u"半導體類指數",
  "eftri03":u"電腦及週邊設備類指數",
  "eftri04":u"光電類指數",
  "eftri05":u"通信網路類指數",
  "eftri06":u"電子零組件類指數",
  "eftri07":u"電子通路類指數",
  "eftri08":u"資訊服務類指數",
  "eftri09":u"其他電子類指數",
  "eftri10":u"金融保險類指數",
}


OTHER_EXPONENT={
  ##其他指數 資訊
  "tw.FRMSA":u"寶島股價指數",
  "tw.MI_INDEX4":u"上市上櫃跨市場成交資訊",

  "tw.EMP99":u"臺灣就業99指數",
  "tw.HC100":u"臺灣高薪100指數",

  #TWSE
  "tw.MFI94U":u"發行量加權股價報酬指數",
  "tw.TTDR":u"臺指槓桿及反向指數",
  "tw.MI_5MINS_HIST":u"發行量加權股價指數",
  "tw.TWT91U":u"未含金融電子股指數",
  "tw.SC300":u"小型股300指數",
  "tw.EFTRI_HIST":u"電子類指數及金融保險類指數",
  "tw.EFTRI":u"電子類報酬指數及金融保險類報酬指數",
  "tw.CG100":u"臺灣公司治理100指數",

  #FTSE
  "tw.CG100":u"臺灣公司治理100指數",
  "tw.BFM44U":u"臺灣50指數月平均市場價差",
  "tw.TAI100I":u"臺灣中型100指數",
  "tw.BFM44U_TWMC":u"臺灣中型100指數月平均市場價差",
  "tw.TAIINTI":u"臺灣資訊科技指數",
  "tw.BFM44U_TWIT":u"臺灣資訊科技指數月平均市場價差",
  "tw.TAIEI":u"臺灣發達指數",
  "tw.BFM44U_TWEI":u"臺灣發達指數月平均市場價差",
  "tw.TAIDIVIDI":u"臺灣高股息指數",
  "tw.BFM44U_TWDP":u"臺灣高股息指數月平均市場價差",
}


IG_EXPONENT = {
  "TXV1":u"台灣指數",
}



# get-other-exponent 
# start_index 
# all_len

# code:[value, len]
OTHER_EXPONENT_CONF={
  "FRMSA":[1, 3],
  #"FRMSA":[0, 4],
  "MIINDEX4":[2, 4],
  #"MIINDEX4":[1, 5],

  "EMP99":[1, 3],
  #"EMP99":[1, 4],
  "HC100":[1, 3],
  #"HC100":[1, 4],

  "MFI94U":[1, 2],
  "TTDR":[1, 3],
  "MI5MINSHIST":[4, 5],
  "TWT91U":[1, 3],
  "SC300":[1, 3],
  "CG100":[1, 3],
  #"tw.EFTRI_HIST":u"電子類指數及金融保險類指數",
  #"tw.EFTRI":u"電子類報酬指數及金融保險類報酬指數",

  "TAI50I":[1, 3],
  "BFM44U":[2, 6],
  "TAI100I":[1, 3],
  "BFM44UTWMC":[2, 6],
  "TAIINTI":[1, 3],
  "BFM44UTWIT":[2, 6],

  "TAIEI":[1, 3],
  "BFM44UTWEI":[2, 6],
  "TAIDIVIDI":[1, 3],
  "BFM44UTWDP":[2, 6],
}





YAHOO_EXPONENT = {
  "twse01":{"name":u"發行量加權股價指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23001&callback=twse01",},
  "twse02":{"name":u"未含金融保險股指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23002&callback=twse02",},
  "twse03":{"name":u"未含電子股指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=2300&callback=twse03",},
  "twse04":{"name":u"未含金融電子股指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=3000&callback=twse04",},
  "twse05":{"name":u"水泥類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23011&callback=twse05",},
  "twse06":{"name":u"食品類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23007&callback=twse06",},
  "twse07":{"name":u"塑膠類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23012&callback=twse07",},
  "twse08":{"name":u"紡織纖維類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23008&callback=twse08",},

  "twse09":{"name":u"電機機械類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23013&callback=twse09",},
  "twse10":{"name":u"電器電纜類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23014&callback=twse10",},
  "twse11":{"name":u"化學生技醫療類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23015&callback=twse11",},
  "twse12":{"name":u"化學類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23068&callback=twse12",},
  "twse13":{"name":u"生技醫療類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23069&callback=twse13",},
  "twse14":{"name":u"玻璃陶瓷類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23016&callback=twse14",},
  "twse15":{"name":u"造紙類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23009&callback=twse15",},
  "twse16":{"name":u"鋼鐵類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23017&callback=twse16",},

  "twse17":{"name":u"橡膠類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23018&callback=twse17",},
  "twse18":{"name":u"汽車類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23019&callback=twse18",},
  "twse19":{"name":u"電子類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23020&callback=twse19",},
  "twse20":{"name":u"半導體類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23071&callback=twse20",},
  "twse21":{"name":u"電腦及週邊設備類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23072&callback=twse21",},
  "twse22":{"name":u"光電類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23073&callback=twse22",},
  "twse23":{"name":u"通信網路類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23074&callback=twse23",},
  "twse24":{"name":u"電子零組件類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23075&callback=twse24",},

  "twse25":{"name":u"電子通路類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23076&callback=twse25",},
  "twse26":{"name":u"資訊服務類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23077&callback=twse26",},
  "twse27":{"name":u"其他電子類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23078&callback=twse27",},
  "twse28":{"name":u"建材營造類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23006&callback=twse28",},
  "twse29":{"name":u"航運類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23021&callback=twse29",},
  "twse30":{"name":u"觀光類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23022&callback=twse30",},
  "twse31":{"name":u"金融保險類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23010&callback=twse31",},
  "twse32":{"name":u"貿易百貨類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23023&callback=twse32",},

  "twse33":{"name":u"油電燃氣類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23070&callback=twse33",},
  "twse34":{"name":u"其他類指數", "yahoo_url":"https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10&sym=%23024&callback=twse34",},
}


BANK_RATE = { 
  "BANKTAIWAN":{"code":"0040000", "name":"台灣銀行"},
}





