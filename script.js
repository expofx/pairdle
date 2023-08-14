const player = window.location.search.substring(1);
console.log(player)

let won = false;

let words = [];

const queueInterval = setInterval(async function(){
  async function getqueue(){
    const response = await fetch("http://34.134.131.133/queuestatus?player=" + player);
    const resp = await response.json();
    
    return resp["status"];
  }
  const status = await getqueue();
  if(status == "done"){
    document.getElementById("instructions").style.visibility = "visible";
    document.getElementById("loading").hidden = true;
    document.getElementById("main").hidden = false;
    const zz = setInterval(async function(){
      async function getgame(){
        const response = await fetch("http://34.134.131.133/api/gamestate?player=" + player);
        const resp = await response.json();
        return resp;
      }
      const r = await getgame();
      document.getElementById("you").innerHTML = r["you"];
      document.getElementById("opp").innerHTML = r["opp"];
      let table = document.getElementById("score-table");
      table.innerHTML = "";
      let r0 = table.insertRow(0);
      let c01 = r0.insertCell(0);
      let c02 = r0.insertCell(1);
      c01.innerText = "Guesses";
      c02.innerText = "Scores";
      for(let i = 0; i < r["history"].length; i++){
        let row = table.insertRow(1); // We are adding at the end
         
        // Create table cells
        let c1 = row.insertCell(0);
        let c2 = row.insertCell(1);
      
        // Add data to c1 and c2

        c1.innerText = r["history"][i]
        if(r["scores"].length > i){
          r["scores"][i] = (Math.round(1000*Math.pow((r["scores"][i] - 0.7)/0.3, 1))/1000);
          c2.innerText = r["scores"][i]
        }
        console.log(r['scores'][r['scores'].length-1]);
        if (!won && i == r["scores"].length-1 && r['scores'][r['scores'].length-1]==1.0){
          alert('You win!!');
          won = true;
          clearInterval(zz);
          won = true;
          if(r["scores"].length != 1){
                  document.getElementById("guessing").innerHTML = "Loading embedding graph...";
                  const resp1 = await fetch("/getimg?player=" + player);
                  const sta = await resp1.json();
                  let img = document.createElement("img");
                  img.src = "/img/" + player + ".png";
                  document.getElementById("instructions").innerHTML = "";
                  document.getElementById("instructions").style = "";
                  document.getElementById("instructions").appendChild(img);
                  console.log("HI");
                  document.getElementById("guessing").innerHTML = "";
                  document.getElementById("instructions").id = "";
          }
        }
      }

      let t = document.getElementById('word-table');
      if(t.innerHTML==''){
        words = r["words"]
        for(let i = 0; i < r["words"].length; i+=5){
        let row = t.insertRow(-1); 
         
        // Create table cells
        let c1 = row.insertCell(0);
        let c2 = row.insertCell(1);
        let c3 = row.insertCell(2);
        let c4 = row.insertCell(3);
        let c5 = row.insertCell(4);
      
        // Add data to c1 and c2
        c1.innerText = r["words"][i]
        c2.innerText = r["words"][i+1]
        c3.innerText = r["words"][i+2]
        c4.innerText = r["words"][i+3]
        c5.innerText = r["words"][i+4]
        
      }
      }
      
      
    }, 700);
    clearInterval(queueInterval);
  }
}, 700);

async function sendAnswer(){
  var answer = document.getElementById('pairdle-guess').value.toLowerCase().trim();
  if(words.includes(answer)){
    const response = await fetch("http://34.134.131.133/api/gameupd?player=" + player + "&word=" + answer);
  }
  else{
    alert('sucks to suck fr')
  }

 document.getElementById('pairdle-guess').value = '';
  
}

async function quitGame(){
  const response = await fetch("http://34.134.131.133/api/quitgame?player=" + player);
}

//document.getElementById("myBtn").addEventListener("click", sendAnswer);
