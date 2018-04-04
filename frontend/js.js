function populateLabels(extend=false)
{
  var chainID = document.getElementById("chainID").value;
  var rowsCountHTML = document.getElementById("rowsCount");
  var rowsCount = parseInt(rowsCountHTML.value);
  var searchTerm = document.getElementById("searchBar").value;
  var startDate = document.getElementById("timePeriod").value;
  var endDate = getCurrentDate();
  var labelTableHTML = document.getElementById("labelTable");
  var listLength = labelTableHTML.rows.length - 1;

  if (extend == false)
  {
    labelTableHTML.innerHTML = "";
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
        if (chainID == 2 || chainID == 4){
            utxoHeader.innerHTML = "<b>Total Unspent Output (BCH)</b>";
        }
        else
        {
        utxoHeader.innerHTML = "<b>Total Unspent Output (BTC)</b>";
        }
      }
      var body = labelTableHTML.createTBody();
      for (var i = 0; i < labels.length; i++)
      {
        var bodyRow = body.insertRow(i);
        var rank = bodyRow.insertCell(0);
        var label = bodyRow.insertCell(1);
        var utxo = bodyRow.insertCell(2);
        rank.innerHTML = labels[i]["rank"];
        label.innerHTML = "<a href=/publiclabel.html&chainID=" + chainID + "&startDate=" + startDate + "&endDate=" + endDate + "&publicLabel=" + encodeURI(labels[i]["label"]) + " >" + labels[i]["label"] + "</a>";
        utxo.innerHTML = labels[i]["amt"].toFixed(8)
      }
      if (extend=true)
      {
        window.scrollTo(0,document.body.scrollHeight);
      }
    }
  };
  // gets the data applying the specified search criteria
  req.open("GET", "/api/?function=getPublicLabelAggregates&chainID=" + chainID + "&startPos=" + startPos + "&endPos=" + endPos + "&startDate=" + startDate + "&endDate=" + endDate + "&searchTerm=" + searchTerm, true);
  req.send();

}

function populatePublicLabels(extend=false)
{
  selectCoinByUrl();

  var searchParams = new URLSearchParams(location.href);
  var chainID = searchParams.get("chainID");

  var rowsCountHTML = document.getElementById("rowsCount");
  var rowsCount = parseInt(rowsCountHTML.value);
  var searchTerm = document.getElementById("searchBar").value;
  var startDate = searchParams.get('startDate');
  var endDate = searchParams.get('endDate');

  var publicLabel = searchParams.get('publicLabel');
  var publicLabelMessage = document.getElementById("publicLabelMessage");
  publicLabelMessage.innerHTML = publicLabel;
  if (!publicLabel) {
      var tableMessage = document.getElementById("tableMessage");
      tableMessage.innerHTML = "This table shows the full list of transactions with public labels.<br>Search using the transaction id.";
      }

  var labelTableHTML = document.getElementById("labelTable");
  var listLength = labelTableHTML.rows.length - 1;

  if (extend == false)
  {
    labelTableHTML.innerHTML = "";
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
        var txDateHeader = headerRow.insertCell(0);
        var txIDHeader = headerRow.insertCell(1);
        var utxoHeader = headerRow.insertCell(2);
        txDateHeader.innerHTML = "<b>Tx Date</b>";
        txIDHeader.innerHTML = "<b>Tx ID</b>";
        if (chainID == 2 || chainID == 4){
            utxoHeader.innerHTML = "<b>Total Output (BCH)</b>";
        }
        else
        {
            utxoHeader.innerHTML = "<b>Total Output (BTC)</b>";
        }
        var spentHeader = headerRow.insertCell(3);
        spentHeader.innerHTML = "<b>Spent?</b>";

      }
      var body = labelTableHTML.createTBody();
      for (var i = 0; i < labels.length; i++)
      {
        var bodyRow = body.insertRow(i);
        var txDate = bodyRow.insertCell(0);
        var txID = bodyRow.insertCell(1);
        var utxo = bodyRow.insertCell(2);
        var spent = bodyRow.insertCell(3);
        var spentDate = bodyRow.insertCell(4);

        var date = new Date(labels[i]["unixTimeCreated"]*1000);
        txDate.innerHTML = date.toDateString();
        txID.innerHTML = labels[i]["txid"];
        utxo.innerHTML = labels[i]["amt"].toFixed(8);

        if (labels[i]["unixTimeSpent"] == 0)
        {
            spent.innerHTML = "No";
        }
        else
        {
            var dateSpent = new Date(labels[i]["unixTimeSpent"]*1000);
            spent.innerHTML = "Yes " + dateSpent.toDateString();
        }

      }
      if (extend==true)
      {
        window.scrollTo(0,document.body.scrollHeight);
      }
    }
  };
  // gets the data applying the specified search criteria
  req.open("GET", "/api/?function=getPublicLabelOutputs&chainID=" + chainID + "&startDate=" + startDate + "&endDate=" + endDate + "&publicLabel=" + encodeURI(publicLabel) + "&searchTerm=" + encodeURI(searchTerm), true);
  req.send();

}

function txSearch()
{
    var chainID = document.getElementById("chainID").value;
    var searchTerm = document.getElementById("searchBar").value;
    var startDate = document.getElementById("timePeriod").value;
    var endDate = getCurrentDate();
    location.href = "/publiclabel.html&chainID=" + chainID + "&startDate=" + startDate + "&endDate=" + endDate + "&searchTerm=" + encodeURI(searchTerm) + "&publicLabel=";
}

