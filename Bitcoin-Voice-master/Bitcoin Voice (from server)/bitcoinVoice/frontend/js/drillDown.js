function setupPage() //called on initial load of page and also when "reset" button pressed
{
  window.setInterval(populatePublicLabelOutputs, 10*1000*60); //refresh every 10 mins
  clearScreen(); //for when this function is called to reset page and not on ititialisation
  getUiDefaults(); //get ui default parameters and insert them into UI fields
  extractUrlArguments(); //extract arguments from url and insert them into UI
  populatePublicLabelOutputs(); //populate pub label table
  mobileAdjust(); //adjust screen layout for phones
}

function extractUrlArguments() //extract arguments provided in the url from the main page and import them into the UI/webpage
{
    var coin = timePeriod = false; //Explained below...
    var timePeriodsHTML = document.getElementById("timePeriod");
    var publicLabelHTML = document.getElementById("publicLabel");
    var publicLabelDisplayHTML = document.getElementById("publicLabelDisplay");
    var onlyUnspentHTML = document.getElementById("onlyUnspent");
    var url = window.location.href.replace("#", "")
    url = new URL(url);
    var publicLabel = url.searchParams.get("publicLabel");
    try{// in case one of the following args isn't provided in the url, we use a try/catch statement
        var chainID = url.searchParams.get("chainID");
        var coin = ["btc","bch","btc_test"][chainID-1];
        var timePeriod = url.searchParams.get("timePeriod");
    }catch(e){}
    if (timePeriod){
        for (timePeriodHTML of timePeriodsHTML.options)
        {
            if (timePeriodHTML.text == timePeriod)
            {
                timePeriodHTML.selected = true
                timePeriodsHTML.value = timePeriodHTML.value;
            }
        }
    }
    if (coin)
    {
        selectCoin(coin);
    }

    publicLabelHTML.value = publicLabel; //inserts pub label into hidden persistence element for later access by other functions
    console.log(publicLabel);
    publicLabelDisplayHTML.innerHTML = escapeHtml(publicLabel); //inserts public label into text element which displays it at top of page
}
function populatePublicLabelOutputs(extend=false)
{
  var chainID = document.getElementById("chainID").value;
  var rowsCountHTML = document.getElementById("rowsCount");
  var rowsCount = parseInt(rowsCountHTML.value);
  var publicLabel = document.getElementById("publicLabel").value;
  var startDate = document.getElementById("timePeriod").value;
  var endDate = getCurrentDate();
  var publicLabelOutputTableHTML = document.getElementById("publicLabelOutputTable");
  var onlyUnspentHTML = document.getElementById("onlyUnspent");
  if (onlyUnspentHTML.checked){var onlyUnspent=1}else{var onlyUnspent = 0}
  var listLength = publicLabelOutputTableHTML.rows.length - 1; //0 indexed

  if (extend == false) //if we should simply add extend the table with more labels or overwrite it
  {
    publicLabelOutputTableHTML.innerHTML = "";//clear table
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
      var publicLabelOutputs = JSON.parse(APIResponseJSON);

      if (extend == false){//if resetting the table, create the header row with the column labels:
        var header = publicLabelOutputTableHTML.createTHead();
        var headerRow = header.insertRow(0);
        var txidHeader = headerRow.insertCell(0);
        var amountHeader = headerRow.insertCell(1);
        var creationDateHeader = headerRow.insertCell(2);
        var spentHeader = headerRow.insertCell(3);
        txidHeader.innerHTML = "<b>TXID</b>";
        if (chainID == 2 || chainID == 4){
            amountHeader.innerHTML = "<b>Amount (BCH)</b>";
        }
        else{
            amountHeader.innerHTML = "<b>Amount (BTC)</b>";
        }
        creationDateHeader.innerHTML = "<b>Creation Date</b>";
        spentHeader.innerHTML = "<b>Spent</b>";
      }//add pub label utxo rows
      var body = publicLabelOutputTableHTML.createTBody();
      for (var i = 0; i < publicLabelOutputs.length; i++)
      {
        var bodyRow = body.insertRow(i);
        var txid = bodyRow.insertCell(0);
        var amount = bodyRow.insertCell(1);
        var creationDate = bodyRow.insertCell(2);
        var spent = bodyRow.insertCell(3);
        if (chainID == 1){ //must use correct block explorer website link for each coin
            txid.innerHTML = "<a target='_blank' href='" + "https://explorer.bitcoin.com/btc/tx/" + publicLabelOutputs[i]["txid"] + "\'>" + publicLabelOutputs[i]["txid"] + "</a>";
        }
        if (chainID == 2){
            txid.innerHTML = "<a target='_blank' href='" + "https://explorer.bitcoin.com/bch/tx/" + publicLabelOutputs[i]["txid"] + "\'>" + publicLabelOutputs[i]["txid"] + "</a>";
        }
        if (chainID == 3){
            txid.innerHTML = "<a target='_blank' href='" + "https://live.blockcypher.com/btc-testnet/tx/" + publicLabelOutputs[i]["txid"] + "\'>" + publicLabelOutputs[i]["txid"] + "</a>";
        }
        amount.innerHTML = publicLabelOutputs[i]["amt"].toFixed(8);
        creationDate.innerHTML = timeConverter(publicLabelOutputs[i]["unixTimeCreated"])
        //if spent, display spend date
        if (publicLabelOutputs[i]["unixTimeSpent"] != 0){
            spent.innerHTML="Yes<br>" + timeConverter(publicLabelOutputs[i]["unixTimeSpent"]);
        }else{
            spent.innerHTML = "No";
        }
      }
    }
  };
  // gets the data applying the specified search criteria from server
  req.open("GET", "/api/?function=getPublicLabelOutputs&chainID=" + chainID + "&startPos=" + startPos + "&endPos=" + endPos + "&startDate=" + startDate + "&endDate=" + endDate + "&publicLabel=" + encodeURIComponent(publicLabel) + "&onlyUnspent=" + onlyUnspent, true);
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
  if (event){populatePublicLabelOutputs()}
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
  var onlyUnspent = uiDefaults["onlyUnspent"];
  var rowsCountHTML = document.getElementById("rowsCount");
  var timePeriodHTML = document.getElementById("timePeriod");
  var onlyUnspentHTML = document.getElementById("onlyUnspent");
  selectCoin(coin); //auto highlight (select) default coin in UI
  rowsCountHTML.value = rowsCount;
  rowsCountHTML.default = rowsCount;

  //check non-zero checkbox if specified
  if (onlyUnspent == 1){onlyUnspentHTML.checked=true}else{onlyUnspentHTML.checked=false}

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
  var publicLabelOutputTableHTML = document.getElementById("publicLabelOutputTable");
  var onlyUnspentHTML = document.getElementById("onlyUnspent");

  onlyUnspentHTML.checked = false;
  rowsCountHTML.value = "";
  timePeriodHTML.innerHTML = "";
  publicLabelOutputTableHTML.value = "";
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


function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var time = date + '/' + month + '/' + year;
  return time;
}

function escapeHtml(str) { //escapes any html in public labels, as some had html in them that altered the website
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    var label = div.innerHTML;
    label = urlify(label);
    return label;
}

function urlify(text) {
    var urlRegex = /(((https?:\/\/)|(www\.))[^\s]+)/g;
    //var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function(url,b,c) {
        var url2 = (c == 'www.') ?  'http://' +url : url;
        return '<a href="' +url2+ '" target="_blank">' + url + '</a>';
    })
}