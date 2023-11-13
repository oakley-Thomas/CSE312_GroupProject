function update() {
    const request = new XMLHttpRequest();

    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clear();
            const dataSet = JSON.parse(this.responseText);
            for (const data of dataSet) {
                addGrade(data);
            }
        }
    };

    request.open("GET", "/user_posted_quizzes_grades"); // replace path with whatever path in the approute
    request.send();

}

let lastQuestion = "";

function addGrade(data) {
    const tableNum = document.getElementById("tableNum");
//    for (const userGrade of data) {
        const questionHTML = (lastQuestion !== data.question) ? `<td>${data.question}</td>` : '<td></td>'; //checks to see if question equals prev question and if it does returns empty tabledata
//      tableNum.innerHTML += gradeHTML(questionHTML, userGrade);
        tableNum.innerHTML += gradeHTML(questionHTML, data)
        lastQuestion = data.question;
//    }
}

function gradeHTML(questionHTML, userGrade) {
    const username = userGrade.username;
    const grade = userGrade.grade;
    return `<tr>
                ${questionHTML}
                <td>${grade}</td>
                <td>${username}</td>
            </tr>`;
}


function clear() {
    const tableNum = document.getElementById("tableNum");
    tableNum.innerHTML = "";
}

document.addEventListener("DOMContentLoaded", update);