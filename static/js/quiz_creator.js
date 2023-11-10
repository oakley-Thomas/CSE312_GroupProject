function postData() {
    // Extract title
    const title = document.getElementById("Title").value;

    // Extract all choices and json encode
    const userAnswers = document.getElementsByName("user-answer");

    // Extract the correct answer
    var correct = "NONE";
    const choices = {}
    for (var i = 0; i < userAnswers.length; i++) {
        // Store "option1 : option1-text.value
        choice = userAnswers[i].id; // option0
        choiceName = choice + "-text";
        choiceValue = document.getElementById(choiceName).value;
        choices[choice] = choiceValue;
        if (userAnswers[i].checked){
            correct = userAnswers[i].value
        }
    }

    // Extract the duration
    const duration = document.getElementById("quizDuration").value;

    JSON.stringify(choices);

    if (correct != "NONE"){
        const post = { title: title, correct: correct, choices: choices, duration: duration};
        axios.post('/submit-quiz', post)
                .then(response => confirmSubmission())
                .catch(error => console.error(error));
    }
    else{
        alert("Please select the correct answer");
    }
    updatePostHistory();
}

function showQuizCreator()
{
    // Set the HTML
    document.getElementById("postInput").innerHTML = 
    `
    <form id="myForm">
    <input class="inputTitle" type="text" name="Title" id="Title" placeholder="Title: "><br>
    <div class="formLine"></div>
    <div class="multipleChoiceOptions">
        <!-- Choice 1 -->
        <input type="radio" id="option1" name="user-answer" value="option1">
        <label for="option1">
            <input class="user-entered-answer" type="text" name="option1-text" id="option1-text" placeholder="Enter answer here">
        </label><br>
        <!-- Choice 2 -->
        <input type="radio" id="option2" name="user-answer" value="option2">
        <label for="option2">
            <input class="user-entered-answer" type="text" name="option2-text" id="option2-text" placeholder="Enter answer here">
        </label><br>
        <!-- Choice 3 -->
        <input type="radio" id="option3" name="user-answer" value="option3">
        <label for="option3">
            <input class="user-entered-answer" type="text" name="option3-text" id="option3-text" placeholder="Enter answer here">
        </label><br>
        <br>
        <br>
        <div class="timer">
            <label for="quizDuration">Duration:</label>
            <select name="duration" id="quizDuration">
                <option value="1">1 Hour</option>
                <option value="6">6 Hours</option>
                <option value="12">12 Hours</option>
                <option value="24">24 Hours</option>
            </select>
        </div>
    </div>
    </form>`;
    // Change the button text and onclick functionality
    document.getElementById("sendButton").value = "Submit";
    document.getElementById("sendButton").onclick = function() { postData() }
    // Change back button onclick
    document.getElementById("backButton").onclick = function() { hideQuizCreator() }

}

function hideQuizCreator(inResponse)
{
    document.getElementById("postInput").innerHTML = '<h1>Welcome!</h1>'
    // Send button
    document.getElementById("sendButton").value = "Create Quiz!";
    document.getElementById("sendButton").onclick = function() { showQuizCreator() }

    document.getElementById("backButton").onclick = function() { returnHome() }
}

function returnHome() {
    location.replace("/");
}

function confirmSubmission()
{
    document.getElementById("postInput").innerHTML = '<h1>Submitted!</h1>'
    setTimeout(function() { hideQuizCreator() }, 2500);
}