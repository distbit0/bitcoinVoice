function setupPage() //called on initial load of page and also when "reset" button pressed
{
  window.setInterval(populateLabels, 10*1000*60); //refresh every 10 mins
  clearScreen(); //for when this function is called to reset page and not on ititialisation
  getUiDefaults(); //get ui default parameters and insert them into UI fields
  populateLabels(); //populate pub label table
  mobileAdjust(); //adjust screen layout for phones
}


function populateLabels(extend=false)
{
  var chainID = document.getElementById("chainID").value;
  var rowsCountHTML = document.getElementById("rowsCount");
  var rowsCount = parseInt(rowsCountHTML.value);
  var searchTerm = document.getElementById("searchBar").value;
  var timePeriodHTML = document.getElementById("timePeriod");
  var startDate = timePeriodHTML.value;
  var timePeriod = timePeriodHTML.options[timePeriodHTML.selectedIndex].text; //this would be "Day" or "All time" and retreivs the currently selected time period
  var endDate = getCurrentDate();
  var labelTableHTML = document.getElementById("labelTable");
  var listLength = labelTableHTML.rows.length - 1; //0 indexed

  if (extend == false)
  {
    labelTableHTML.innerHTML = "";//clear table
    var endPos = rowsCount; //start pos is the position of the end of the list
    var startPos = 0;
  }
  else
  {
    var endPos = listLength + rowsCount;
    var startPos = listLength;
  }
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200)//wait for response
    {
      var APIResponseJSON = req.responseText;
      var labels = JSON.parse(APIResponseJSON);

      if (extend == false){//if resetting the table, create the header row:
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
      }//add pub label rows
      var body = labelTableHTML.createTBody();
      for (var i = 0; i < labels.length; i++)
      {
        var bodyRow = body.insertRow(i);
        var rank = bodyRow.insertCell(0);
        var label = bodyRow.insertCell(1);
        var utxo = bodyRow.insertCell(2);
        rank.innerHTML = labels[i]["rank"];
        //add link to drill down page on each label
        var copyButtonHtml = '<input type="button" value="Copy Label" class="button" onclick="var pl = document.getElementById(\'publicLabel\'); pl.value = \'' + labels[i]['label'] + '\'; pl.type =\'\'; pl.select(); document.execCommand(\'copy\'); pl.type =\'hidden\';">';
        label.innerHTML = copyButtonHtml + ' <a href="/drillDown.html#?chainID=' + chainID + '&timePeriod=' + timePeriod + '&publicLabel=' + encodeURIComponent(labels[i]['label']) + '">' + escapeHtml(labels[i]['label']) + '</a>';
        utxo.innerHTML = labels[i]["amt"].toFixed(8)
      }
    }
  };
  // gets the data applying the specified search criteria from server
  req.open("GET", "/api/?function=getPublicLabelAggregates&chainID=" + chainID + "&startPos=" + startPos + "&endPos=" + endPos + "&startDate=" + startDate + "&endDate=" + endDate + "&searchTerm=" + searchTerm, true);
  req.send();

}


function selectCoin(coin, event=false)
{
  var chainID = document.getElementById("chainID");
  var activateHTML = document.getElementById(coin);
  var coins = ["btc","bch","btc_test"]

  activateHTML.classList.add("active");
  chainID.value = coins.indexOf(coin) + 1
  //delete selected coin from list of coins to de-activate
  coins.splice(coins.indexOf(coin), 1)

  // deactive other sections
  try { //only one element will be active but it deactivates all besides selected one so some will error
      for (chain of coins){
          var chainHTML = document.getElementById(chain);
          chainHTML.classList.remove("active");
      }
  } catch (e) {}
  //If this coin change resulted from a user clicking, update the pub labels
  if (event){populateLabels()}
}


function getUiDefaults()
{
  var req = new XMLHttpRequest();
  req.open("GET", "/api/?function=getUiDefaults", false);
  req.send();
  var APIResponseJSON = req.responseText;
  var uiDefaults = JSON.parse(APIResponseJSON);
  //extract UI defaults from json response from server
  var coin = uiDefaults["coin"];
  var rowsCount = uiDefaults["rowsCount"];
  var timePeriod = uiDefaults["timePeriod"];
  var timePeriods = uiDefaults["timePeriods"];
  var rowsCountHTML = document.getElementById("rowsCount");
  var timePeriodHTML = document.getElementById("timePeriod");
  selectCoin(coin); //auto highlight (select) default coin in UI
  rowsCountHTML.value = rowsCount;
  rowsCountHTML.default = rowsCount;

  //contruct the drop down list of time ranges
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
{//called when "reset" button is clicked and clears UI
  var rowsCountHTML = document.getElementById("rowsCount");
  var timePeriodHTML = document.getElementById("timePeriod");
  var searchBarHTML = document.getElementById("searchBar");
  var labelTableHTML = document.getElementById("labelTable");

  rowsCountHTML.value = "";
  timePeriodHTML.innerHTML = "";
  searchBarHTML.value = "";
  labelTableHTML.value = "";
}


function mobileAdjust(){ //adjust to mobile screen sizes atomatically
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


//########################Auxiliary Functions#####################

function getCurrentDate()
{
  Date.prototype.toDateInputValue = (function() {
  var local = new Date(this);
  local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
  return local.getTime()/1000;});
  return new Date().toDateInputValue()
}


function getSortedKeys(obj) { //dict sorting
    var keys = []; for(var key in obj) keys.push(key);
    return keys.sort(function(a,b){return obj[b]-obj[a]}).reverse();
}


function escapeHtml(str) { //escapes any html in public labels, as some had html in them that altered the website
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}