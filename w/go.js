(function () {
  var m = location.pathname.match(/^\/w\/([a-z0-9-]+)/i);
  var row = m && window.DA_LINKS && DA_LINKS[m[1].toLowerCase()];
  var url = DA_CHANNEL;
  if (row && row[1] && Date.now() >= Date.parse(row[1])) {
    url = "https://www.youtube.com/watch?v=" + row[0] + "&list=" + DA_LIST;
  }
  location.replace(url);
})();
