async function getuid(){
  const response = await fetch("http://34.134.131.133/initmatch?username=" + document.getElementById("uname").value);
  const resp = await response.text();
  return resp;
}

async function enterlobby(){
  const id = await getuid();
  window.location = "/game.html?" + id;
}
