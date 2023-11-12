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
    const quizTitle = messageJSON.title;
    const timeRemaining = messageJSON.duration;
    const owner = messageJSON.username;
    const image = messageJSON.image
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
    postHTML += "<div class='postLine'></div>";
    return postHTML;
}

function answerQuiz(form) {
    var selectedRadioButton = form.querySelector("input[name='user-answer']:checked");
    var quizID = form.id
    if (selectedRadioButton){
        const post = { id: quizID, answer: selectedRadioButton.id};
        axios.post('/answer-quiz', post)
            .then(response => handleSubmission(response))
            .catch(error => console.error(error));
    }
    else{
        alert("Please choose an answer to submit.");
    }
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

function handleSubmission(response)
{
    if (response.data == "OK"){
        document.getElementById("postInput").innerHTML = '<h1>Submitted!</h1>'
    }
    else if (response.data == "Unauthenticated"){
        document.getElementById("postInput").innerHTML = '<h1>Sorry, log in to answer this quiz!</h1>'
    }
    setTimeout(function() { hideQuizCreator() }, 2500);

}

function onLoadRun() {
    updatePostHistory();
    setInterval(updatePostHistory, 5000);
}
