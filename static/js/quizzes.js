function clearQuizHistory() {
    const postHistory = document.getElementById("postHistory");
    postHistory.innerHTML = "";
}

function addQuiz(messageJSON) {
    const postHistory = document.getElementById("postHistory");
    postHistory.innerHTML += postHTML(messageJSON);
    postHistory.scrollIntoView(false);
    postHistory.scrollTop = postHistory.scrollHeight - postHistory.clientHeight;
}

function postHTML(messageJSON) {
    const quizCategory = messageJSON.category;
    // This is kind of a hacky way to encode the ?'s (the reason for this is the request doesn't treat the ? as part of the string)
    // Decoce
    const quizTitle = messageJSON.title.replace(/_/g," ").replace("*", "?");
    // Encode
    const urlLookup = messageJSON.title.replace(/ /g,"_").replace("?", "*")
    const owner = messageJSON.username;

    const image = messageJSON.image

    let postHTML = "<a href=/view-quiz/"+urlLookup+">" + quizTitle + "</a><br>"
    /*
    let postHTML = "<form id='" + quizTitle + "'>"
    postHTML += "<h2 class='postTitle'>" + quizCategory + "</h2>";
    postHTML += "<h3 class='postTitle'>" + quizTitle + "</h2>";
    postHTML += "<p> Time Remaining: " + timeRemaining + "</p>";
    for (const [optionLabel, optionValue] of Object.entries(messageJSON.choices))
    {
        postHTML += "<input type='radio' id='" + optionLabel + "' name='user-answer' value='" + optionValue + "'></input>"
        postHTML += "<label for='" + optionLabel + "'>" + optionValue + "</label><br></br>"
    }
    if (image) {
        postHTML += "<img src='" + image + "' class='postImage'>";
    }
    postHTML += "<input type='button' value='Answer' onclick='answerQuiz(this.form)'>"
    postHTML += "</form>"
    postHTML += "<div class='postOwner'>Posted by: " + owner + "</div>";
    postHTML += "<div class='postLine'></div>";*/
    return postHTML;
}



function updatePostHistory() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearQuizHistory();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                console.log(message);
                addQuiz(message);
            }
        }
    }
    request.open("GET", "/quiz-history");
    request.send();
}



function onLoadRun() {
    updatePostHistory();
    setInterval(updatePostHistory, 1000);
}
