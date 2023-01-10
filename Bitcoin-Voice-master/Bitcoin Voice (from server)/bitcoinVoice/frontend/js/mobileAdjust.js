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