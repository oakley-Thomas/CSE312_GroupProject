function set_user(){
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
        if (username !== ""){
            element.innerHTML += "Welcome Back, ";
            element.innerHTML += "<br>";
            element.innerHTML += username;

            b1 = document.getElementById("button1");
            b1_text = document.getElementById("button1_text");
            b1.action = "/posts";
            b1_text.innerHTML = "Posts";

            b2 = document.getElementById("button2")
            b2_text = document.getElementById("button2_text");
            b2.action = "/";
            b2_text.innerHTML = "Logout";


        }
    }