function sunChange(init=false, command="toggle"){
  var bodyHTML = $("#body");
  var sunChangeButtonHTML = document.getElementById("sunChange");
  function toDay(){
      setCookie("sun", "day", 10000);
      bodyHTML.removeClass("nightTimeBody");
      $("#labelTable").removeClass("nightTimeLabelTable");
      sunChangeButtonHTML.value = "Night Mode";
  }

  function toNight(){
      setCookie("sun", "night", 10000);
      bodyHTML.addClass("nightTimeBody");
      $("#labelTable").addClass("nightTimeLabelTable");
      sunChangeButtonHTML.value = "Day Mode";
  }
  if (init == true)
  {
    if (getCookie("sun") != ""){
        if (getCookie("sun") == "day")
            {
                toDay();
            }
        else
            {
                toNight();
            }
    }
    else
        {
            change(command);
        }
  }
  else
    {
        change(command);
    }
  function change(command){
      if (command == "toggle")
      {
        if (bodyHTML.hasClass("nightTimeBody"))
        {
          toDay();
        }
        else
        {
          toNight();
        }
      }
      else if (command == "night"){
        toNight();
      }
      else if (command == "day"){
        toDay();
      }
  }
}


function setupPage()
{
  window.setInterval(populateLabels, 10*1000*60);

  clearScreen();
  getUiDefaults(init=true);
  populateLabels();
  mobileAdjust();
}

function setupPagePublicLabels()
{

  window.setInterval(populatePublicLabels, 10*1000*60);

  clearScreen();
  getUiDefaults(init=true);
  populatePublicLabels();
  mobileAdjust();

}

function selectCoinByUrl()
{
  searchParams = new URLSearchParams(location.href);
  var chainIDobj = document.getElementById("chainID");
  var chainID = searchParams.get("chainID");

  if (chainID > 0)
  {
      chainIDobj.value = chainID;

      var coin = "";
      if (chainID == 1) coin = 'btc';
      if (chainID == 2) coin = 'bch';
      if (chainID == 3) coin = 'btc_test';

      if (coin != "") selectCoin(coin, false);
  }
}

function selectCoin(coin, event=false)
{
  var pageHTML = document.getElementById("pageName").name;
  var chainID = document.getElementById("chainID");
  var activateHTML = document.getElementById(coin);

  if (coin == "bch")
  {
    chainID.value = 2;
    var deactivate1HTML = document.getElementById("btc");
    var deactivate2HTML = document.getElementById("btc_test");
    var deactivate3HTML = document.getElementById("bch_test");
  }
  else if (coin == "btc")
  {
    chainID.value = 1;
    //debugger;
    var deactivate1HTML = document.getElementById("bch");
    var deactivate2HTML = document.getElementById("btc_test");
    var deactivate3HTML = document.getElementById("bch_test");
  }
  else if (coin == "btc_test")
  {
    chainID.value = 3;
    //debugger;
    var deactivate1HTML = document.getElementById("btc");
    var deactivate2HTML = document.getElementById("bch");
    var deactivate3HTML = document.getElementById("bch_test");
  }


  // activate selected section
  if (activateHTML)
      if (!activateHTML.className.includes("active"))
      {
        activateHTML.className += " active";
      }

  try {
  // deactive other sections
  deactivate1HTML.className = deactivate1HTML.className.replace(" active", "");
  deactivate2HTML.className = deactivate2HTML.className.replace(" active", "");
  deactivate3HTML.className = deactivate3HTML.className.replace(" active", "");
    } catch (e) {}


  if (event){
      if (pageHTML == "index")
          populateLabels();

      if (pageHTML == "publiclabel")
      {
          location.href = "/index.html&chainID=" + chainID.value;
      }
  }

}


function getUiDefaults(init=false)
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
  var orbitState = uiDefaults["orbitState"];
  var rowsCountHTML = document.getElementById("rowsCount");
  var timePeriodHTML = document.getElementById("timePeriod");
  selectCoin('bch');
  sunChange(init=init, orbitState);
  rowsCountHTML.value = rowsCount;
  rowsCountHTML.default = rowsCount;

  // build the datetime filter list
  var d = new Date();
  var currentDate = d.getTime();
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
      option.selected = true
      timePeriodHTML.value = timePeriod;
    }
    option.value = startDate.getTime()/1000;
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


function getCurrentDate()
{
  Date.prototype.toDateInputValue = (function() {
  var local = new Date(this);
  local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
  return local.getTime()/1000;});
  return new Date().toDateInputValue()
}


function getSortedKeys(obj) {
    var keys = []; for(var key in obj) keys.push(key);
    return keys.sort(function(a,b){return obj[b]-obj[a]}).reverse();
}


function mobileAdjust(){
  var userAgent = navigator.userAgent.toLowerCase();
  var isMobile = {
    Android: function() {
        return userAgent.indexOf("android") != -1;
    },
    iOS: function() {
        return (userAgent.indexOf("iphone") != -1 || navigator.userAgent.indexOf("ipod") != -1 || navigator.userAgent.indexOf("ipad") != -1);
    },
    Opera: function() {
        return userAgent.indexOf("opera mini") != -1;
    },
    Windows: function() {
        return userAgent.indexOf("emobile") != -1;
    },
    any: function() {
        return (isMobile.Android() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
    }
  };
  if (isMobile.any() == true)
  {
    document.getElementById("mainPage").style.width = "100%";
  }
}



function pageSwap(){
  function isHidden(el) {
      var style = window.getComputedStyle(el);
      return (style.display === 'none')
  }
  var mainPageHTML = document.getElementById("mainPage");
  var aboutPageHML = document.getElementById("aboutPage");
  if (isHidden(mainPageHTML))
  {
    mainPageHTML.style.display = "";
    aboutPageHML.style.display = "none";
  }
  else
  {
    mainPageHTML.style.display = "none";
    aboutPageHML.style.display = "";
  }
}


function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
