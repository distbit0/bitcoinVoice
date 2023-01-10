function createNavBar(){
    var navbarDivHTML = document.getElementById("navbarDiv");
    navbarDivHTML.innerHTML = `<ul id=\"navbar\">
 <li><a href=\"/\">Votes</a></li>
  <li><a href=\"/faq.html\">FAQ</a></li>
  <li><a href=\"/protocol.html\">Protocol</a></li>
  <li><a href=\"/api.html\">API</a></li>
  <li><a target=\"_blank\" href=\"https:\/\/github.com/picrypto/bitcoinVoice\">Github</a></li>
  <li><a target=\"_blank\" href=\"https:\/\/twitter.com/BitcoinVoice/">Twitter</a></li>
</ul>`;
    var navbarHTML = document.getElementById("navbar");
    var links = navbarHTML.getElementsByTagName("li");
    for (link of links){
        if (link.innerHTML.includes('\"' + window.location.pathname + '\"')){
            link.classList.add("active");
        }
    }
}

