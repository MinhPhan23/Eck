function hideLogIn() {
    document.getElementById("login").style.display = "none";
}

function hideTweets() {
    document.getElementById("tweets").style.display = "none";
}

function hideError() {
    document.getElementById("error").style.display = "none";
}

function hideMakePost() {
    document.getElementById("makePost").style.display = "none";
}

function showLogIn() {
    document.getElementById("login").style.display = "block";
}

function showTweets() {
    document.getElementById("tweets").style.display = "block";
}

function showError() {
    document.getElementById("error").style.display = "block";
}

function showMakePost() {
    document.getElementById("makePost").style.display = "block";
}

function loadLogIn() {
    hideError();
    hideTweets();
    hideMakePost();
    showLogIn();
}

function getTweet(){
    // this is a closure, gets variables
    // from method it is in
    function loadTweet() {
        hideLogIn();
        hideError();
        showMakePost();
        showTweets();

        var content = xhr.responseText;
        var tweetObj = JSON.parse(content);
        var theDiv = document.getElementById("tweets");


        //create table list of tweets
        var output = "<table>\n";
        for (const key in tweetObj) {
            var content = tweetObj[key].split(":", 2)
            //id for the text field is T+id
            output += "<tr><td><label for=\"T"+ key +"\" >"+ content[0] +"</label><input type=\"text\" id=\"T"+ key +"\" name=\"Tweet\" value=\"" + content[1] + 
            "\"></td><td><button type=\"button\" id = "+ key +" onclick=updateTweet(this.id)>Update</button></td></tr>\n";
        }
        output += "<tr><td>Nothing below here</td></tr>";
        output += "</table>\n";
        theDiv.innerHTML = output;
    }

    // basic from 
    // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Using_XMLHttpRequest
    // probably will not work from localhost!
    var xhr = new XMLHttpRequest();
    // We want to get the IP address, but I don't want to talk too much about CORS!
    xhr.open("GET", "api/tweet");
    // hey, we can do this, but don't have to (in this case)
    xhr.setRequestHeader("Accept","application/json");

    xhr.onreadystatechange = function() {//Call a function when the state changes.
        if(xhr.readyState == 4) {
            if (xhr.status == 200) {
                loadTweet();
            }
            else if (xhr.status == 401){
                loadLogIn();
            }
            else if (xhr.status == 500){
                alert("The server is in maintenance, please try again later")
            }
        }
    }
    xhr.send();
}

function postLogin() {
    // basic from 
    // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Using_XMLHttpRequest
    // probably will not work from localhost!
    var xhr = new XMLHttpRequest();
    // We want to get the IP address, but I don't want to talk too much about CORS!
    xhr.open("POST", "api/login");
    
    var content = document.getElementById("usr").value;
    content = "usr="+content;
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {//Call a function when the state changes.
        if(xhr.readyState == 4) {
            if (xhr.status == 200) {
                getTweet();
            }
            else if (xhr.status == 500){
                alert("The server is in maintenance, please try again later")
            }
        }
    }
    xhr.send(content);
}

function postTweet() {
    var xhr = new XMLHttpRequest();
    // We want to get the IP address, but I don't want to talk too much about CORS!
    xhr.open("POST", "api/tweet");
    
    var content = document.getElementById("content").value;
    document.getElementById('content').value='';
    content = "content="+content;
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {//Call a function when the state changes.
        if(xhr.readyState == 4) {
            if (xhr.status == 200) {
                getTweet();
            }
            else if (xhr.status == 401){
                loadLogIn();
                alert("You are not logged in. Please log in.")
            }
            else if (xhr.status == 409){
                alert("You are posting too fast, please try again")
            }
            else if (xhr.status == 500){
                alert("The server is in maintenance, please try again later")
            }
        }
    }
    xhr.send(content);
}

function updateTweet(id) {
    var xhr = new XMLHttpRequest();
    // We want to get the IP address, but I don't want to talk too much about CORS!
    xhr.open("PUT", "api/tweet/"+id);
    
    var content = document.getElementById("T"+id).value;
    content = "content="+content;
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {//Call a function when the state changes.
        if(xhr.readyState == 4) {
            if (xhr.status == 200) {
                getTweet();
            }
            else if (xhr.status == 401){
                alert("You are not logged in. Please log in.")
                loadLogIn();
            }
            else if (xhr.status == 409){
                alert("You are updating too fast, please try again")
            }
            else if (xhr.status == 500){
                alert("The server is in maintenance, please try again later")
            }
        }
    }
    xhr.send(content);
}