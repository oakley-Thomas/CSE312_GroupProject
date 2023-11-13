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

    request.open("GET", "/user_grades");
    request.send();

}

let lastQuestion = "";

function addGrade(data) {
    const tableNum = document.getElementById("tableNum");
    const questionHTML = (lastQuestion !== data.question) ? `<td>${data.question}</td>` : '<td></td>';
    tableNum.innerHTML += gradeHTML(questionHTML, data);
    lastQuestion = data.question;
}

function gradeHTML(questionHTML, data) {
    const grade = data.userGrades;
    return `<tr>
                ${questionHTML}
                <td>${grade}</td>
            </tr>`;
}

function clear() {
    const tableNum = document.getElementById("tableNum");
    tableNum.innerHTML = "";
}

document.addEventListener("DOMContentLoaded", update);