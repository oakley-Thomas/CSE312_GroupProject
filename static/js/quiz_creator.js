function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

async function postData() {
    // Extract title
    const title = document.getElementById("Title").value;

    // Extract all choices and json encode
    const userAnswers = document.getElementsByName("user-answer");

    // add image
    const imageFile = document.getElementById("image").files[0];
    let image;
    if (imageFile) {
        image = await getBase64(imageFile);
    }

    // Extract the correct answer
    var correct = "NONE";
    const choices = {}
    for (var i = 0; i < userAnswers.length; i++) {
        // Store "option1 : option1-text.value
        choice = userAnswers[i].id; // option0
        choiceName = choice + "-text";
        choiceValue = document.getElementById(choiceName).value;
        choices[choice] = choiceValue;

        console.log(choice + ": " + choiceValue)
        if (userAnswers[i].checked){
            console.log("Correct Answer: " + userAnswers[i].value)
            correct = userAnswers[i].value
        }
    }
    JSON.stringify(choices);

    if (correct != "NONE"){
        const post = { title: title, correct: correct, choices: choices};
        if (image) {
            post.image = image;
        }
        axios.post('/submit-quiz', post)
                .then(response => console.log(response.data))
                .catch(error => console.error(error));
    }
    else{
        alert("Please select the correct answer");
    }

}

