function check_for_token(){
        const str = document.cookie;
        const cookies = str.split(';');
        var username = "";
        for (let idx = 0; idx < cookies.length; idx++){
            const c = cookies[idx].split("=");
            if(c[0] === "username"){
                username = c[1];
            }
        }
        var element = document.getElementById("welcome_message");

        element.innerHTML += "Welcome Back, ";
        element.innerHTML += "<br>";
        element.innerHTML += username;

        if (username !== ""){
            b1 = document.getElementById("button1");
            b1_text = document.getElementById("button1_text");
            b1.action = "/login";
            b1_text.innerHTML = "Renew Session";
        }
    }
function verifyEmail() {
    fetch('/verify_email', {
        method: 'POST',
    })
    .then(() => {
        console.log('Verification email sent.');
    })
    .catch(error => console.error('Error Verifying Email:', error));
}
